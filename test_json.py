import json

with open("data/taipei-attractions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data["result"]["results"][0])