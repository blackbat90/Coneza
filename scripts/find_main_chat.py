import sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'@app\.(post|get)\([^)]*chat[^)]*\)', text):
    print(m.group(0))

for line in text.splitlines():
    if 'def ' in line and 'chat' in line.lower():
        print("Function:", line.strip())
