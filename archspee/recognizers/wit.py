from archspee.recognizers import RecognizerBase
import grequests
import json
import traceback

_LOG_LEVEL = 'DEBUG'

_CONTENT_TYPE = 'audio/raw;encoding=signed-integer;bits=16;rate=16000;endian=little'

class WitRecognizer(RecognizerBase):
    def __init__(self, text_callback, intent_callback, error_callback, access_token):
        self.__log_level = _LOG_LEVEL
        super(WitRecognizer, self).__init__(text_callback, intent_callback, error_callback)
        assert access_token != ""
        self.access_token = access_token

    def response_callback(self, trigger_id, r, *args, **kwargs):
        # response example:
        # {
        #   "_text" : "you tube",
        #   "entities" : {
        #     "search_query" : [ {
        #       "suggested" : true,
        #       "confidence" : 0.93803,
        #       "value" : "tube",
        #       "type" : "value"
        #     } ]
        #   },
        #   "msg_id" : "1W3bRED50G49ot6SE"
        # }
        self.logger.debug("response received, trigger_id=%d, r.text=%s" % (trigger_id, r.text))
        try:
            response = json.loads(r.text)
            text = response['_text']
            entities = response['entities']
            intent = None
            if 'intent' in entities:
                intent = entities['intent'][0]['value']
                entities.pop('intent', None)
            self.invoke_intent_callback(trigger_id, text, intent, entities)
        except Exception:
            traceback.print_exc()
            self.logger.warning("exception occured")
            self.invoke_error_callback(trigger_id, r.status_code, r.text)

    def recognize(self, trigger_id, audio_data):
        url = 'https://api.wit.ai/speech?v=20160526'
        headers = {'Authorization': 'Bearer '+self.access_token, 'Content-Type': _CONTENT_TYPE}
        callback = lambda r, *args, **kwargs: self.response_callback(trigger_id, r, *args, **kwargs)
        hooks = {'response': [callback]}
        req = grequests.post(url, headers=headers, data=audio_data, hooks=hooks)
        job = grequests.send(req, grequests.Pool(1))
        self.logger.debug("request sent")
        
