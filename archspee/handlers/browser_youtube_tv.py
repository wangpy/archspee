from archspee.handlers import HandlerBase
import subprocess
import time
import json
from urllib.parse import quote
from gi.repository import GLib

_LOG_LEVEL = 'DEBUG'

def subprocess_call(args):
    GLib.idle_add(subprocess.call, args)

def _open_browser(browser_exec, url, args=[]):
    cmds = ['xdotool', 'exec', browser_exec] + args
    cmds.append(url)
    subprocess_call(cmds)

def _xdotool(command_list):
    subprocess_call(['xdotool'] + command_list)

def _send_key(keystroke):
    _xdotool(['key', keystroke])

def _send_text_input(text):
    _xdotool(['type', text])

class BrowserYouTubeTVIntentHandler(HandlerBase):
    def __init__(self, intent_handled_callback, error_handled_callback,
                 browser_exec='chromium-browser',
                 args='',
                 homepage_url='https://www.youtube.com/tv/#/channel?c=UC4R8DWoMoI7CAwX8_LjQHig&resume',
                 search_url_prefix='https://www.youtube.com/tv/#/search?resume&q='):
        self.__log_level = _LOG_LEVEL
        super(BrowserYouTubeTVIntentHandler, self).__init__(intent_handled_callback, error_handled_callback)
        self.browser_exec = browser_exec
        self.browser_args = args
        self.search_url_prefix = search_url_prefix
        self.open_browser(homepage_url)

    def open_browser(self, url, args=""):
        _open_browser(self.browser_exec, url, args=[self.browser_args, args])

    def handle_error(self, trigger_id, status_code, response_text):
        self.invoke_error_handled_callback(trigger_id, status_code, response_text, 'Error occured', response_text, 'error')

    def handle_intent(self, trigger_id, spoken_text, intent, entities):
        self.logger.debug('handle_intent: %s, entities=%s' % (intent, json.dumps(entities)))
        notify_send = lambda summary, body, level: self.invoke_intent_handled_callback(trigger_id, spoken_text, intent, entities, summary, body, level)

        operation = 'noop'
        if intent is not None:
            operation = intent

        # check for special intent first (which implies the operation to perform), then the operation.
        if 'query' in entities: # operation == 'search_query'
            query = entities['query'][0]['value']
            notify_send('perform search_query: %s' % query, 'You spoke: '+spoken_text, 'info')
            #self.open_browser(self.search_url_prefix + quote(query))
            for _ in range(3):
                _send_key('Escape')
            _send_key('s')
            _send_text_input(query)
            _send_key('Return')
        elif 'index' in entities:
            index = entities['index'][0]['value']
            notify_send('select search result index=%d' % index, 'You spoke: '+spoken_text, 'info')
            for _ in range(6):
                _send_key('Down')
            time.sleep(0.5)
            for _ in range(index-1):
                _send_key('Right')
            time.sleep(0.5)
            _send_key('Return')
        elif 'move_direction' in entities:
            move_direction = entities['move_direction'][0]['value']
            count = 1
            if 'count' in entities:
                count = entities['count'][0]['value']
            notify_send('move %s %d times' % (move_direction, count), 'You spoke: '+spoken_text, 'info')
            move_direction_key_map = {
              'up': 'Up',
              'down': 'Down',
              'left': 'Left',
              'right': 'Right'
            }
            for _ in range(count):
                _send_key(move_direction_key_map[move_direction])
        elif 'topic' in entities:
            topic = entities['topic'][0]['value']
            notify_send('play random videos about %s' % topic, 'You spoke: '+spoken_text, 'info')
            self.open_browser('https://neverthink.tv/'+topic.replace(' ', '-'))
        elif operation == 'go_back':
            # put this in front of 'seek_direction' because it might detect 'back'
            notify_send('go back', 'You spoke: '+spoken_text, 'info')
            _send_key('Escape')
        elif 'seek_direction' in entities:
            seek_direction = entities['seek_direction'][0]['value']
            count = 3
            # TODO: extract duration from entities
            notify_send('seek %s %d times' % (seek_direction, count), 'You spoke: '+spoken_text, 'info')

            seek_direction_key_map = {
                'back': 'Left',
                'forward': 'Right'
            }
            _send_key('Up')
            time.sleep(0.5)
            _send_key('Up')
            for _ in range(count+1):
                time.sleep(0.2)
                _send_key(seek_direction_key_map[seek_direction])
            time.sleep(0.5)
            _send_key('Return')
        elif operation == 'page_pause_media' or operation == 'page_resume_media':
            notify_send('toggle media playing', 'You spoke: '+spoken_text, 'info')
            _send_key('space')
            _send_key('Escape')
        elif operation == 'page_select' or operation == 'skip_ad':
            notify_send('select current focused item', 'You spoke: '+spoken_text, 'info')
            _send_key('Return')
        else:
            notify_send('noop - do nothing', 'You spoke: '+spoken_text, 'discard')
