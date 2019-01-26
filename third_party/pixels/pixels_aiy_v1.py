import time
import queue
import threading
import RPi.GPIO as GPIO

_GPIO_PIN = 25

class Pixels:

    def __init__(self):
        self.is_light_on = 1
        self.count_down = 0
        self.light_on_count = 0
        self.light_off_count = 0

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(_GPIO_PIN, GPIO.OUT)
        self.next = threading.Event()
        self.queue = queue.Queue()
        self.off()

        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()



    def wakeup(self, direction=0):
        self.next.set()
        self.queue.put((1, 1))

    def listen(self):
        self.next.set()
        self.queue.put((3, 3))

    def think(self):
        self.next.set()
        self.queue.put((5, 5))

    def speak(self):
        self.next.set()
        self.queue.put((10, 0))

    def off(self):
        self.next.set()
        self.queue.put((0, 10))

    def _set_light_on(self, on):
        pos = GPIO.HIGH if on else GPIO.LOW
        GPIO.output(_GPIO_PIN, pos)

    def _run(self):
        while True:
            (on_count, off_count) = self.queue.get()
            self.light_on_count = on_count
            self.light_off_count = off_count
            self.is_light_on = 0
            self.count_down = 0
            self.next.clear()
            while not self.next.is_set():
                if self.count_down == 0:
                    self.is_light_on = not self.is_light_on
                    if self.is_light_on:
                        self.count_down = self.light_on_count
                    else:
                        self.count_down = self.light_off_count
                    if self.count_down == 0:
                        continue
                    self._set_light_on(self.is_light_on)
                #print('is_on=%d, count_down=%d' % (self.is_light_on, self.count_down))
                time.sleep(0.1)
                self.count_down -= 1

pixels = Pixels()

if __name__ == '__main__':
    while True:

        try:
            pixels.wakeup()
            time.sleep(3)
            pixels.listen()
            time.sleep(3)
            pixels.think()
            time.sleep(3)
            pixels.speak()
            time.sleep(3)
            pixels.off()
            time.sleep(3)
        except KeyboardInterrupt:
            break


    pixels.off()
    time.sleep(1)
