# Method of Procedure (MOP): Containerlab Operations & Lifecycle Management

| Document Property | Value |
|---|---|
| **Document Version** | 1.0 |
| **Applies To** | Containerlab v0.77.0+ on Ubuntu 24.04 LTS (`ubuntu-rm1dev`) |
| **Target Audience** | NOC Engineers, Network Architects, Automation Engineers |
| **Author** | Resonant Networks Engineering |

---

## 1. Scope & Prerequisites

This MOP establishes the operational procedures for creating, validating, managing, and tearing down containerized network topologies using **Containerlab**.

### Prerequisites
* Docker Engine 24+ installed and running.
* Containerlab CLI installed (`/usr/bin/containerlab` or `bin/containerlab`).
* Root privileges (`sudo`) required for veth interface creation and namespace binding.
* Base images available (e.g. `ghcr.io/nokia/srlinux:latest`, `alpine:latest`).

---

## 2. Standard Lifecycle Commands

| Lifecycle Phase | Command | Description |
|---|---|---|
| **Deploy** | `sudo containerlab deploy -t <topo.yml>` | Parses YAML, creates veth pairs, boots containers, applies exec commands |
| **Re-deploy** | `sudo containerlab deploy -t <topo.yml> --reconfigure` | Overwrites running instances with fresh configs |
| **Inspect** | `sudo containerlab inspect -t <topo.yml>` | Displays running container IDs, management IPs, IPv6 links, state |
| **Graph** | `sudo containerlab graph -t <topo.yml> --srv :5008` | Launches built-in web visualization server |
| **Save Configs** | `sudo containerlab save -t <topo.yml>` | Extracts running configs from network NOSes into startup directories |
| **Destroy** | `sudo containerlab destroy -t <topo.yml> --cleanup` | Shuts down containers, removes bridge networks, and deletes lab artifacts |

---

## 3. Step-by-Step Procedure: Deploying a Lab Topology

### Step 1: Pre-flight Verification
Check running Docker containers to avoid IP or port conflicts:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Step 2: Deploy the Topology
```bash
cd /path/to/topology/directory
sudo containerlab deploy -t topology.clab.yml
```

### Step 3: Verify Node Health & Management IPs
```bash
sudo containerlab inspect --all
```
Ensure all required nodes indicate status `running`.

---

## 4. Node Access Procedures

### 4.1 Nokia SR Linux Access
```bash
# Direct CLI access via sr_cli
docker exec -it clab-<lab-name>-<node-name> sr_cli

# Linux bash shell access
docker exec -it clab-<lab-name>-<node-name> bash

# SSH access (default credentials: admin / admin or nokia / nokia123)
ssh admin@<management-ip>
```

### 4.2 Linux Host / Endpoint Access
```bash
docker exec -it clab-<lab-name>-<node-name> sh
```

---

## 5. Live Packet Capture on Virtual Links

### Option A: Using Built-in Edgeshark / Packetflix Web UI
Navigate to `http://192.168.0.9:5001/` in your browser. Locate the container and interface (e.g., `e1-1`), and click **Wireshark Live Stream**.

### Option B: Direct CLI tcpdump & Wireshark Piping
```bash
# Live packet dump on specific interface
sudo ip netns exec clab-<lab>-<node> tcpdump -ni e1-1 -vv
```

---

## 6. Teardown & Post-Lab Cleanup

Always clean up virtual interfaces and lab artifacts when testing is complete:

```bash
sudo containerlab destroy -t topology.clab.yml --cleanup
```
The `--cleanup` flag removes the directory containing generated certificates, hosts files, and runtime state.
