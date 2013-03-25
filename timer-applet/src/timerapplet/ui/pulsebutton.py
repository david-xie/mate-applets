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

import math
import time

from gi.repository import GObject
from gi.repository import Gtk

class PulseButton(Gtk.Button):
    anim_period_seconds = 0.7
    start_time = 0.0
    factor = 0.0

    def __init__(self):
        super(PulseButton, self).__init__()

    def start_pulsing(self):
        self.start_time = time.time()
        GObject.timeout_add(10, self._on_timeout)

    def stop_pulsing(self):
        self.start_time = 0

    def _on_timeout(self, data=None):
        if self.start_time <= 0.0:
            return False
        if self.window != None:
            delta = time.time() - self.start_time
            if delta > self.anim_period_seconds:
                delta = self.anim_period_seconds
                self.start_time = time.time()
            fraction = delta/self.anim_period_seconds
            self.factor = math.sin(fraction * math.pi)
        self.window.invalidate_rect(self.allocation, True)
        return True

    def do_expose_event(self, event):
        Gtk.Button.do_expose_event(self, event)
        if self.start_time > 0:
            context = event.window.cairo_create()
            context.rectangle(0, 0, self.allocation.width, self.allocation.height)
            #color = self.style.bg[Gtk.StateType.SELECTED]
            #color = Gdk.Color(65535, 65535, 65535)
            color = Gdk.Color(0, 0, 0)
            red = color.red / 65535.0
            green = color.green / 65535.0
            blue = color.blue / 65535.0
            context.set_source_rgba(red, green, blue, self.factor * 0.8)
            context.fill()
        return False

GObject.type_register(PulseButton)
