# Copyright (C) 2008 Jimmy Do <jimmydo@users.sourceforge.net>
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

from gettext import gettext as _
from gi.repository import Gtk

from timerapplet import utils
from timerapplet import config
from timerapplet.core import PresetsStore
from timerapplet.ui import ManagePresetsDialog
from timerapplet.ui import AddEditPresetDialog


class GlobalController(object):
    def __init__(self):
        self.presets_store = PresetsStore(config.PRESETS_PATH)
        self.manage_presets_dialog = ManagePresetsDialog(
                    self.presets_store.get_model(),
                    lambda row_iter: utils.get_preset_display_text(self._presets_store,
                                                                   row_iter))
        self.manage_presets_dialog.connect('clicked-add', self.on_mgr_clicked_add)
        self.manage_presets_dialog.connect('clicked-edit', self.on_mgr_clicked_edit)
        self.manage_presets_dialog.connect('clicked-remove', self.on_mgr_clicked_remove)

        Gtk.Window.set_default_icon_from_file(config.ICON_PATH)

    def on_mgr_clicked_add(self, sender, data=None):
        add_dialog = AddEditPresetDialog(
            _('Add Preset'),
            lambda name: utils.is_valid_preset_name(name, self.presets_store))

        result = add_dialog.get_preset()
        if result is not None:
            (name, hours, minutes, seconds, command, next_timer, auto_start) = result
            self.presets_store.add_preset(name, hours, minutes, seconds,
                                           command, next_timer, auto_start)

    def on_mgr_clicked_edit(self, sender, row_path, data=None):
        row_iter = self._presets_store.get_model().get_iter(row_path)
        (name, hours, minutes, seconds, command, next_timer, auto_start) = \
                self.presets_store.get_preset(row_iter)

        edit_dialog = AddEditPresetDialog(
                         _('Edit Preset'),
                         lambda name: utils.is_valid_preset_name(name,
                                                                 self.presets_store,
                                                                 (name,)),
                         name,
                         hours,
                         minutes,
                         seconds,
                         command,
                         next_timer,
                         auto_start
                        )

        result = edit_dialog.get_preset()
        if result is not None:
            (name, hours, minutes, seconds, command, next_timer, auto_start) = result
            self.presets_store.modify_preset(row_iter, name, hours, minutes,
                                              seconds, command, next_timer,
                                              auto_start)

    def on_mgr_clicked_remove(self, sender, row_path, data=None):
        row_iter = self.presets_store.get_model().get_iter(row_path)
        self.presets_store.remove_preset(row_iter)

    # TODO
    def on_mgr_next_timer_is_being_edited(self, sender, row_path, data=None):
        """Show a dropdown widget to help completing the next timer."""
        raise NotImplementedError("Not implemented, yet")


