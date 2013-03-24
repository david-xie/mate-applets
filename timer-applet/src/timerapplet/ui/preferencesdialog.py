# Copyright (C) 2008 Jimmy Do <jimmydo@users.sourceforge.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
from gi.repository import GObject
from gi.repository import Gtk

from timerapplet.config import GLADE_PREFERENCES_DIALOG


class PreferencesDialog(GObject.GObject):
    __gsignals__ = \
    {
        'show-remaining-time-changed': 
        (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_BOOLEAN,)
        ),
        'play-sound-changed':
        (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_BOOLEAN,)
        ),
        'use-custom-sound-changed':
        (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_BOOLEAN,)
        ),
        'show-popup-notification-changed':
        (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_BOOLEAN,)
        ),
        'show-pulsing-icon-changed':
        (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_BOOLEAN,)
        ),
        'custom-sound-path-changed':
        (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_STRING,)
        )
    }

    __gproperties__ = \
    {
        'show-remaining-time':
        (bool,
         'Show remaining time',
         'Whether to show remaining time when the timer is running',
         False,
         GObject.PARAM_WRITABLE
        ),
       'play-sound':
        (bool,
         'Play notification sound',
         'Whether to play notification sound when the timer is finished',
         False,
         GObject.PARAM_WRITABLE
        ),
       'use-custom-sound':
        (bool,
         'Use custom sound',
         'Whether to use a custom notification sound',
         False,
         GObject.PARAM_WRITABLE
        ),
       'show-popup-notification':
        (bool,
         'Show Popup notification',
         'Whether to show a popup notifcation when timer finished', 
         False,
         GObject.PARAM_WRITABLE
        ), 
       'show-pulsing-icon':
        (bool,
         'Show pulsing icon',
         'Whether to show pulsing icon when timer finished', 
         False,
         GObject.PARAM_WRITABLE
        ), 
       'custom-sound-path':
        (str,
         'Custom sound path',
         'Path to a custom notification sound',
         '',
         GObject.PARAM_WRITABLE
        )
    }
                        
    def __init__(self):
        GObject.GObject.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_file(GLADE_PREFERENCES_DIALOG)
        self.preferences_dialog = builder.get_object('preferences_dialog')
        self.show_time_check = builder.get_object('show_time_check')
        self.play_sound_check = builder.get_object('play_sound_check')
        self.use_default_sound_radio = builder.get_object('use_default_sound_radio')
        self.use_custom_sound_radio = builder.get_object('use_custom_sound_radio')
        self.sound_chooser_button = builder.get_object('sound_chooser_button')
        self.play_sound_box = builder.get_object('play_sound_box')
        #: Popup notification checkbutton
        self.popup_notification_check = builder.get_object('popup_notification_check')
        #: Pulsing icon checkbutton
        self.pulsing_icon_check = builder.get_object('pulsing_trayicon_check')

        #######################################################################
        # Signals
        #######################################################################
        self.show_time_check.connect('toggled', self._on_show_time_check_toggled)
        self.play_sound_check.connect('toggled', self._on_play_sound_check_toggled)
        self.use_custom_sound_radio.connect('toggled', self._on_use_custom_sound_radio_toggled)
        #: Popup notification checkbutton 'toggled' signal
        self.popup_notification_check.connect('toggled', self._on_popup_notification_toggled)
        #: Pulsing icon checkbutton 'toggled' signal
        self.pulsing_icon_check.connect('toggled', self._on_pulsing_icon_toggled)
        
        self.sound_chooser_button.connect('selection-changed', self._on_sound_chooser_button_selection_changed)
        self.preferences_dialog.connect('delete-event', Gtk.Widget.hide_on_delete)
        self.preferences_dialog.connect('response', lambda dialog, response_id: self.preferences_dialog.hide())

    def show(self):
        self.preferences_dialog.present()

    def _on_show_time_check_toggled(self, widget):
        self.emit('show-remaining-time-changed', widget.props.active)

    def _on_play_sound_check_toggled(self, widget):
        self.emit('play-sound-changed', widget.props.active)

    def _on_use_custom_sound_radio_toggled(self, widget):
        self.emit('use-custom-sound-changed', widget.props.active)

    def _on_popup_notification_toggled(self, widget):
        """Emit a signal when `self.popup_notification_check` gets toggled in
        the Preferences dialog window."""
        self.emit('show-popup-notification-changed', widget.props.active)

    def _on_pulsing_icon_toggled(self, widget):
        """Emit a signal when `self.popup_notification_check` gets toggled in
        the Preferences dialog window."""
        self.emit('show-pulsing-icon-changed', widget.props.active)

    def _on_sound_chooser_button_selection_changed(self, chooser_button):
        filename = chooser_button.get_filename()
        
        # Work around an issue where calling set_filename() will cause
        # 3 selection-changed signals to be emitted: first two will have a None filename
        # and the third will finally have the desired filename.
        if filename is not None:
            print 'Custom sound changed to path: %s' % filename
            self.emit('custom-sound-path-changed', filename)

    def do_set_property(self, pspec, value):
        if pspec.name == 'show-remaining-time':
            self.show_time_check.props.active = value
        elif pspec.name == 'play-sound':
            self.play_sound_check.props.active = value
            self.play_sound_box.props.sensitive = value
        elif pspec.name == 'use-custom-sound':
            if value == True:
                self.use_custom_sound_radio.props.active = True
                self.sound_chooser_button.props.sensitive = True
            else:
                # Note: Setting _use_custom_sound_radio.props.active to False
                # does not automatically set _use_default_sound_radio.props.active to True
                self.use_default_sound_radio.props.active = True
                self.sound_chooser_button.props.sensitive = False
        elif pspec.name == 'show-popup-notification':
            self.popup_notification_check.props.active = value
        elif pspec.name == 'show-pulsing-icon':
            self.pulsing_icon_check.props.active = value
        elif pspec.name == 'custom-sound-path':
            # Prevent infinite loop of events.
            if self.sound_chooser_button.get_filename() != value:
                self.sound_chooser_button.set_filename(value)
