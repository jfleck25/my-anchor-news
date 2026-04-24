import time

body_data = "hello world" * 1000

t0 = time.time()
for _ in range(100000):
    b = body_data.encode('ASCII')
print("Encode:", time.time() - t0)

t0 = time.time()
for _ in range(100000):
    b = body_data
print("No encode:", time.time() - t0)
