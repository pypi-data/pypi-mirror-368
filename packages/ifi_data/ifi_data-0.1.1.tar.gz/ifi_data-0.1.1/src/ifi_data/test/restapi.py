import datetime as dt

import dotenv
import httpx

cfg = dotenv.dotenv_values(".env")
rest_api_host = cfg["HOST"]
rest_api_port = cfg["REST_API_PORT"]

# health
resp = httpx.get(f"http://{rest_api_host}:{rest_api_port}/health")
assert resp.status_code == 200

resp = resp.json()
assert resp["status"] == "healthy"
assert resp["database"] == "connected"

# insert
row = {
    "reading": 456,
    "datetime": str(dt.datetime.now()),
}
resp = httpx.post(f"http://{rest_api_host}:{rest_api_port}/insert/restapi_test", json={"data": row})
resp = resp.json()
assert resp["status"] == "success"
