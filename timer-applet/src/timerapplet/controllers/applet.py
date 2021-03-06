# Copyright (C) 2008 Jimmy Do <jimmydo@users.sourceforge.net>
# Copyright (C) 2010 Kenny Meyer <knny.myer@gmail.com>
# Copyright (C) 2013 David Xie <david.scriptfan@gmail.com>
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
import gi
gi.require_version("Gtk", "2.0")

import gst
import subprocess
import shlex
import threading
from gettext import gettext as _
from gettext import ngettext
from datetime import datetime
from datetime import timedelta
from gi.repository import MatePanelApplet
from gi.repository import Gtk
from gi.repository import Gdk
from timerapplet import utils
from timerapplet import config
from timerapplet.ui import AboutDialog
from timerapplet.ui import StatusButton
from timerapplet.ui import Notifier
from timerapplet.ui import StartNextTimerDialog
from timerapplet.ui import StartTimerDialog
from timerapplet.ui import ContinueTimerDialog
from timerapplet.ui import PreferencesDialog
from timerapplet.core import Timer
from timerapplet.core import TimerAppletSettings


def on_widget_button_press_event(sender, event, data=None):
    if event.button != 1:
        sender.stop_emission('button-press-event')
    return False


def force_no_focus_padding(widget):
    Gtk.rc_parse_string('\n'
                        '   style "timer-applet-button-style"\n'
                        '   {\n'
                        '      GtkWidget::focus-line-width=0\n'
                        '      GtkWidget::focus-padding=0\n'
                        '   }\n'
                        '\n'
                        '   widget "*.timer-applet-button" style "timer-applet-button-style"\n'
                        '\n')
    widget.set_name('timer-applet-button')


