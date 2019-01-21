from archspee.presenters import PresenterBase
from archspee.listeners import ListenerStatus

import threading
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import GLib, Gtk, GObject
from gi.repository import AppIndicator3
from gi.repository import Notify

_LOG_LEVEL = None # 'DEBUG'

_APPINDICATOR_ID = 'myappindicator'
_ICONS = [
    'gtk-ok', #'/opt/cloudmosa/puffin_demo/product_logo_256.png',
    'gtk-dialog-warning',
    'gtk-dialog-question',
    'gtk-media-record',
    'gtk-execute'
]
_ICON_DISABLED = 'gtk-stop'

class GtkAppIndicatorPresenter(PresenterBase):
    def __init__(self, action_callback):
        self.__log_level = _LOG_LEVEL
        super(GtkAppIndicatorPresenter, self).__init__(action_callback)
        self.status = ListenerStatus.standby
        self.disabled = False
        self.processing = False
        
        self.indicator = None
        self.menu_item_active = None
        self.thread = None

    def notify_show(self, title, body):
        Notify.Notification.new(title, body).show()

    def set_indicator_icon(self, name):
        GLib.idle_add(self.indicator.set_icon, name)

    def on_listener_status(self, trigger_id, status, is_disabled):
        if status != self.status or is_disabled != self.disabled:
            if is_disabled and status is ListenerStatus.standby:
                self.set_indicator_icon(_ICON_DISABLED)
            else:
                if self.processing:
                    status = ListenerStatus.processing
                elif status.value == 1:
                    GLib.idle_add(self.notify_show, 'At Your Service.', 'trigger_id=%d' % trigger_id)
                elif status.value == 2:
                    GLib.idle_add(self.notify_show, 'Speak What You Want...', '')
                self.set_indicator_icon(_ICONS[status.value])
            self.logger.debug('status changed: from %s to %s' % (repr(self.status), repr(status)))
            self.status = status
            self.disabled = is_disabled
            self.menu_item_active.set_active(not is_disabled)

    def on_recognization_started(self, trigger_id):
        self.logger.debug('on_recognization_started')
        self.processing = True
        self.on_listener_status(trigger_id, ListenerStatus.processing, self.disabled)

    def on_intent_handled(self, trigger_id, spoken_text, intent, entities, summary, body, level):
        self.logger.debug('on_intent_handled')
        GLib.idle_add(self.notify_show, summary, body)
        self.processing = False
        self.on_listener_status(trigger_id, ListenerStatus.standby, self.disabled)

    def on_error_handled(self, trigger_id, status_code, response_text, summary, body, level):
        self.logger.debug('on_error_handled')
        GLib.idle_add(self.notify_show, summary, body)
        self.processing = False
        self.on_listener_status(trigger_id, ListenerStatus.standby, self.disabled)

    def handle_menu_item_active_activated(self, source):
        is_item_active = self.menu_item_active.get_active()
        is_disabled = not is_item_active
        self.logger.debug('set disabled = %d' % is_disabled)
        self.invoke_action_callback('disable' if is_disabled else 'enable')

    def handle_menu_item_panic_activated(self, source):
        self.invoke_action_callback('panic')

    def start(self):
        self.logger.debug('start()')
        self.indicator = AppIndicator3.Indicator.new(_APPINDICATOR_ID, _ICONS[0], AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        menu = Gtk.Menu()
        self.menu_item_active = Gtk.CheckMenuItem('Listen for Hotword')
        self.menu_item_active.set_active(True)
        self.menu_item_active.connect('activate', self.handle_menu_item_active_activated)
        menu.append(self.menu_item_active)
        menu_item_panic = Gtk.MenuItem('Panic!')
        menu_item_panic.connect('activate', self.handle_menu_item_panic_activated)
        menu.append(menu_item_panic)
        menu.show_all()
        self.indicator.set_menu(menu)

        Notify.init(_APPINDICATOR_ID)
        self.logger.debug('invoking Gtk.main()')
        Gtk.main()
        self.logger.debug('Gtk.main() returned')

    def terminate(self):
        self.logger.debug('terminate()')
        Notify.uninit()
        Gtk.main_quit()
        self.logger.debug('Gtk.main_quit() called')
