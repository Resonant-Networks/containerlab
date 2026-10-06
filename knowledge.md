# Containerlab — Engineer's Runbook

## 1. Project Layout

```
containerlab/
├── cmd/          # CLI command implementations (deploy, destroy, inspect, ...)
├── core/         # Lab orchestration logic
├── nodes/        # Kind-specific node implementations (srl/, ceos/, linux/, ...)
├── links/        # Virtual wiring (veth, bridge, vxlan, macvlan, ...)
├── runtime/      # Docker/Podman runtime abstraction
├── types/        # Type definitions
├── git/          # Git repo cloning for remote topology files
├── constants/    # Labels, env vars, defaults
├── schemas/      # JSON schema for topology validation
├── docs/         # Zensical documentation site
│   ├── cmd/      # CLI command reference
│   ├── manual/   # Topology file, nodes, kinds, networking docs
│   │   └── kinds/  # 61 kind-specific docs
│   └── rn/       # Release notes
├── lab-examples/ # 42 ready-to-deploy example labs (srlceos01, clos01, ...)
├── tests/        # Robot Framework integration tests
├── bin/          # Built containerlab binary lives here
├── main.go       # Entry point
├── Makefile      # Build, test, lint, docs targets
└── knowledge.md  # ← You are here
```

---

## 2. Build the Binary

```bash
cd /home/ubuntu/containerlab
make build
```

The binary is placed at `bin/containerlab` with setuid root (required for creating network interfaces). Alias it for convenience:

```bash
alias clab='sudo /home/ubuntu/containerlab/bin/containerlab'
```

---

## 3. Pick and Navigate to a Lab

All example labs are in `lab-examples/`. Each is self-contained:

```bash
ls lab-examples/
```

Pick one, e.g. `srlceos01`:

```bash
cd /home/ubuntu/containerlab/lab-examples/srlceos01
```

Inspect the topology file:

```bash
cat srlceos01.clab.yml
```

Expected output:

```yaml
name: srlceos01

topology:
  nodes:
    srl:
      kind: nokia_srlinux
      image: ghcr.io/nokia/srlinux:24.10
    ceos:
      kind: arista_ceos
      image: ceos:4.32.0F

  links:
    - endpoints: ["srl:ethernet-1/1", "ceos:eth1"]
```

---

## 4. Deploy the Lab

```bash
sudo containerlab deploy
```

Containerlab auto-discovers `*.clab.y*ml` in the current directory. On success, a summary table prints:

```
+---+---------------------+--------------+-----------------------+---------------+---------+-----------------+
| # |        Name         | Container ID |         Image         |     Kind      |  State  |  IPv4 Address   |
+---+---------------------+--------------+-----------------------+---------------+---------+-----------------+
| 1 | clab-srlceos01-ceos | 6ec1b1367a77 | ceos:4.32.0F          | arista_ceos   | running | 172.20.20.11/24 |
| 2 | clab-srlceos01-srl  | 6af1e33f4573 | ghcr.io/nokia/srlinux | nokia_srlinux | running | 172.20.20.10/24 |
+---+---------------------+--------------+-----------------------+---------------+---------+-----------------+
```

If you need to pick a specific topology file (or run from another directory):

```bash
sudo containerlab deploy --topo /home/ubuntu/containerlab/lab-examples/srlceos01/srlceos01.clab.yml
```

For debug output:

```bash
sudo containerlab deploy -d
```

---

## 5. Inspect the Running Lab

From any directory:

```bash
sudo containerlab inspect
```

Show all labs, wide format:

```bash
sudo containerlab inspect -a -w
```

Show details as JSON:

```bash
sudo containerlab inspect --details
```

Inspect interfaces on a node:

```bash
sudo containerlab inspect interfaces --topo srlceos01.clab.yml
```

---

## 6. Connect to Nodes

### Via SSH (if supported by the NOS)

```bash
ssh admin@clab-srlceos01-srl
```

### Via docker exec

```bash
# Nokia SR Linux CLI
sudo docker exec -it clab-srlceos01-srl sr_cli

# Arista cEOS CLI
sudo docker exec -it clab-srlceos01-ceos Cli

# Any node — bash shell
sudo docker exec -it clab-srlceos01-srl bash
```

### Via exec command

Run a command on all nodes of a given kind:

```bash
sudo containerlab exec --cmd "show version" --label clab-node-kind=nokia_srlinux
```

Output format can be `json` or `plain`:

```bash
sudo containerlab exec --cmd "show version" --format json
```

---

## 7. Save Configurations

```bash
sudo containerlab save --topo srlceos01.clab.yml
```

Configs are saved to `~/clab-<lab-name>/`. To copy saved configs to a specific directory:

```bash
sudo containerlab save --topo srlceos01.clab.yml --copy /path/to/backup
```

To save only specific nodes:

```bash
sudo containerlab save --topo srlceos01.clab.yml --node-filter srl
```

---

## 8. Generate a Topology Graph

Start an interactive graph web server:

```bash
sudo containerlab graph --topo srlceos01.clab.yml --srv :8080
```

Open `http://<host>:8080` in a browser.

Print a Mermaid flowchart to stdout:

```bash
sudo containerlab graph --topo srlceos01.clab.yml --mermaid
```

Generate a DOT file (for Graphviz):

```bash
sudo containerlab graph --topo srlceos01.clab.yml --dot
```

Graph offline (from topology file only, no running containers needed):

```bash
sudo containerlab graph --topo srlceos01.clab.yml --offline --mermaid
```

---

## 9. Deploy from a CLOS Template

Generate a fat-tree topology file:

