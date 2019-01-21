from archspee.core import ArchspeeBaseClass
from abc import abstractmethod

class HandlerBase(ArchspeeBaseClass):
    def __init__(self, intent_handled_callback, error_handled_callback):
        super(HandlerBase, self).__init__()
        self.__intent_handled_callback = intent_handled_callback
        self.__error_handled_callback = error_handled_callback

    def invoke_intent_handled_callback(self, trigger_id, spoken_text, intent, entities, title, body, level):
        self.__intent_handled_callback(trigger_id, spoken_text, intent, entities, title, body, level)

    def invoke_error_handled_callback(self, trigger_id, status_code, response_text, title, body, level):
        self.__error_handled_callback(trigger_id, status_code, response_text, title, body, level)

    @abstractmethod
    def handle_intent(self, trigger_id, spoken_text, intent, entities):
        pass

    @abstractmethod
    def handle_error(self, trigger_id, status_code, response_text):
        pass
