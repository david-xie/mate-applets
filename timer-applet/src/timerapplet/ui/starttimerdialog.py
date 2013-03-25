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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango

from gettext import gettext as _
from shlex import split as shell_tokenize
from subprocess import check_call, CalledProcessError

from durationchooser import DurationChooser
from scrollablebuttonlist import ScrollableButtonList
from timerapplet.config import GLADE_START_TIMER_DIALOG

class StartTimerDialog(GObject.GObject):
    __gsignals__ = {'clicked-start':
                        (GObject.SignalFlags.RUN_LAST, None, ()),
                    'clicked-cancel':
                        (GObject.SignalFlags.RUN_LAST, None, ()),
                    'clicked-manage-presets':
                        (GObject.SignalFlags.RUN_LAST, None, ()),
                    'clicked-save':
                        (GObject.SignalFlags.RUN_LAST,
                         None,
                         (GObject.TYPE_STRING,
                          GObject.TYPE_INT,
                          GObject.TYPE_INT,
                          GObject.TYPE_INT,
                          GObject.TYPE_STRING,
                          GObject.TYPE_STRING,
                          GObject.TYPE_BOOLEAN)),
                    'clicked-preset':
                        (GObject.SignalFlags.RUN_LAST,
                         None,
                         (GObject.TYPE_PYOBJECT,)),
                    'double-clicked-preset':
                        (GObject.SignalFlags.RUN_LAST,
                         None,
                         (GObject.TYPE_PYOBJECT,))}

    def __init__(self, name_validator_func, presets_store, preset_display_func):
        GObject.GObject.__init__(self)

        self._valid_name_func = name_validator_func;
        self.presets_store = presets_store
        self._preset_display_func = preset_display_func
        
        self.presets_list = ScrollableButtonList()
        labels_size_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.duration_chooser = DurationChooser(labels_size_group)

        builder = Gtk.Builder()
        builder.add_from_file(GLADE_START_TIMER_DIALOG)
        self.dialog = builder.get_object('start_timer_dialog')
        self.ok_button = builder.get_object('ok_button')
        name_label = builder.get_object('name_label')
        self.name_entry = builder.get_object('name_entry')
        self.save_button = builder.get_object('save_button')
        duration_chooser_container = builder.get_object('duration_chooser_container')
        presets_chooser_container = builder.get_object('presets_chooser_container')
        self.presets_section = builder.get_object('presets_section')
        #: The TextEntry control for running a custom command
        self.command_entry = builder.get_object('command_entry')
        #: The "Invalid Command" label
        self.invalid_cmd_label = builder.get_object('invalid_command_label')
        #: The next timer combo box
        self.next_timer_combo = builder.get_object('next_timer_combo_entry')
        self.next_timer_combo.set_model(self.presets_store)
        self.next_timer_combo.set_text_column(0) # The column to be shown
        #: The auto-start check button.
        self.auto_start_check = builder.get_object('auto_start_check')
        
        labels_size_group.add_widget(name_label)
        self.dialog.set_default_response(Gtk.ResponseType.OK)
        duration_chooser_container.pack_start(self.duration_chooser, True, True, 0)
        presets_chooser_container.pack_start(self.presets_list, True, True, 0)
        
        self.dialog.connect('response', self._on_dialog_response)
        self.dialog.connect('delete-event', self.dialog.hide_on_delete)
        self.dialog.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.duration_chooser.connect('duration-changed', self._on_duration_changed)
        self.name_entry.connect('changed', self._on_name_entry_changed)
        self.save_button.connect('clicked', self._on_save_button_clicked)
        # Check that executable is valid while inserting text
        self.command_entry.connect('changed', self._check_is_valid_command)
        self.next_timer_combo.get_child().connect("changed",
                                self._on_next_timer_combo_entry_child_changed)
        builder.get_object('manage_presets_button').connect('clicked',
                                                                  self._on_manage_presets_button_clicked)
        #self.presets_store.connect('row-deleted',
        #                            lambda model, row_path: self._update_presets_list())
        #self.presets_store.connect('row-changed',
        #                            lambda model, row_path, row_iter: self._update_presets_list())

        self._update_presets_list()
        self.duration_chooser.show()
        self.presets_list.show()

    def show(self):
        if not self.dialog.props.visible:
            self.duration_chooser.clear()
            self.duration_chooser.focus_hours()
            self.name_entry.set_text('')
        self._check_for_valid_start_timer_input()
        self._check_for_valid_save_preset_input()
        self.dialog.present()
        
    def hide(self):
        self.dialog.hide()
        
    def get_control_data(self):
        """Return name and duration in a tuple.
        
        The returned tuple is in this format: 
            
            (name, hours, minutes, seconds, next_timer, auto_start)
        
        """
        return (self.name_entry.get_text().strip(),) + \
                self.duration_chooser.get_duration() + \
                (self.command_entry.get_text().strip(),
                 self.next_timer_combo.get_child().get_text().strip(),
                 self.auto_start_check.get_active())
        
    def set_name_and_duration(self, name, hours, minutes, seconds, *args):
        self.name_entry.set_text(name)
        self.command_entry.set_text(args[0])
        self.next_timer_combo.get_child().set_text(args[1])
        self.auto_start_check.set_active(args[2])
        self.duration_chooser.set_duration(hours, minutes, seconds)

    def _update_presets_list(self):
        self._check_for_valid_save_preset_input()

        if len(self.presets_store) == 0:
            self.presets_section.hide()
            
            # Make window shrink
            self.dialog.resize(1, 1)
        else:
            self.presets_section.show()
            
        for button in self.presets_list.get_buttons():
            button.destroy()
            
        row_iter = self.presets_store.get_iter_first()
        while row_iter is not None:
            name = self._preset_display_func(row_iter)
            label = Gtk.Label(label=name)
            label.set_ellipsize(Pango.EllipsizeMode.END)
            button = Gtk.Button()
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.add(label)
            self.presets_list.add_button(button)
            
            button.connect('clicked', 
                           self._on_preset_button_clicked,
                           self.presets_store.get_path(row_iter))
            button.connect('button_press_event',
                           self._on_preset_button_double_clicked,
                           self.presets_store.get_path(row_iter))
            
            label.show()
            button.show()
            
            row_iter = self.presets_store.iter_next(row_iter)
    
    def _check_is_valid_command(self, widget, data=None):
        """
        Check that input in the command entry TextBox control is a valid
        executable.
        """
        try:
            data = widget.get_text()
            executable = shell_tokenize(data)[0]
            # Check if command in path, else raise CalledProcessError
            # The idea of using `which` to check if a command is in PATH
            # originated from the Python mailing list.
            check_call(['which', executable])
            self.invalid_cmd_label.set_label('')
        except (ValueError, IndexError, CalledProcessError):
            self.invalid_cmd_label.set_label(_("<b>Command not found.</b>"))
            if data is '':
                self.invalid_cmd_label.set_label('')

    def _non_zero_duration(self):
        (hours, minutes, seconds) = self.duration_chooser.get_duration()
        return (hours > 0 or minutes > 0 or seconds > 0)

    def _check_for_valid_save_preset_input(self):
        self.save_button.props.sensitive = (self._non_zero_duration() and
                                             self._valid_name_func(self.name_entry.get_text()))
        # TODO: Add validator for next_timer_combo
    
    def _check_for_valid_start_timer_input(self):
        self.ok_button.props.sensitive = self._non_zero_duration()
    
    def _on_preset_button_clicked(self, button, row_path):
        self.emit('clicked-preset', row_path)

    def _on_preset_button_double_clicked(self, button, event, row_path):
        """Emit the `double-clicked-preset' signal."""
        # Check that the double-click event shot off on the preset button
        if event.type == Gdk._2BUTTON_PRESS:
            self.emit('double-clicked-preset', row_path)

    def _on_manage_presets_button_clicked(self, button):
        self.emit('clicked-manage-presets')
    
    def _on_duration_changed(self, data=None):
        self._check_for_valid_start_timer_input()
        self._check_for_valid_save_preset_input()
    
    def _on_name_entry_changed(self, entry):
        self._check_for_valid_save_preset_input()

    def _on_dialog_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.duration_chooser.normalize_fields()
            self.emit('clicked-start')
        elif response_id == Gtk.ResponseType.CANCEL:
            self.emit('clicked-cancel')
        self.dialog.hide()
        
    def _on_save_button_clicked(self, button):
        self.duration_chooser.normalize_fields()
        (hours, minutes, seconds) = self.duration_chooser.get_duration()
        name = self.name_entry.get_text()
        command = self.command_entry.get_text()
        next_timer = self.next_timer_combo.get_child().get_text()
        auto_start = self.auto_start_check.get_active()
        self.emit('clicked-save', name, hours, minutes, seconds, command,
                  next_timer, auto_start)

    def _on_next_timer_combo_entry_child_changed(self, widget, data=None):
        """Validate selection of the Next Timer ComboBoxEntry."""
        modelfilter = self.presets_store.filter_new()
        # Loop through all rows in ListStore
        # TODO: Using a generator may be more memory efficient in this case.
        for row in modelfilter:
            # Check that name of preset is the exact match of the the text in
            # the ComboBoxEntry
            if widget.get_text() == row[0]:
                # Yes, it matches! Make the auto-start checkbox sensitive
                # (activate it).
                self.auto_start_check.set_sensitive(True)
                break
            else:
                # If value of ComboBoxEntry is None then de-activate the
                # auto-start checkbox.
                self.auto_start_check.set_sensitive(False)

