with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize newline for matching if needed, or match directly
# 1. Add <th>Epic</th>
old_th = """                                <th>Jira Key</th>
                                <th>Typ</th>"""
new_th = """                                <th>Jira Key</th>
                                <th>Epic</th>
                                <th>Typ</th>"""
if old_th not in content:
    # try with CRLF
    old_th = old_th.replace('\n', '\r\n')
    new_th = new_th.replace('\n', '\r\n')

assert old_th in content, "old_th not found in index.html"
content = content.replace(old_th, new_th, 1)

# 2. Update tbody colspan and row columns
old_body = """                if (tickets.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:var(--text-muted);">Keine Jira Tickets vorhanden.</td></tr>`;
                    return;
                }

                tickets.forEach(t => {
                    const tr = document.createElement("tr");
                    const isQuestion = (t.summary || '').includes('[Rückfrage');
                    const prioClass = t.priority === 'High' ? 'badge-danger' : (t.priority === 'Medium' ? 'badge-engineer' : 'badge');
                    const statusClass = t.status === 'OPEN' ? 'badge-online' : 'badge';

                    tr.innerHTML = `
                        <td style="font-family: var(--font-mono); font-weight: 700; color: var(--blue);">
                            ${escapeHtml(t.jira_key)}
                            ${t.synced_with_jira ? '<span title="Mit Jira synchronisiert" style="color:var(--status-online); margin-left:4px;">☁️</span>' : '<span title="Lokale Warteschlange" style="color:var(--text-muted); margin-left:4px;">💾</span>'}
                        </td>
                        <td><span class="badge ${isQuestion ? 'badge-super' : 'badge'}" style="font-size:0.72rem;">${escapeHtml(t.issue_type)}</span></td>"""

new_body = """                if (tickets.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:2rem; color:var(--text-muted);">Keine Jira Tickets vorhanden.</td></tr>`;
                    return;
                }

                tickets.forEach(t => {
                    const tr = document.createElement("tr");
                    const isQuestion = (t.summary || '').includes('[Rückfrage');
                    const prioClass = t.priority === 'High' ? 'badge-danger' : (t.priority === 'Medium' ? 'badge-engineer' : 'badge');
                    const statusClass = t.status === 'OPEN' ? 'badge-online' : 'badge';

                    tr.innerHTML = `
                        <td style="font-family: var(--font-mono); font-weight: 700; color: var(--blue);">
                            <a href="https://easy-eza.atlassian.net/browse/${escapeHtml(t.jira_key)}" target="_blank" style="color:inherit; text-decoration:none;">${escapeHtml(t.jira_key)}</a>
                            ${t.synced_with_jira ? '<span title="Mit Jira synchronisiert" style="color:var(--status-online); margin-left:4px;">☁️</span>' : '<span title="Lokale Warteschlange" style="color:var(--text-muted); margin-left:4px;">💾</span>'}
                        </td>
                        <td>
                            <a href="https://easy-eza.atlassian.net/browse/${escapeHtml(t.epic_key || 'EEP-94')}" target="_blank" style="text-decoration:none;" title="Übergeordnetes Epic: AI Continous improvement">
                                <span class="badge" style="background:#e9d8fd; color:#6b46c1; font-weight:600; font-size:0.72rem; cursor:pointer;">🟣 ${escapeHtml(t.epic_key || 'EEP-94')}</span>
                            </a>
                        </td>
                        <td><span class="badge ${isQuestion ? 'badge-super' : 'badge'}" style="font-size:0.72rem;">${escapeHtml(t.issue_type)}</span></td>"""

if old_body not in content:
    old_body = old_body.replace('\n', '\r\n')
    new_body = new_body.replace('\n', '\r\n')

assert old_body in content, "old_body not found in index.html"
content = content.replace(old_body, new_body, 1)

# 3. Add epic_key: 'EEP-94' to openCreateJiraTicketModal
old_modal = """                body: JSON.stringify({
                    summary: summary.trim(),
                    description: description ? description.trim() : "",
                    issue_type: "Task",
                    priority: "High"
                })"""

new_modal = """                body: JSON.stringify({
                    summary: summary.trim(),
                    description: description ? description.trim() : "",
                    issue_type: "Task",
                    priority: "High",
                    epic_key: "EEP-94"
                })"""

if old_modal not in content:
    old_modal = old_modal.replace('\n', '\r\n')
    new_modal = new_modal.replace('\n', '\r\n')

assert old_modal in content, "old_modal not found in index.html"
content = content.replace(old_modal, new_modal, 1)

with open('backend/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: index.html updated.")
