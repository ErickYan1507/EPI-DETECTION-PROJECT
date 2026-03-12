import requests
import json
import os

BASE='http://127.0.0.1:5000'
email='ainaerickandrianavalona@gmail.com'

print('POST /api/email/senders ->', email)
try:
    r=requests.post(f'{BASE}/api/email/senders', json={'email': email}, timeout=5)
    print('Status', r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print('POST ERR', e)

print('\nGET /api/email/senders')
try:
    r=requests.get(f'{BASE}/api/email/senders', timeout=5)
    print('Status', r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print('GET ERR', e)

# Read .sender_history file
sh_path = os.path.join(os.path.dirname(__file__), '..', '.sender_history')
sh_path = os.path.abspath(sh_path)
print(f'\nReading file: {sh_path}')
try:
    with open(sh_path, 'r', encoding='utf-8') as f:
        print('--- .sender_history contents ---')
        print(f.read())
except Exception as e:
    print('File read error', e)
