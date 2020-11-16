from box import Box
from src import repos
from src.processors import SelfIteratingProcessor
from src.processors import use_cases


def CallbackSpreader(config: Box = None):
    use_case = use_cases.DispatchMessageToSubscribersUseCase(
        notifications_repo=repos.Notifications(config.NOTIFICATIONS_REPO),
        delivery_outbox_repo=repos.DeliveryOutbox(config.DELIVERY_OUTBOX_REPO),
        subscriptions_repo=repos.Subscriptions(config.SUBSCRIPTIONS_REPO),
    )
    return SelfIteratingProcessor(use_case=use_case)
