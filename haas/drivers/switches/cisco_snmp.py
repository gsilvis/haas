# Copyright 2013-2014 Massachusetts Open Cloud Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.


"""A switch driver for Cisco switches, using SNMP

See the documentation for the haas.drivers package for a description of this
module's interface.
"""

from subprocess import check_call
from haas.dev_support import no_dry_run

@no_dry_run
def apply_networking(net_map, config):

    # Prefix for all snmp commands
    snmp = ['snmpset', '-v2c', '-c', 'private', config["ip"]]

    def create_vlan(vlan):
        def get_dot10said(vlan):
            dot10said = 100000 + int(vlan_id)
            dot10said = "%x" % (dot10said)
            return dot10said.zfill(8)
        dot10said = get_dot10said(vlan)
        check_call(snmp + ['vtpVlanEditOperation.1', 'i', '2'])
        check_call(snmp + ['vtpVlanEditRowStatus.1.'+vlan, 'i', '4'])
        check_call(snmp + ['vtpVlanEditType.1.'+vlan, 'i', '1'])
        check_call(snmp + ['vtpVlanEditName.1.'+vlan, 's', '"vlan_'+vlan+'"'])
        # Below is to set a strange(?) so-called dot10said, which is a hex of
        # 100000+vlan_id
        check_call(snmp + ['vtpVlanEditDot10Said.1.'+vlan, 'x', dot10said])
        check_call(snmp + ['vtpVlanEditOperation.1', 'i', '3'])

    def delete_vlan(vlan):
        check_call(snmp + ['vtpVlanEditOperation.1', 'i', '2'])
        check_call(snmp + ['vtpVlanEditRowStatus.1.'+vlan, 'i', '6'])
        check_call(snmp + ['vtpVlanEditOperation.1', 'i', '3'])

    def set_access_vlan(port, vlan):
        """Set the given port to be able to access only the given VLAN.  If
        vlan_id is None, disable the port."""

        # FIXME: This function doesn't ensure that the port is in 'access'
        # mode. (gsilvis)

        # The ifIndex for FastEthernet0/1 is 2, for FastEthernet0/48 is 49.
        # Except the 48 FastEthernet ports.  There are two ports
        # GigabitEthernet0/1 and GigabitEthernet0/2
        ifIndex = str(int(port_id) + 1)

        if vlan is None:
            # remove the port by setting it to belong to the default vlan 1

            # FIXME: This is NOT the same as setting it to access
            # nothing. (gsilvis)
            check_call(snmp + ['vmVlan.'+ifIndex, 'i', '1'])
        else:
            check_call(snmp + ['vmVlan.'+ifIndex, 'i', vlan])

    # Iterate over the port map
    for port_id in net_map:
        set_access_vlan(port_id, net_map[port_id])