class TimerApplet(object):
    ## You can find Timer Applet's schemas file in data/timer-applet.schemas.in
    KEY_SHOW_REMAINING_TIME = 'show-remaining-time'
    KEY_PLAY_SOUND = 'play-notification-sound'
    KEY_USE_CUSTOM_SOUND = 'use-custom-notification-sound'
    KEY_SHOW_POPUP_NOTIFICATION = 'show-popup-notification'
    KEY_SHOW_PULSING_ICON = 'show-pulsing-icon'
    KEY_CUSTOM_SOUND_PATH = 'custom-notification-sound-path'

    PRESETS_PATH = '/popups/popup/Presets'
    PRESETS_PLACEHOLDER_NAME = 'Placeholder'
    PRESETS_PLACEHOLDER_PATH = PRESETS_PATH + '/' + PRESETS_PLACEHOLDER_NAME

    def __init__(self, presets_store, manage_presets_dialog, applet, timer, gsettings):
        self.presets_store = presets_store
        self.manage_presets_dialog = manage_presets_dialog
        self.applet = applet
        self.timer = timer
        self.gsettings = gsettings

        self.gst_playbin = gst.element_factory_make('playbin', 'player')
        def bus_event(bus, message):
            t = message.type
            if t == gst.MESSAGE_EOS:
                self.gst_playbin.set_state(gst.STATE_NULL)
            elif t == gst.MESSAGE_ERROR:
                self.gst_playbin.set_state(gst.STATE_NULL)
                err, debug = message.parse_error()
                print 'Error playing sound: %s' % err, debug
            return True
        self.gst_playbin.get_bus().add_watch(bus_event)

        self.status_button = StatusButton()
        self.notifier = Notifier('TimerApplet', Gtk.STOCK_DIALOG_INFO, self.status_button)
        self.start_next_timer_dialog = StartNextTimerDialog(
                            "Start next timer",
                            "Would you like to start the next timer?")
        self.start_timer_dialog = StartTimerDialog(
                                       lambda name: utils.is_valid_preset_name(name,
                                                                               self._presets_store),
                                       self.presets_store.get_model(),
                                       lambda row_iter: utils.get_preset_display_text(self._presets_store,
                                                                                      row_iter))
        self.continue_dialog = ContinueTimerDialog(_('Continue timer countdown?'),
                                                   _('The timer is currently paused. Would you like to continue countdown?'))

        self.preferences_dialog = PreferencesDialog()

        self.about_dialog = AboutDialog()

        # FIX ME: this needs to fix
        #self.applet.set_applet_flags(mateapplet.EXPAND_MINOR)

        # FIX ME: need a Gtk.ActionGroup here!
        # Learn how to add an ActionGroup
        action_group = Gtk.ActionGroup("applet_actions")
        action_group.add_actions(
                [('PauseTimer', Gtk.STOCK_MEDIA_PAUSE, _("PauseTimer"), None, None, lambda action: self.timer.stop()),
                 ('ContinueTimer', Gtk.STOCK_MEDIA_PLAY, _("ContinueTimer"), None, None, lambda action: self.timer.start()),
                 ('StopTimer', Gtk.STOCK_MEDIA_STOP, _("StopTimer"), None, None, lambda action: self.timer.reset()),
                 ('RestartTimer', Gtk.STOCK_REFRESH, _("RestartTimer"), None, None, lambda action: self._restart_timer()),
                 ('StartNextTimer', Gtk.STOCK_MEDIA_NEXT, _("StartNextTimer"), None, None, lambda action: self._start_next_timer()),
                 ('ManagePresets', Gtk.STOCK_INFO, _("ManagePresets"), None, None, lambda action: self.manage_presets_dialog.show()),
                 ('Preferences', Gtk.STOCK_PREFERENCES, _("Preferences"), None, None, lambda action: self.preferences_dialog.show()),
                 ('About', Gtk.STOCK_ABOUT, _("About"), None, None, lambda action: self.about_dialog.show())]
            )
        self.applet.setup_menu_from_file(
            config.POPUP_MENU_FILE_PATH,
            action_group
        )
        self.applet.add(self.status_button)

        # Remove padding around button contents.
        force_no_focus_padding(self.status_button)

        # TODO:
        # Fix bug in which button would not propogate middle-clicks
        # and right-clicks to the applet.
        self.status_button.connect('button-press-event', on_widget_button_press_event)

        self.status_button.set_relief(Gtk.ReliefStyle.NONE)
        #self.status_button.set_icon(config.ICON_PATH);

        self.applet.set_tooltip_text(_("Timer Applet"))

        self._connect_signals()
        #self._update_status_button()
        #self._update_popup_menu()
        #self._update_preferences_dialog()
        self.status_button.show()
        self.applet.show_all()

    def _connect_signals(self):
        self.applet.connect('change-orient', lambda applet, orientation: self._update_status_button())
        self.applet.connect('change-size', lambda applet, size: self._update_status_button())
        self.applet.connect('change-background', self._on_applet_change_background)
        self.applet.connect('destroy', self._on_applet_destroy)

        """
        self.presets_store.get_model().connect('row-deleted', 
                                                lambda model,
                                                row_path: self._update_popup_menu())
        self.presets_store.get_model().connect('row-changed',
                                                lambda model,
                                                row_path,
                                                row_iter: self._update_popup_menu())
        """

        self.timer.connect('time-changed', self._on_timer_time_changed)
        self.timer.connect('state-changed', self._on_timer_state_changed)
        self.status_button.connect('clicked', self._on_status_button_clicked)
        self.start_timer_dialog.connect('clicked-start',
                                         self._on_start_dialog_clicked_start)
        self.start_timer_dialog.connect('clicked-manage-presets',
                                         self._on_start_dialog_clicked_manage_presets)
        self.start_timer_dialog.connect('clicked-save',
                                         self._on_start_dialog_clicked_save)
        self.start_timer_dialog.connect('clicked-preset',
                                         self._on_start_dialog_clicked_preset)
        self.start_timer_dialog.connect('double-clicked-preset',
                                         self._on_start_dialog_double_clicked_preset)

        self.preferences_dialog.connect('show-remaining-time-changed', self._on_prefs_show_time_changed)
        self.preferences_dialog.connect('play-sound-changed', self._on_prefs_play_sound_changed)
        self.preferences_dialog.connect('use-custom-sound-changed', self._on_prefs_use_custom_sound_changed)
        self.preferences_dialog.connect('show-popup-notification-changed', self._on_prefs_show_popup_notification_changed)
        self.preferences_dialog.connect('show-pulsing-icon-changed', self._on_prefs_show_pulsing_icon_changed)
        self.preferences_dialog.connect('custom-sound-path-changed', self._on_prefs_custom_sound_path_changed)

        self.gsettings.add_notify(TimerApplet.KEY_SHOW_REMAINING_TIME, self._on_mateconf_changed)
        self.gsettings.add_notify(TimerApplet.KEY_PLAY_SOUND, self._on_mateconf_changed)
        self.gsettings.add_notify(TimerApplet.KEY_USE_CUSTOM_SOUND, self._on_mateconf_changed)
        self.gsettings.add_notify(TimerApplet.KEY_SHOW_PULSING_ICON, self._on_mateconf_changed)
        self.gsettings.add_notify(TimerApplet.KEY_SHOW_POPUP_NOTIFICATION, self._on_mateconf_changed)
        self.gsettings.add_notify(TimerApplet.KEY_CUSTOM_SOUND_PATH, self._on_mateconf_changed)

    ## Private methods for updating UI ##

    def _update_status_button(self):
        current_state = self.timer.get_state()
        if current_state == Timer.STATE_IDLE:
            print 'Idle'
            # This label text should not be visible because the label
            # is hidden when the timer is idle.
            self.status_button.set_label('--:--:--')
            self.status_button.set_tooltip(_('Click to start a new timer countdown.'))
        elif current_state == Timer.STATE_RUNNING:
            print 'Running'
        elif current_state == Timer.STATE_PAUSED:
            print 'Paused'
            self.status_button.set_tooltip(_('Paused. Click to continue timer countdown.'))
        elif current_state == Timer.STATE_FINISHED:
            print 'Finished'
            self.status_button.set_label(_('Finished'))
            name_str = self.timer.get_name()
            time_str = utils.get_display_text_from_datetime(self.timer.get_end_time())
            if len(name_str) > 0:
                # "<timer name>" finished at <time>
                self.status_button.set_tooltip(_('"%s" finished at %s.\nClick to stop timer.') % (name_str, time_str))
            else:
                # Timer finished at <time>
                self.status_button.set_tooltip(_('Timer finished at %s.\nClick to stop timer.') % time_str)

        self.status_button.set_sensitized(current_state == Timer.STATE_RUNNING or
                                           current_state == Timer.STATE_FINISHED)
        self.status_button.set_use_icon(current_state == Timer.STATE_IDLE)
        self.status_button.set_show_remaining_time(current_state != Timer.STATE_IDLE and
                self.gsettings.get_boolean(TimerApplet.KEY_SHOW_REMAINING_TIME))

        if current_state == Timer.STATE_PAUSED:
            self.status_button.set_pie_fill_color(0.4, 0.4, 0.4)
        else:
            # Use theme color
            color = self.applet.style.base[Gtk.StateType.SELECTED]
            red = color.red / 65535.0
            green = color.green / 65535.0
            blue = color.blue / 65535.0
            self.status_button.set_pie_fill_color(red, green, blue)

        orientation = self.applet.get_orient()
        size = self.applet.get_size()
        # FIX ME: I lost size here. should have size >= mateapplet.SIZE_MEDIUM,
        # but I can't find it in any MatePanelApplet
        use_vertical = (orientation == MatePanelApplet.AppletOrient.ORIENT_LEFT or
                        orientation == MatePanelApplet.AppletOrient.ORIENT_RIGHT)
        self.status_button.set_use_vertical_layout(use_vertical)

    def _update_popup_menu(self):
        popup = self.applet.get_popup_component()

        timer_state = self.timer.get_state()
        has_next_timer = self.timer.get_next_timer()
        show_pause = (timer_state == Timer.STATE_RUNNING)
        show_continue = (timer_state == Timer.STATE_PAUSED)
        show_stop = (timer_state == Timer.STATE_RUNNING or
                     timer_state == Timer.STATE_PAUSED or
                     timer_state == Timer.STATE_FINISHED)
        show_restart = (timer_state == Timer.STATE_RUNNING or
                        timer_state == Timer.STATE_PAUSED or
                        timer_state == Timer.STATE_FINISHED)
        show_next_timer = ((timer_state == Timer.STATE_RUNNING or
                           timer_state == Timer.STATE_PAUSED or
                           timer_state == Timer.STATE_FINISHED) and
                           # Only show this popup menu item if it has a
                           # next_timer defined. Clever, huh? ;)
                           has_next_timer)

        show_presets_menu = (len(self.presets_store.get_model()) > 0)
        show_separator = (
            show_presets_menu or
            show_pause or
            show_next_timer or
            show_continue or
            show_stop or
            show_restart)

        to_hidden_str = lambda show: ('0', '1')[not show]
        popup.set_prop('/commands/PauseTimer', 'hidden', to_hidden_str(show_pause))
        popup.set_prop('/commands/ContinueTimer', 'hidden', to_hidden_str(show_continue))
        popup.set_prop('/commands/StopTimer', 'hidden', to_hidden_str(show_stop))
        popup.set_prop('/commands/RestartTimer', 'hidden', to_hidden_str(show_restart))
        popup.set_prop('/commands/StartNextTimer', 'hidden', to_hidden_str(show_next_timer))
        popup.set_prop(TimerApplet.PRESETS_PATH, 'hidden', to_hidden_str(show_presets_menu))
        popup.set_prop('/popups/popup/Separator1', 'hidden', to_hidden_str(show_separator))

        # Rebuild the Presets submenu
        if popup.path_exists(TimerApplet.PRESETS_PLACEHOLDER_PATH):
            popup.rm(TimerApplet.PRESETS_PLACEHOLDER_PATH)
        popup.set_translate(TimerApplet.PRESETS_PATH,
                            '<placeholder name="%s"/>' % TimerApplet.PRESETS_PLACEHOLDER_NAME)

        preset_number = 1
        row_iter = self.presets_store.get_model().get_iter_first()
        while row_iter is not None:
            verb = ('Preset_%d' % preset_number)
            preset_number += 1
            display_text = utils.get_preset_display_text(self._presets_store, row_iter)
            node_xml = '<menuitem verb="%s" name="%s" label="%s"/>' % (verb, verb, display_text)
            popup.set_translate(TimerApplet.PRESETS_PLACEHOLDER_PATH, node_xml)
            popup.add_verb(verb,
                           self._on_presets_submenu_item_activated,
                           self.presets_store.get_model().get_path(row_iter))
            row_iter = self.presets_store.get_model().iter_next(row_iter)

    def _update_preferences_dialog(self):
        self.preferences_dialog.props.show_remaining_time = \
            self.gsettings.get_boolean(TimerApplet.KEY_SHOW_REMAINING_TIME)
        self.preferences_dialog.props.play_sound = \
            self.gsettings.get_boolean(TimerApplet.KEY_PLAY_SOUND)
        self.preferences_dialog.props.use_custom_sound = \
            self.gsettings.get_boolean(TimerApplet.KEY_USE_CUSTOM_SOUND)
        self.preferences_dialog.props.show_popup_notification = \
            self.gsettings.get_boolean(TimerApplet.KEY_SHOW_POPUP_NOTIFICATION)
        self.preferences_dialog.props.show_pulsing_icon = \
            self.gsettings.get_boolean(TimerApplet.KEY_SHOW_PULSING_ICON)
        self.preferences_dialog.props.custom_sound_path = \
            self.gsettings.get_string(TimerApplet.KEY_CUSTOM_SOUND_PATH)
    
    ## Applet callbacks ##
    
    def _on_applet_change_background(self, applet, background_type, color, pixmap):
        applet.set_style(None)
        rc_style = Gtk.RcStyle()
        applet.modify_style(rc_style)

        if background_type == MatePanelApplet.AppletBackgroundType.NO_BACKGROUND:
            pass
        elif background_type == MatePanelApplet.AppletBackgroundType.COLOR_BACKGROUND:
            applet.modify_bg(Gtk.StateType.NORMAL, color)
        elif background_type == MatePanelApplet.AppletBackgroundType.PIXMAP_BACKGROUND:
            style = applet.style.copy()
            style.bg_pixmap[Gtk.StateType.NORMAL] = pixmap
            applet.set_style(style)
    
    def _on_applet_destroy(self, sender, data=None):
        self._call_notify(show=False)
        if self.timer.get_state() != Timer.STATE_IDLE:
            self.timer.reset() # will stop timeout
        self.gsettings.remove_all_notify()
        
    ## Popup menu callbacks ##
        
    def _on_presets_submenu_item_activated(self, component, verb, row_path):
        # Try hiding the Start Timer dialog, just in case it's open.
        self.start_timer_dialog.hide()
        row_iter = self.presets_store.get_model().get_iter(row_path)
        (name, hours, minutes, seconds, command, next_timer, auto_start) = self.presets_store.get_preset(row_iter)
        self._start_timer_with_settings(name, hours, minutes, seconds, command,
                                       next_timer, auto_start)
    
    ## MateConf callbacks ##
    
    def _on_mateconf_changed(self, mateconf_value, data=None):
        self._update_status_button()
        self._update_preferences_dialog()
    
    ## PreferencesDialog callbacks ##
    
    def _on_prefs_show_time_changed(self, sender, show_time):
        self.gsettings.set_boolean(TimerApplet.KEY_SHOW_REMAINING_TIME,
                             show_time)
        
    def _on_prefs_play_sound_changed(self, sender, play_sound):
        self.gsettings.set_boolean(TimerApplet.KEY_PLAY_SOUND,
                             play_sound)
        
    def _on_prefs_use_custom_sound_changed(self, sender, use_custom_sound):
        self.gsettings.set_boolean(TimerApplet.KEY_USE_CUSTOM_SOUND,
                             use_custom_sound)
    
    def _on_prefs_show_pulsing_icon_changed(self, sender, show_pulsing_icon):
        self.gsettings.set_boolean(TimerApplet.KEY_SHOW_PULSING_ICON, 
                             show_pulsing_icon)

    def _on_prefs_show_popup_notification_changed(self, sender,
                                                  show_popup_notification):
        self.gsettings.set_boolean(TimerApplet.KEY_SHOW_POPUP_NOTIFICATION,
                             show_popup_notification)
        
    def _on_prefs_custom_sound_path_changed(self, sender, custom_sound_path):
        self.gsettings.set_string(TimerApplet.KEY_CUSTOM_SOUND_PATH, 
                               custom_sound_path)
    
    ## Timer callbacks ##
    
    def _on_timer_time_changed(self, timer):
        hours, minutes, seconds = utils.seconds_to_hms(timer.get_remaining_time())
        print 'Remaining time: %d, %d, %d' % (hours, minutes, seconds)
        name = self.timer.get_name()
        self.status_button.set_label(utils.construct_time_str(self.timer.get_remaining_time(),
                                                         show_all=False))

        fraction_remaining = float(self.timer.get_remaining_time()) / self.timer.get_duration()
        progress = min(1.0, max(0.0, 1.0 - fraction_remaining))
        self.status_button.set_progress(progress)

        if len(name) > 0:
            # HH:MM:SS (<timer name>)
            self.status_button.set_tooltip(_('%02d:%02d:%02d (%s)') % (hours, minutes, seconds, name))
        else:
            # HH:MM:SS
            self.status_button.set_tooltip(_('%02d:%02d:%02d') % (hours, minutes, seconds))
    
    def _on_timer_state_changed(self, timer, data=None):
        # TODO:
        # Refactor me!
        print 'State changed'
        new_state = timer.get_state()
        print '  new state: %d' % new_state
        
        # These actions should be done once upon a state change.
        # That's why they're done here and not in self._update_status_button();
        # self._update_status_button() could be called multiple times
        # while in the same state.
        if new_state == Timer.STATE_FINISHED:
            name = self.timer.get_name()
            command = self.timer.get_command()
            end_time = self.timer.get_end_time()
            time_text = utils.get_display_text_from_datetime(end_time)
            summary = None
            message = None
            if len(name) > 0:
                # "<timer name>" Finished
                summary = (_('"%s" Finished') % name)
                
                # "<timer name>" finished at <time>
                message = (_('"%s" finished at %s') % (name, time_text))
            else:
                summary = _('Timer Finished')
            
                # Timer finished at <time>
                message = (_('Timer finished at %s') % time_text)
            
            
            def reminder_message_func():
                elapsed_time = datetime.now() - end_time
                message = None
                if elapsed_time < timedelta(seconds=60):
                    message = ngettext('Timer finished about <b>%d second</b> ago',
                                       'Timer finished about <b>%d seconds</b> ago',
                                       elapsed_time.seconds) % elapsed_time.seconds
                else:
                    minutes = elapsed_time.seconds / 60
                    message = ngettext('Timer finished about <b>%d minute</b> ago',
                                       'Timer finished about <b>%d minutes</b> ago',
                                       minutes) % minutes
                return message
            
            # TODO:
            # FIXME:
            # Reason for using a Python thread:
            #  To do all the procedures after timer has ended.  If I don't do
            #  this then after the timer ended and it had an auto-start and next
            #  timer defined, it would directly switch without any notification.
            #  Trying time.sleep() doesn't work as expected; it correctly starts
            #  the next timer, but it doesn't show the notification and the
            #  rest.
            class MyThread(threading.Thread):
                def __init__(self, timer_instance):
                    threading.Thread.__init__(self)
                    self.timer = timer_instance

                def run(self):
                    print "Starting thread..."
                    print "Calling popup notification.",
                    self.timer._call_notify(summary, message, reminder_message_func)
                    print "Starting pulsing button.", 
                    self.timer._start_pulsing_button()
                    print "Playing notification sound.", 
                    self.timer._play_notification_sound()
                    print "Running custom command.", 
                    self.timer._run_custom_command(command)

                    print "Ending Thread..."
            thread = MyThread(self)
            thread.start()
            thread.join()

            next_timer = self.timer.get_next_timer()
            auto_start = self.timer.get_auto_start()
            if auto_start and next_timer:
                # Start next timer
                self._stop_sound()
                self._call_notify(show=False)
                self._stop_pulsing_button()
                self._start_next_timer()
            elif not(auto_start) and next_timer:
                self.status_button.props.sensitive = False
                dialog_result = self.start_next_timer_dialog.get_response()
                self.status_button.props.sensitive = True
                if dialog_result:
                    # Start next timer
                    self._stop_sound()
                    self._call_notify(show=False)
                    self._stop_pulsing_button()
                    self._start_next_timer()
        else:
            self._stop_sound()
            self._call_notify(show=False)
            self._stop_pulsing_button()
        
        print "Updating status button..."
        self._update_status_button()
        print "Updating popup menu..."
        self._update_popup_menu()
    
    ## StatusButton callbacks ##
    
    def _on_status_button_clicked(self, button, data=None):
        current_state = self.timer.get_state()
        if current_state == Timer.STATE_IDLE:
            self.start_timer_dialog.show()
        elif current_state == Timer.STATE_FINISHED:
            self.timer.reset()
        elif current_state == Timer.STATE_PAUSED:
            # Temporarily disable status button while the Continue dialog is open.
            self.status_button.props.sensitive = False
            dialog_result = self.continue_dialog.get_response()
            self.status_button.props.sensitive = True
            if dialog_result == ContinueTimerDialog.CONTINUE_TIMER:
                self.timer.start()
            elif dialog_result == ContinueTimerDialog.STOP_TIMER:
                self.timer.reset()
            elif dialog_result == ContinueTimerDialog.KEEP_PAUSED:
                pass
            else:
                assert False
        elif current_state == Timer.STATE_RUNNING:
            self.timer.stop()
    
    ## StartTimerDialog callbacks ##
    
    def _on_start_dialog_clicked_start(self, sender, data=None):
        (name, hours, minutes, seconds, command, next_timer, auto_start) = \
            self.start_timer_dialog.get_control_data()
        self._start_timer_with_settings(name, hours, minutes, seconds, command,
                                       next_timer, auto_start)
    
    def _on_start_dialog_clicked_manage_presets(self, sender, data=None):
        self.manage_presets_dialog.show()
    
    def _on_start_dialog_clicked_save(self, sender, name,
                                      hours, minutes, seconds, command,
                                      next_timer, auto_start, data=None):
        self.presets_store.add_preset(name, hours, minutes, seconds, command,
                                       next_timer, auto_start)
       
    def _on_start_dialog_clicked_preset(self, sender, row_path, data=None):
        row_iter = self.presets_store.get_model().get_iter(row_path)
        (name, hours, minutes, seconds, command, next_timer, auto_start) = \
               self.presets_store.get_preset(row_iter)
        self.start_timer_dialog.set_name_and_duration(name, hours, minutes,
                                                       seconds, command,
                                                       next_timer, auto_start)

    def _on_start_dialog_double_clicked_preset(self, sender, row_path, data=None):
        """Preset is double-clicked. Start the selected preset, and hide the
        dialog."""
        row_iter = self.presets_store.get_model().get_iter(row_path)
        (name, hours, minutes, seconds, command, next_timer, auto_start) = \
               self.presets_store.get_preset(row_iter)
        self._start_timer_with_settings(name, hours, minutes, seconds, command,
                                       next_timer, auto_start)
        self.start_timer_dialog.hide()

    ## Private methods ##
    def _start_timer_with_settings(self, name, hours, minutes, seconds,
                                   command, next_timer, auto_start):
        print "Resetting timer"
        if self.timer.get_state() != Timer.STATE_IDLE:
            self.timer.reset()
        self.timer.set_duration(utils.hms_to_seconds(hours, minutes, seconds))
        self.timer.set_name(name)
        self.timer.set_command(command)
        self.timer.set_next_timer(next_timer)
        self.timer.set_auto_start(auto_start)
        self.timer.start()

    def _restart_timer(self):
        self.timer.reset()
        self.timer.start()

    def _start_next_timer(self):
        """Start next timer, if defined."""
        next_timer = self.timer.get_next_timer()
        for row in self.presets_store.get_model():
            #print dir(row)
            if str(row[0]) == next_timer:
               (name, hours, minutes, seconds, command, next_timer, auto_start) = \
                    self.presets_store.get_preset(row.iter)
               break
        print "Starting timer with settings: ",
        print (name, hours, minutes, seconds, command, next_timer, auto_start)
        self._start_timer_with_settings(name, hours, minutes, seconds, command,
                                        next_timer, auto_start)

    def _play_notification_sound(self):
        if not self.gsettings.get_boolean(TimerApplet.KEY_PLAY_SOUND):
            return
            
        sound_path = config.DEFAULT_SOUND_PATH
        if self.gsettings.get_boolean(TimerApplet.KEY_USE_CUSTOM_SOUND):
            sound_path = self.gsettings.get_string(TimerApplet.KEY_CUSTOM_SOUND_PATH)
            
        print 'Playing notification sound: "%s"' % str(sound_path)
        self._play_sound(sound_path)
        print 'Started playing notification sound.'

    def _play_sound(self, file_path):
        if not file_path:
            print 'Invalid path to sound file'
            return
        self.gst_playbin.set_state(gst.STATE_NULL)
        sound_uri = 'file://' + file_path
        print 'Using GStreamer to play: ' + sound_uri
        self.gst_playbin.set_property('uri', sound_uri)
        self.gst_playbin.set_state(gst.STATE_PLAYING)

    def _run_custom_command(self, command):
        if command:
            print "Running custom command: " + command
            try:
                subprocess.call(shlex.split(command))
            except OSError:
                print "... failed. Command not found."

    def _stop_sound(self):
        self.gst_playbin.set_state(gst.STATE_NULL)

    def _start_pulsing_button(self):
        if self.gsettings.get_boolean(TimerApplet.KEY_SHOW_PULSING_ICON):
            self.status_button.start_pulsing()

    def _stop_pulsing_button(self):
        self.status_button.stop_pulsing()
        
    def _show_about_dialog(self):
        self.about_dialog.run()
        self.about_dialog.hide()

    def _call_notify(self, summary=None, message=None,
                     reminder_message_func=None, show=True):
        if self.gsettings.get_boolean(TimerApplet.KEY_SHOW_POPUP_NOTIFICATION):
            if show:
                self.notifier.begin(summary, message, reminder_message_func)
            else:
                self.notifier.end()
