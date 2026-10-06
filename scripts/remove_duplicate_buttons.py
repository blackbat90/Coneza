import re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILE_PATH = 'backend/templates/index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

print("Original length:", len(content))

# 1. In Header: remove btnQuestionnaireHeader and clean btnCreatePlantHeader
old_header_buttons = """            <button class="btn" id="btnQuestionnaireHeader" style="display: none; background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(6, 182, 212, 0.18)); border: 1.5px solid #10b981; color: #10b981; font-weight: 700;" onclick="openPlantQuestionnaireModal()">
                📋 Fragebogen (Kein SLD nötig)
            </button>
            <button class="btn btn-primary" id="btnCreatePlantHeader" style="display: none;" onclick="openPlantQuestionnaireModal()">
                🧙‍♂️ + Neue Anlage (Wizard)
            </button>"""

new_header_buttons = """            <button class="btn btn-primary" id="btnCreatePlantHeader" style="display: none;" onclick="openPlantQuestionnaireModal()">
                + Neue Anlage
            </button>"""

assert old_header_buttons in content, "Could not find old header buttons"
content = content.replace(old_header_buttons, new_header_buttons, 1)
print("Updated header buttons: removed redundant Fragebogen button!")

# 2. In Tab 1: remove redundant Fragebogen button next to + Neue Anlage
old_tab_buttons = """                    <button class="btn" onclick="loadPlants()">🔄 Aktualisieren</button>
                    <button class="btn" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15)); border: 1.5px solid #10b981; color: #10b981; font-weight: 700;" onclick="openPlantQuestionnaireModal()">📋 Fragebogen (Kein SLD nötig)</button>
                    <button class="btn btn-primary" id="btnCreatePlantInTab" onclick="openPlantQuestionnaireModal()">🧙‍♂️ + Neue Anlage (Wizard)</button>"""

new_tab_buttons = """                    <button class="btn" onclick="loadPlants()">🔄 Aktualisieren</button>
                    <button class="btn btn-primary" id="btnCreatePlantInTab" onclick="openPlantQuestionnaireModal()">+ Neue Anlage</button>"""

assert old_tab_buttons in content, "Could not find old tab buttons"
content = content.replace(old_tab_buttons, new_tab_buttons, 1)
print("Updated tab 1 buttons: removed redundant Fragebogen button!")

# 3. In Hero 1-Click Fast Configuration Card: remove redundant button
old_hero_buttons = """                    <button type="button" class="btn" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); color: #e2e8f0; font-weight: 600;" onclick="runQuickConfigDemo()">
                        🧪 Musterdaten testen
                    </button>
                    <button type="button" class="btn" style="background: linear-gradient(135deg, #10b981, #0ea5e9); color: #fff; font-weight: 700; border: none; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35); padding: 0.65rem 1.35rem;" onclick="openPlantQuestionnaireModal()">
                        📋 Interaktiver Fragebogen (Kein SLD nötig)
                    </button>
                    <button type="button" class="btn btn-primary" style="background: linear-gradient(135deg, #06b6d4, #2563eb); border: none; font-weight: 700; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4); padding: 0.65rem 1.35rem;" onclick="openQuickConfigModal()">
                        🚀 Express mit SLD-Upload
                    </button>"""

new_hero_buttons = """                    <button type="button" class="btn" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); color: #e2e8f0; font-weight: 600;" onclick="runQuickConfigDemo()">
                        🧪 Musterdaten testen
                    </button>
                    <button type="button" class="btn btn-primary" style="background: linear-gradient(135deg, #06b6d4, #2563eb); border: none; font-weight: 700; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4); padding: 0.65rem 1.35rem;" onclick="openQuickConfigModal()">
                        🚀 Express mit SLD-Upload
                    </button>"""

assert old_hero_buttons in content, "Could not find old hero buttons"
content = content.replace(old_hero_buttons, new_hero_buttons, 1)
print("Updated hero card buttons: removed duplicate button!")

# 4. In JS: remove reference to btnQuestionnaireHeader
old_js_line = """            const questBtnHeader = document.getElementById("btnQuestionnaireHeader");
            if (questBtnHeader) questBtnHeader.style.display = 'inline-flex';"""

if old_js_line in content:
    content = content.replace(old_js_line, "", 1)
    print("Removed JS reference to btnQuestionnaireHeader!")

# 5. In quickConfigModal: update button text
content = content.replace("Fragebogen öffnen ➔", "+ Neue Anlage anlegen ➔")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html successfully! New length:", len(content))
