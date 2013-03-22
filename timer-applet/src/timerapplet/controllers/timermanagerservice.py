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
import dbus
import dbus.service

DBUS_INTERFACE_NAMESPACE = 'org.mate.panel.applets.TimerApplet.TimerManager'

class TimerManagerService(dbus.service.Object):
    timer_id_list = []

    def __init__(self, bus_name, object_path):
        dbus.service.Object.__init__(self,
                                     dbus.service.BusName(bus_name, bus=dbus.SessionBus()),
                                     object_path)

    def create_and_register_timer_id(self):
        timer_id = str(uuid.uuid4())
        self.register_timer_id(timer_id)
        return timer_id

    def register_timer_id(self, timer_id):
        self.timer_id_list.append(timer_id)

    def unregister_timer_id(self, timer_id):
        self.timer_id_list.remove(timer_id)

    @dbus.service.method(dbus_interface=DBUS_INTERFACE_NAMESPACE, out_signature='as')
    def GetTimerIDList(self):
        return self.timer_id_list
