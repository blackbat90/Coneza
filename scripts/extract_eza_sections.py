import pypdf

reader = pypdf.PdfReader("VDE_AR_N_4110_2023.pdf")

with open("vde_eza_sections.txt", "w", encoding="utf-8") as f_out:
    # 10.2.2 Blindleistung (pages 82-93)
    # 10.2.3 FRT (pages 93-101)
    # 10.2.4 Wirkleistung (pages 101-110)
    # 10.3 Schutz (pages 110-121)
    # 11.3 Komponentenzertifikat / EZA-Regler (pages 145-150)
    # 11.4 Anlagenzertifikat (pages 150-160)
    for p in range(78, 165):
        f_out.write(f"\n\n==================== PAGE {p+1} ====================\n\n")
        f_out.write(reader.pages[p].extract_text() or "")

print("Saved pages 79-165 to vde_eza_sections.txt")
