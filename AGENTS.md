# Containerlab — Network Simulation Labs

## What this is
Containerlab network topology labs for testing routing protocols, network OS configurations, and multi-vendor scenarios.

## Structure
- `lab-examples/` — Individual lab topologies (SRL, FRR, vJunos, vMX, Cisco, FortiGate, etc.)
- `README.md` — Project overview
- `vscode-remote-access-guide.md` — VS Code setup guide

## Common commands
```bash
# Deploy a lab
sudo containerlab deploy -t lab-examples/<lab>/<topo>.clab.yml

# Destroy a lab
sudo containerlab destroy -t lab-examples/<lab>/<topo>.clab.yml
```

## Access
All labs run via Docker on the Ubuntu VM. Individual node SSH details are printed during `containerlab deploy`.
