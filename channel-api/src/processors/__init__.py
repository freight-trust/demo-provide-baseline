import time
from libtrustbridge.websub.processors import Processor


class SelfIteratingProcessor(Processor):
    def start(self):  # pragma: no cover
        for iteration in self:
            time.sleep(1)
