import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '<select' in line:
        for j in range(max(0, i - 1), min(len(lines), i + 6)):
            print(f"{j+1}: {lines[j]}", end="")
