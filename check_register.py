import requests

res = requests.post(
    "http://127.0.0.1:8000/register",
    json={"username": "newuser", "password": "secret"}
)
print(res.status_code, res.json())
