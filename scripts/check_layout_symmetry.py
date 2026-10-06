import re

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

print("--- Margin / Padding left & right ---")
for m in re.finditer(r'(?:style=["\'][^"\']*|[{;]\s*)(padding-(?:left|right)|margin-(?:left|right))\s*:\s*([^;"]+)', text):
    print(f"{m.group(1)}: {m.group(2).strip()}")

print("\n--- Any 4-value padding/margin ---")
for m in re.finditer(r'(?:padding|margin)\s*:\s*([^;"]+)', text):
    parts = m.group(1).strip().split()
    if len(parts) == 4 and parts[1] != parts[3]:
        print(f"ASYMMETRIC: {m.group(0)}")
