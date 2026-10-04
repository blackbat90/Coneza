import pypdf

reader = pypdf.PdfReader("VDE_AR_N_4110_2023.pdf")

def search_text_in_pages(start_page, end_page):
    res = {}
    for p in range(start_page, end_page):
        txt = reader.pages[p].extract_text() or ""
        res[p+1] = txt
    return res

# 10.2.2 Blindleistungsbereitstellung: around page 82-93
# 10.2.3 Dynamische Netzstützung: around page 93-101
# 10.2.4 Wirkleistungsabgabe: around page 101-110
# 11.3.2 EZA-Regler: around page 138-145
# 11.4 / 11.6 Anlagenzertifikat: around page 145-160

# Let's inspect 11.3.2 EZA-Regler
for p in range(130, 145):
    txt = reader.pages[p].extract_text() or ""
    if "11.3.2" in txt or "EZA-Regler" in txt:
        print(f"=== PAGE {p+1} ===")
        for line in txt.split("\n"):
            if any(k in line for k in ["11.3.2", "EZA-Regler", "Zertifikat", "Regelgenauigkeit", "Einschwingzeit", "Reaktionszeit"]):
                print("  ", line.strip())
