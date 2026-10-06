with open('backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_def = '''@app.post("/api/chat", response_model=DocumentChatResponse)
async def general_coneza_chat(
    payload: DocumentChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_flexible)
):'''

new_def = '''@app.post("/api/chat", response_model=DocumentChatResponse)
async def general_coneza_chat(
    payload: DocumentChatRequest
):'''

assert old_def in code, "Could not find old_def"
code = code.replace(old_def, new_def, 1)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated general_coneza_chat signature successfully!")
