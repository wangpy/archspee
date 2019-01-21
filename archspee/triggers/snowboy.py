from archspee.triggers import TriggerBase
from third_party.snowboy import snowboydetect
import os

_LOG_LEVEL = None

TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "../../third_party/snowboy/resources/common.res")

class SnowboyTrigger(TriggerBase):
    def __init__(self, trigger_ids, decoder_model, sensitivity=[], audio_gain=1.0):
        self.__log_level = _LOG_LEVEL
        super(SnowboyTrigger, self).__init__()

        self.trigger_ids = trigger_ids

        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=RESOURCE_FILE.encode(), model_str=model_str.encode())
        self.detector.SetAudioGain(audio_gain)
        self.detector.ApplyFrontend(False)
        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity * self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())


    def check_audio_and_return_triggered_id(self, audio_data):
        status = self.detector.RunDetection(audio_data)
        if status > 0:
            return self.trigger_ids[status-1]
        return -1
