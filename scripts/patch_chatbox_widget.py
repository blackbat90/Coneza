import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILE_PATH = 'backend/templates/index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add pulseChat animation to CSS
if '@keyframes pulseChat' not in content:
    chat_css = """
        @keyframes pulseChat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.12); }
        }
    """
    content = content.replace('    </style>', chat_css + '\n    </style>', 1)
    print("Added pulseChat animation to <style>!")

# 2. Replace lines 8279-8280 (pcuDocumentDraftLink) with Coneza AI Chatbox widget
old_link = """<a id="pcuDocumentDraftLink" style="position:fixed;bottom:18px;right:18px;z-index:100;background:#83e4c2;color:#102334;padding:12px 18px;border-radius:10px" href="pcu-draft">SLD + E8/E9: PCU-Entwurf</a>
<script>document.getElementById("pcuDocumentDraftLink").href=(location.pathname.startsWith("/portal")?"/portal":"")+"/pcu-draft";</script>"""

assert old_link in content, "Could not find old pcuDocumentDraftLink"

new_chatbox_html = """    <!-- ========================================================================= -->
    <!-- Coneza AI Copilot Chatbox Widget                                          -->
    <!-- ========================================================================= -->

    <!-- Floating Chatbox Launcher Pill Button -->
    <div id="conezaChatLauncherBtn" onclick="toggleConezaChatbox()" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; align-items: center; gap: 0.6rem; padding: 0.75rem 1.25rem; border-radius: 9999px; background: linear-gradient(135deg, #0284c7, #10b981); color: #ffffff; font-weight: 700; font-size: 0.92rem; box-shadow: 0 8px 25px rgba(2, 132, 199, 0.4); cursor: pointer; transition: all 0.25s ease; border: 1.5px solid rgba(255, 255, 255, 0.3); user-select: none;" onmouseover="this.style.transform='translateY(-2px) scale(1.03)';" onmouseout="this.style.transform='none';">
        <span style="font-size: 1.25rem;">💬</span>
        <span>Coneza Copilot</span>
        <span style="background: rgba(255, 255, 255, 0.25); font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 9999px; font-weight: 800; letter-spacing: 0.03em;">KI</span>
    </div>

    <!-- Floating Chatbox Window -->
    <div id="conezaChatboxWidget" style="position: fixed; bottom: 82px; right: 20px; z-index: 10000; width: 440px; max-width: 92vw; height: 580px; max-height: 82vh; background: #ffffff; border-radius: 18px; box-shadow: 0 20px 60px rgba(11, 23, 40, 0.35); border: 1px solid #cbd5e1; display: none; flex-direction: column; overflow: hidden;">
        <!-- Chat Header -->
        <div style="background: linear-gradient(135deg, #0b1728 0%, #152235 100%); color: #ffffff; padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #0284c7, #10b981); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);">
                    🤖
                </div>
                <div>
                    <div style="font-size: 0.98rem; font-weight: 800; display: flex; align-items: center; gap: 0.4rem;">
                        Coneza Copilot
                        <span style="font-size: 0.68rem; background: rgba(16, 185, 129, 0.25); color: #34d399; padding: 0.1rem 0.45rem; border-radius: 9999px; border: 1px solid rgba(16, 185, 129, 0.4); font-weight: 700;">Online</span>
                    </div>
                    <div style="font-size: 0.74rem; color: #94a3b8;">VDE-AR-N 4110 &amp; EZA-Regler Experte</div>
                </div>
            </div>
            <div style="display: flex; gap: 0.4rem; align-items: center;">
                <button type="button" class="btn btn-sm" style="background: rgba(255, 255, 255, 0.1); color: #cbd5e1; border: none; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.85rem;" onclick="toggleConezaChatbox()" title="Minimieren">✕</button>
            </div>
        </div>

        <!-- Messages Container -->
        <div id="conezaChatMessages" style="flex: 1; padding: 1.1rem; overflow-y: auto; display: flex; flex-direction: column; gap: 0.85rem; background: #f8fafc; font-size: 0.86rem;">
            <!-- Welcome Message -->
            <div style="align-self: flex-start; max-width: 90%; background: #ffffff; border: 1px solid #e2e8f0; padding: 0.85rem 1rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); color: #152235; line-height: 1.5;">
                👋 <b>Guten Tag!</b> Ich bin Ihr <b>Coneza EZA-Copilot</b>.<br>
                Wie kann ich Ihnen bei der Netzintegration, VDE-AR-N 4110 Regler-Parametrierung (Phoenix Contact AXC F 2152), Komponenten oder Modbus-Registern helfen?
            </div>

            <!-- Quick Suggestion Chips -->
            <div id="conezaChatSuggestions" style="display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.25rem;">
                <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Schnellfragen:</div>
                <button type="button" class="btn btn-sm" style="text-align: left; font-size: 0.78rem; background: #ffffff; border: 1px solid #cbd5e1; color: #0284c7; padding: 0.45rem 0.75rem; border-radius: 8px;" onclick="askConezaChatSuggestion('Welche Blindleistungsmodi fordert die VDE-AR-N 4110?')">
                    💡 Welche Blindleistungsmodi fordert die VDE-AR-N 4110?
                </button>
                <button type="button" class="btn btn-sm" style="text-align: left; font-size: 0.78rem; background: #ffffff; border: 1px solid #cbd5e1; color: #0284c7; padding: 0.45rem 0.75rem; border-radius: 8px;" onclick="askConezaChatSuggestion('Welche Modbus-Register nutzt der Phoenix Contact AXC F 2152?')">
                    ⚡ Welche Modbus-Register nutzt der Phoenix Contact AXC F 2152?
                </button>
                <button type="button" class="btn btn-sm" style="text-align: left; font-size: 0.78rem; background: #ffffff; border: 1px solid #cbd5e1; color: #0284c7; padding: 0.45rem 0.75rem; border-radius: 8px;" onclick="askConezaChatSuggestion('Wie dimensioniere ich den Maschinentransformator für eine 1.5 MW PV-Anlage?')">
                    🔄 Wie dimensioniere ich den Trafo für 1.5 MW PV?
                </button>
            </div>
        </div>

        <!-- Chat Input Area -->
        <div style="padding: 0.85rem 1rem; background: #ffffff; border-top: 1px solid #e2e8f0; display: flex; gap: 0.5rem; align-items: center;">
            <input type="text" id="conezaChatInput" class="form-input" placeholder="Frage an den Coneza Copilot stellen..." style="flex: 1; font-size: 0.88rem; padding: 0.6rem 0.85rem; border-radius: 8px;" onkeypress="handleConezaChatKey(event)">
            <button type="button" id="conezaChatSendBtn" class="btn btn-primary" onclick="sendConezaChatMessage()" style="padding: 0.6rem 1rem; font-weight: 700; background: linear-gradient(135deg, #0284c7, #10b981); border: none; border-radius: 8px; box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3); cursor: pointer;">
                ➔
            </button>
        </div>
    </div>

    <script>
        let conezaChatHistory = [];

        function toggleConezaChatbox() {
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
        }

        function handleConezaChatKey(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                sendConezaChatMessage();
            }
        }

        function askConezaChatSuggestion(questionText) {
            const input = document.getElementById("conezaChatInput");
            if (input) {
                input.value = questionText;
                sendConezaChatMessage();
            }
        }

        async function sendConezaChatMessage() {
            const input = document.getElementById("conezaChatInput");
            const text = input ? input.value.trim() : "";
            if (!text) return;

            const chatMessages = document.getElementById("conezaChatMessages");
            input.value = "";

            // Hide initial suggestions once user chats
            const sugg = document.getElementById("conezaChatSuggestions");
            if (sugg) sugg.style.display = "none";

            // Append user message
            const userMsgDiv = document.createElement("div");
            userMsgDiv.style.alignSelf = "flex-end";
            userMsgDiv.style.maxWidth = "85%";
            userMsgDiv.style.background = "linear-gradient(135deg, #0284c7, #0ea5e9)";
            userMsgDiv.style.color = "#ffffff";
            userMsgDiv.style.padding = "0.75rem 1rem";
            userMsgDiv.style.borderRadius = "12px";
            userMsgDiv.style.lineHeight = "1.45";
            userMsgDiv.innerText = text;
            chatMessages.appendChild(userMsgDiv);

            // Append loading indicator
            const loadingId = "conezaChatLoading_" + Date.now();
            const loadingDiv = document.createElement("div");
            loadingDiv.id = loadingId;
            loadingDiv.style.alignSelf = "flex-start";
            loadingDiv.style.maxWidth = "85%";
            loadingDiv.style.background = "#ffffff";
            loadingDiv.style.border = "1px solid #e2e8f0";
            loadingDiv.style.padding = "0.75rem 1rem";
            loadingDiv.style.borderRadius = "12px";
            loadingDiv.style.color = "#64748b";
            loadingDiv.innerHTML = `<span class="spinner" style="display:inline-block; width:12px; height:12px; border:2px solid #0284c7; border-top-color:transparent; border-radius:50%; animation:spin 1s linear infinite; margin-right:6px; vertical-align:middle;"></span> <b>Coneza Copilot</b> analysiert...`;
            chatMessages.appendChild(loadingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            conezaChatHistory.push({ role: "user", content: text });

            try {
                const headers = { "Content-Type": "application/json" };
                if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

                const res = await fetch(`${API_BASE}/api/chat`, {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify({
                        message: text,
                        history: conezaChatHistory
                    })
                });

                const loader = document.getElementById(loadingId);
                if (loader) loader.remove();

                if (res.ok) {
                    const data = await res.json();
                    const aiAnswer = data.response || "Antwort erhalten.";
                    conezaChatHistory.push({ role: "assistant", content: aiAnswer });

                    const aiMsgDiv = document.createElement("div");
                    aiMsgDiv.style.alignSelf = "flex-start";
                    aiMsgDiv.style.maxWidth = "90%";
                    aiMsgDiv.style.background = "#ffffff";
                    aiMsgDiv.style.border = "1px solid #e2e8f0";
                    aiMsgDiv.style.padding = "0.85rem 1rem";
                    aiMsgDiv.style.borderRadius = "12px";
                    aiMsgDiv.style.boxShadow = "0 1px 3px rgba(0,0,0,0.04)";
                    aiMsgDiv.style.lineHeight = "1.5";
                    aiMsgDiv.style.color = "#152235";

                    let clausesHtml = "";
                    if (data.referenced_clauses && data.referenced_clauses.length > 0) {
                        clausesHtml = `
                            <div style="margin-top: 0.6rem; padding-top: 0.5rem; border-top: 1px dashed #e2e8f0; display: flex; flex-wrap: wrap; gap: 0.35rem;">
                                ${data.referenced_clauses.map(c => `<span style="font-size: 0.7rem; background: #e0f2fe; color: #0369a1; padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 600;">📜 ${escapeHtml(c)}</span>`).join('')}
                            </div>
                        `;
                    }

                    let followupsHtml = "";
                    if (data.suggested_followups && data.suggested_followups.length > 0) {
                        followupsHtml = `
                            <div style="margin-top: 0.6rem; display: flex; flex-direction: column; gap: 0.3rem;">
                                ${data.suggested_followups.slice(0, 2).map(f => `
                                    <button type="button" class="btn btn-sm" style="text-align: left; font-size: 0.74rem; background: #f8fafc; border: 1px solid #cbd5e1; color: #0284c7; padding: 0.3rem 0.6rem; border-radius: 6px;" onclick="askConezaChatSuggestion('${escapeHtml(f)}')">
                                        ➔ ${escapeHtml(f)}
                                    </button>
                                `).join('')}
                            </div>
                        `;
                    }

                    aiMsgDiv.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="font-size: 0.95rem;">🤖</span>
                            <b style="font-size: 0.82rem; color: #0284c7;">Coneza Copilot</b>
                        </div>
                        <div>${formatChatMarkdown(aiAnswer)}</div>
                        ${clausesHtml}
                        ${followupsHtml}
                    `;
                    chatMessages.appendChild(aiMsgDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                } else {
                    const errData = await res.json().catch(() => ({}));
                    const errDiv = document.createElement("div");
                    errDiv.style.alignSelf = "flex-start";
                    errDiv.style.maxWidth = "85%";
                    errDiv.style.background = "#fee2e2";
                    errDiv.style.color = "#991b1b";
                    errDiv.style.padding = "0.75rem 1rem";
                    errDiv.style.borderRadius = "12px";
                    errDiv.innerText = errData.detail || "Fehler beim Abrufen der Copilot-Antwort.";
                    chatMessages.appendChild(errDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            } catch (err) {
                const loader = document.getElementById(loadingId);
                if (loader) loader.remove();
                const errDiv = document.createElement("div");
                errDiv.style.alignSelf = "flex-start";
                errDiv.style.maxWidth = "85%";
                errDiv.style.background = "#fee2e2";
                errDiv.style.color = "#991b1b";
                errDiv.style.padding = "0.75rem 1rem";
                errDiv.style.borderRadius = "12px";
                errDiv.innerText = "Netzwerkfehler: Copilot-Antwort konnte nicht geladen werden.";
                chatMessages.appendChild(errDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    </script>"""

content = content.replace(old_link, new_chatbox_html, 1)

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced floating button with Coneza Chatbox widget successfully! New length:", len(content))
