# VS Code Remote Access — Containerlab Server

## Connection Architecture

```
Windows (VS Code)
     │
     │  ssh jumpuser@<wsl-ip>
     ▼
WSL / Ubuntu 22.04  ←  <wsl-hostname>  (jump host)
     │
     │  ssh user@<tailscale-ip>  (via Tailscale)
     ▼
Containerlab Server  ←  <server-hostname>  (target)
     IPs: <tailscale-ip> (Tailscale)
          <lan-ip>        (LAN)
```

Two hops:
1. Windows VS Code → WSL jump host (`jumpuser@<wsl-ip>`)
2. WSL jump host → Containerlab server (`user@<tailscale-ip>` via Tailscale)

---

## Prerequisites

### Containerlab Server (<server-hostname>)

- SSH server installed and running
- Tailscale connected and authenticated

Check:
```bash
sudo ss -tlnp | grep :22
# Expected: LISTEN ... 0.0.0.0:22

tailscale status | grep "$(hostname)"
# Expected: <tailscale-ip>  <server-hostname>  ...  active
```

### WSL Jump Host (<wsl-hostname>)

- SSH server installed and running (so VS Code can connect)
- Password or key-based access configured

Check:
```bash
sudo systemctl status ssh  # should show active (running)
```

---

## Setup Steps

### 1. On Containerlab Server — Enable SSH

```bash
sudo apt update && sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo ss -tlnp | grep :22  # verify
```

### 2. On WSL Jump Host — Enable SSH

```bash
sudo apt update && sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

### 3. Add Your Public Key

On **Windows**, get your public key:

```powershell
type C:\Users\<windows-user>\.ssh\id_ed25519.pub
```

Or generate one if none exists:

```powershell
ssh-keygen -t ed25519
```

Copy the output, then add it to `authorized_keys` on both the jump host and the server.

On **WSL jump host**:
```bash
echo "<paste-key>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

On **Containerlab server**:
```bash
echo "<paste-key>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. Configure VS Code on Windows

Edit `C:\Users\<windows-user>\.ssh\config`:

```
Host containerlab-server
    HostName <tailscale-ip>
    User <server-user>
    ProxyJump <jump-user>@<wsl-ip>

Host <wsl-ip>
    User <jump-user>
```

**Explanation:**
- When you connect to `containerlab-server`, VS Code first SSHes into WSL (`<jump-user>@<wsl-ip>`)
- Then from WSL, it SSHes to the server (`<server-user>@<tailscale-ip>`)
- `<wsl-ip>` is WSL's internal IP (changes if WSL is restarted — check with `hostname -I`)

### 5. Connect

In VS Code on Windows:

- `Ctrl+Shift+P` → **Remote-SSH: Connect to Host...**
- Select `containerlab-server`
- VS Code opens `/home/ubuntu/containerlab`

---

## Testing Connectivity

### On Windows → WSL

```powershell
ssh <jump-user>@<wsl-ip>
```

### On WSL → Containerlab Server

```bash
ssh <server-user>@<tailscale-ip>
```

### On Containerlab Server — Verify it's ready

```bash
hostname          # should show <server-hostname>
tailscale ip -4   # should show <tailscale-ip>
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ssh: connect to host ... port 22: Connection timed out` | SSH server not running on target | `sudo systemctl enable --now ssh` on the target machine |
| `ssh: connect to host ... port 22: Connection refused` | SSH server not installed | `sudo apt install -y openssh-server` on the target |
| `Permission denied (publickey)` | Public key not in `authorized_keys` | Append your Windows public key to `~/.ssh/authorized_keys` on the target |
| `WSL IP changed` | WSL VM restarted | Run `hostname -I` in WSL, update `<wsl-ip>` in VS Code SSH config |
| Can't reach Jump Host | WSL not running | Start WSL from Windows Terminal or PowerShell: `wsl` |
| Can't reach server from WSL | No Tailscale route | `tailscale status` on server — verify it's connected and has an IP |
| `ProxyJump` errors | SSH version too old | Windows 10/11 OpenSSH supports ProxyJump. Run `ssh -V` to verify 8.x+ |
| VS Code "Resolver error" | See VS Code output panel | `Ctrl+Shift+P` → **Remote-SSH: Show Log** for detailed error |

### WSL IP Changes After Restart

WSL gets a new IP each time it restarts. Update `<wsl-ip>` in your `~/.ssh/config` accordingly.

To find the current WSL IP from Windows:

```powershell
wsl hostname -I
```

Or use a static approach — add this to your VS Code SSH config to resolve dynamically:

```
Host wsl-jump
    HostName <wsl-ip>
    User <jump-user>
    # Update this IP when WSL restarts
```

### If ProxyJump Fails

Test each hop manually:

1. From Windows PowerShell: `ssh <jump-user>@<wsl-ip>` ✓
2. From that WSL session: `ssh <server-user>@<tailscale-ip>` ✓
3. If both work, ProxyJump should work too

---

## Quick Reference

| Machine | User | IP | Role |
|---|---|---|---|
| Windows | (VS Code) | — | Client |
| <wsl-hostname> (WSL) | `<jump-user>` | `<wsl-ip>` | Jump host |
| <server-hostname> | `<server-user>` | `<tailscale-ip>` (Tailscale) | Target (containerlab server) |

> **Tip**: For a cleaner setup, install Tailscale inside WSL (`sudo tailscale up`). Then WSL can reach the Tailscale IP `<tailscale-ip>` directly without needing the server on the local LAN.
