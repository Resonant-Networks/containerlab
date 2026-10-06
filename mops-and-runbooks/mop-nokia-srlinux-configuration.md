# Method of Procedure (MOP): Nokia SR Linux Configuration & Management in Containerlab

## 1. Document Control
- **Document ID:** MOP-CLAB-SRLINUX-001
- **Platform:** Nokia SR Linux (NOS) within Containerlab (Docker Runtime)
- **Target Images:** `ghcr.io/nokia/srlinux:24.10`, `ghcr.io/nokia/srlinux:24.7`, `ghcr.io/nokia/srlinux:latest`
- **Scope:** CLI workflows, datastore commit model, BGP EVPN configuration, and automation integration.

---

## 2. Overview & Architecture

Nokia SR Linux uses an open, Linux-native microservices architecture structured around a unified YANG-modeled state and candidate datastore.

### Key Characteristics:
- **CLI Shell:** `sr_cli` (runs on top of standard Bash inside the container)
- **Datastore Model:**
  - `running`: Active operational configuration
  - `candidate`: Private or shared scratchpad where changes are prepared and validated
  - `state`: Real-time operational state and telemetry
- **Default Credentials:**
  - Username: `admin`
  - Password: `NokiaSrl1!` or `admin` (depending on license/release defaults)

---

## 3. Accessing the SR Linux CLI

### Direct Console Access via Docker
From the host system:
```bash
docker exec -it <container_name> sr_cli
```
*Example:*
```bash
docker exec -it clab-small-campus-core1 sr_cli
```

### SSH Access
Containerlab maps management IP addresses onto the `clab` Docker bridge network:
```bash
ssh admin@<management_ip>
```

---

## 4. Configuration Workflow (Candidate Datastore)

SR Linux requires entering `candidate` mode prior to making configuration adjustments:

```text
--{ running }--[ ]--
# enter candidate

--{ * candidate shared }--[ ]--
# set / interface ethernet-1/1 admin-state enable
# diff
# commit stay
```

### Essential CLI Navigation Commands:
| Command | Description |
|---|---|
| `enter candidate [private \| shared]` | Enter candidate datastore editing session |
| `diff` | Compare candidate configuration against running |
| `discard [now]` | Abort changes in candidate and revert to running |
| `validate` | Syntactically and semantically validate candidate against YANG models |
| `commit stay` | Commit changes to running datastore and stay in candidate mode |
| `commit now` | Commit changes to running datastore and return to running mode |
| `commit save` | Commit changes and persist configuration to disk (`config.json`) |
| `quit` | Exit candidate mode or close `sr_cli` |

---

## 5. Standard Configuration Patterns

### 5.1 System Loopback Interface (`system0`)
```text
enter candidate
set / interface system0 admin-state enable
set / interface system0 subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 1.1.1.10/32
set / network-instance default interface system0.0
commit stay
```

### 5.2 Routed P2P Core Interface
```text
enter candidate
set / interface ethernet-1/1 admin-state enable
set / interface ethernet-1/1 subinterface 0 admin-state enable ipv4 admin-state enable ipv4 address 10.0.1.1/30
set / network-instance default interface ethernet-1/1.0
commit stay
```

### 5.3 Bridged Access Port (VLAN-tagged or untagged)
```text
enter candidate
set / interface ethernet-1/2 admin-state enable
set / interface ethernet-1/2 subinterface 0 admin-state enable type bridged vlan encap single-tagged vlan-id 10
commit stay
```

### 5.4 BGP Underlay & Overlay (EVPN)
```text
enter candidate
set / network-instance default protocols bgp autonomous-system 65000
set / network-instance default protocols bgp router-id 1.1.1.10
set / network-instance default protocols bgp group ebgp-underlay admin-state enable peer-as 65011
set / network-instance default protocols bgp group ebgp-underlay afi-safi ipv4-unicast admin-state enable
set / network-instance default protocols bgp group ebgp-underlay afi-safi evpn admin-state enable
set / network-instance default protocols bgp neighbor 10.0.1.2 admin-state enable peer-group ebgp-underlay peer-as 65011
commit stay
```

### 5.5 VXLAN Tunnel & MAC-VRF (L2 EVPN)
```text
enter candidate
set / tunnel-interface vxlan1 vxlan-interface 1 type bridged egress source-ip use-system-ipv4-address vni 100
set / network-instance mac-vrf-10 type mac-vrf admin-state enable
set / network-instance mac-vrf-10 interface ethernet-1/2.0
set / network-instance mac-vrf-10 vxlan-interface vxlan1.1
set / network-instance mac-vrf-10 protocols bgp-evpn bgp-instance 1 admin-state enable vxlan-interface vxlan1.1 evi 100 ecmp 2
commit stay
```

---

## 6. Operational Verification & Troubleshooting

### Show Interfaces
```text
show interface brief
show interface ethernet-1/1
```

### Show Network Instances
```text
show network-instance summary
show network-instance default
show network-instance mac-vrf-10
```

### Show BGP State
```text
show network-instance default protocols bgp summary
show network-instance default protocols bgp neighbor
show network-instance default protocols bgp routes evpn summary
```

### Show MAC Address Table (in MAC-VRF)
```text
show network-instance mac-vrf-10 bridge-table mac-table all
```

---

## 7. Automated Configuration Delivery

Scripts can feed configuration batches into SR Linux via `sr_cli` standard input non-interactively:

```python
import subprocess

def push_srl_config(container_name, commands):
    script_body = "\n".join(commands) + "\n"
    res = subprocess.run(
        ["docker", "exec", "-i", container_name, "sr_cli"],
        input=script_body,
        text=True,
        capture_output=True
    )
    print("STDOUT:", res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
```
*(Reference: see `topologies/leaf-spine-evpn/apply_evpn_config.py` for complete executable implementation).*
