# DevOps History: Containerlab Installation, Experiments & State

## 1. Executive Summary

This document records the installation, configuration history, and architectural experiments performed on the lab server regarding Containerlab, its ecosystem tools (`containerlab-web`, `clab-api-server`), and its production runtime state.

---

## 2. Component History & Log Tracking

### 2.1 Containerlab CLI
- **Installation Date:** 2026-06-25
- **Install Method:** Official installer script:
  ```bash
  bash -c "$(curl -sL https://get.containerlab.dev)"
  ```
- **Current Version:** v0.77.0 (`/usr/bin/containerlab` and source build in `bin/containerlab`)
- **Status:** **Active & Production Ready**

### 2.2 Containerlab-Web App Experiment
- **Evaluation Date:** 2026-06-25 05:55 (Ref: DevOps Daily Log 03)
- **Image:** `ghcr.io/srl-labs/containerlab-web:latest`
- **Initial Deployment:** Standalone Node.js container mapped to port `:3001`.
- **Finding:** The web UI was tested for visual topology interaction. However, because network topologies were managed via Git and CLI automation, and it lacked full reverse proxy / auth integration, it was decommissioned to conserve server memory.
- **Current Status:** Container and Docker image removed.
- **Rollback / Re-deploy Command:**
  ```bash
  docker run -d --name containerlab-app --restart always \
    -p 3001:3001 \
    ghcr.io/srl-labs/containerlab-web:latest
  ```

### 2.3 Containerlab API Server Experiment
- **Evaluation Date:** 2026-06-25 10:45 (Ref: DevOps Daily Log 05)
- **Install Method:**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/srl-labs/clab-api-server/main/install.sh | sudo bash -s -- install
  ```
- **Configuration Path:** `/etc/clab-api-server/clab-api-server.env`
- **Finding:** Evaluated for headless remote orchestration over REST API. Due to direct shell and python automation workflows being preferred, the service was stopped and removed to eliminate background daemon overhead. Configuration files were preserved on disk at `/etc/clab-api-server/`.
- **Current Status:** Container removed, systemd unit disabled.
- **Rollback / Re-deploy Command:**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/srl-labs/clab-api-server/main/install.sh | sudo bash -s -- install
  sudoedit /etc/clab-api-server/clab-api-server.env
  ```

---

## 3. Current Host Configuration & Capabilities

- **Docker Bridge:** Containerlab automatically creates and manages the `clab` Docker network interface (`172.20.20.0/24`).
- **Permissions:** Sudo privileges or setuid root binary configured for network interface creation (`ip link`, `veth` pairs, `netns` operations).
- **Active Topologies Running:**
  - `small-campus` (7 containers): Core switches, Access switches, Linux clients.
