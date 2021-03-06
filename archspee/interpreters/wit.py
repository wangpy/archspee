from archspee.interpreters import InterpreterBase
import grequests
import json
import traceback
import threading
import time
from urllib.parse import quote

_LOG_LEVEL = 'DEBUG'

class WitInterpreter(InterpreterBase):
    def __init__(self, intent_callback, error_callback, access_token):
        self.__log_level = _LOG_LEVEL
        super(WitInterpreter, self).__init__(intent_callback, error_callback)
        assert access_token != ""
        self.access_token = access_token
        self.request_pool = grequests.Pool(2)

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
        print("response received, trigger_id=%d, r.text=%s" % (trigger_id, r.text))
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

    def req_task(self, trigger_id, text):
        url = 'https://api.wit.ai/message?v=20160526&q=' + quote(text)
        self.logger.debug('request URL=%s' % url)
        headers = {'Authorization': 'Bearer '+self.access_token}
        callback = lambda r, *args, **kwargs: self.response_callback(trigger_id, r, *args, **kwargs)
        hooks = {'response': [callback]}
        req = grequests.get(url, headers=headers, hooks=hooks, timeout=10)
        job = grequests.send(req, self.request_pool)
        time.sleep(5) # FIXME: necessary to receive response callback

    def interpret(self, trigger_id, text):
        req_task = lambda: self.req_task(trigger_id, text)
        req_thread = threading.Thread(target=req_task)
        req_thread.start()
