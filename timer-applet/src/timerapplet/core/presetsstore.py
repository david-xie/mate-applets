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

import os
from os import path

import timerapplet.utils as utils
from gi.repository import GObject
from gi.repository import Gtk

from timerapplet.defs import VERSION
from timerapplet.utils import serialize_bool
from timerapplet.utils import deserialize_bool
from timerapplet.utils import seconds_to_hms
from timerapplet.utils import hms_to_seconds

try:
    from xml.etree import ElementTree as et
except:
    from elementtree import ElementTree as et


def load_presets(model, filename):
    try:
        tree = et.parse(filename)
    except:
        return

    root = tree.getroot()

    for node in root:
        name = node.get('name')
        (hours, minutes, seconds) = seconds_to_hms(int(node.get('duration')))
        command = node.get('command')
        next_timer = node.get('next_timer')
        auto_start = node.get('auto_start')
        model.append((name, hours, minutes, seconds, command, next_timer,
                      deserialize_bool(auto_start)))


def save_presets(model, filename):
    root = et.Element('timerapplet')
    root.set('version', VERSION)

    def add_xml_node(model, path, row_iter):
        (name, hours, minutes, seconds, command, next_timer, auto_start) = \
                model.get(row_iter, 
                          PresetsStore.NAME_COL,
                          PresetsStore.HOURS_COL,
                          PresetsStore.MINUTES_COL,
                          PresetsStore.SECONDS_COL, 
                          PresetsStore.COM_COL,
                          PresetsStore.NEXT_COL,
                          PresetsStore.AUTO_START_COL
                        )
        node = et.SubElement(root, 'preset')
        node.set('name', name)
        node.set('duration', str(hms_to_seconds(hours, minutes, seconds)))
        node.set('command', command or '')
        node.set('next_timer', next_timer or '')
        node.set('auto_start', serialize_bool(auto_start))

    model.foreach(add_xml_node)
    tree = et.ElementTree(root)

    file_dir = path.dirname(filename)
    if not path.exists(file_dir):
        print 'Creating config directory: %s' % file_dir
        os.makedirs(file_dir, 0744)
    tree.write(filename)


class PersistentStore(Gtk.ListStore):
    def __init__(self, load_func, save_func, *args):
        GObject.GObject.__init__(self)
        load_func(self)
        self.connect('row-deleted', lambda model, row_path: save_func(self))
        self.connect('row-changed', lambda model, row_path, row_iter: save_func(self))


class PresetsStore(GObject.GObject):
    (NAME_COL,
     HOURS_COL,
     MINUTES_COL,
     SECONDS_COL,
     COM_COL,
     NEXT_COL,
     AUTO_START_COL) = xrange(7)

    def __init__(self, filename):
        #object.__init__(self)
        self.model = PersistentStore(lambda model: load_presets(model, filename),
                                      lambda model: save_presets(model, filename))

    def get_model(self):
        """Return GtkTreeModel.
        Should not rely on it being any particular subtype of GtkTreeModel.
        """
        return self.model

    def get_preset(self, row_iter):
        return self.model.get(row_iter,
                              PresetsStore.NAME_COL,
                              PresetsStore.HOURS_COL,
                              PresetsStore.MINUTES_COL,
                              PresetsStore.SECONDS_COL,
                              PresetsStore.COM_COL,
                              PresetsStore.NEXT_COL,
                              PresetsStore.AUTO_START_COL,
                            )

    def add_preset(self, name, hours, minutes, seconds, command, next_timer,
                   auto_start):
        self.model.append((name, hours, minutes, seconds, command, next_timer,
                           auto_start))

    def modify_preset(self, row_iter, name, hours, minutes, seconds, command,
                      next_timer, auto_start):
        self.model.set(row_iter,
                       PresetsStore.NAME_COL, name,
                       PresetsStore.HOURS_COL, hours,
                       PresetsStore.MINUTES_COL, minutes,
                       PresetsStore.SECONDS_COL, seconds,
                       PresetsStore.COM_COL, command,
                       PresetsStore.NEXT_COL, next_timer,
                       PresetsStore.AUTO_START_COL, auto_start
                    )

    def remove_preset(self, row_iter):
        self.model.remove(row_iter)

    def preset_name_exists_case_insensitive(self, preset_name):
        preset_name = preset_name.lower()
        for preset in self.model:
            if preset_name == preset[PresetsStore.NAME_COL].lower():
                return True
        return False
