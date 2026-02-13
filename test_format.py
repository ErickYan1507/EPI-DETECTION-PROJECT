x = None
try:
    print(f'{x or 0:.1f}')
except Exception as e:
    print(e)

y = None
try:
    print(f'{y:.2f}')
except Exception as e:
    print(e)
