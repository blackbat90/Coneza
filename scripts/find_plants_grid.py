import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.splitlines():
    if 'plantsGrid' in line or 'cachedPlants' in line:
        print(line)
