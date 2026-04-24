import re
import time

html_content = "<html><head><style>body { color: red; }</style></head><body><p>Hello world!</p>" * 100 + "</body></html>"

t0 = time.time()
for _ in range(1000):
    no_scripts = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    text_only = re.sub(r'<[^>]+>', ' ', no_scripts)
    clean_text = ' '.join(text_only.split())
print("Uncompiled:", time.time() - t0)


SCRIPT_STYLE_RE = re.compile(r'<(script|style).*?>.*?</\1>', flags=re.IGNORECASE | re.DOTALL)
HTML_TAGS_RE = re.compile(r'<[^>]+>')
CONTROL_CHARS_RE = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')

t0 = time.time()
for _ in range(1000):
    no_scripts = SCRIPT_STYLE_RE.sub('', html_content)
    text_only = HTML_TAGS_RE.sub(' ', no_scripts)
    clean_text = ' '.join(text_only.split())
print("Compiled:", time.time() - t0)
