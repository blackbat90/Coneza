import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'execute_document_chat' in line or 'chat_with_document' in line:
        print(f"Line {i+1}: {line.strip()[:100]}")
        for j in range(max(0, i - 5), min(len(lines), i + 45)):
            print(f"{j+1}: {lines[j]}", end="")
        break
