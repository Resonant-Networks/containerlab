import urllib.request
import json
import sys

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

# Get Host Group ID for "Containerlab Network Fabric"
groups = api("hostgroup.get", {"filter": {"name": "Containerlab Network Fabric"}}, auth=auth)
group_id = groups[0]["groupid"] if groups else "23"

dashboard_params = {
    "name": "Containerlab EVPN Fabric Dashboard",
    "display_period": 30,
    "auto_start": 1,
    "pages": [
        {
            "name": "EVPN Fabric Health & Telemetry",
            "widgets": [
                {
                    "type": "clock",
                    "name": "NOC Local Time",
                    "x": 0, "y": 0, "width": 6, "height": 3,
                    "fields": [
                        {"type": 0, "name": "time_type", "value": 0}
                    ]
                },
                {
                    "type": "hostavail",
                    "name": "Containerlab Nodes Availability",
                    "x": 6, "y": 0, "width": 12, "height": 3,
                    "fields": [
                        {"type": 2, "name": "groupids", "value": group_id},
                        {"type": 0, "name": "layout", "value": 0}
                    ]
                },
                {
                    "type": "problems",
                    "name": "Active Fabric Incidents",
                    "x": 18, "y": 0, "width": 6, "height": 6,
                    "fields": [
                        {"type": 2, "name": "groupids", "value": group_id},
                        {"type": 0, "name": "show_suppressed", "value": 0}
                    ]
                },
                {
                    "type": "svggraph",
                    "name": "Fabric Latency & ICMP Response Time",
                    "x": 0, "y": 3, "width": 18, "height": 7,
                    "fields": [
                        {"type": 2, "name": "groupids", "value": group_id},
                        {"type": 1, "name": "ds.0.hosts.0", "value": "*"},
                        {"type": 1, "name": "ds.0.items.0", "value": "ICMP ping response time"}
                    ]
                }
            ]
        }
    ]
}

existing = api("dashboard.get", {"filter": {"name": "Containerlab EVPN Fabric Dashboard"}}, auth=auth)
if existing:
    d_id = existing[0]["dashboardid"]
    dashboard_params["dashboardid"] = d_id
    api("dashboard.update", dashboard_params, auth=auth)
    print(f"Updated existing dashboard ID: {d_id}")
else:
    res = api("dashboard.create", dashboard_params, auth=auth)
    d_id = res["dashboardids"][0]
    print(f"Created new dashboard ID: {d_id}")

