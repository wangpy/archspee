from archspee.core import ArchspeeBaseClass
from abc import abstractmethod

class TriggerBase(ArchspeeBaseClass):
    def __init__(self):
        super(TriggerBase, self).__init__()

    @abstractmethod
    def check_audio_and_return_triggered_id(self, audio_data):
        return -1
