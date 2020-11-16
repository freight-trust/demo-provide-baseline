import random
import urllib
import requests
from libtrustbridge.websub.domain import Pattern
from src import repos
from src.loggers import logging


logger = logging.getLogger(__name__)


class PostNotificationUseCase:
    """
    Base use case to send message for notification
    """

    def __init__(self, notification_repo: repos.Notifications):
        self.notifications_repo = notification_repo

    def publish(self, message):
        topic = self.get_topic(message)
        job_payload = {
            'topic': topic,
            'content': {
                'id': message['id']
            }
        }
        logger.debug('publish notification %r', job_payload)
        self.notifications_repo.post_job(job_payload)

    @staticmethod
    def get_topic(message):
        raise NotImplementedError


class PublishNewMessageUseCase(PostNotificationUseCase):
    """
    Given new message,
    message id should be posted for notification"""

    @staticmethod
    def get_topic(message):
        return f"jurisdiction.{message['message']['receiver']}"


class NewMessagesNotifyUseCase:
    """
    Query shared database in order to receive new messages directed
    to the endpoint and send notification for each message.
    """

    def __init__(
        self,
        receiver: str = None,
        channel_repo: repos.Channel = None,
        notifications_repo: repos.Notifications = None
    ):
        self.channel_repo = channel_repo
        self.notifications_repo = notifications_repo
        self.receiver = receiver

    def execute(self):
        # receiving MessageResponse dict from channel-api
        queue_message = self.channel_repo.get_job()
        if not queue_message:
            return False
        queue_msg_id, message = queue_message
        # filtering messages based on the receiver property
        # if we're not the receiver we must skip a message
        if message['message']['receiver'] != self.receiver:
            return False
        PublishNewMessageUseCase(self.notifications_repo).publish(message)
        self.channel_repo.delete(queue_msg_id)
        return True


class InvalidCallbackResponse(Exception):
    pass


class DispatchMessageToSubscribersUseCase:
    """
    Used by the callbacks spreader worker.

    This is the "fan-out" part of the WebSub,
    where each event dispatched
    to all the relevant subscribers.
    For each event (notification),
    it looks-up the relevant subscribers
    and dispatches a callback task
    so that they will be notified.

    There is a downstream delivery processor
    that actually makes the callback,
    it is insulated from this process
    by the delivery outbox message queue.

    """

    def __init__(
        self,
        notifications_repo: repos.Notifications = None,
        delivery_outbox_repo: repos.DeliveryOutbox = None,
        subscriptions_repo: repos.Subscriptions = None
    ):
        self.notifications = notifications_repo
        self.delivery_outbox = delivery_outbox_repo
        self.subscriptions = subscriptions_repo

    def execute(self):
        job = self.notifications.get_job()
        if not job:
            return False
        return self.process(*job)

    def process(self, msg_id, payload):
        content = payload['content']
        topic = payload['topic']

        subscriptions = self._get_subscriptions(topic)

        for subscription in subscriptions:
            if not subscription.is_valid:
                continue
            job = {
                's': subscription.callback_url,
                'topic': topic,
                'payload': content,
            }
            logger.info("Scheduling notification of \n[%s] with the content \n%s", subscription.callback_url, content)
            self.delivery_outbox.post_job(job)

        self.notifications.delete(msg_id)

    def _get_subscriptions(self, topic):
        subscribers = self.subscriptions.get_subscriptions_by_pattern(Pattern(topic))
        if not subscribers:
            logger.info("Nobody to notify about the topic %s", topic)
        return subscribers


class DeliverCallbackUseCase:
    """
    Is used by a callback deliverer worker

    Reads queue delivery_outbox_repo consisting of tasks in format:
        (url, message)

    Then such message should be either sent to this URL and the task is deleted
    or, in case of any error, not to be re-scheduled again
    (up to MAX_ATTEMPTS times)

    """

    MAX_RETRY_TIME = 90
    MAX_ATTEMPTS = 3

    def __init__(
        self,
        delivery_outbox_repo: repos.DeliveryOutboxRepo = None,
        channel_url: str = None,
        topic_base_self_url: str = None
    ):
        topic_base_self_url = (
            topic_base_self_url
            if topic_base_self_url.endswith('/')
            else topic_base_self_url + '/'
        )
        self.topic_base_self_url = topic_base_self_url
        self.delivery_outbox = delivery_outbox_repo
        self.channel_url = channel_url

    def execute(self):
        self._last_retry_time = 0
        deliverable = self.delivery_outbox.get_job()
        if not deliverable:
            return

        queue_msg_id, payload = deliverable
        return self.process(queue_msg_id, payload)

    def process(self, queue_msg_id, job):
        subscribe_url = job['s']
        payload = job['payload']
        topic = job['topic']
        attempt = int(job.get('retry', 1))
        try:
            logger.debug('[%s] deliver notification to %s with payload: %s, topic: %s (attempt %s)',
                         queue_msg_id, subscribe_url, payload, topic, attempt)
            self._deliver_notification(subscribe_url, payload, topic)
        except InvalidCallbackResponse as e:
            logger.info("[%s] delivery failed", queue_msg_id)
            logger.exception(e)
            if attempt < self.MAX_ATTEMPTS:
                logger.info("[%s] re-schedule delivery", queue_msg_id)
                self._retry(subscribe_url, payload, topic, attempt)

        self.delivery_outbox.delete(queue_msg_id)

    def _retry(self, subscribe_url, payload, topic, attempt):
        logger.info("Delivery failed, re-schedule it")
        job = {'s': subscribe_url, 'payload': payload, 'retry': attempt + 1, 'topic': topic}
        self.delivery_outbox.post_job(job, delay_seconds=self._get_retry_time(attempt))

    def _deliver_notification(self, url, payload, topic):
        """
        Send the payload to subscriber's callback url

        https://indieweb.org/How_to_publish_and_consume_WebSub
        https://www.w3.org/TR/websub/#x7-content-distribution
        """

        logger.info("Sending WebSub payload \n    %s to callback URL \n    %s", payload, url)
        topic_self_url = urllib.parse.urljoin(self.topic_base_self_url, topic)
        header = {
            'Link': f'<{self.channel_url}>; rel="hub", <{topic_self_url}>; rel="self"'
        }
        try:
            resp = requests.post(url, json=payload, headers=header)
            if 200 <= resp.status_code < 300:
                return
        except requests.exceptions.RequestException as e:
            raise InvalidCallbackResponse("Connection error, url: %s", url) from e

        raise InvalidCallbackResponse("Subscription url %s seems to be invalid, returns %s", url, resp.status_code)

    def _get_retry_time(self, attempt):
        """exponential back off with jitter"""
        base = 8
        delay = min(base * 2 ** attempt, self.MAX_RETRY_TIME)
        jitter = random.uniform(0, delay / 2)
        # for easier integration testing, randomness is a very hard thing to test without mocking
        self._last_retry_time = int(delay / 2 + jitter)
        return self._last_retry_time
