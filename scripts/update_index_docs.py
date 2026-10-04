with open("backend/templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update plant details document item
old_plant_doc = """                            <div style="display: flex; gap: 0.5rem;">
                                <a href="${API_BASE}/api/documents/${doc.id}/download" target="_blank" class="btn" style="padding: 0.35rem 0.8rem; font-size: 0.78rem;">
                                    📄 Herunterladen / Ansehen
                                </a>
                            </div>"""

new_plant_doc = """                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                <a href="${API_BASE}/api/documents/${doc.id}/download" target="_blank" class="btn" style="padding: 0.35rem 0.8rem; font-size: 0.78rem;">
                                    📄 Herunterladen / Ansehen
                                </a>
                                <button class="btn btn-danger" style="padding: 0.35rem 0.8rem; font-size: 0.78rem;" onclick="deleteDocument('${doc.id}', '${escapeHtml(doc.filename)}', '${plant.id}')">
                                    🗑️ Löschen
                                </button>
                            </div>"""

# 2. Update loadDocuments and add deleteDocument function
old_load_doc = """                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><span class="badge badge-super">${doc.doc_type}</span></td>
                        <td style="font-weight: 600;">${doc.filename}</td>
                        <td style="font-size: 0.8rem; font-family: var(--font-mono);">${entStr}</td>
                        <td>
                            <button class="btn" style="padding: 0.35rem 0.75rem; font-size: 0.78rem;" onclick="quickAnalyzeSingle('${doc.id}')">Analyze</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                console.error("Load documents failed:", err);
            }
        }"""

new_load_doc = """                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><span class="badge badge-super">${escapeHtml(doc.doc_type)}</span></td>
                        <td style="font-weight: 600;">${escapeHtml(doc.filename)}</td>
                        <td style="font-size: 0.8rem; font-family: var(--font-mono);">${entStr}</td>
                        <td>
                            <div style="display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap;">
                                <a href="${API_BASE}/api/documents/${doc.id}/download" target="_blank" class="btn" style="padding: 0.35rem 0.65rem; font-size: 0.78rem;" title="Dokument ansehen / herunterladen">📄 Ansehen</a>
                                <button class="btn" style="padding: 0.35rem 0.65rem; font-size: 0.78rem;" onclick="quickAnalyzeSingle('${doc.id}')">Analyze</button>
                                <button class="btn btn-danger" style="padding: 0.35rem 0.65rem; font-size: 0.78rem;" onclick="deleteDocument('${doc.id}', '${escapeHtml(doc.filename)}')">🗑️ Löschen</button>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                console.error("Load documents failed:", err);
            }
        }

        async function deleteDocument(docId, filename, plantId = null) {
            if (!confirm(`Möchten Sie das Dokument "${filename || docId}" wirklich unwiderruflich löschen?`)) {
                return;
            }

            try {
                const res = await fetch(`${API_BASE}/api/documents/${docId}`, {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${authToken}`
                    }
                });

                if (res.ok) {
                    loadDocuments();
                    if (plantId && activePlantId === plantId) {
                        openPlantDetail(plantId);
                    } else if (activePlantId) {
                        openPlantDetail(activePlantId);
                    }
                } else {
                    const err = await res.json().catch(() => ({ detail: "Fehler beim Löschen des Dokuments" }));
                    alert(`Löschen fehlgeschlagen: ${err.detail || "Unzureichende Berechtigungen oder Fehler aufgetreten"}`);
                }
            } catch (err) {
                console.error("Delete document failed:", err);
                alert(`Netzwerkfehler beim Löschen des Dokuments: ${err.message}`);
            }
        }"""

assert old_plant_doc in content, "old_plant_doc not found"
assert old_load_doc in content, "old_load_doc not found"

content = content.replace(old_plant_doc, new_plant_doc, 1)
content = content.replace(old_load_doc, new_load_doc, 1)

with open("backend/templates/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated backend/templates/index.html")
