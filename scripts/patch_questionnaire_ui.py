"""
Patch script to add the interactive Plant Questionnaire (SLD replacement) to index.html.
"""

import os
import re

html_path = "backend/templates/index.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Header Button
target_header_btn = """            <button class="btn" id="btnQuickConfigHeader" style="display: none; background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2)); border: 1px solid var(--cyan-accent); color: var(--cyan-accent); font-weight: 700;" onclick="openQuickConfigModal()">
                ⚡ 1-Klick Auto-Config (SLD + E.9/E.8)
            </button>"""

replacement_header_btn = """            <button class="btn" id="btnQuestionnaireHeader" style="display: none; background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(6, 182, 212, 0.18)); border: 1.5px solid #10b981; color: #10b981; font-weight: 700;" onclick="openPlantQuestionnaireModal()">
                📋 Fragebogen (Kein SLD nötig)
            </button>
            <button class="btn" id="btnQuickConfigHeader" style="display: none; background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2)); border: 1px solid var(--cyan-accent); color: var(--cyan-accent); font-weight: 700;" onclick="openQuickConfigModal()">
                ⚡ 1-Klick Auto-Config (SLD + E.9/E.8)
            </button>"""

if target_header_btn not in content:
    target_header_btn = target_header_btn.replace('\n', '\r\n')
    replacement_header_btn = replacement_header_btn.replace('\n', '\r\n')

assert target_header_btn in content, "target_header_btn not found"
content = content.replace(target_header_btn, replacement_header_btn, 1)


# 2. Hero Action Button
target_hero = """                    <button class="btn btn-primary" onclick="switchTab('geminiTab', document.querySelectorAll('.tab-btn')[2])">
                        ✨ Gemini Netzprüfung starten
                    </button>
                    <button class="btn" onclick="switchTab('docsTab', document.querySelectorAll('.tab-btn')[1])">
                        📄 Dokumente hochladen (E.8 / E.9 / SLD)
                    </button>"""

replacement_hero = """                    <button class="btn btn-primary" onclick="openPlantQuestionnaireModal()" style="background: linear-gradient(135deg, #10b981, #0ea5e9); border:none; box-shadow: 0 4px 14px rgba(16,185,129,0.35); font-weight:700;">
                        📋 Schneller Fragebogen (Kein SLD nötig)
                    </button>
                    <button class="btn" onclick="switchTab('geminiTab', document.querySelectorAll('.tab-btn')[2])">
                        ✨ Gemini Netzprüfung starten
                    </button>
                    <button class="btn" onclick="switchTab('docsTab', document.querySelectorAll('.tab-btn')[1])">
                        📄 Dokumente hochladen (E.8 / E.9 / SLD)
                    </button>"""

if target_hero not in content:
    target_hero = target_hero.replace('\n', '\r\n')
    replacement_hero = replacement_hero.replace('\n', '\r\n')

assert target_hero in content, "target_hero not found"
content = content.replace(target_hero, replacement_hero, 1)


# 3. Tab 1 Plants Header Buttons
target_tab1_btn = """                    <button class="btn" style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(59, 130, 246, 0.15)); border: 1px solid var(--cyan-accent); color: var(--cyan-accent); font-weight: 700;" onclick="openQuickConfigModal()">⚡ SLD + E.9/E.8 Express-Konfiguration</button>"""

replacement_tab1_btn = """                    <button class="btn" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15)); border: 1.5px solid #10b981; color: #10b981; font-weight: 700;" onclick="openPlantQuestionnaireModal()">📋 Fragebogen (Kein SLD nötig)</button>
                    <button class="btn" style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(59, 130, 246, 0.15)); border: 1px solid var(--cyan-accent); color: var(--cyan-accent); font-weight: 700;" onclick="openQuickConfigModal()">⚡ SLD + E.9/E.8 Express-Konfiguration</button>"""

if target_tab1_btn not in content:
    target_tab1_btn = target_tab1_btn.replace('\n', '\r\n')
    replacement_tab1_btn = replacement_tab1_btn.replace('\n', '\r\n')

assert target_tab1_btn in content, "target_tab1_btn not found"
content = content.replace(target_tab1_btn, replacement_tab1_btn, 1)


