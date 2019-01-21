from archspee.presenters import PresenterBase
from archspee.listeners import ListenerStatus

_LOG_LEVEL = None

class LogPresenter(PresenterBase):
    def __init__(self, action_callback, **kwargs):
        self.__log_level = _LOG_LEVEL
        super(LogPresenter, self).__init__(action_callback)
        self.status = ListenerStatus.standby
        self.disabled = False

    def on_listener_status(self, trigger_id, status, is_disabled):
        if status != self.status or is_disabled != self.disabled:
            self.logger.info('Status changed: status=%s, disabled=%d' % (repr(status), is_disabled))
            self.status = status
            self.disabled = is_disabled

    def on_recognization_started(self, trigger_id):
        self.logger.info('Recognization started')

    def on_intent_handled(self, trigger_id, spoken_text, intent, entities, summary, body, level):
        self.logger.info('Intent handled: %s, %s (%s)' % (summary, body, level))

    def on_error_handled(self, trigger_id, status_code, response_text, summary, body, level):
        self.logger.info('Error handled: %s, %s (%s)' % (summary, body, level))

    def start(self):
        self.logger.info('Log presenter started.');

    def terminate(self):
        self.logger.info('Log presenter terminated.');
