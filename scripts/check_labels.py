from pathlib import Path
from collections import Counter
p=Path('dataset/labels')
counts=Counter()
for f in p.rglob('*.txt'):
    for line in f.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        parts=line.strip().split()
        try:
            cls=int(float(parts[0]))
        except:
            continue
        counts[cls]+=1
print('classes found:',sorted(counts.keys()))
print('counts:')
for k,v in sorted(counts.items()):
    print(k, v)
