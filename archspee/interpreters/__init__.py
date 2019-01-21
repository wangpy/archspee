from archspee.core import ArchspeeBaseClass
from abc import abstractmethod

class InterpreterBase(ArchspeeBaseClass):
    def __init__(self, intent_callback, error_callback):
        super(InterpreterBase, self).__init__()
        assert intent_callback is not None
        assert error_callback is not None
        self.__intent_callback = intent_callback
        self.__error_callback = error_callback

    def invoke_intent_callback(self, trigger_id, text, intent, entities):
        self.__intent_callback(trigger_id, text, intent, entities)

    def invoke_error_callback(self, trigger_id, status_code, response_text):
        self.__error_callback(trigger_id, status_code, response_text)

    @abstractmethod
    def interpret(trigger_id, text):
        pass
