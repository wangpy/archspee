from archspee.core import ArchspeeBaseClass
import importlib
import traceback
import time

_LOG_LEVEL = 'WARNING'

try:
    from custom import config
except ImportError:
    print('Config does not exists. Load default config.')
    from archspee import default_config as config

def _instantiate_class(fqname, **kwargs):
    last_dot_index = fqname.rfind('.')
    assert last_dot_index > 0
    module_name = fqname[0:last_dot_index]
    class_name = fqname[last_dot_index+1:]
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    instance = class_(**kwargs)
    return instance

class ArchspeeMain(ArchspeeBaseClass):
    def __init__(self, config):
        self.__log_level = _LOG_LEVEL
        super(ArchspeeMain, self).__init__()
        assert config is not None
        self.init()

    def init(self):
        self.listeners = []
        self.triggers = []
        self.presenters = []
        self.recognizers = {}
        self.interpreters = {}
        self.handlers = {}
        self.init_listeners(config.LISTENERS)
        self.init_triggers(config.TRIGGERS)
        self.init_presenters(config.PRESENTERS)
        self.init_recognizers(config.RECOGNIZERS)
        self.init_interpreters(config.INTERPRETERS)
        self.init_handlers(config.HANDLERS)

    def init_listeners(self, listener_args_list):
        for listener_args in listener_args_list:
            (class_fqname, kwargs) = listener_args
            self.logger.info("Create listener: %s" % class_fqname)
            self.listeners.append(_instantiate_class(class_fqname,
                                                    check_trigger_callback=self.handle_check_trigger,
                                                    audio_data_callback=self.handle_audio_data,
                                                    status_callback=self.handle_listener_status,
                                                    **kwargs))

    def init_triggers(self, trigger_args_list):
        for trigger_args in trigger_args_list:
            (class_fqname, kwargs) = trigger_args
            self.logger.info("Create trigger: %s" % class_fqname)
            self.triggers.append(_instantiate_class(class_fqname, **kwargs))
 
    def init_presenters(self, presenter_args_list):
        for presenter_args in presenter_args_list:
            (class_fqname, kwargs) = presenter_args
            self.logger.info("Create presenter: %s" % class_fqname)
            self.presenters.append(_instantiate_class(class_fqname,
                                                     action_callback=self.handle_action,
                                                     **kwargs))

    def init_recognizers(self, recognizer_args_list):
        for recognizer_args in recognizer_args_list:
            (trigger_ids, class_fqname, kwargs) = recognizer_args
            self.logger.info("Create recognizer: %s for trigger IDs %s" % (class_fqname, repr(trigger_ids)))
            recognizer = _instantiate_class(class_fqname,
                                           text_callback=self.handle_recognized_text,
                                           intent_callback=self.handle_intent,
                                           error_callback=self.handle_error,
                                           **kwargs)
            if not isinstance(trigger_ids, list):
                trigger_ids = [trigger_ids]
            for trigger_id in trigger_ids:
                self.recognizers[trigger_id] = recognizer

    def init_interpreters(self, interpreter_args_list):
        for interpreter_args in interpreter_args_list:
            (trigger_ids, class_fqname, kwargs) = interpreter_args
            self.logger.info("Create interpreter: %s for trigger IDs %s" % (class_fqname, repr(trigger_ids)))
            interpreter = _instantiate_class(class_fqname,
                                           intent_callback=self.handle_intent,
                                           error_callback=self.handle_error,
                                           **kwargs)
            if not isinstance(trigger_ids, list):
                trigger_ids = [trigger_ids]
            for trigger_id in trigger_ids:
                self.interpreters[trigger_id] = interpreter

    def init_handlers(self, handler_args_list):
        for handler_args in handler_args_list:
            (trigger_ids, class_fqname, kwargs) = handler_args
            self.logger.info("Create handler: %s for trigger IDs %s" % (class_fqname, repr(trigger_ids)))
            handler = _instantiate_class(class_fqname,
                                        intent_handled_callback=self.present_intent_handled,
                                        error_handled_callback=self.present_error_handled,
                                        **kwargs)
            if not isinstance(trigger_ids, list):
                trigger_ids = [trigger_ids]
            for trigger_id in trigger_ids:
                self.handlers[trigger_id] = handler

    def handle_check_trigger(self, audio_data):
        for trigger in self.triggers:
            result = trigger.check_audio_and_return_triggered_id(audio_data)
            if result > 0:
                return result
        return -1

    def handle_audio_data(self, trigger_id, audio_data):
        self.logger.debug('handle_audio_data trigger_id=%d, audio_data_len=%d' % ((trigger_id, len(audio_data))))
        if trigger_id in self.recognizers:
            self.recognizers[trigger_id].recognize(trigger_id, audio_data)
        else:
            self.logger.warning('unhandled handle_audio_data trigger_id=%d' % trigger_id)
            return
        for presenter in self.presenters:
            presenter.on_recognization_started(trigger_id)

    def handle_listener_status(self, trigger_id, status, is_disabled):
        for presenter in self.presenters:
            presenter.on_listener_status(trigger_id, status, is_disabled)

    def handle_action(self, action):
        if action == 'panic':
            self.terminate()
        elif action == 'disable':
            for listener in self.listeners:
                listener.set_disabled(True)
        elif action == 'enable':
            for listener in self.listeners:
                listener.set_disabled(False)

    def handle_recognized_text(self, trigger_id, spoken_text):
        if trigger_id in self.interpreters:
            self.interpreters[trigger_id].interpret(trigger_id, spoken_text)
        else:
            self.logger.warning('unhandled handle_recognized_text trigger_id=%d' % trigger_id)

    def handle_intent(self, trigger_id, spoken_text, intent, entities):
        self.logger.debug('handle_intent trigger_id=%d, spoken_text=%s' % (trigger_id, spoken_text))
        if trigger_id in self.handlers:
            self.handlers[trigger_id].handle_intent(trigger_id, spoken_text, intent, entities)
        else:
            self.logger.warning('unhandled handle_intent trigger_id=%d' % trigger_id)

    def handle_error(self, trigger_id, status_code, response_text):
        self.logger.warning('handle_error trigger_id=%d, status_code=%d, response_text=%s' % (trigger_id, status_code, response_text))
        if trigger_id in self.handlers:
            self.handlers[trigger_id].handle_error(trigger_id, status_code, response_text)
        else:
            self.logger.warning('unhandled handle_error trigger_id=%d' % trigger_id)

    def present_intent_handled(self, trigger_id, spoken_text, intent, entities, summary, body, level):
        for presenter in self.presenters:
            presenter.on_intent_handled(trigger_id, spoken_text, intent, entities, summary, body, level)

    def present_error_handled(self, trigger_id, status_code, response_text, summary, body, level):
         for presenter in self.presenters:
            presenter.on_error_handled(trigger_id, status_code, response_text, summary, body, level)
       
    def start(self):
        for listener in self.listeners:
            try:
                self.logger.debug('starting listener %s' % repr(listener))
                listener.start()
                self.logger.debug('started listener %s' % repr(listener))
            except:
                traceback.print_exc()
        for presenter in self.presenters:
            try:
                self.logger.debug('starting presenter %s' % repr(presenter))
                presenter.start()
                self.logger.debug('started presenter %s' % repr(presenter))
            except:
                traceback.print_exc()

    def terminate(self):
        for listener in self.listeners:
            listener.terminate()
        for presenter in self.presenters:
            presenter.terminate()

def archspee_main():
    instance = ArchspeeMain(config)

    import signal
    def signal_handler(signal, frame):
        instance.logger.warn('Ctrl-C received')
        instance.terminate()

    signal.signal(signal.SIGINT, signal_handler)

    instance.start()

if __name__ == '__main__':
    archspee_main()
