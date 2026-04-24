import time
s = "this is a test string to match"
l = [str(i) for i in range(100)] + ["test"]

t0 = time.time()
for _ in range(100000):
    any(x in s for x in l)
print(time.time() - t0)
