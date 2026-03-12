import requests
from pathlib import Path

BASE_URL = 'http://127.0.0.1:5000'

print('='*60)
print('TEST PAGE NOTIFICATIONS')
print('='*60)

# Test 1: Accès à la page
print('\n1. GET /notifications')
try:
    r = requests.get(f'{BASE_URL}/notifications', timeout=5)
    print(f'   Status: {r.status_code}')
    if r.status_code == 200:
        content = r.text[:500]
        print(f'   ✅ Page chargée ({len(r.text)} bytes)')
        if 'notifications' in r.text.lower() or 'email' in r.text.lower():
            print('   ✅ Content looks correct')
        else:
            print('   ⚠️ Content may be wrong')
    else:
        print(f'   ❌ Error: {r.status_code}')
        print(f'   Response: {r.text[:200]}')
except Exception as e:
    print(f'   ❌ ERROR: {e}')

# Test 2: API endpoints
endpoints = [
    '/api/email/config',
    '/api/email/recipients',
    '/api/email/status'
]

print('\n2. API Endpoints:')
for ep in endpoints:
    try:
        r = requests.get(f'{BASE_URL}{ep}', timeout=3)
        status = '✅' if r.status_code == 200 else '❌'
        print(f'   {status} {ep}: {r.status_code}')
    except Exception as e:
        print(f'   ❌ {ep}: {str(e)[:30]}')

print('\n' + '='*60)
print('TEST COMPLETE!')
print('='*60)
