from archspee.listeners import ListenerBase, ListenerStatus
from third_party.snowboy import snowboydecoder
import audioop
import threading

_SPEECH_BUFFER_SEC = 5.0
_SILENCE_BUFFER_SEC = 0.5

_LOG_LEVEL = None

import collections
import pyaudio
import snowboydetect
import time
import wave
import os
import logging
from ctypes import *
from contextlib import contextmanager
import queue

def py_error_handler(filename, line, function, err, fmt):
    pass

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass

class RingBuffer(object):

    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        self._buf.extend(data)

    def get(self):
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp

class VoiceActivityDetector(object):
    def __init__(self, sensitivity=0.5, audio_gain=1, audio_bit_depth=16, audio_sample_rate=16000, logger=None):
        self.sensitivity = sensitivity
        self.audio_gain = audio_gain
        self.audio_bit_depth = audio_bit_depth
        self.audio_sample_rate = audio_sample_rate
        self.num_channels = 1
        self._queue = queue.Queue()
        self.logger = logger

        self.ring_buffer = RingBuffer(int(self.num_channels * self.audio_sample_rate * 5))
        self.silence_ring_buffer = RingBuffer(int(self.num_channels * self.audio_sample_rate / 2))

        # for vad
        self.energy_threshold = 10000 # given a high enough initial value, this will be adaptively tweaked
        self.dynamic_energy_threshold = True
        self.dynamic_energy_adjustment_damping = 0.15
        self.dynamic_energy_ratio = 1.5
        self.pause_threshold = 0.8

    def stop(self):
        self._queue.put(('STOP',));

    def start(self, vad_callback=None, sleep_time=0.03):
        self._running = True

        def audio_data_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        with no_alsa_error():
            self.audio = pyaudio.PyAudio()
        self.stream_in = self.audio.open(
            input=True, output=False,
            format=self.audio.get_format_from_width(
                self.audio_bit_depth / 8),
            channels=1,
            rate=self.audio_sample_rate,
            frames_per_buffer=2048,
            stream_callback=audio_data_callback)

        try:
            queue_task = self._queue.get(block=False)
            command = queue_task[0]
            if command == 'STOP':
                self.logger.debug('detect stop command')
                return
        except queue.Empty:
            pass

        self.logger.debug("detecting...")

        state = "PASSIVE"
        vad_status = -2
        pause_count = 0
        pause_buffer_count = int(self.pause_threshold * self.audio_sample_rate)
        while self._running is True:
            try:
                queue_task = self._queue.get(block=False)
                command = queue_task[0]
                if command == 'STOP':
                    self.logger.debug("detect voice break")
                    break
            except queue.Empty:
                pass

            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            seconds_per_buffer = float(len(data)) / self.audio_sample_rate
            energy = audioop.rms(data, int(self.audio_bit_depth / 8))  # energy of the audio signal
            self.logger.debug('audio energy=%f' % energy)
            if vad_status < 0:
                if energy > self.energy_threshold:
                    vad_status = 0
                    pause_count = 0
                elif self.dynamic_energy_threshold:
                    damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer  # account for different chunk sizes and rates
                    target_energy = energy * self.dynamic_energy_ratio
                    self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)
            else:
                if energy > self.energy_threshold:
                    pause_count = 0
                else:
                    pause_count += len(data)
                if pause_count > pause_buffer_count:
                    vad_status = -2

            status = vad_status
            if vad_callback is not None:
                status = vad_callback(vad_status, data)

            #small state machine to handle recording of phrase after keyword
            if state == "PASSIVE":
                if status > 0: #key word found
                    self.recordedData = []
                    self.recordedData.append(self.silence_ring_buffer.get())
                    self.recordedData.append(data)
                    silentCount = 0
                    recordingCount = 0
                    continue
                elif status < 0:
                    self.silence_ring_buffer.extend(data)

        self.logger.debug("finished.")

    def terminate(self):
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
        self._running = False

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass


class AlsaPortAudioListener(ListenerBase):
    def __init__(self, check_trigger_callback, audio_data_callback, status_callback,
                 sensitivity=0.5, audio_gain=1.0,
                 audio_bit_depth=16, audio_sample_rate=16000):
        self.__log_level = _LOG_LEVEL
        super(AlsaPortAudioListener, self).__init__(check_trigger_callback, audio_data_callback, status_callback)
        self.detector = VoiceActivityDetector(sensitivity, audio_gain, audio_bit_depth, audio_sample_rate, logger=self.logger)
        buffer_size_sec = (audio_bit_depth / 8) * audio_sample_rate
        self.speech_ring_buffer = snowboydecoder.RingBuffer(size=int(buffer_size_sec * _SPEECH_BUFFER_SEC))
        self.silence_ring_buffer = snowboydecoder.RingBuffer(size=int(buffer_size_sec * _SILENCE_BUFFER_SEC))
        self.audio_status = -2
        self.status = ListenerStatus.standby
        self.disabled = False
        self.triggered_id = None
        self.continuous_for_trigger_id = None
        self.interrupted = False
        self.thread = None

    def _vad_callback(self, audio_status, data):
        check_trigger_result = self.invoke_check_trigger_callback(data)

        # detect state transition
        if self.status is ListenerStatus.standby and not self.disabled:
            if (self.continuous_for_trigger_id is not None and audio_status >= 0) or check_trigger_result > 0:
                if self.continuous_for_trigger_id is None:
                    self.triggered_id = check_trigger_result
                    self.status = ListenerStatus.waiting_for_silence
                else:
                    self.triggered_id = self.continuous_for_trigger_id
                    self.status = ListenerStatus.recording
        elif self.status is ListenerStatus.waiting_for_silence:
            if audio_status < 0:
                self.status = ListenerStatus.waiting_for_speech
        elif self.status is ListenerStatus.waiting_for_speech:
            if audio_status >= 0:
                self.status = ListenerStatus.recording
        elif self.status is ListenerStatus.recording:
            if audio_status < 0:
                self.invoke_audio_data_callback(self.triggered_id, self.speech_ring_buffer.get())
                self.triggered_id = None
                self.status = ListenerStatus.standby

        # this must be after state transition so it can currently record current audio data frame if needed
        if self.status is ListenerStatus.recording:
            silence_data = self.silence_ring_buffer.get()
            if len(silence_data) > 0:
                self.speech_ring_buffer.extend(silence_data)
            self.speech_ring_buffer.extend(data)
        else:
            self.silence_ring_buffer.extend(data)

        if audio_status != self.audio_status and not (self.status is ListenerStatus.standby and self.disabled):
            self.logger.info('activity level changed to %d, current_state = %s' % (audio_status, repr(self.status)))
        self.audio_status = audio_status
        self.invoke_status_callback(self.triggered_id, self.status, self.disabled)

        if check_trigger_result > 0:
            return check_trigger_result
        else:
            return audio_status

    def start(self):
        def main_loop():
            self.logger.warning('Listening...')
            self.detector.start(vad_callback=self._vad_callback,
                                sleep_time=0.03)
            self.logger.warning('Terminating...')
            self.detector.terminate()
        self.thread = threading.Thread(target=main_loop)
        self.thread.start()

    def terminate(self):
        self.detector.stop()
