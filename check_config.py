from config import config

print('='*60)
print('CONFIGURATION CHARGEE DANS L APP')
print('='*60)

print(f'\nSENDER_EMAIL: {config.SENDER_EMAIL}')
print(f'SENDER_PASSWORD: {"***" if config.SENDER_PASSWORD else "VIDE"}')
print(f'SMTP_SERVER: {config.SMTP_SERVER}')
print(f'SMTP_PORT: {config.SMTP_PORT}')

if config.SENDER_EMAIL and config.SENDER_PASSWORD:
    print('\n✅ Configuration complète')
else:
    print('\n❌ Configuration INCOMPLETE')
    if not config.SENDER_EMAIL:
        print('   - SENDER_EMAIL est vide')
    if not config.SENDER_PASSWORD:
        print('   - SENDER_PASSWORD est vide')
