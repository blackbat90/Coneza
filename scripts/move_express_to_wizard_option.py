import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILE_PATH = 'backend/templates/index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Verify and remove the 1-Click Fast Configuration Hero Card from plantsTab
hero_start_token = "<!-- 1-Click Fast Configuration Hero Card -->"
assert hero_start_token in content, "Could not find hero card start"

# Find end of hero card: </div>\n\n            <!-- KPI Tiles -->
hero_start_idx = content.find(hero_start_token)
kpi_tiles_idx = content.find("<!-- KPI Tiles -->", hero_start_idx)
assert kpi_tiles_idx != -1, "Could not find KPI Tiles"

hero_block = content[hero_start_idx:kpi_tiles_idx]
print("Hero block to remove length:", len(hero_block))

# Remove hero block
content = content[:hero_start_idx] + content[kpi_tiles_idx:]
print("Removed Express hero card from plantsTab!")

# 2. Add Express option banner inside plantQuestionnaireModal
# Right after Modal Header (after `<!-- Schnellvorlagen (Presets) Bar -->` or right above it)
presets_bar_token = "<!-- Schnellvorlagen (Presets) Bar -->"
assert presets_bar_token in content, "Could not find presets bar"

express_option_html = """<!-- Option: Express-Inbetriebnahme mit vorhandenem SLD / E.9 Dokument -->
            <div style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(37, 99, 235, 0.05)); border: 1.5px solid rgba(6, 182, 212, 0.3); border-radius: 12px; padding: 0.85rem 1.25rem; margin-bottom: 1.15rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.4rem;">⚡</span>
                    <div>
                        <div style="font-size: 0.88rem; font-weight: 700; color: var(--navy);">Option: Express-Inbetriebnahme mit vorhandenem SLD / E.9 Bogen</div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.4;">Haben Sie bereits einen PDF-Übersichtsschaltplan oder Netzanschlussbogen? Das System extrahiert alle technischen Daten automatisch.</div>
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <button type="button" class="btn btn-sm btn-primary" style="font-size: 0.82rem; font-weight: 700; background: linear-gradient(135deg, #06b6d4, #2563eb); border: none; padding: 0.45rem 1rem; box-shadow: 0 2px 8px rgba(6, 182, 212, 0.35); cursor: pointer;" onclick="closePlantQuestionnaireModal(); openQuickConfigModal();">
                        🚀 Express via SLD-Upload öffnen
                    </button>
                </div>
            </div>

            """

content = content.replace(presets_bar_token, express_option_html + presets_bar_token, 1)
print("Added Express option inside plantQuestionnaireModal!")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated successfully! New length:", len(content))
