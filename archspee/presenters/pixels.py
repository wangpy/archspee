from archspee.presenters import PresenterBase
from archspee.listeners import ListenerStatus

from third_party.pixels.pixels_2mic_hat import pixels

_LOG_LEVEL = None

class PixelsPresenter(PresenterBase):
    def __init__(self, action_callback, **kwargs):
        self.__log_level = _LOG_LEVEL
        super(PixelsPresenter, self).__init__(action_callback)
        self.status = ListenerStatus.standby
        self.processing = False
        self.disabled = False
        pixels.off()


    def on_listener_status(self, trigger_id, status, is_disabled):
        if status != self.status or is_disabled != self.disabled:
            if is_disabled:
                pixels.off()
            elif self.processing:
                pixels.think()
            elif status is ListenerStatus.waiting_for_silence:
                pixels.wakeup()
            elif status is ListenerStatus.waiting_for_speech:
                pixels.listen()
            elif status is ListenerStatus.recording:
                pixels.speak()
            elif status is ListenerStatus.standby:
                if self.status is ListenerStatus.recording:
                    pixels.think()
                else:
                    pixels.off()
            self.status = status
            self.disabled = is_disabled

    def on_recognization_started(self, trigger_id):
        self.processing = True
        self.on_listener_status(trigger_id, ListenerStatus.processing, self.disabled))

    def on_intent_handled(self, trigger_id, spoken_text, intent, entities, summary, body, level):
        self.processing = False
        self.on_listener_status(trigger_id, ListenerStatus.standby, self.disabled)

    def on_error_handled(self, trigger_id, status_code, response_text, summary, body, level):
        self.processing = False
        self.on_listener_status(trigger_id, ListenerStatus.standby, self.disabled)

    def start(self):
        pixels.off()

    def terminate(self):
        pixels.off()
