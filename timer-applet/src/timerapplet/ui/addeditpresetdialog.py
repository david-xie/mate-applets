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
import gi
gi.require_version("Gtk", "2.0")

from gi.repository import Gtk

from durationchooser import DurationChooser
from timerapplet.config import GLADE_ADD_EDIT_PRESET_DIALOG

class AddEditPresetDialog(object):
    def __init__(self, title, name_validator_func,
                 name='', hours=0, minutes=0, seconds=0, command='',
                 next_timer='', auto_start=False):
        self._valid_name_func = name_validator_func

        builder = Gtk.Builder()
        builder.add_from_file(GLADE_ADD_EDIT_PRESET_DIALOG)
        self.dialog = builder.get_object('add-edit-preset-dialog')
        self.ok_button = builder.get_object('ok-button')
        cancel_button = builder.get_object('cancel-button')
        cancel_button.connect("clicked", lambda action: self.dialog.hide_on_delete())

        self.name_entry = builder.get_object('name-entry')
        duration_chooser_container = builder.get_object('duration-chooser-container')
        self.duration_chooser = DurationChooser(Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL))
        self.command_entry = builder.get_object('command-entry')
        self.next_timer_entry = builder.get_object('next-timer-entry')
        self.auto_start_check = builder.get_object('auto-start-check')

        duration_chooser_container.pack_start(self.duration_chooser, True, True, 0)

        self.dialog.set_title(title)
        self.dialog.set_default_response(Gtk.ResponseType.OK)
        self.name_entry.set_text(name)
        self.command_entry.set_text(command)
        self.duration_chooser.set_duration(hours, minutes, seconds)
        self.next_timer_entry.set_text(next_timer)
        self.auto_start_check.set_active(auto_start)

        self.name_entry.connect('changed', lambda entry: self._check_for_valid_save_preset_input())
        self.duration_chooser.connect('duration-changed',
                                       lambda chooser: self._check_for_valid_save_preset_input())
        self.duration_chooser.show()

    def _non_zero_duration(self):
        (hours, minutes, seconds) = self.duration_chooser.get_duration()
        return (hours > 0 or minutes > 0 or seconds > 0)

    def _check_for_valid_save_preset_input(self):
        self.ok_button.props.sensitive = (self._non_zero_duration() and 
                                           self._valid_name_func(self.name_entry.get_text()))

    ## Callback for saving ##

    def get_preset(self):
        self._check_for_valid_save_preset_input()
        result = self.dialog.run()
        self.dialog.hide()
        if result == Gtk.ResponseType.OK:
            (hours, minutes, seconds) = self.duration_chooser.get_duration()
            cmd = self.command_entry.get_text()
            next_timer = self.next_timer_entry.get_text()
            auto_start = self.auto_start_check.get_active()
            return (self.name_entry.get_text(), hours, minutes, seconds, cmd,
                    next_timer, auto_start)
        else:
            return None
