from box import Box
from src import repos
from src.processors import SelfIteratingProcessor
from src.processors import use_cases


def CallbackDelivery(config: Box = None):
    use_case = use_cases.DeliverCallbackUseCase(
        delivery_outbox_repo=repos.DeliveryOutbox(config.DELIVERY_OUTBOX_REPO),
        topic_base_self_url=config.TOPIC_BASE_SELF_URL,
        channel_url=config.CHANNEL_URL
    )
    return SelfIteratingProcessor(use_case=use_case)
