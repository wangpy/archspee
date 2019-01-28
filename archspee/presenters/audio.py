from archspee.presenters import PresenterBase
from archspee.listeners import ListenerStatus
import alsaaudio
from gi.repository import GLib
import subprocess

_LOG_LEVEL = None


class AudioPresenter(PresenterBase):
    def __init__(self, action_callback, toggle_mute_script=None):
        self.__log_level = _LOG_LEVEL
        super(AudioPresenter, self).__init__(action_callback)
        self.status = ListenerStatus.standby
        self.disabled = False
        self.is_silenced = False
        self.audio_mixer = None
        self.orig_volume = None
        self.toggle_mute_script = toggle_mute_script

    def maybe_execute_toggle_mute(self):
        if self.toggle_mute_script is not None:
            GLib.idle_add(subprocess.call, ['bash', self.toggle_mute_script])

    def on_listener_status(self, trigger_id, status, is_disabled):
        if status != self.status or is_disabled != self.disabled:
            should_silence = (status is ListenerStatus.waiting_for_silence 
                                or status is ListenerStatus.waiting_for_speech
                                or status is ListenerStatus.recording
                             )
            if should_silence != self.is_silenced:
                if should_silence:
                    self.audio_mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
                    self.logger.debug('Original volume: %d' % int(self.audio_mixer.getvolume()[0]))
                    self.orig_volume = int(self.audio_mixer.getvolume()[0])
                    self.audio_mixer.setvolume(int(self.orig_volume / 10))
                    self.maybe_execute_toggle_mute()
                    self.logger.debug('New volume: %d' % int(self.audio_mixer.getvolume()[0]))
                else:
                    self.logger.debug('Original volume: %d' % int(self.audio_mixer.getvolume()[0]))
                    self.audio_mixer.setvolume(self.orig_volume)
                    self.maybe_execute_toggle_mute()
                    self.logger.debug('New volume: %d' % int(self.audio_mixer.getvolume()[0]))
                    self.audio_mixer = None
                    self.orig_volume = None
                self.is_silenced = should_silence
            self.status = status
            self.disabled = is_disabled

    def on_recognization_started(self, trigger_id):
        pass

    def on_intent_handled(self, trigger_id, spoken_text, intent, entities, summary, body, level):
        pass

    def on_error_handled(self, trigger_id, status_code, response_text, summary, body, level):
        pass

    def start(self):
        pass

    def terminate(self):
        if self.audio_mixer is not None:
            self.logger.debug('Original volume: %d' % int(self.audio_mixer.getvolume()[0]))
            self.audio_mixer.setvolume(self.orig_volume)
            self.maybe_execute_toggle_mute()
            self.logger.debug('New volume: %d' % int(self.audio_mixer.getvolume()[0]))
            self.audio_mixer = None
            self.orig_volume = None
