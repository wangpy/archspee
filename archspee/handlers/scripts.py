from archspee.handlers import HandlerBase
import subprocess
import json
from pathlib import Path
import shlex
from gi.repository import GLib

_LOG_LEVEL = 'DEBUG'

def subprocess_call(args):
    GLib.idle_add(subprocess.call, args)

class ScriptsIntentHandler(HandlerBase):
    def __init__(self, intent_handled_callback, error_handled_callback,
                 scripts_path='intent_scripts'):
        self.__log_level = _LOG_LEVEL
        super(ScriptsIntentHandler, self).__init__(intent_handled_callback, error_handled_callback)
        self.scripts_path = scripts_path

    def open_browser(self, url, args=""):
        _open_browser(self.browser_exec, url, args=[self.browser_args, args])

    def handle_error(self, trigger_id, status_code, response_text):
        self.invoke_error_handled_callback(trigger_id, status_code, response_text, 'Error occured', response_text, 'error')

    def handle_intent(self, trigger_id, spoken_text, intent, entities):
        self.logger.debug('handle_intent: %s, entities=%s' % (intent, json.dumps(entities)))
        notify_send = lambda summary, body, level: self.invoke_intent_handled_callback(trigger_id, spoken_text, intent, entities, summary, body, level)

        # TODO: add argument support

        script_filename = shlex.quote(intent).replace('/', '\\/') + '.sh'
        p = Path(self.scripts_path) / script_filename
        try:
            script_pathname = str(p.resolve())
            subprocess_call(['bash', script_pathname])
            notify_send('Execute script: %s' % script_filename, 'You spoke: '+spoken_text, 'info')
        except:
            notify_send('Script not found: %s' % script_filename, 'You spoke: '+spoken_text, 'discard')
