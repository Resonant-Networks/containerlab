import subprocess
import time

def run_sr_cli(container, commands):
    script = "\n".join(commands)
    cmd = ["docker", "exec", "-i", container, "sr_cli"]
    res = subprocess.run(cmd, input=script, text=True, capture_output=True)
    print(f"=== Configured {container} ===")
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print("ERR:", res.stderr)

# 1. SPINE1 CONFIG
spine1_cmds = [
    "enter candidate",
    # Interface e1-1 to leaf1
    "set / interface ethernet-1/1 admin-state enable",
    "set / interface ethernet-1/1 subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 10.0.1.1/30",
    # Interface e1-2 to leaf2
    "set / interface ethernet-1/2 admin-state enable",
    "set / interface ethernet-1/2 subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 10.0.2.1/30",
    # System Loopback
    "set / interface system0 admin-state enable subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 1.1.1.10/32",
    # Default Network Instance
    "set / network-instance default interface ethernet-1/1.0",
    "set / network-instance default interface ethernet-1/2.0",
    "set / network-instance default interface system0.0",
    # BGP Configuration
    "set / network-instance default protocols bgp autonomous-system 65000",
    "set / network-instance default protocols bgp router-id 1.1.1.10",
    "set / network-instance default protocols bgp group ebgp-underlay admin-state enable peer-as 65011",
    "set / network-instance default protocols bgp group ebgp-underlay afi-safi ipv4-unicast admin-state enable",
    "set / network-instance default protocols bgp group ebgp-underlay afi-safi evpn admin-state enable",
    "set / network-instance default protocols bgp neighbor 10.0.1.2 admin-state enable peer-group ebgp-underlay peer-as 65011",
    "set / network-instance default protocols bgp neighbor 10.0.2.2 admin-state enable peer-group ebgp-underlay peer-as 65012",
    "commit stay"
]

# 2. LEAF1 CONFIG
leaf1_cmds = [
    "enter candidate",
    # Interface e1-1 to spine1
    "set / interface ethernet-1/1 admin-state enable",
    "set / interface ethernet-1/1 subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 10.0.1.2/30",
    # Interface e1-2 to client1 (Access Port)
    "set / interface ethernet-1/2 admin-state enable",
    "set / interface ethernet-1/2 subinterface 0 admin-state enable type bridged vlan encap single-tagged vlan-id 10",
    # System Loopback
    "set / interface system0 admin-state enable subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 1.1.1.11/32",
    # VXLAN Tunnel Interface
    "set / tunnel-interface vxlan1 vxlan-interface 1 type bridged egress source-ip use-system-ipv4-address vni 100",
    # Default Network Instance (Underlay)
    "set / network-instance default interface ethernet-1/1.0",
    "set / network-instance default interface system0.0",
    "set / network-instance default protocols bgp autonomous-system 65011",
    "set / network-instance default protocols bgp router-id 1.1.1.11",
    "set / network-instance default protocols bgp group ebgp-underlay admin-state enable peer-as 65000",
    "set / network-instance default protocols bgp group ebgp-underlay afi-safi ipv4-unicast admin-state enable",
    "set / network-instance default protocols bgp group ebgp-underlay afi-safi evpn admin-state enable",
    "set / network-instance default protocols bgp neighbor 10.0.1.1 admin-state enable peer-group ebgp-underlay peer-as 65000",
    # MAC-VRF 10 (EVPN Overlay L2 Domain)
    "set / network-instance mac-vrf-10 type mac-vrf admin-state enable",
    "set / network-instance mac-vrf-10 interface ethernet-1/2.0",
    "set / network-instance mac-vrf-10 vxlan-interface vxlan1.1",
    "set / network-instance mac-vrf-10 protocols bgp-evpn bgp-instance 1 admin-state enable vxlan-interface vxlan1.1 evi 100 ecmp 2",
    "set / network-instance mac-vrf-10 protocols bgp-vpn bgp-instance 1 route-target export target:65000:100 import target:65000:100",
    "commit stay"
]

# 3. LEAF2 CONFIG
leaf2_cmds = [
    "enter candidate",
    # Interface e1-1 to spine1
    "set / interface ethernet-1/1 admin-state enable",
    "set / interface ethernet-1/1 subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 10.0.2.2/30",
    # Interface e1-2 to client2 (Access Port)
    "set / interface ethernet-1/2 admin-state enable",
    "set / interface ethernet-1/2 subinterface 0 admin-state enable type bridged vlan encap single-tagged vlan-id 10",
    # System Loopback
    "set / interface system0 admin-state enable subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 1.1.1.12/32",
    # VXLAN Tunnel Interface
    "set / tunnel-interface vxlan1 vxlan-interface 1 type bridged egress source-ip use-system-ipv4-address vni 100",
    # Default Network Instance (Underlay)
    "set / network-instance default interface ethernet-1/1.0",
    "set / network-instance default interface system0.0",
    "set / network-instance default protocols bgp autonomous-system 65012",
    "set / network-instance default protocols bgp router-id 1.1.1.12",
    "set / network-instance default protocols bgp group ebgp-underlay admin-state enable peer-as 65000",
    "set / network-instance default protocols bgp group ebgp-underlay afi-safi ipv4-unicast admin-state enable",
    "set / network-instance default protocols bgp group ebgp-underlay afi-safi evpn admin-state enable",
    "set / network-instance default protocols bgp neighbor 10.0.2.1 admin-state enable peer-group ebgp-underlay peer-as 65000",
    # MAC-VRF 10 (EVPN Overlay L2 Domain)
    "set / network-instance mac-vrf-10 type mac-vrf admin-state enable",
    "set / network-instance mac-vrf-10 interface ethernet-1/2.0",
    "set / network-instance mac-vrf-10 vxlan-interface vxlan1.1",
    "set / network-instance mac-vrf-10 protocols bgp-evpn bgp-instance 1 admin-state enable vxlan-interface vxlan1.1 evi 100 ecmp 2",
    "set / network-instance mac-vrf-10 protocols bgp-vpn bgp-instance 1 route-target export target:65000:100 import target:65000:100",
    "commit stay"
]

if __name__ == "__main__":
    run_sr_cli("clab-demo-clos-spine1", spine1_cmds)
    run_sr_cli("clab-demo-clos-leaf1", leaf1_cmds)
    run_sr_cli("clab-demo-clos-leaf2", leaf2_cmds)
    print("EVPN VXLAN Configuration complete!")
