import re

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD CSS for compact animated chat launcher
css_anchor = "    </style>"
new_chat_css = """        /* Floating Coneza Copilot Chat Launcher Button */
        .coneza-chat-launcher {
            position: fixed;
            bottom: 22px;
            right: 22px;
            z-index: 9999;
            display: none; /* Only shown when login is successful */
            align-items: center;
            gap: 0.45rem;
            padding: 0.42rem 0.85rem;
            border-radius: 9999px;
            background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%);
            color: #ffffff;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 0.02em;
            box-shadow: 0 4px 18px rgba(2, 132, 199, 0.35), 0 0 10px rgba(13, 148, 136, 0.2);
            cursor: pointer;
            border: 1.5px solid rgba(255, 255, 255, 0.25);
            user-select: none;
            backdrop-filter: blur(10px);
            transition: all 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
            animation: chatLauncherBreathing 4s ease-in-out infinite;
        }

        .coneza-chat-launcher:hover {
            transform: translateY(-3px) scale(1.06);
            box-shadow: 0 8px 25px rgba(2, 132, 199, 0.55), 0 0 18px rgba(16, 185, 129, 0.45);
            border-color: rgba(255, 255, 255, 0.6);
            background: linear-gradient(135deg, #0369a1 0%, #059669 100%);
        }

        .coneza-chat-launcher:hover .chat-icon {
            transform: rotate(-12deg) scale(1.18);
        }

        .coneza-chat-launcher:active {
            transform: translateY(1px) scale(0.93);
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);
            transition: all 0.08s ease;
        }

        .coneza-chat-launcher.chat-open {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            border-color: rgba(37, 199, 201, 0.5);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }

        .coneza-chat-launcher .chat-icon {
            font-size: 1.05rem;
            display: inline-block;
            transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .coneza-chat-launcher .chat-badge {
            background: rgba(255, 255, 255, 0.22);
            font-size: 0.62rem;
            padding: 0.1rem 0.4rem;
            border-radius: 9999px;
            font-weight: 800;
            letter-spacing: 0.04em;
        }

        @keyframes chatLauncherBreathing {
            0%, 100% {
                box-shadow: 0 4px 18px rgba(2, 132, 199, 0.35), 0 0 10px rgba(13, 148, 136, 0.2);
            }
            50% {
                box-shadow: 0 6px 24px rgba(2, 132, 199, 0.5), 0 0 16px rgba(16, 185, 129, 0.35);
            }
        }
    </style>"""

assert css_anchor in content, "css_anchor not found"
content = content.replace(css_anchor, new_chat_css, 1)

# 2. UPDATE HTML for the launcher button
old_button_html = """    <!-- Floating Chatbox Launcher Pill Button -->
    <div id="conezaChatLauncherBtn" onclick="toggleConezaChatbox()" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; align-items: center; gap: 0.6rem; padding: 0.75rem 1.25rem; border-radius: 9999px; background: linear-gradient(135deg, #0284c7, #10b981); color: #ffffff; font-weight: 700; font-size: 0.92rem; box-shadow: 0 8px 25px rgba(2, 132, 199, 0.4); cursor: pointer; transition: all 0.25s ease; border: 1.5px solid rgba(255, 255, 255, 0.3); user-select: none;" onmouseover="this.style.transform='translateY(-2px) scale(1.03)';" onmouseout="this.style.transform='none';">
        <span style="font-size: 1.25rem;">💬</span>
        <span>Coneza Copilot</span>
        <span style="background: rgba(255, 255, 255, 0.25); font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 9999px; font-weight: 800; letter-spacing: 0.03em;">KI</span>
    </div>"""

new_button_html = """    <!-- Floating Chatbox Launcher Pill Button (Compact & Animated) -->
    <div id="conezaChatLauncherBtn" class="coneza-chat-launcher" onclick="toggleConezaChatbox()" title="Coneza EZA-Copilot öffnen">
        <span class="chat-icon" id="conezaChatIcon">💬</span>
        <span id="conezaChatLabel">Copilot</span>
        <span class="chat-badge">KI</span>
    </div>"""

assert old_button_html in content, "old_button_html not found"
content = content.replace(old_button_html, new_button_html, 1)

# 3. UPDATE logout() to hide chatbox button and window
old_logout = """            const loginHeaderBtn = document.getElementById("btnLoginHeaderBtn");
            if (loginHeaderBtn) loginHeaderBtn.style.display = "inline-flex";

            openAuthModal('login');"""

new_logout = """            const loginHeaderBtn = document.getElementById("btnLoginHeaderBtn");
            if (loginHeaderBtn) loginHeaderBtn.style.display = "inline-flex";

            const chatBtn = document.getElementById("conezaChatLauncherBtn");
            if (chatBtn) chatBtn.style.display = "none";
            const chatWidget = document.getElementById("conezaChatboxWidget");
            if (chatWidget) chatWidget.style.display = "none";

            openAuthModal('login');"""

assert old_logout in content, "old_logout not found"
content = content.replace(old_logout, new_logout, 1)

# 4. UPDATE updateUserUI() to show chatbox button when login is successful
old_update_user = """            const loginHeaderBtn = document.getElementById("btnLoginHeaderBtn");
            if (loginHeaderBtn) loginHeaderBtn.style.display = "none";"""

new_update_user = """            const loginHeaderBtn = document.getElementById("btnLoginHeaderBtn");
            if (loginHeaderBtn) loginHeaderBtn.style.display = "none";

            const chatBtn = document.getElementById("conezaChatLauncherBtn");
            if (chatBtn) chatBtn.style.display = "inline-flex";"""

assert old_update_user in content, "old_update_user not found"
content = content.replace(old_update_user, new_update_user, 1)

# 5. UPDATE toggleConezaChatbox() to animate icon and label
old_toggle = """        function toggleConezaChatbox() {
            const widget = document.getElementById("conezaChatboxWidget");
            if (!widget) return;
            const isOpen = widget.style.display === "flex";
            widget.style.display = isOpen ? "none" : "flex";
            if (!isOpen) {
                setTimeout(() => {
                    const input = document.getElementById("conezaChatInput");
                    if (input) input.focus();
                }, 100);
            }
        }"""

new_toggle = """        function toggleConezaChatbox() {
            const widget = document.getElementById("conezaChatboxWidget");
            const btn = document.getElementById("conezaChatLauncherBtn");
            const icon = document.getElementById("conezaChatIcon");
            const label = document.getElementById("conezaChatLabel");
            if (!widget) return;
            const isOpen = widget.style.display === "flex";
            widget.style.display = isOpen ? "none" : "flex";
            if (btn) btn.classList.toggle("chat-open", !isOpen);
            if (icon) icon.textContent = !isOpen ? "✕" : "💬";
            if (label) label.textContent = !isOpen ? "Schließen" : "Copilot";
            if (!isOpen) {
                setTimeout(() => {
                    const input = document.getElementById("conezaChatInput");
                    if (input) input.focus();
                }, 100);
            }
        }"""

assert old_toggle in content, "old_toggle not found"
content = content.replace(old_toggle, new_toggle, 1)

with open('backend/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated chat button size, animation, and login gating in index.html!")
