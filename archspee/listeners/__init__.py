from enum import Enum
from archspee.core import ArchspeeBaseClass
from abc import abstractmethod

class ListenerStatus(Enum):
    standby = 0
    waiting_for_silence = 1
    waiting_for_speech = 2
    recording = 3
    processing = 4


class ListenerBase(ArchspeeBaseClass):
    def __init__(self, check_trigger_callback, audio_data_callback, status_callback):
        super(ListenerBase, self).__init__()
        assert check_trigger_callback is not None
        assert audio_data_callback is not None
        assert status_callback is not None
        self.__check_trigger_callback = check_trigger_callback
        self.__audio_data_callback = audio_data_callback
        self.__status_callback = status_callback
        self.status = ListenerStatus.standby
        self.disabled = False

    def set_disabled(self, disabled):
        self.disabled = disabled

    def invoke_check_trigger_callback(self, audio_data):
        return self.__check_trigger_callback(audio_data)

    def invoke_audio_data_callback(self, triggered_id, audio_data):
        self.__audio_data_callback(triggered_id, audio_data)

    def invoke_status_callback(self, triggered_id, status, disabled):
        self.__status_callback(triggered_id, status, disabled)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def terminate(self):
        pass
