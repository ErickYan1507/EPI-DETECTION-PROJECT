import requests

BASE_URL = 'http://127.0.0.1:5000'

print('='*60)
print('TESTING EMAIL SENDING VIA API')
print('='*60)

# Test 1: Check if server is running
print('\n1. GET / (check if server is alive)')
try:
    r = requests.get(f'{BASE_URL}/', timeout=3)
    print(f'   Status: {r.status_code}')
    if r.status_code == 200:
        print('   ✅ Server is running!')
    else:
        print(f'   Status: {r.status_code}')
except Exception as e:
    print(f'   ❌ ERROR: Server not responding')
    print(f'      Please start: .venv/Scripts/python.exe run.py --mode run')
    exit(1)

# Test 2: Check email status
print('\n2. GET /api/email/status')
try:
    r = requests.get(f'{BASE_URL}/api/email/status', timeout=3)
    if r.status_code == 200:
        data = r.json()
        smtp_ok = data.get('smtp_configured')
        smtp_conn = data.get('smtp_connected')
        recip_count = data.get('recipients_count')
        print(f'   SMTP Configured: {smtp_ok}')
        print(f'   SMTP Connected: {smtp_conn}')
        print(f'   Recipients: {recip_count}')
        if not smtp_ok or not smtp_conn:
            print(f'   ⚠️ Email not fully configured!')
    else:
        print(f'   Status: {r.status_code}')
except Exception as e:
    print(f'   Error: {str(e)[:50]}')

# Test 3: Send test email
print('\n3. POST /api/email/send-test')
try:
    r = requests.post(f'{BASE_URL}/api/email/send-test',
        json={'recipient': 'ainaerickandrianavalona@gmail.com'},
        timeout=10)
    data = r.json()
    print(f'   Status: {r.status_code}')
    success = data.get('success')
    print(f'   Success: {success}')
    if success:
        print(f'   ✅ {data.get("message")}')
    else:
        print(f'   ❌ Error: {data.get("error")}')
except Exception as e:
    print(f'   Error: {str(e)[:50]}')

# Test 4: Send daily report
print('\n4. POST /api/email/send-report (daily)')
try:
    r = requests.post(f'{BASE_URL}/api/email/send-report',
        json={'type': 'daily'},
        timeout=10)
    data = r.json()
    print(f'   Status: {r.status_code}')
    success = data.get('success')
    print(f'   Success: {success}')
    if success:
        print(f'   ✅ {data.get("message")}')
    else:
        print(f'   ❌ Error: {data.get("error")}')
except Exception as e:
    print(f'   Error: {str(e)[:50]}')

print('\n' + '='*60)
print('DIAGNOSTIC COMPLETE')
print('='*60)
