import time
import random
import string

text = "".join(random.choices(string.ascii_letters, k=50000))
subject = "Daily Newsletter"
keywords = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon", "xyz"]

start = time.time()
for _ in range(1000):
    has_keyword = any(k.lower() in text.lower() or k.lower() in subject.lower() for k in keywords)
end = time.time()
print(f"Unoptimized: {end - start:.4f} seconds")

start = time.time()
for _ in range(1000):
    text_lower = text.lower()
    subject_lower = subject.lower()
    has_keyword = any(k.lower() in text_lower or k.lower() in subject_lower for k in keywords)
end = time.time()
print(f"Optimized: {end - start:.4f} seconds")
