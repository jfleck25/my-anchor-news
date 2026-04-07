with open("main.py", "r") as f:
    content = f.read()
old_code = """def _fetch_one_message(args):
    \"\"\"Fetch a single Gmail message. Used by parallel workers. Returns (index, email_block, is_priority) or (index, None, None) on skip/error.\"\"\"
    index, message_id, creds_dict, keywords, priority_sources = args
    try:
        creds = Credentials(**creds_dict)
        service = build('gmail', 'v1', credentials=creds)
        msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()"""
new_code = """def _fetch_one_message(args):
    \"\"\"Fetch a single Gmail message. Used by parallel workers. Returns (index, email_block, is_priority) or (index, None, None) on skip/error.\"\"\"
    index, message_id, creds_dict, keywords, priority_sources = args
    try:
        if not hasattr(_worker_thread_locals, 'gmail_service'):
            creds = Credentials(**creds_dict)
            _worker_thread_locals.gmail_service = build('gmail', 'v1', credentials=creds)
        service = _worker_thread_locals.gmail_service
        msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()"""
if old_code in content:
    content = content.replace(old_code, new_code)
    with open("main.py", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Code not found")
