import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ['scrollIntoView', 'onEnergyFlowPlantChange', 'selectPlantForEnergyFlow', 'flowPlantSelect']):
        print(f"{i+1}: {line.strip()[:100]}")
