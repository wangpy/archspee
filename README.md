
## Introduction

Build your own super smart display with Raspberry Pi and **archspee**. It is Highly modularized and customizable voice assistant platform for Raspberry Pi.

### Highlights

- Super easy to integrate with other services (hotword detection, STT, NLU, input / presentation modules, etc.)
- Super easy to create your own hotword trigger (based on Snowboy) or from any input.
- Super easy to handle multiple-purpose scenario:
  - Register different trigger to different service / handler for different purposes.
  - Split your different scenario to different NLU application to manage them with ease.
- Super easy to extend (add your own NLU rules and add / extend handler module or just add new intent script files)
  - It's possible to also integrate Google Assistant, Alexa, or both at the same time.
- Designed for smart display scenario in mind:
  - Providing visual feedback presentation module for notification icon, notification bubbles and activity graphics
  - Providing a [default application](#default-application) to use YouTube TV and perform some device operations with voice

### Prerequisites

1. It is strongly recommended to use Raspberry Pi 3 B+ model. (**archspee** is only tested on RPI3B+)
2. You need to have an external microphone to your Raspberry Pi unit to receive audio input. You can use any of the following components / kits:
   - USB microphone or sound card
   - External microphone HAT
   - AIY Voice Kit
3. You can use to an HDMI external monitor or any display component, including DSI display (Offical 7" Touchscreen Display), or SPI display.
   - SPI display basically has low refresh rates. To improve the performance, you can check the **[fbcp-ili9341](https://github.com/juj/fbcp-ili9341)** project and see if it helps.
5. It basically works with the **`chromium-browser`** browser which is shipped in Raspbian image, however it is recommended to use **[Puffin Internet Terminal](www.puffin.com)** for better web browsing performance (Refer to [Install Puffin Internet Terminal](#install-puffin-internet-terminal) section)

### Default Application

This is the appication which the author actually uses in his daily life. Anyone can easily modify / extend the application following the steps in [Customization](#customization) section. It includes 2 scenarios.

- Browse YouTube TV website (same website which Firefox TV uses) / [Neverthink](https://neverthink.tv/) website
  - Speak **Snowboy** hotword and issue the following command:
    - **`Move (Down|Up|Left|Right) [number] times`**
    - **`Select`** (the current focused item)
    - **`Search [query]`**
    - (After search) **`Select (first|second|...) result`**
    - **`Pause the video`** / **`Resume playing`**
    - **`Go back`**
    - **`Seek (forward|back) [number] seconds`**
    - **`Give me some random [topic] videos`**: Opens a new tab to [Neverthink](https://neverthink.tv/) and play the specified topic channel.
- Perform device action
  - Speak **Alexa** hotword and issue the following command:
    - **`Show me the IP`**: Open a terminal window and show network interface IP addresses for 10 seconds
    - **`Wakeup`**: Exit the blank screensaver
    - **`Turn (on|off) the blacklight`** (only effective for system with DSI/SPI display)

Click the following image to watch the demo video:

[![Watch YouTube using Raspberry Pi Smart Display with Puffin Internet Terminal](http://img.youtube.com/vi/Al8i7aQ4tA4/0.jpg)](http://www.youtube.com/watch?v=Al8i7aQ4tA4 "Watch YouTube using Raspberry Pi Smart Display with Puffin Internet Terminal")

(Note that the current released **Puffin Internet Terminal** does not have the fullscreen feature yet. The demo below is using an development build.)

## Installation

1. Clone the repository: `git clone https://github.com/wangpy/archspee`
2. Enter the repository: `cd archspee/`
3. Execute Installation script: `./install.sh`
4. Done! Continue to the [Configuration](#configuration) section to setup your device correctly before you can start using **archspee**.

## Configuration

### Install Puffin Internet Terminal

**[Puffin Internet Terminal](https://www.puffin.com/raspberry-pi/)** is a fast web browser on Raspberry Pi. Actually it is the only usable web browser to general Internet. You can still use the **`chromium-browser`** which is shipped in official Raspbian image but the performance is barely acceptable.

The default configuration file launches **Puffin Internet Terminal** to browse websites. If you want to use **chromium** instead, you need to modify the configuration file.

You can install **Puffin Internet Terminal** by either of the two ways:
- [Using prebuilt Raspbian system image](#using-prebuilt-raspbian-system-image)
- [Downloading Debian package file and installing manually](#downloading-debian-package-file-and-installing-manually)

**NOTE if your Raspberry Pi system has DSI/SPI display:**
- Before installation, make sure you connect to an external HDMI monitor before you boot Raspberry Pi or you might not be able to continue the process. (This is due to the default GL Driver settings of the image)
- After installation of **Puffin Internet Terminal**, you need to make follow [the steps](#set-gl-driver-to-fake-kms) to change GL driver to Fake KMS to let the DSI/SPI display work correctly.

#### Using Prebuilt Raspbian System Image

1. Follow the [instruction on official website](https://www.puffin.com/raspberry-pi/how-to-install.php) to download and flash the image to the SD card.
2. Boot Raspberry Pi with the SD card and complete the setup wizard.
3. Follow the [Installation steps](#installation) to install **archspee** on the system.
4. **(Only for system with DSI/SPI display)** Follow [the steps](#set-gl-driver-to-fake-kms) to set GL Driver to Fake KMS.

#### Downloading Debian Package File and Installing Manually

1. Download the Debian package from the [official website](https://www.puffin.com/raspberry-pi/).
2. Apply the following configuration change using **`raspi-config`**
   1. `sudo raspi-config`
   2. Go to  **Advanced options > GL Driver**  and select **`G1 GL (Full KMS)`**.
   3. Go to  **Advanced options > Memory Split**  and change settings to  **`384`**.
   4. Exit the Configuration Tool and reboot.
3. Install the Debian package: `sudo dpkg -i puffin-internet-terminal-demo_7.7.x-dev_armhf.deb` (Change the file name according to your actual downloaded file)
4. **(Only for system with DSI/SPI display)** Follow [the steps](#set-gl-driver-to-fake-kms) to set GL Driver to Fake KMS.

#### Set GL Driver to Fake KMS

**This part is only necessary for system with DSI/SPI display** because they need dispmanx interface to work, and Full KMS GL Driver does not have provide the interface.

1. `sudo raspi-config`
2. Go to  **Advanced options > GL Driver**  and select **`G2 GL (Fake KMS)`**.
3. Exit the Configuration Tool and reboot.

### Configure and Test the Audio

You need to make sure you have configured your audio devices correctly to use **archspee**. The following instruction in this part is cited from [Google Assistant Library Documentaion](https://developers.google.com/assistant/sdk/guides/library/python/embed/audio).

1.  Find your recording and playback devices.
    1.  Locate your USB microphone in the list of capture hardware devices. Write down the card number and device number.
		```
        arecord -l
		```
    2.  Locate your speaker in the list of playback hardware devices. Write down the card number and device number. Note that the 3.5mm-jack is typically labeled  `Analog`  or  `bcm2835 ALSA`  (not  `bcm2835 IEC958/HDMI`).
		```
		aplay -l
		```
2.  Create a new file named  `.asoundrc`  in the home directory (`/home/pi`). Make sure it has the right slave definitions for microphone and speaker; use the configuration below but replace  `<card number>`  and  `<device number>`  with the numbers you wrote down in the previous step. Do this for both  `pcm.mic`  and  `pcm.speaker`.
	```
    pcm.!default  { type asym
      capture.pcm "mic" playback.pcm "speaker"
    }
    pcm.mic { type plug
      slave { pcm "hw:<card number>,<device number>"  }
    }
    pcm.speaker { type plug
      slave { pcm "hw:<card number>,<device number>"  }
    }
    ```
3.  Verify that recording and playback work:
    1.  Adjust the playback volume.
		```
		alsamixer
		```
        Press the up arrow key to set the playback volume level to around 70.

    2.  Play a test sound (this will be a person speaking). Press Ctrl+C when done. If you don't hear anything when you run this, check your speaker connection.
	     ```
        speaker-test -t wav
	    ```
    3.  Record a short audio clip.
		```
        arecord --format=S16_LE --duration=5 --rate=16000 --file-type=raw out.raw
           ```
    4.  Check the recording by replaying it. If you don't hear anything, you may need to check the recording volume in  `alsamixer`.
        ```
        aplay --format=S16_LE --rate=16000 out.raw
           ```
    If recording and playback are working, then you are done configuring audio. If not, check that the microphone and speaker are properly connected. If this is not the issue, then try a different microphone or speaker.

    Note that if you have both an HDMI monitor and a 3.5mm jack speaker connected, you can play audio out of either one. Run the following command:
	```
	sudo raspi-config
	```
    Go to  **Advanced options > Audio**  and select the desired output device.

## Execution

- Launch **archspee** manually:
  1. Enter the repository: `cd archspee/`
  2. Execute run script: `./run.sh`
- Install the `systemd` service to launch **archspee** on boot:
  1. Execute service installer script: `scripts/service_installer.sh`
  2. To uninstall, run the service uninstaller script: `scripts/service_uninstaller.sh`

## Customization

Customization can be easily made by putting custom configuration and modules into `custom` directory:
1. Copy from default configuration files: \
   `cp archspee/default_config.py custom/config.py`
2. **(Optional)** [Add your own hotwords](#add-your-own-hotwords) or [add additional trigger methods](#add-additional-trigger-methods) (push button, etc)
3. **(Optional)** [Add additional status indicators (presenters)](#add-additional-status-indicators-presenters)
4. **(Optional)** [Add your own action and Intent Script to perform device action](#add-your-own-action-and-intent-script-to-perform-device-action)
5. **(Optional)** [Integrate with other STT or NLU service](#integrate-with-other-stt-or-nlu-service)
6. **(Optional)** For further customization / extension, refer to the [architecture section](#archspee-architecture)

### Add Your Own Hotwords

1. Register an account on [Snowboy website](https://snowboy.kitt.ai) and get your API key on user profile page (as documented [here](http://docs.kitt.ai/snowboy/#api-v1-train))
2. Train a personal model using Snowboy API: \
   `SNOWBOY_API_TOKEN=<TOKEN> env/bin/python scripts/train_snowboy_model.py out.pmdl` \
   (Change the **\<TOKEN\>** to your Snowboy API token)
3. Test your personal model: \
   `PYTHONPATH=$PWD/third_party/snowboy env/bin/python scripts/test_snowboy_model.py`
4. Move the `out.pmdl` to `custom` folder and rename.
5. Modify `custom/config.py` to replace the hotword you want to replace in `decoder_model` list to yours in `SnowboyTrigger` settings.

### Add Additional Trigger Methods

1. `GpioButtonTrigger` GPIO (push button) trigger
   1. Uncomment `GpioButtonTrigger` item in `TRIGGERS` list.
   2. Change the `gpio_pins` value according to your system.
2. You can write your own trigger by subclassing `archspee.triggers.TriggerBase` class.

### Add Additional Status Indicators (Presenters)

1. `PixelPresenter`: Pixel (LED)
   1. Modify `custom/config.py` and uncomment the commented items in `PRESENTERS` list according to your need.
   2. The default `PixelPresenter` is for ReSpeaker 2-mic HAT. You can copy `archspee/presenters/pixels.py` to `custom` folder, modify the code and change the class name to `custom.pixels.PixelsPresenter` in the item.
2. You can write your own presenter by subclassing `archspee.presenters.PresenterBase` class.

### Add your Own Action and Intent Script to Perform Device Action

The default application is using [Wit.ai](https://wit.ai) to perform natural language understanding. The Wit app data is exported and put in the repository. You can get the app data and import in your own Wit app to extend it.
1. Get the exported app data zip file [here](https://github.com/wangpy/archspee/blob/master/samples/wit_data/BrowserYouTubeTvEn-2019-01-20-17-19-02.zip).
2. Create an app in Wit.ai and import the app data zip file above.
3. You can train the app to understand new intent values. (Refer to the [official getting started guide](https://wit.ai/getting-started) and the tutorials to understand how to do it)
4. Put a script `[new_intent_value].sh` in `intent_scripts` folder.
5. Modify the `access_token` of `WitInterpreter` in `custom/config.py` to the token of your created app.
6. Test it! You can utilize the **INBOX** feature in Wit.ai console to train the app from the command you issue.

### Integrate with other STT or NLU service

There are many services we can utilize to perform STT (speech to text) and NLU (natural language understanding). The following services are supported in **archspee**:
- [Wit.ai](https://wit.ai) for STT & NLU in multiple languages
- [speech_recognition](https://github.com/Uberi/speech_recognition) module for STT (which utilizes different services)
- [OLAMI](https://olami.ai) for STT & NLU in Chinese

It's possible to integrate Google Assistant, Alexa or other voice assistant library / service / API into **archspee**:
- You can write your own recognizer by subclassing `archspee.recognizers.RecognizerBase` class to integrate the service which performs STT (and perhaps also NLU) - Speech to Text or Speech to Intent
- You can write your own interpreter by subclassing `archspee.interpreters.InterpreterBase` class to integrate the service which performs NLU - Text to Intent

## archspee Architecture

**archspee** is designed to be highly modularized and highly customizable so anyone can:
- Swap different modules to compare performance or across different scenarios.
- Split different scanarios to different NLU applications so it's easy to building a new voice assistant from several "building-blocks" NLU applications.

### Key / Built-in Components

- `ArchspeeMain` - main class of **archspee** which loads config and utilize all components to perform voice assistant jobs.
- `Listener` - the audio frontend to process audio input and perform VAD (voice activity detection)
  - `AlsaPortAudioListener` - audio frontend with portaudio API and VAD (same algorithm from python [speech_recognition](https://github.com/Uberi/speech_recognition) module)
- `Trigger` - detects trigger from audio input (hotword) or other input. Other Hotword Detection solution can be integrated as a trigger module.
  - `SnowboyTrigger` - audio hotword trigger using [Snowboy](https://snowboy.kitt.ai) 
  - `GpioButtonTrigger` - physical button trigger via GPIO
- `Presenter` - presents visual feedback on screen or on any output device (and can also receive `action` from UI)
  - `GtkAppIndicatorPresenter` - show notification on taskbar, display notification balloons and activity graphics.
  - `AudioPresenter` - to lower volume when active (can also play sound effects here)
  - `PixelsPresenter` - control LEDs on various HATs with RGB LEDs
- `Recognizer` - accepts speech audio input and perform STT (speech-to-text) or STT+NLU (speech-to-intent)
  - `WitRecognizer` - use [Wit.ai](https://wit.ai) to perform STT+NLU (`/speech` API)
  - `OlamiRecognizer` - use to [OLAMI](https://olami.ai) perform STT+NLU (ASR+NLI)
  - `GoogleSpeechRecognizer` - use recognize_google() in [speech_recognition](https://github.com/Uberi/speech_recognition) module to perform STT
- `Interpreter` - accepts natural langage text input and performs NLU (text-to-intent)
  - `WitInterpreter` - use [Wit.ai](https://wit.ai) to perform NLU (`/message` API)
  - `OlamiRecognizer` use to [OLAMI](https://olami.ai) perform NLU (NLI)
- `Handler` - perform action from intent and entities.
  - `BrowserYouTubeTVIntentHandler` - launches web browser and perform various action according to intents.
  - `ScriptsIntentHandler` - execute script file with the name for the respective intent in `intent_scripts` directory.
  
### Designing Scenarios

When designing the scenarios you want to provide the actions for, each scenario can be assigned a unique **trigger ID** so they can be processed by designated `Recognizer`, (maybe also `Interpreter` if the recognizer only performs STT) and `Handler`. Take the default application as example:

- `SnowboyTrigger` emits trigger ID **`1`** via **Snowboy** hotword -> `WitRecognizer` -> `BrowserYouTubeTVIntentHandler`
- `SnowboyTrigger` emits trigger ID **`2`** via  **Alexa** hotword -> `GoogleSpeechRecognizer` -> `WitInterpreter` -> `ScriptsIntentHandler`

Note that the trigger ID is not exclusively bound between each connection:
- Different triggers can emit same trigger ID.
- Intent data from same trigger ID after STT and NLU, it can be processed by multiple handlers at the same time.

This gives maximum flexibility to combine modules to build for different multi-purposed scenarios.
