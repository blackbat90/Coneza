import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
for m in re.finditer(r'openQuickConfigModal', text):
    start = max(0, m.start() - 60)
    end = min(len(text), m.end() + 60)
    print(text[start:end].replace('\n', ' '))
