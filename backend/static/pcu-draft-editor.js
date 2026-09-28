/* Manual draft annotations never replace extracted evidence or grant approval. */
(function (root) {
    'use strict';
    function annotate(draft, key, value, note) {
        if (!draft || !Array.isArray(draft.fields) || !draft.fields.some(field => field.key === key)) {
            throw new Error('Unbekanntes Entwurfsfeld');
        }
        if (typeof value !== 'string' || typeof note !== 'string' || value.length > 2000 || note.length > 2000) {
            throw new Error('Ergänzung und Begründung dürfen jeweils maximal 2000 Zeichen enthalten');
        }
        const result = JSON.parse(JSON.stringify(draft));
        result.status = 'DRAFT';
        result.deployable = false;
        result.manual_overrides = (result.manual_overrides || []).filter(item => item.key !== key);
        if (value.trim() || note.trim()) {
            result.manual_overrides.push({key, value: value.trim(), note: note.trim(),
                origin: 'manual', status: 'unreviewed'});
        }
        return result;
    }
    if (typeof module !== 'undefined' && module.exports) module.exports = {annotate};
    else root.PcuDraftEditor = {annotate};
})(typeof window === 'undefined' ? globalThis : window);
