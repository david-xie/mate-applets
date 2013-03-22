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
import dbus
import dbus.service
from timerapplet.core import Timer
from timerapplet import utils

DBUS_INTERFACE_NAMESPACE = 'org.mate.panel.applets.TimerApplet.Timer'

class TimerService(dbus.service.Object):
    def __init__(self, bus_name, object_path, timer):
        dbus.service.Object.__init__(self,
                     dbus.service.BusName(bus_name, bus=dbus.SessionBus()),
                     object_path)
        self.timer = timer

    @dbus.service.method(dbus_interface=DBUS_INTERFACE_NAMESPACE, in_signature='siii')
    def Start(self, name, hours, minutes, seconds):
        if self.timer.get_state() != Timer.STATE_IDLE:
            self.timer.reset()
        self.timer.set_duration(utils.hms_to_seconds(hours, minutes, seconds))
        self.timer.set_name(name)
        self.timer.start()

    @dbus.service.method(dbus_interface=DBUS_INTERFACE_NAMESPACE)
    def Stop(self):
        if self.timer.get_state() != Timer.STATE_IDLE:
            self.timer.reset()

    @dbus.service.method(dbus_interface=DBUS_INTERFACE_NAMESPACE)
    def PauseContinue(self):
        if self.timer.get_state() == Timer.STATE_RUNNING:
            self.timer.stop()
        elif self.timer.get_state() == Timer.STATE_PAUSED:
            self.timer.start()
