from archspee.triggers import TriggerBase
import RPi.GPIO as GPIO
import os
import queue

_LOG_LEVEL = 'DEBUG'

TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "../../third_party/snowboy/resources/common.res")

class GpioButtonTrigger(TriggerBase):
    def __init__(self, trigger_ids, gpio_pins):
        self.__log_level = _LOG_LEVEL
        super(GpioButtonTrigger, self).__init__()
        self._queue = queue.Queue()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        assert len(gpio_pins) == len(trigger_ids)
        self.gpio_pin_trigger_map = {}
        for i in range(len(gpio_pins)):
            gpio_pin = gpio_pins[i]
            trigger_id = trigger_ids[i]
            self.gpio_pin_trigger_map[gpio_pin] = trigger_id
            GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(gpio_pin, GPIO.RISING, callback=lambda channel: self.button_clicked(gpio_pin, channel))

    def button_clicked(self, pin, channel):
        self.logger.debug('button %d pushed, channel=%d' % (pin, channel))
        self._queue.put(('PUSHED', pin))

    def check_audio_and_return_triggered_id(self, audio_data):
        try:
            queue_item = self._queue.get(block=False)
            assert queue_item[0] == 'PUSHED'
            pin = queue_item[1]
            return self.gpio_pin_trigger_map[pin]
        except queue.Empty:
            pass

        return -1
