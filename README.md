# Resonant Networks — Containerlab Infrastructure & MOPs

Welcome to the central repository for **Containerlab** network topologies, automation scripts, and Methods of Procedure (MOP) at Resonant Networks.

---

## 1. Repository Structure

```
containerlab/
├── topologies/
│   ├── campus-network/            # Enterprise Campus Topology (Nokia SR Linux + Alpine)
│   │   ├── campus.clab.yml        # Core & Access switches, endpoints topology definition
│   │   ├── core1.cfg, core2.cfg   # Initial node configurations
│   │   ├── access1.cfg, access2.cfg
│   │   └── README.md              # Topology details, IP allocation & verification
│   └── leaf-spine-evpn/           # Data Center Clos Fabric (BGP EVPN / VXLAN)
│       ├── topo.clab.yml          # Spine1, Leaf1, Leaf2, Clients topology
│       ├── topo.clab.yml.annotations.json
│       ├── apply_evpn_config.py   # Automated BGP EVPN & VXLAN configuration script
│       └── README.md              # Fabric overview & automation instructions
├── automation-scripts/
│   ├── setup_containerlab_monitoring.py  # Zabbix JSON-RPC node discovery & host registration
│   └── create_containerlab_dashboard.py  # Programmatic Zabbix dashboard builder
├── mops-and-runbooks/
│   ├── mop-containerlab-operations.md       # Master Containerlab operations & lifecycle MOP
│   ├── mop-nokia-srlinux-configuration.md   # Nokia SR Linux candidate datastore & CLI MOP
│   ├── mop-monitoring-integration-zabbix.md # Zabbix monitoring & alert integration MOP
│   ├── devops-history-and-setup.md          # CLI install, web app, and API server history
│   └── vscode-remote-access-guide.md        # VS Code Remote SSH & Containerlab extension setup
├── lab-examples/                  # 43 production-grade vendor reference topologies
├── knowledge.md                   # Internal engineering runbook & cheat sheet
├── AGENTS.md                      # Agent operational context
└── README.md                      # This document
```

---

## 2. Topologies Overview

### 2.1 Enterprise Campus Network (`topologies/campus-network`)
A modular enterprise campus topology designed to test layer-2/layer-3 demarcation, VLAN tagging, and client routing.
- **Core Layer:** 2x Nokia SR Linux switches (`core1`, `core2`)
- **Access Layer:** 2x Nokia SR Linux switches (`access1`, `access2`)
- **Endpoints:** 3x Alpine Linux containers (`campus-server`, `pc-eng`, `pc-sales`)
- **Deploy:**
  ```bash
  sudo containerlab deploy -t topologies/campus-network/campus.clab.yml
  ```

### 2.2 Leaf-Spine Clos Fabric with EVPN VXLAN (`topologies/leaf-spine-evpn`)
A modern 2-tier data center Clos fabric showcasing EVPN control plane and VXLAN encapsulation for L2 multi-tenancy.
- **Spine Layer:** 1x Nokia SR Linux (`spine1`, AS 65000)
- **Leaf Layer:** 2x Nokia SR Linux (`leaf1` AS 65011, `leaf2` AS 65012)
- **Clients:** 2x Alpine Linux hosts in VLAN 10 (VNI 100)
- **Deploy & Configure:**
  ```bash
  sudo containerlab deploy -t topologies/leaf-spine-evpn/topo.clab.yml
  python3 topologies/leaf-spine-evpn/apply_evpn_config.py
  ```

---

## 3. Operations & MOPs Directory

| Document | Purpose |
|---|---|
| [MOP: Containerlab Operations](mops-and-runbooks/mop-containerlab-operations.md) | Standard deployment, teardown, inspection, capture, and health check procedures. |
| [MOP: Nokia SR Linux Configuration](mops-and-runbooks/mop-nokia-srlinux-configuration.md) | Guide to candidate datastores, BGP EVPN configuration, and `sr_cli` commands. |
| [MOP: Zabbix Monitoring Integration](mops-and-runbooks/mop-monitoring-integration-zabbix.md) | Automatic discovery and dashboard creation in Zabbix for topology nodes. |
| [DevOps History & Setup](mops-and-runbooks/devops-history-and-setup.md) | Historical logs of containerlab setup, web app evaluation, and current host state. |
| [VS Code Remote Access Guide](mops-and-runbooks/vscode-remote-access-guide.md) | Connecting VS Code to remote containerlab hosts and managing labs via IDE. |
| [Engineer's Runbook](knowledge.md) | Deep-dive guide with CLI reference, kind specifications, and debugging commands. |

---

## 4. Monitoring Automation

To register active topology containers with the local Zabbix monitoring server:

```bash
cd automation-scripts
python3 setup_containerlab_monitoring.py
python3 create_containerlab_dashboard.py
```
This adds the nodes under the host group `Containerlab Topology`, attaches ICMP ping health checks, and renders a dedicated performance dashboard.

---

## 5. Quick CLI Reference

```bash
# Deploy a topology
sudo containerlab deploy -t <path/to/topo.clab.yml>

# Inspect running labs
sudo containerlab inspect --all

# Launch browser web topology graph
sudo containerlab graph -t <path/to/topo.clab.yml>

# Execute command inside a node
docker exec -it <container_name> bash
docker exec -it <container_name> sr_cli

# Packet capture on link interface
sudo ip netns exec <node_netns> tcpdump -ni <interface> -w capture.pcap

# Save active configurations
sudo containerlab save -t <path/to/topo.clab.yml>

# Destroy lab and clean up interfaces
sudo containerlab destroy -t <path/to/topo.clab.yml> --cleanup
```

---

## 6. Upstream Resources
- **Documentation:** [https://containerlab.dev](https://containerlab.dev)
- **GitHub Repository:** [https://github.com/srl-labs/containerlab](https://github.com/srl-labs/containerlab)
- **Discord Community:** [https://discord.gg/vAyddtaEV9](https://discord.gg/vAyddtaEV9)
