sudo apt-get update

sudo apt-get -y install python3-dev python3-venv portaudio19-dev flac

python3 -m venv env
env/bin/python -m pip install --upgrade pip setuptools wheel

# snowboy
sudo apt-get -y install python3-pyaudio sox
sudo apt-get -y install libatlas-base-dev libffi-dev
env/bin/python -m pip install --upgrade pyaudio cffi

# wit / REST API
env/bin/python -m pip install --upgrade grequests

# pyGTK
sudo apt-get -y install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 gir1.2-notify-0.7 libglib2.0-dev libgirepository1.0-dev libcairo2-dev
env/bin/python -m pip install --upgrade pycairo
env/bin/python -m pip install --upgrade pygobject


# notification
sudo apt-get -y install dunst libnotify-bin libnotify-cil-dev

# remote control
sudo apt-get -y install xdotool

# audio mixer control
sudo apt-get -y install libasound2-dev
env/bin/python -m pip install pyalsaaudio

# speech recognition
sudo apt-get -y install flac
env/bin/python -m pip install SpeechRecognition

# gpio button
sudo apt-get -y install python-rpi.gpio python3-rpi.gpio
env/bin/python -m pip install RPi.GPIO

# pixels
env/bin/python -m pip install spidev
