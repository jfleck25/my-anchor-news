import time
import random
import string

text = "".join(random.choices(string.ascii_letters, k=100000))
subject = "Daily Newsletter from NYT"
keywords = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon", "xyz"]
sender = "NYT Newsletter"
priority_sources = ["WSJ", "NYT", "Washington Post", "The Guardian", "xyz"]

start = time.time()
for _ in range(100):
    if keywords:
        has_keyword = any(k.lower() in text.lower() or k.lower() in subject.lower() for k in keywords)
    is_priority = any(p.lower() in sender.lower() for p in priority_sources)
end = time.time()
print(f"Unoptimized: {end - start:.4f} seconds")

start = time.time()
keywords_lower = [k.lower() for k in keywords]
priority_sources_lower = [p.lower() for p in priority_sources]
for _ in range(100):
    if keywords_lower:
        text_lower = text.lower()
        subject_lower = subject.lower()
        has_keyword = any(k in text_lower or k in subject_lower for k in keywords_lower)
    sender_lower = sender.lower()
    is_priority = any(p in sender_lower for p in priority_sources_lower)
end = time.time()
print(f"Optimized: {end - start:.4f} seconds")
