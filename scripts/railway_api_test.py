#!/usr/bin/env python3
"""
Fully automated Railway setup:
1. Set environment variables via Railway API
2. Trigger alembic migration
3. Verify everything works
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

TOKEN = "afdae3a0-1724-4cc1-a4b5-3b764336ddb4"
PROJECT = "7737571a-f0e8-48a2-9e8d-d20436500d72"
ENV_ID = "e73198d6-2655-44d8-8d46-1f72ed949143"
SERVICE_API = "084a5193-c6d6-4188-b037-c2f0bc890ee1"

graphql_endpoint = "https://backboard.railway.app/graphql/v2"

def gql(query, variables=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    data = json.dumps(payload).encode()
    req = urllib.request.Request(graphql_endpoint, data=data, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        if "errors" in result:
            print(f"  GQL Error: {result['errors']}", file=sys.stderr)
            return None
        return result.get("data")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error: {e.code} - {e.read().decode()}", file=sys.stderr)
        return None

# Step 1: Check variableUpsert mutation
print("=== Checking variableUpsert mutation ===")
q = """
mutation upsertVar($projectId: String!, $environmentId: String!, $name: String!, $value: String!) {
    variableUpsert(
        projectId: $projectId
        environmentId: $environmentId
        name: $name
        value: $value
    )
}
"""
result = gql(q, {
    "projectId": PROJECT,
    "environmentId": ENV_ID,
    "name": "TEST_VAR",
    "value": "test_value_123",
})
print(f"  Result: {json.dumps(result, indent=2)}")

if result and result.get("variableUpsert"):
    print("  variableUpsert WORKS!")
else:
    print("  variableUpsert failed. Trying variableCollectionUpsert...")
    q2 = """
    mutation upsertVars($projectId: String!, $environmentId: String!, $variables: [VariableUpsertInput!]!) {
        variableCollectionUpsert(
            projectId: $projectId
            environmentId: $environmentId
            variables: $variables
        )
    }
    """
    vars_def = """
    mutation upsertVars($projectId: String!, $environmentId: String!, $name: String!, $value: String!) {
        variableCollectionUpsert(
            projectId: $projectId
            environmentId: $environmentId
            variables: [{name: $name, value: $value}]
        )
    }
    """
    result2 = gql(vars_def, {
        "projectId": PROJECT,
        "environmentId": ENV_ID,
        "name": "TEST_VAR",
        "value": "test_value_123",
    })
    print(f"  Result: {json.dumps(result2, indent=2)}")

print("\n=== Cleanup test var ===")
cleanup = """
mutation delVar($projectId: String!, $environmentId: String!, $name: String!) {
    variableDelete(
        projectId: $projectId
        environmentId: $environmentId
        name: $name
    )
}
"""
gql(cleanup, {
    "projectId": PROJECT,
    "environmentId": ENV_ID,
    "name": "TEST_VAR",
})
print("  Cleanup done")
