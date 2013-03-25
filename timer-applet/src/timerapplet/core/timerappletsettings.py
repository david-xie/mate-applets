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

from os import path
from gi.repository import Gio

class TimerAppletSettings(object):
    connection_ids = []

    def __init__(self, gschema):
        self.settings = Gio.Settings.new(gschema)

    def get_string(self, key):
        return self.settings.get_string(key)

    def get_boolean(self, key):
        return self.settings.get_boolean(key)

    def set_string(self, key, val):
        self.settings.set_string(key, val)

    def set_boolean(self, key, val):
        self.settings.set_boolean(key, val)

    def remove_all_notify(self):
        for connection_id in self.connection_ids:
            self.settings.disconnect(connection_id)
        self.connection_ids = []

    def add_notify(self, key, callback, args=None):
        connection_id = self.settings.connect("changed::%s" % key, callback, args)
        self.connection_ids.append(connection_id)
        return connection_id

    def remove_notify(self, connection_id):
        self.connection_ids.pop(connection_id)
        self.settings.disconnect(connection_id)
