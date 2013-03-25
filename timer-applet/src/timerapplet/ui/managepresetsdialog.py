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
from gi.repository import GObject

from timerapplet.config import GLADE_MANAGE_PRESETS_DIALOG

class ManagePresetsDialog(GObject.GObject):
    __gsignals__ = {'clicked-add':
                        (GObject.SignalFlags.RUN_LAST, None, ()),
                    'clicked-edit':
                        (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
                    'clicked-remove':
                        (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,))}

    def __init__(self, presets_store, preset_display_func):
        GObject.GObject.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_file(GLADE_MANAGE_PRESETS_DIALOG)
        self.dialog = builder.get_object('manage_presets_dialog')
        self.presets_view = builder.get_object('presets_view')
        self.delete_button = builder.get_object('delete_button')
        self.edit_button = builder.get_object('edit_button')
        self.add_button = builder.get_object('add_button')

        self.presets_view.set_model(presets_store)
        renderer = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn('Preset', renderer)

        def preset_cell_data_func(col, cell, model, row_iter, user_data=None):
            cell.props.text = preset_display_func(row_iter)

        col.set_cell_data_func(renderer, preset_cell_data_func)
        self.presets_view.append_column(col)

        self.dialog.connect('response', self._on_dialog_response)
        self.dialog.connect('delete-event', self.dialog.hide_on_delete)
        self.presets_view.get_selection().connect('changed', lambda selection: self._update_button_states())
        self.delete_button.connect('clicked', self._on_delete_button_clicked)
        self.edit_button.connect('clicked', self._on_edit_button_clicked)
        self.add_button.connect('clicked', self._on_add_button_clicked)

        self._update_button_states()
        self.dialog.set_default_size(300, 220)

    def show(self):
        self.dialog.present()

    def _get_selected_path(self):
        selection = self.presets_view.get_selection()
        (model, selection_iter) = selection.get_selected()
        return model.get_path(selection_iter)

    def _update_button_states(self):
        selection = self.presets_view.get_selection()
        num_selected = selection.count_selected_rows()
        self.delete_button.props.sensitive = num_selected >= 1
        self.edit_button.props.sensitive = num_selected == 1

    def _on_delete_button_clicked(self, button):
        row_path = self._get_selected_path()
        self.emit('clicked-remove', row_path)

    def _on_edit_button_clicked(self, button):
        row_path = self._get_selected_path()
        self.emit('clicked-edit', row_path)

    def _on_add_button_clicked(self, button):
        self.emit('clicked-add')

    def _on_dialog_response(self, dialog, response_id):
        dialog.hide()

