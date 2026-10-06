# Method of Procedure (MOP): Zabbix Monitoring Integration for Containerlab

## 1. Document Control
- **Document ID:** MOP-CLAB-ZBX-001
- **Platform:** Zabbix 7.0+ Integration with Containerlab Topology Nodes
- **Associated Scripts:**
  - `automation-scripts/setup_containerlab_monitoring.py`
  - `automation-scripts/create_containerlab_dashboard.py`

---

## 2. Architecture & Objective

Containerlab spins up virtual networking elements (Nokia SR Linux, Arista cEOS, Alpine hosts) with bridge interfaces on the host Docker network (`clab` or `br-clab`). 

This MOP establishes automated monitoring of virtual topology nodes inside Zabbix:
1. **Discovery & Registration:** Automatically query running containerlab instances and register them as monitored hosts in Zabbix under a dedicated hostgroup (`Containerlab Topology`).
2. **Availability Checks:** Apply the `Linux by Zabbix agent` or `ICMP Ping` templates to track node up/down status, ping latency, and interface health.
3. **Visualization:** Programmatically generate interactive Zabbix dashboards summarizing topology status, latency graphs, and alerts.

---

## 3. Prerequisites

- Zabbix Server & Frontend reachable at `http://localhost:8080` (or host IP:8080).
- Zabbix Admin credentials configured in Python automation environment.
- Python 3 with `requests` installed:
  ```bash
  pip install requests
  ```

---

## 4. Automated Host Provisioning Procedure

### 4.1 Script Execution
Navigate to `automation-scripts/` and execute `setup_containerlab_monitoring.py`:

```bash
cd /home/ubuntu/containerlab/automation-scripts
python3 setup_containerlab_monitoring.py
```

### 4.2 Provisioning Workflow
1. Authenticates against the Zabbix JSON-RPC API (`/api_jsonrpc.php`).
2. Validates or creates the Host Group `Containerlab Topology`.
3. Discovers nodes from the active Containerlab deployment:
   - `core1` (`172.20.20.10`)
   - `core2` (`172.20.20.11`)
   - `access1` (`172.20.20.12`)
   - `access2` (`172.20.20.13`)
   - `campus-server` (`172.20.20.14`)
   - `pc-eng` (`172.20.20.15`)
   - `pc-sales` (`172.20.20.16`)
4. Links the `ICMP Ping` template (`Template Module ICMP Ping`).
5. Activates polling intervals.

---

## 5. Dashboard Generation Procedure

### 5.1 Script Execution
Execute `create_containerlab_dashboard.py`:

```bash
python3 create_containerlab_dashboard.py
```

### 5.2 Dashboard Layout
The script builds a custom dashboard named `Containerlab - Small Campus Overview`:
- **Top Bar:** System Status and Active Problems widget.
- **Left Panel:** Host Availability grid showing ping status for each node.
- **Center Panel:** ICMP Ping response time graph comparing Core and Access nodes.
- **Right Panel:** Topology inventory list with IP mappings and container IDs.

---

## 6. Verification & Validation

1. Log in to the Zabbix Web UI (`http://<SERVER_IP>:8080`).
2. Navigate to **Data collection > Hosts**:
   - Filter by Host Group: `Containerlab Topology`.
   - Verify all 7 nodes show Green status for availability.
3. Navigate to **Dashboards**:
   - Select `Containerlab - Small Campus Overview`.
   - Confirm graph rendering and telemetry feeds.
4. Test failover / down detection:
   ```bash
   docker stop clab-small-campus-pc-sales
   ```
   - Confirm problem trigger fires within 60 seconds on Zabbix dashboard.
   - Restart container:
   ```bash
   docker start clab-small-campus-pc-sales
   ```
