from box import Box
from src import repos
from src.processors import SelfIteratingProcessor
from src.processors import use_cases


def NewMessagesObserver(config: Box = None):
    use_case = use_cases.NewMessagesNotifyUseCase(
        receiver=config.RECEIVER,
        channel_repo=repos.Channel(config.CHANNEL_REPO),
        notifications_repo=repos.Notifications(config.NOTIFICATIONS_REPO)
    )
    return SelfIteratingProcessor(use_case=use_case)
