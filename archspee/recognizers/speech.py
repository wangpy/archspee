from archspee.recognizers import RecognizerBase
import traceback
import threading
import os
import time
import speech_recognition as sr
from gi.repository import GLib

_LOG_LEVEL = 'DEBUG'

class GoogleSpeechRecognizer(RecognizerBase):
    def __init__(self, text_callback, intent_callback, error_callback, key=None, language="en-US"):
        self.__log_level = _LOG_LEVEL
        super(GoogleSpeechRecognizer, self).__init__(text_callback, intent_callback, error_callback)
        self.key = key
        self.language = language
        self.recognizer = sr.Recognizer()

    def req_task(self, trigger_id, audio_data):
        self.logger.debug('req_task trigger_id=%d audio_len=%d' % (trigger_id, len(audio_data)))
        try:
            audio = sr.AudioData(audio_data, 16000, 2)
            try:
                text = self.recognizer.recognize_google(audio, key=self.key, language=self.language)
            except sr.UnknownValueError: # no speech recognition result in response, probably empty
                text = ''
            self.logger.debug('speech recognition response: %s' % text)
            self.invoke_text_callback(trigger_id, text)
        except:
            traceback.print_exc()
            self.invoke_error_callback(trigger_id, 500, '')

    def recognize(self, trigger_id, audio_data):
        #req_task = lambda: self.req_task(trigger_id, audio_data)
        #req_thread = threading.Thread(target=req_task)
        #req_thread.start()
        self.logger.debug('recognize trigger_id=%d audio_len=%d' % (trigger_id, len(audio_data)))
        GLib.idle_add(self.req_task, trigger_id, audio_data)
