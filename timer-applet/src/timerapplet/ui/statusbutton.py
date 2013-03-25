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
from gi.repository import Gtk

from pulsebutton import PulseButton
from piemeter import PieMeter

class StatusButton(PulseButton):
    def __init__(self):
        PulseButton.__init__(self)
        self.tooltip = Gtk.Tooltip()
        self.icon = Gtk.Image()
        self.pie_meter = PieMeter()
        self.label = Gtk.Label()
        self.visual_box = Gtk.HBox()
        self.visual_box.pack_start(self.icon, True, True, 0)
        self.visual_box.pack_start(self.pie_meter, True, True, 0)
        self.layout_box = None
        self.use_vertical = None
        self.set_use_vertical_layout(False)
        # pie_meter will default to visible while
        # icon_widget will default to hidden.
        self.pie_meter.show()
        self.visual_box.show()
        self.label.show()
    
    def set_tooltip(self, tip_text):
        self.tooltip.set_text(tip_text)
    
    def set_label(self, text):
        self.label.set_text(text)
        
    def set_icon(self, image_path):
        self.label.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(image_path, -1, 20))
        #elf._icon_widget.set_from_file(image_path)

    def set_use_icon(self, use_icon):
        if use_icon:
            self.pie_meter.hide()
            self.icon.show()
        else:
            self.pie_meter.show()
            self.icon.hide()

    def set_sensitized(self, sensitized):
        self.label.props.sensitive = sensitized
        
    def set_show_remaining_time(self, show_remaining_time):
        if show_remaining_time:
            self.label.show()
        else:
            self.label.hide()

    def set_progress(self, progress):
        self.pie_meter.set_progress(progress)

    def set_use_vertical_layout(self, use_vertical):
        if self.use_vertical == use_vertical:
            return

        self.use_vertical = use_vertical
        if self.layout_box is not None:
            self.layout_box.remove(self.visual_box)
            self.layout_box.remove(self.label)
            self.remove(self.layout_box)
            self.layout_box.destroy()
            self.layout_box = None

        new_layout_box = None
        if self.use_vertical:
            new_layout_box = Gtk.VBox(False, 2)
        else:
            new_layout_box = Gtk.HBox(False, 2)

        new_layout_box.pack_start(self.visual_box, True, True, 0)
        new_layout_box.pack_start(self.label, False, False, 0)

        self.layout_box = new_layout_box
        self.add(self.layout_box)
        self.layout_box.show()

    def set_pie_fill_color(self, red, green, blue):
        self.pie_meter.set_fill_color(red, green, blue)