# 4. Tab 1 Hero Card CTA
target_hero_card_cta = """                    <button type="button" class="btn btn-primary" style="background: linear-gradient(135deg, #06b6d4, #2563eb); border: none; font-weight: 700; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4); padding: 0.65rem 1.35rem;" onclick="openQuickConfigModal()">
                        🚀 Jetzt konfigurieren & PCU anzeigen
                    </button>"""

replacement_hero_card_cta = """                    <button type="button" class="btn" style="background: linear-gradient(135deg, #10b981, #0ea5e9); color: #fff; font-weight: 700; border: none; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35); padding: 0.65rem 1.35rem;" onclick="openPlantQuestionnaireModal()">
                        📋 Interaktiver Fragebogen (Kein SLD nötig)
                    </button>
                    <button type="button" class="btn btn-primary" style="background: linear-gradient(135deg, #06b6d4, #2563eb); border: none; font-weight: 700; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4); padding: 0.65rem 1.35rem;" onclick="openQuickConfigModal()">
                        🚀 Express mit SLD-Upload
                    </button>"""

if target_hero_card_cta not in content:
    target_hero_card_cta = target_hero_card_cta.replace('\n', '\r\n')
    replacement_hero_card_cta = replacement_hero_card_cta.replace('\n', '\r\n')

assert target_hero_card_cta in content, "target_hero_card_cta not found"
content = content.replace(target_hero_card_cta, replacement_hero_card_cta, 1)


# 5. Quick Config Modal Banner pointing to Questionnaire
target_quick_modal_form = """            <form id="quickConfigForm" onsubmit="handleQuickConfigSubmit(event)">"""

replacement_quick_modal_form = """            <div style="background: rgba(16, 185, 129, 0.12); border: 1.5px solid rgba(16, 185, 129, 0.45); border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.25rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <div>
                    <strong style="color: #34d399; font-size: 0.9rem; display: block;">💡 Kein Übersichtsschaltplan (SLD) als PDF zur Hand?</strong>
                    <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 2px;">
                        Nutzen Sie unseren einfachen Fragebogen mit marktüblichen Wechselrichtern & Trafos – ein SLD ist nicht mehr erforderlich!
                    </div>
                </div>
                <button type="button" class="btn" style="background: #10b981; color: #fff; font-size: 0.82rem; font-weight: 700; white-space: nowrap; padding: 0.45rem 0.95rem; border: none; border-radius: 6px; cursor: pointer;" onclick="closeQuickConfigModal(); openPlantQuestionnaireModal();">
                    Fragebogen öffnen ➔
                </button>
            </div>

            <form id="quickConfigForm" onsubmit="handleQuickConfigSubmit(event)">"""

if target_quick_modal_form not in content:
    target_quick_modal_form = target_quick_modal_form.replace('\n', '\r\n')
    replacement_quick_modal_form = replacement_quick_modal_form.replace('\n', '\r\n')

assert target_quick_modal_form in content, "target_quick_modal_form not found"
content = content.replace(target_quick_modal_form, replacement_quick_modal_form, 1)


# 6. Update Auth UI to show questionnaire header button
target_auth_ui = """            const quickBtnHeader = document.getElementById("btnQuickConfigHeader");
            if (quickBtnHeader) quickBtnHeader.style.display = canManagePlants ? 'inline-flex' : 'none';"""

replacement_auth_ui = """            const questBtnHeader = document.getElementById("btnQuestionnaireHeader");
            if (questBtnHeader) questBtnHeader.style.display = 'inline-flex';
            const quickBtnHeader = document.getElementById("btnQuickConfigHeader");
            if (quickBtnHeader) quickBtnHeader.style.display = canManagePlants ? 'inline-flex' : 'none';"""

if target_auth_ui not in content:
    target_auth_ui = target_auth_ui.replace('\n', '\r\n')
    replacement_auth_ui = replacement_auth_ui.replace('\n', '\r\n')

assert target_auth_ui in content, "target_auth_ui not found"
content = content.replace(target_auth_ui, replacement_auth_ui, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Part 1 (Buttons, Links, Header) patched.")
