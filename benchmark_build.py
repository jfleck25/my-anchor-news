import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials(token='fake_token')
start = time.time()
build('gmail', 'v1', credentials=creds)
end = time.time()
print(f"Time to build: {end - start:.4f} seconds")
