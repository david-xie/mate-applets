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

from gettext import gettext as _
from timerapplet.config import VERSION
from timerapplet.config import ICON_PATH
from timerapplet.config import GLADE_ABOUT_DIALOG

properties = {
        "program-name" : _("TimerApplet"),
        "version" : VERSION,
        "comments" : _("Test"),
        "copyright" : "sdgasg"
    }

class AboutDialog(object):
    def show(self):
        dialog = Gtk.AboutDialog()
        try:
            properties['logo'] = GdkPixbuf.Pixbuf.new_from_file_at_size(join(mate_invest.ART_DATA_DIR, "invest_neutral.svg"), 96, 96)
        except Exception, msg:
            pass
        dialog.connect('response', lambda self, *args: self.destroy())
        for key, value in properties.items():
            dialog.set_property(key, value)
        dialog.show_all()
