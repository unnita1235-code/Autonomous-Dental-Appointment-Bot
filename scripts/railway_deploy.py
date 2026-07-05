#!/usr/bin/env python3
"""Set preDeployCommand and trigger a redeploy on Railway."""
import json
import urllib.request
import urllib.error

TOKEN = "17e5bd52-8be8-49bb-8305-13ccebc5e600"
GQL = "https://backboard.railway.app/graphql/v2"
SERVICE_ID = "084a5193-c6d6-4188-b037-c2f0bc890ee1"
ENV_ID = "e73198d6-2655-44d8-8d46-1f72ed949143"
PROJECT = "7737571a-f0e8-48a2-9e8d-d20436500d72"

def gql(query, variables=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    data = json.dumps(payload).encode()
    req = urllib.request.Request(GQL, data=data, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        if "errors" in result:
            print(f"GQL Error: {result['errors']}")
            return None
        return result.get("data")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}")
        return None

# Check the ServiceInstanceUpdateInput type
print("=== Checking ServiceInstanceUpdateInput fields ===")
q = '{ __type(name: "ServiceInstanceUpdateInput") { inputFields { name type { name kind ofType { name } } } } }'
result = gql(q)
if result:
    for field in result["__type"]["inputFields"]:
        print(f"  {field['name']}: {field['type'].get('name') or field['type'].get('ofType', {}).get('name')}")

# Set preDeployCommand
print("\n=== Setting preDeployCommand ===")
q = """
mutation {
    serviceInstanceUpdate(
        input: {
            serviceId: "084a5193-c6d6-4188-b037-c2f0bc890ee1"
            environmentId: "e73198d6-2655-44d8-8d46-1f72ed949143"
            preDeployCommand: "alembic upgrade head"
        }
    )
}
"""
result = gql(q)
if result:
    print(f"  Result: {result}")
else:
    print("  Failed with no preDeployCommand field")
    # Try without it - check what works
    q2 = """
    mutation {
        serviceInstanceUpdate(
            input: {
                serviceId: "084a5193-c6d6-4188-b037-c2f0bc890ee1"
                environmentId: "e73198d6-2655-44d8-8d46-1f72ed949143"
            }
        )
    }
    """
    result2 = gql(q2)
    print(f"  Minimal mutation: {result2}")

# Trigger redeploy
print("\n=== Triggering redeploy ===")
q3 = """
mutation {
    serviceInstanceRedeploy(
        environmentId: "e73198d6-2655-44d8-8d46-1f72ed949143"
        serviceId: "084a5193-c6d6-4188-b037-c2f0bc890ee1"
    )
}
"""
result3 = gql(q3)
print(f"  Redeploy: {result3}")
