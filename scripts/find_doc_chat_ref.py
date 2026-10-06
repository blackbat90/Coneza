import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.splitlines():
    if 'DocumentChat' in line:
        print(line)
