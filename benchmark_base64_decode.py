import base64

s = "A" * 1000000

import time

t0 = time.time()
for _ in range(100):
    decoded_data = base64.urlsafe_b64decode(s.encode('ASCII'))
print("Encode:", time.time() - t0)

t0 = time.time()
for _ in range(100):
    decoded_data = base64.urlsafe_b64decode(s)
print("No encode:", time.time() - t0)
