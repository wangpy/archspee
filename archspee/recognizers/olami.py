from archspee.recognizers import RecognizerBase
from third_party.olami_asrapi import SpeechAPISample
import traceback
import threading
import json
import wave
import os
import time
from gi.repository import GLib

_LOG_LEVEL = 'DEBUG'

_OLAMI_API_LOCALIZATION = 'https://tw.olami.ai/cloudservice/api'

def _pack_to_pcm_data(audio_data, nchannels=1, sampwidth=16, samprate=16000):
    filename = 'tmp' + str(int(time.time())) + '.wav'
    wf = wave.open(filename, 'wb')
    wf.setnchannels(nchannels)
    wf.setsampwidth(int(sampwidth / 8))
    wf.setframerate(samprate)
    wf.writeframes(audio_data)
    wf.close()
    with open(filename, "rb") as audioFile:
        af = audioFile.read()
        bAudioData = bytearray(af)
    os.remove(filename)
    return bAudioData

class OlamiRecognizer(RecognizerBase):
    def __init__(self, text_callback, intent_callback, error_callback, app_key="", app_secret="", api_localization=_OLAMI_API_LOCALIZATION):
        self.__log_level = _LOG_LEVEL
        super(OlamiRecognizer, self).__init__(text_callback, intent_callback, error_callback)
        assert app_key != "" and app_secret != ""
        self.asr_api = SpeechAPISample()
        self.asr_api.setLocalization(api_localization)
        self.asr_api.setAuthorization(app_key, app_secret)

    def process_response(self, trigger_id, text, response_obj):
        # {
        #   "data": {
        #     "nli": [
        #       {
        #         "desc_obj": {
        #           "result": "那就太好了，因為我也是！",
        #           "status": 0
        #         },
        #         "semantic": [
        #           {
        #             "app": "cc",
        #             "input": "我愛歐拉蜜",
        #             "slots": [ ],
        #             "modifier": [ ],
        #             "customer": "xxxxxxxxxxxxxxxxxxxxxxxx"
        #           }
        #         ],
        #         "type": "cc"
        #       }
        #     ]
        #   },
        #   "status": "ok"
        # }
        
        if 'data' not in response_obj or 'nli' not in response_obj['data']:
            self.invoke_error_callback(trigger_id, 400, 'interpretation failed: '+json.dumps(response_obj))
            return

        nli = response_obj['data']['nli'][0]
        if 'semantic' not in nli:
            if 'desc_obj' in nli and 'result' in nli['desc_obj']:
                self.invoke_intent_callback(trigger_id, text, None, {})
            else:
                self.invoke_error_callback(trigger_id, 400, 'interpretation failed: '+json.dumps(response_obj))
            return

        semantic = nli['semantic'][0]
        intent = None
        if len(semantic['modifier']) > 0:
            intent = semantic['modifier'][0]
        entities = {}
        for slot in semantic['slots']:
            name = slot['name']
            if not name in entities:
                entities[name] = []
            if 'num_detail' in slot:
                slot['text_value'] = slot['value']
                slot['value'] = int(slot['num_detail']['recommend_value'])
            entities[name].append(slot)

        self.invoke_intent_callback(trigger_id, text, intent, entities)

    def req_task(self, trigger_id, audio_data):
        response_string = ''
        try:
            # submit audio
            wav_audio_data = _pack_to_pcm_data(audio_data)
            response_string = self.asr_api.sendAudioData(self.asr_api.API_NAME_ASR, "nli,seg", True, wav_audio_data, False)
            self.logger.debug('submit audio response_string: %s' % response_string)
            response_obj = json.loads(response_string)
            if response_obj['status'] != 'ok':
                self.invoke_error_callback(trigger_id, 400, 'submit audio data failed: '+response_string)
                return
            # poll recognition result
            while (True):
                response_string = self.asr_api.getRecognitionResult(self.asr_api.API_NAME_ASR, "nli,seg")
                self.logger.debug('get result response_string: %s' % response_string)
                response_obj = json.loads(response_string)
                if response_obj['status'] != 'ok':
                    self.invoke_error_callback(trigger_id, 400, 'get recognition result failed: '+response_string)
                    return
                if (response_obj['data']['asr']['status'] > 0
                    or not response_obj['data']['asr']['final'] 
                    or 'nli' not in response_obj['data']):
                    time.sleep(1)
                    continue
                text = response_obj['data']['asr']['result']
                self.process_response(trigger_id, text, response_obj)
        except:
            traceback.print_exc()
            self.invoke_error_callback(trigger_id, 500, response_string)

    def recognize(self, trigger_id, audio_data):
        req_task = lambda: self.req_task(trigger_id, audio_data)
        req_thread = threading.Thread(target=req_task)
        req_thread.start()
