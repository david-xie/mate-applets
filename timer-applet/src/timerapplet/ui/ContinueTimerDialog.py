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

from gettext import gettext as _
from gi.repository import Gtk

class ContinueTimerDialog(object):
    (STOP_TIMER, KEEP_PAUSED, CONTINUE_TIMER) = xrange(3)

    def __init__(self, glade_file_name, header_text, body_text):
        self._dialog = Gtk.Dialog(_('Continue Timer'),
                                  None,
                                  Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                  (_('_Stop Timer'), Gtk.ResponseType.NO,
                                   _('_Keep Paused'), Gtk.ResponseType.CLOSE,
                                   _('_Continue Timer'), Gtk.ResponseType.YES))
        self._dialog.props.border_width = 6
        self._dialog.props.has_separator = False
        self._dialog.props.resizable = False
        self._dialog.vbox.props.spacing = 12
        self._dialog.set_default_response(Gtk.ResponseType.YES)

        hbox = Gtk.HBox(False, 0)
        hbox.props.spacing = 12
        hbox.props.border_width = 6
        
        image = Gtk.Image.new_from_stock(Gtk.STOCK_DIALOG_QUESTION, Gtk.IconSize.DIALOG)
        image.props.yalign = 0.0
        
        label = Gtk.Label('<span weight="bold" size="larger">%s</span>\n\n%s' % (header_text, body_text))
        label.props.use_markup = True
        label.props.wrap = True
        label.props.yalign = 0.0
        
        hbox.pack_start(image, False, False, 0)
        hbox.pack_start(label, False, False, 0)
        self._dialog.vbox.pack_start(hbox, False, False, 0)
        
        hbox.show_all()

    def get_response(self):
        dialog_result = self._dialog.run()
        self._dialog.hide()
        if dialog_result == Gtk.ResponseType.YES:
            return ContinueTimerDialog.CONTINUE_TIMER
        elif dialog_result == Gtk.ResponseType.NO:
            return ContinueTimerDialog.STOP_TIMER
        else:
            return ContinueTimerDialog.KEEP_PAUSED

