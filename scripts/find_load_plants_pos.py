import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'async function loadPlants()' in line:
        print(f"loadPlants at line {i+1}")
        for j in range(i, min(len(lines), i + 35)):
            print(f"{j+1}: {lines[j]}", end="")
        break
