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

import os.path as path

try:
    from defs import *
except ImportError:
    PACKAGE = 'timer-applet'
    VERSION = '0'
    GETTEXT_PACKAGE = ''
    LOCALE_DIR = ''
    RESOURCES_DIR = path.join(path.dirname(__file__), '../../data')
    IMAGES_DIR = path.join(path.dirname(__file__), '../../images')

print 'Using these definitions:'
print 'GETTEXT_PACKAGE: %s' % GETTEXT_PACKAGE
print 'LOCALE_DIR: %s' % LOCALE_DIR
print 'RESOURCES_DIR: %s' % RESOURCES_DIR
print 'IMAGES_DIR: %s' % IMAGES_DIR

GLADE_ABOUT_DIALOG = path.join(RESOURCES_DIR, 'glades/about-dialog.glade')
GLADE_MANAGE_PRESETS_DIALOG = path.join(RESOURCES_DIR, 'glades/manage-presets-dialog.glade')
GLADE_PREFERENCES_DIALOG = path.join(RESOURCES_DIR, 'glades/preferences-dialog.glade')
GLADE_START_TIMER_DIALOG = path.join(RESOURCES_DIR, 'glades/start-timer-dialog.glade')
GLADE_ADD_EDIT_PRESET_DIALOG = path.join(RESOURCES_DIR, 'glades/add-edit-preset-dialog.glade')
POPUP_MENU_FILE_PATH = path.join(RESOURCES_DIR, 'TimerApplet.xml')
GSCHEMA = 'org.mate.panel.applets.TimerApplet'
ICON_PATH = path.join(IMAGES_DIR, 'timer-applet.png')
PRESETS_PATH = path.expanduser('~/.config/mate/timer-applet/presets.xml')
DEFAULT_SOUND_PATH = '/usr/share/sounds/gtk-events/clicked.wav'
