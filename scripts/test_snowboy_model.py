import sys
try:
    from third_party.snowboy import snowboydecoder
except:
    print('snowboydecoder cannot be imported. Try running the scripts with PYTHONPATH environment variable including "third_party/snowboy" path.')
    sys.exit(-1)

import signal

detector = None

def signal_handler(signal, frame):
    global detector
    detector.stop()

def detected_callback(index):
    print("Hotword %d detected" % index)
    
if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=[])
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=detected_callback,
               sleep_time=0.03)

detector.terminate()
