#!/usr/bin/env python3
"""Railway migration via API."""
import json, urllib.request, urllib.error

TOKEN = "17e5bd52-8be8-49bb-8305-13ccebc5e600"
GQL = "https://backboard.railway.app/graphql/v2"

def gql(query):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(GQL, data=data, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "body": e.read().decode()}

# 1. Check type info
print("=== Checking execution input type ===")
r = gql('{ __type(name: "DeploymentInstanceExecutionCreateInput") { inputFields { name type { name kind ofType { name } } } } }')
print(json.dumps(r, indent=2)[:1000])

# 2. Try redeploy
print("\n=== Triggering redeploy ===")
r2 = gql('mutation { serviceInstanceRedeploy(environmentId: "e73198d6-2655-44d8-8d46-1f72ed949143", serviceId: "084a5193-c6d6-4188-b037-c2f0bc890ee1") }')
print(json.dumps(r2, indent=2))

# 3. Try to get current service instance settings
print("\n=== Inspecting environment services ===")
r3 = gql('{ project(id: "7737571a-f0e8-48a2-9e8d-d20436500d72") { environments { edges { node { id name services { edges { node { id name serviceInstances { edges { node { id startCommand preDeployCommand } } } } } } } } } } }')
if "data" in r3 and r3["data"]:
    for env_edge in r3["data"]["project"]["environments"]["edges"]:
        env = env_edge["node"]
        print(f"Env: {env['name']} ({env['id']})")
        for svc_edge in env["services"]["edges"]:
            s = svc_edge["node"]
            print(f"  Service: {s['name']} ({s['id']})")
            for inst_edge in s["serviceInstances"]["edges"]:
                i = inst_edge["node"]
                start_cmd = (i.get("startCommand") or "N/A")[:100]
                pre_cmd = i.get("preDeployCommand") or "not set"
                print(f"    Instance: {i['id']}")
                print(f"    startCommand: {start_cmd}")
                print(f"    preDeployCommand: {pre_cmd}")
else:
    print(json.dumps(r3, indent=2)[:500])

# 4. Get service instance details directly
print("\n=== Service instance for api ===")
r4 = gql('{ project(id: "7737571a-f0e8-48a2-9e8d-d20436500d72") { services { edges { node { id name serviceInstances { edges { node { id startCommand preDeployCommand } } } } } } } }')
if "data" in r4 and r4.get("data"):
    for svc_edge in r4["data"]["project"]["services"]["edges"]:
        s = svc_edge["node"]
        print(f"Service: {s['name']} ({s['id']})")
        for inst_edge in s["serviceInstances"]["edges"]:
            i = inst_edge["node"]
            print(f"  startCommand: {(i.get('startCommand') or 'N/A')[:100]}")
            print(f"  preDeployCommand: {i.get('preDeployCommand') or 'not set'}")
else:
    print(json.dumps(r4, indent=2)[:500])
