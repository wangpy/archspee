import os

_CREDENTIALS = {}
for key in ['WIT_ACCESS_TOKEN', 'WIT_ACCESS_TOKEN_2', 'OLAMI_APP_KEY', 'OLAMI_APP_SECRET']:
    _CREDENTIALS[key] = ''
    if key in os.environ:
        _CREDENTIALS[key] = os.environ[key]


LISTENERS = [
    ( 'archspee.listeners.alsa_port_audio.AlsaPortAudioListener', {} )
]

TRIGGERS = [
    (
        'archspee.triggers.snowboy.SnowboyTrigger',
        {
            'decoder_model': [
                'third_party/snowboy/resources/snowboy.umdl',
                'third_party/snowboy/resources/alexa.umdl'
            ],
            'trigger_ids': [1, 2],
            'sensitivity': [],
            'audio_gain': 1.0
        }
    ),
    #( 'archspee.triggers.gpio.GpioButtonTrigger', { 'gpio_pins': [17], 'trigger_ids': [2] } )
]

PRESENTERS = [
    ( 'archspee.presenters.log.LogPresenter', {} ),
    ( 'archspee.presenters.audio.AudioPresenter', {} ),
    #( 'archspee.presenters.pixels.PixelsPresenter', {} ),
    # FIXME: Gtk presenter should be the last presenter due that Gtk.main() blocks main thread
    ( 'archspee.presenters.gtk_app_indicator.GtkAppIndicatorPresenter', {} )
]

RECOGNIZERS = [
    # this recognizer includes intent interpreting
    (
        1,
        'archspee.recognizers.wit.WitRecognizer',
        { 'access_token': _CREDENTIALS['WIT_ACCESS_TOKEN'] }
    ),
    # this recognizer does not include interpreting so need to hook another interpreter to this trigger ID
    (
        2,
        'archspee.recognizers.speech.GoogleSpeechRecognizer',
        { 'language': 'en-US' }
    )
]

INTERPRETERS = [
    (
        2,
        'archspee.interpreters.wit.WitInterpreter',
        { 'access_token': _CREDENTIALS['WIT_ACCESS_TOKEN_2'] }
    )
]

HANDLERS = [
    (
        [1],
        'archspee.handlers.browser_youtube_tv.BrowserYouTubeTVIntentHandler',
        {
            'browser_exec': 'puffin_demo',
            'args': '--kiosk'
        }
    ),
    (
        [2],
        'archspee.handlers.scripts.ScriptsIntentHandler',
        {}
    )
]
