import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'id="plantQuestionnaireModal"' in line:
        start_idx = i
    if 'id="sldFullscreenModal"' in line:
        end_idx = i

print(f"Modal lines: {start_idx + 1} to {end_idx + 1}")
print("--- FIRST 15 LINES ---")
for i in range(start_idx, start_idx + 15):
    print(lines[i], end="")

print("--- LAST 15 LINES ---")
for i in range(end_idx - 15, end_idx):
    print(lines[i], end="")
