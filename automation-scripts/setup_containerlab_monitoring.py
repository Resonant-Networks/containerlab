import urllib.request, json, sys

URL = "http://localhost:8083/api_jsonrpc.php"

def api(method, params, auth=None):
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    if auth: payload["auth"] = auth
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json-rpc"})
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    if "error" in res:
        print(f"API Error in {method}:", json.dumps(res["error"], indent=2))
        sys.exit(1)
    return res["result"]

auth = api("user.login", {"username": "Admin", "password": "zabbix"})
print("Auth token:", auth)

# 1. Host Group
groups = api("hostgroup.get", {"filter": {"name": "Containerlab Network Fabric"}}, auth=auth)
if groups:
    group_id = groups[0]["groupid"]
    print("Existing Host Group ID:", group_id)
else:
    res = api("hostgroup.create", {"name": "Containerlab Network Fabric"}, auth=auth)
    group_id = res["groupids"][0]
    print("Created Host Group ID:", group_id)

# 2. Template ICMP Ping
template_id = "10564"

nodes = [
    {"host": "clab-demo-clos-spine1", "name": "Spine 01 (clab-spine1)", "ip": "172.30.20.10"},
    {"host": "clab-demo-clos-leaf1", "name": "Leaf 01 (clab-leaf1)", "ip": "172.30.20.11"},
    {"host": "clab-demo-clos-leaf2", "name": "Leaf 02 (clab-leaf2)", "ip": "172.30.20.12"},
    {"host": "clab-demo-clos-client1", "name": "Client 01 (clab-client1)", "ip": "172.30.20.21"},
    {"host": "clab-demo-clos-client2", "name": "Client 02 (clab-client2)", "ip": "172.30.20.22"},
]

for node in nodes:
    existing = api("host.get", {"filter": {"host": node["host"]}}, auth=auth)
    if existing:
        print(f"Host {node['host']} already exists. ID: {existing[0]['hostid']}")
    else:
        hname = node["name"]
        res = api("host.create", {
            "host": node["host"],
            "name": hname,
            "interfaces": [{
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": node["ip"],
                "dns": "",
                "port": "10050"
            }],
            "groups": [{"groupid": group_id}],
            "templates": [{"templateid": template_id}]
        }, auth=auth)
        hid = res["hostids"][0]
        print(f"Created host {hname} (ID: {hid})")
