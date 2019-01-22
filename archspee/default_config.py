_WIT_ACCESS_TOKEN_FOR_BROWSER_TV = '3QTEIGPP4YXNRN6DKPDOLV46EQLSGIUJ'
_WIT_ACCESS_TOKEN_FOR_DEVICE_CONTROL = 'IEGTTI2YDCBYGF6ZYR7AVI2ZOVXLOSMI'

LISTENERS = [
    ( 'archspee.listeners.alsa_port_audio.AlsaPortAudioListener', {} )
]

TRIGGERS = [
    (
        'archspee.triggers.snowboy.SnowboyTrigger',
        {
            'decoder_model': [
                'third_party/snowboy/resources/snowboy.umdl',
                'third_party/snowboy/resources/alexa_02092017.umdl'
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
        { 'access_token': _WIT_ACCESS_TOKEN_FOR_BROWSER_TV }
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
        { 'access_token': _WIT_ACCESS_TOKEN_FOR_DEVICE_CONTROL }
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
