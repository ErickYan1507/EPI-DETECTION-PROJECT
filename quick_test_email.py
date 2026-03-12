import requests
from pathlib import Path

BASE_URL = 'http://127.0.0.1:5000'

print('='*60)
print('TEST CONFIGURATION EMAIL')
print('='*60)

# 1. Get status
print('\n1. GET /api/email/status')
try:
    r = requests.get(f'{BASE_URL}/api/email/status', timeout=5)
    data = r.json()
    print(f'   Success: {data.get("success")}')
    print(f'   SMTP Configured: {data.get("smtp_configured")}')
    print(f'   SMTP Connected: {data.get("smtp_connected")}')
    print(f'   Recipients: {data.get("recipients_count")}')
    print(f'   Scheduler Running: {data.get("scheduler_running")}')
except Exception as e:
    print(f'   ERROR: {e}')

# 2. Get recipients
print('\n2. GET /api/email/recipients')
try:
    r = requests.get(f'{BASE_URL}/api/email/recipients', timeout=5)
    recipients = r.json().get('recipients', [])
    print(f'   Count: {len(recipients)}')
    for email in recipients:
        print(f'      - {email}')
except Exception as e:
    print(f'   ERROR: {e}')

# 3. Send test email
print('\n3. POST /api/email/send-test')
try:
    r = requests.post(f'{BASE_URL}/api/email/send-test', 
        json={'recipient': 'ainaerickandrianavalona@gmail.com'},
        timeout=15)
    data = r.json()
    print(f'   Success: {data.get("success")}')
    if data.get("success"):
        print(f'   Message: {data.get("message")}')
    else:
        print(f'   Error: {data.get("error")}')
except Exception as e:
    print(f'   ERROR: {e}')

# 4. Send daily report
print('\n4. POST /api/email/send-report (daily)')
try:
    r = requests.post(f'{BASE_URL}/api/email/send-report',
        json={'type': 'daily'},
        timeout=15)
    data = r.json()
    print(f'   Success: {data.get("success")}')
    if data.get("success"):
        print(f'   Message: {data.get("message")}')
    else:
        print(f'   Error: {data.get("error")}')
except Exception as e:
    print(f'   ERROR: {e}')

print('\n' + '='*60)
print('TEST COMPLETE!')
