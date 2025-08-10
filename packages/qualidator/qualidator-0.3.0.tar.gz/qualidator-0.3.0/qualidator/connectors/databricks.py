import requests
import os
import json
import time


class DatabricksConnector:

    def __init__(self, host, warehouse_id, token, poll_interval=1, timeout=60):
        self.host = host.rstrip("/")
        self.warehouse_id = warehouse_id
        self.token = token
        self.base_url = f"https://{self.host}/api/2.0/sql"
        self.poll_interval = poll_interval
        self.timeout = timeout


    def __repr__(self):
        return f"DatabricksConnector(host={self.base_url}, warehouse_id={self.warehouse_id})"
    

    def execute_query(self, query):
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "statement": query,
            "warehouse_id": self.warehouse_id
        }

        resp = requests.post(f"{self.base_url}/statements", headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to submit query: {resp.status_code} {resp.text}")

        resp_json = resp.json()
        statement_id = resp_json.get("statement_id")
        if not statement_id:
            raise RuntimeError(f"No statement_id in response: {resp_json}")

        start_time = time.time()
        while True:
            poll_resp = requests.get(f"{self.base_url}/statements/{statement_id}", headers=headers)
            if poll_resp.status_code != 200:
                raise RuntimeError(f"Failed to poll query: {poll_resp.status_code} {poll_resp.text}")

            poll_json = poll_resp.json()
            state = poll_json["status"]["state"]

            if state == "SUCCEEDED":
                return poll_json.get("result", {}).get("data_array", [])
            elif state == "FAILED":
                raise RuntimeError(f"Query failed: {poll_json}")
            
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"Query timed out after {self.timeout} seconds")
            
            time.sleep(self.poll_interval)
