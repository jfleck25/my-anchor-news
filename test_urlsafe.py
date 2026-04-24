import base64
s = "QUJD" # "ABC" in base64
print(base64.urlsafe_b64decode(s))
print(base64.urlsafe_b64decode(s.encode('ASCII')))
