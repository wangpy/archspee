from archspee.core import ArchspeeBaseClass
from abc import abstractmethod

class RecognizerBase(ArchspeeBaseClass):
    def __init__(self, text_callback, intent_callback, error_callback):
        super(RecognizerBase, self).__init__()
        assert text_callback is not None
        assert intent_callback is not None
        assert error_callback is not None
        self.__text_callback = text_callback
        self.__intent_callback = intent_callback
        self.__error_callback = error_callback

    def invoke_text_callback(self, trigger_id, text):
        self.__text_callback(trigger_id, text)

    def invoke_intent_callback(self, trigger_id, text, intent, entities):
        self.__intent_callback(trigger_id, text, intent, entities)

    def invoke_error_callback(self, trigger_id, status_code, response_text):
        self.__error_callback(trigger_id, status_code, response_text)

    @abstractmethod
    def recognize(trigger_id, audio_data):
        pass
