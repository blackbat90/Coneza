import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 2255 <= i <= 2310:
        print(f"{i+1}: {l.strip()[:100]}")
    elif 2353 <= i <= 2360:
        print(f"{i+1}: {l.strip()[:100]}")
    elif 2392 <= i <= 2400:
        print(f"{i+1}: {l.strip()[:100]}")
    elif 2432 <= i <= 2440:
        print(f"{i+1}: {l.strip()[:100]}")
    elif 2468 <= i <= 2478:
        print(f"{i+1}: {l.strip()[:100]}")
    elif 2555 <= i <= 2568:
        print(f"{i+1}: {l.strip()[:100]}")
