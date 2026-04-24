import base64
import time

body_data = "aGVsbG8gd29ybGQ=" * 1000

t0 = time.time()
for _ in range(100000):
    b = base64.urlsafe_b64decode(body_data)
print("No encode:", time.time() - t0)

t0 = time.time()
for _ in range(100000):
    b = base64.urlsafe_b64decode(body_data.encode('ASCII'))
print("Encode:", time.time() - t0)
