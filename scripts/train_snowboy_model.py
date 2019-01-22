import sys
import base64
import requests
import json
import os
import speech_recognition as sr

SAVE_WAV_FILES_FOR_DEBUG = False
REC_WAIT_TIMEOUT = 3 # sec
REC_PHRASE_MAXLEN = 5 # sec

endpoint = "https://snowboy.kitt.ai/api/v1/train/"
token = os.environ['SNOWBOY_API_TOKEN']
hotword_name = 'unknown'
language = 'en'
microphone = 'microphone'

def perform_train(out_filename):
    r = sr.Recognizer()
    wav_data = []
    wav_count = 0
    with sr.Microphone() as source:
        print('Adjusting for ambient noise...')
        r.adjust_for_ambient_noise(source)
        while wav_count < 3:
            print('Recording Sample #%d (Max %d seconds)' % (wav_count+1, REC_PHRASE_MAXLEN))
            try:
                audio = r.listen(source, timeout=REC_WAIT_TIMEOUT, phrase_time_limit=REC_PHRASE_MAXLEN)
            except sr.WaitTimeoutError:
                print('No voice detected in %d seconds, try again!' % REC_WAIT_TIMEOUT)
                continue
            length = len(audio.get_raw_data())
            print('Sample length = %d' % length)
            if length < 96000:
                print('Too short, try again!')
                continue
            wav_data.append(base64.b64encode(audio.get_wav_data()).decode('ascii'))
            if SAVE_WAV_FILES_FOR_DEBUG:
                wav_filename = out_filename+'_train_'+str(wav_count+1)+'.wav'
                with open(wav_filename, 'wb') as outf:
                    outf.write(audio.get_wav_data())
            wav_count = wav_count + 1

    (wav1, wav2, wav3) = wav_data
    data = {
        "name": hotword_name,
        "token": token,
        "microphone": microphone,
        "language": language,
        "voice_samples": [
            {"wave": wav1},
            {"wave": wav2},
            {"wave": wav3}
        ]
    }

    print("Send train request to Snowboy...")
    response = requests.post(endpoint, json=data)
    if response.ok:
        with open(out_filename, "wb") as outfile:
            outfile.write(response.content)
        print("Saved model to '%s'." % out)
        return True
    else:
        print("Request failed.")
        print(response.text)
        return False

if __name__ == "__main__":
    try:
        [_, out] = sys.argv
    except ValueError:
        print("Usage: %s out_model_name" % sys.argv[0])
        sys.exit()

    while True:
        if perform_train(out):
            break

