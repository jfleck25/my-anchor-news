import base64
import time

s = "A" * 1000000

t0 = time.time()
for _ in range(1000):
    base64.urlsafe_b64decode(s.encode('ascii'))
print("With encode:", time.time() - t0)

t0 = time.time()
for _ in range(1000):
    base64.urlsafe_b64decode(s)
print("Without encode:", time.time() - t0)
