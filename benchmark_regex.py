import re
import time

html = "<html><head><style>body { color: red; }</style></head><body><p>Hello world!</p>" * 100 + "</body></html>"

def run_uncompiled(n):
    for _ in range(n):
        s = re.sub(r'<(script|style).*?>.*?</\1>', '', html, flags=re.IGNORECASE | re.DOTALL)
        t = re.sub(r'<[^>]+>', ' ', s)

SCRIPT_STYLE_RE = re.compile(r'<(script|style).*?>.*?</\1>', flags=re.IGNORECASE | re.DOTALL)
HTML_TAGS_RE = re.compile(r'<[^>]+>')

def run_compiled(n):
    for _ in range(n):
        s = SCRIPT_STYLE_RE.sub('', html)
        t = HTML_TAGS_RE.sub(' ', s)

t0 = time.time()
run_uncompiled(1000)
print("Uncompiled:", time.time() - t0)

t0 = time.time()
run_compiled(1000)
print("Compiled:", time.time() - t0)
