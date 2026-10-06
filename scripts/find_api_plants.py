import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '/api/plants' in line and '@app.get' in line:
        for j in range(i, min(len(lines), i + 35)):
            print(f"{j+1}: {lines[j]}", end="")
        break
