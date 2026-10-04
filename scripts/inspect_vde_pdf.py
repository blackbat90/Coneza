import pypdf
import json

reader = pypdf.PdfReader("VDE_AR_N_4110_2023.pdf")
print("Total pages:", len(reader.pages))

# Metadata
info = reader.metadata
print("Metadata:", {k: str(v) for k, v in info.items()} if info else "None")

# Extract outline / bookmarks if any
try:
    outline = reader.outline
    print("\nOutline found:")
    def print_outline(items, level=0):
        for item in items:
            if isinstance(item, list):
                print_outline(item, level + 1)
            else:
                title = getattr(item, 'title', str(item))
                page_num = reader.get_destination_page_number(item) if hasattr(reader, 'get_destination_page_number') else '?'
                print("  " * level + f"- {title} (Page {page_num})")
    print_outline(outline[:30])
except Exception as e:
    print("Could not extract outline:", e)

# Let's extract first 5 pages text (Title, Vorwort, Inhaltsverzeichnis)
print("\n=== FIRST 5 PAGES EXTRACT ===")
for i in range(min(5, len(reader.pages))):
    text = reader.pages[i].extract_text() or ""
    print(f"--- PAGE {i+1} ---")
    print(text[:800])
