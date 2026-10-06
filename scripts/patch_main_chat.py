import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Update backend/main.py to add @app.post("/api/chat")
with open('backend/main.py', 'r', encoding='utf-8') as f:
    main_code = f.read()

endpoint_signature = '@app.post("/api/chat"'
if endpoint_signature not in main_code:
    # Find where @app.post("/api/documents/{doc_id}/chat" is defined
    target_pos = main_code.find('@app.post("/api/documents/{doc_id}/chat"')
    assert target_pos != -1, "Could not find doc chat endpoint"

    new_endpoint = '''@app.post("/api/chat", response_model=DocumentChatResponse)
async def general_coneza_chat(
    payload: DocumentChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_flexible)
):
    """
    General Coneza AI Copilot chat endpoint for VDE-AR-N 4110 / 4120 questions,
    plant configurations, Phoenix Contact AXC F 2152 controller parameters,
    Modbus register maps, and technical commissioning advice.
    """
    user_msg = payload.message.strip()
    history = payload.history or []

    prompt_lines = [
        'Sie sind der "Coneza Copilot", der offizielle KI-Ingenieur und Assistent der Coneza Plattform für Mittelspannungs-Netzintegration (VDE-AR-N 4110 / 4120) und Phoenix Contact EZA-Parkregler (PLCnext AXC F 2152 / SOL-SC-PCU).',
        '',
        'Ihre Kernkompetenzen:',
        '- VDE-AR-N 4110 / VDE-AR-N 4105 / VDE-AR-N 4120 Normen, FGW TR3 / TR8 Zertifizierung.',
        '- Konfiguration von Photovoltaik (PV), Batteriespeichern (BESS), Windkraft und Blockheizkraftwerken/Diesel.',
        '- Berechnung von Transformator-Impedanzen (u_k), Blindleistungsverfahren (Q(U), cos φ(P), Feste Blindleistung), Frequenzhaltung P(f) (LFSM-O).',
        '- Modbus TCP Registerbelegung für Phoenix Contact SOL-SC-PCU (Holding Register 40100-40300).',
        '- Unterstützung beim Erstellen neuer Anlagen ohne SLD über den Coneza Schritt-für-Schritt Wizard.',
        '',
        'Antwort-Vorgaben:',
        '1. Antworten Sie auf Deutsch, hochprofessionell, präzise, technisch fundiert und übersichtlich strukturiert.',
        '2. Verwenden Sie Markdown (Überschriften, Listen, fette Begriffe, Codeblöcke für Register oder Zahlen).',
        '3. Geben Sie stets konkrete VDE-Absätze oder Modbus-Register an, wenn relevant.'
    ]
    system_prompt = "\\n".join(prompt_lines)

    if _openai_chat_client:
        try:
            messages = [{"role": "system", "content": system_prompt}]
            for h in history[-8:]:
                messages.append({"role": h.role, "content": h.content})
            messages.append({"role": "user", "content": user_msg})

            resp = _openai_chat_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.25,
                max_tokens=700
            )
            answer = resp.choices[0].message.content
            return DocumentChatResponse(
                response=answer,
                suggested_followups=[
                    "Welche Modbus-Register werden für Q(U) genutzt?",
                    "Wie lege ich eine Anlage ohne SLD über den Wizard an?",
                    "Wie dimensioniere ich den Maschinentransformator?",
                    "Welche Schutzfunktionen wirken auf den Kuppelschalter Q0?"
                ],
                referenced_clauses=["VDE-AR-N 4110 Abs. 10.2", "VDE-AR-N 4110 Abs. 10.4", "FGW TR8"]
            )
        except Exception as e:
            logger.warning(f"OpenAI general chat call failed: {e}")

    # Fallback to intelligent deterministic response
    dummy_interpretation = {
        "grid_operator": "VNB Verteilnetzbetreiber",
        "connection_point": "Mittelspannungs-NAP",
        "engineering_rationale": {},
        "pcu_mappings": []
    }
    dummy_entities = {
        "active_power_kw": 1500,
        "grid_voltage_v": 20000,
        "reactive_mode": "Q(U)",
        "transformer_uk_percent": 6.0
    }
    return await execute_document_chat(
        doc_type="Allgemeine EZA-Beratung",
        filename="Coneza Plattform",
        user_message=user_msg,
        history=history,
        interpretation=dummy_interpretation,
        entities=dummy_entities,
        full_text_sample=""
    )


'''
    main_code = main_code[:target_pos] + new_endpoint + main_code[target_pos:]
    with open('backend/main.py', 'w', encoding='utf-8') as f:
        f.write(main_code)
    print("Added /api/chat endpoint to backend/main.py!")
else:
    print("/api/chat endpoint already present in main.py")