```bash
cd /home/ubuntu/containerlab
sudo containerlab generate \
  --kind nokia_srlinux \
  --image ghcr.io/nokia/srlinux:24.10 \
  --nodes "leaf:4" \
  --nodes "spine:2" \
  --links leaf:spine:all \
  --file clos.clab.yml
```

Deploy the generated topology:

```bash
sudo containerlab deploy --topo clos.clab.yml
```

---

## 10. Apply Changes to a Running Lab

Edit your topology file to add/remove nodes or links, then preview changes:

```bash
sudo containerlab apply --topo srlceos01.clab.yml --dry-run
```

Apply the changes:

```bash
sudo containerlab apply --topo srlceos01.clab.yml
```

---

## 11. Stop / Start / Restart Nodes

Stop a specific node (keeps the lab structure):

```bash
sudo containerlab stop --topo srlceos01.clab.yml --node ceos
```

Start it again:

```bash
sudo containerlab start --topo srlceos01.clab.yml --node ceos
```

Restart all nodes:

```bash
sudo containerlab restart --topo srlceos01.clab.yml
```

---

## 12. Destroy the Lab

```bash
sudo containerlab destroy --topo srlceos01.clab.yml
```

Destroy and remove the lab directory:

```bash
sudo containerlab destroy --topo srlceos01.clab.yml --cleanup
```

Destroy ALL running labs (skips confirmation with `-y`):

```bash
sudo containerlab destroy --all --cleanup --yes
```

---

## 13. Redeploy (Destroy + Deploy in One Step)

```bash
sudo containerlab redeploy --topo srlceos01.clab.yml
```

With cleanup:

```bash
sudo containerlab redeploy --topo srlceos01.clab.yml --cleanup
```

---

## 14. Work with Remote Topology Files

Deploy directly from a GitHub URL:

```bash
sudo containerlab deploy --topo https://raw.githubusercontent.com/srl-labs/containerlab/main/lab-examples/srlceos01/srlceos01.clab.yml
```

Deploy from a GitHub short URL (`org/repo/path`):

```bash
sudo containerlab deploy --topo srl-labs/containerlab/lab-examples/srlceos01/srlceos01.clab.yml
```

Containerlab clones the repo, deploys the lab, and tags containers with the git branch and hash.

---

## 15. Use Template Variables

Create a variables file (`vars.yaml`):

```yaml
image_tag: 24.10
node_count: 4
```

Reference variables in your topology file:

```yaml
name: templated-lab
topology:
  nodes:
    {{- range $i := until (int .node_count) }}
    router{{ $i }}:
      kind: nokia_srlinux
      image: ghcr.io/nokia/srlinux:{{ .image_tag }}
    {{- end }}
```

Deploy with variables:

```bash
sudo containerlab deploy --topo templated.clab.yml --vars vars.yaml
```

---

## 16. Tools

### Certificate management

```bash
sudo containerlab tools cert generate --topo mylab.clab.yml
```

### SSH X-Forwarding (sshx)

```bash
sudo containerlab tools sshx --topo mylab.clab.yml
```

### Web terminal (GoTTY)

```bash
sudo containerlab tools gotty --topo mylab.clab.yml
```

### Network impairments (netem)

```bash
sudo containerlab tools netem add --topo mylab.clab.yml --node router1 --iface eth1 --delay 50ms
```

### Snapshot and restore

```bash
sudo containerlab tools snapshot --topo mylab.clab.yml
sudo containerlab deploy --topo mylab.clab.yml --restore-all
```

### API server

```bash
sudo containerlab tools api-server
```

---

## 17. Troubleshooting

### Enable debug logging

```bash
sudo containerlab deploy -dd
```

### View lab directory

```bash
ls ~/clab-<lab-name>/
```

Contains startup-configs, certs, and artifacts.

### Check container status

```bash
docker ps -a --filter label=containerlab
```

### View container logs

```bash
docker logs clab-<lab-name>-<node-name>
```

### Verify management bridge

```bash
docker network inspect clab
```

### Check links on host

```bash
ip link show | grep veth
```

### Test connectivity between nodes

```bash
sudo docker exec clab-srlceos01-srl ping 172.20.20.11
```

### Verify images are available

```bash
docker image ls | grep -E "srlinux|ceos"
```

### Cleanup all labs (nuclear option)

```bash
sudo containerlab destroy --all --cleanup --yes
```

---

## 18. Development Tasks

### Run unit tests

```bash
cd /home/ubuntu/containerlab
make test
```

Or run a specific package:

```bash
go test ./nodes/srl/...
```

### Run integration tests

```bash
CLAB_BIN=$(pwd)/bin/containerlab ./tests/rf-run.sh docker tests/02-basic-srl/
```

### Format code

```bash
make format
```

### Lint

```bash
make lint
```

### Serve documentation site locally

```bash
make serve-docs
```

Opens at `http://0.0.0.0:8001`.

---

## 19. Key Facts to Remember

| Fact | Detail |
|---|---|
| Binary location | `bin/containerlab` (setuid root) |
| Required privilege | Most commands need `sudo` |
| Topo file pattern | `*.clab.yml` or `*.clab.yaml` (auto-discovered) |
| Container naming | `clab-<lab-name>-<node-name>` |
| Management network | Docker bridge `clab`, subnet `172.20.20.0/24` |
| Dataplane MTU | Default `9500` |
| Config inheritance | `defaults` → `kinds` → `groups` → `nodes` |
| MAC OUI | `aa:c1:ab` for generated MACs |
| Lab directory | `~/clab-<lab-name>/` |
| JSON schema | `schemas/clab.schema.json` |
