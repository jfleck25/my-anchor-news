import json
import time

d = {"a": "1", "b": 2, "c": [1, 2, 3]}

t0 = time.time()
for _ in range(100000):
    json.dumps(d, sort_keys=True)
print("sort keys:", time.time() - t0)

t0 = time.time()
for _ in range(100000):
    json.dumps(d)
print("no sort keys:", time.time() - t0)
