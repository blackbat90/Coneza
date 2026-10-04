import pypdf
import json

reader = pypdf.PdfReader("VDE_AR_N_4110_2023.pdf")

# Extract Table of Contents text from pages 2 through 10
toc_text = ""
for p in range(1, 11):
    toc_text += f"\n--- TOC PAGE {p+1} ---\n" + (reader.pages[p].extract_text() or "")

with open("vde_toc.txt", "w", encoding="utf-8") as f:
    f.write(toc_text)

print("TOC saved to vde_toc.txt, length:", len(toc_text))
