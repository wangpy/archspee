from archspee.core import ArchspeeBaseClass
from abc import abstractmethod

class PresenterBase(ArchspeeBaseClass):
    def __init__(self, action_callback):
        super(PresenterBase, self).__init__()
        assert action_callback is not None
        self.__action_callback = action_callback
    
    def invoke_action_callback(self, action_name):
        self.__action_callback(action_name)

    @abstractmethod
    def on_listener_status(self, trigger_id, status, is_disabled):
        pass

    @abstractmethod
    def on_recognization_started(self, trigger_id):
        pass

    @abstractmethod
    def on_intent_handled(self, trigger_id, spoken_text, intent, entities, summary, body, level):
        pass

    @abstractmethod
    def on_error_handled(self, trigger_id, status_code, response_text, summary, body, level):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def terminate(self):
        pass
