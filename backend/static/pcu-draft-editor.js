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
    function restore(text) {
        if (typeof text !== 'string' || text.length > 1024 * 1024) throw new Error('Entwurf ist zu groß');
        const data = JSON.parse(text);
        if (data && data.schema_version !== undefined && data.schema_version !== 1) {
            throw new Error('Diese Entwurfsformat-Version wird nicht unterstützt');
        }
        const fail = () => { throw new Error('Ungültiger Dokumentenentwurf'); };
        const string = value => typeof value === 'string' && value.length <= 10000;
        const value = item => item === null || string(item) || (typeof item === 'number' && Number.isFinite(item)) ||
            (Array.isArray(item) && item.length <= 200 && item.every(string));
        if (!data || !Array.isArray(data.fields) || !data.fields.length || data.fields.length > 200) fail();
        const keys = new Set();
        const fields = data.fields.map(field => {
            if (!field || !string(field.key) || !field.key || keys.has(field.key) || !string(field.label) ||
                !string(field.unit) || !value(field.value) || !['missing','conflict','unreviewed'].includes(field.status) ||
                !Array.isArray(field.sources) || field.sources.length > 1000) fail();
            keys.add(field.key);
            const sources = field.sources.map(source => {
                if (!source || !value(source.value) || !string(source.document) ||
                    !['SLD','E8','E9'].includes(source.document_type) ||
                    !(source.page === null || (Number.isInteger(source.page) && source.page > 0))) fail();
                return {value:source.value, document:source.document, document_type:source.document_type, page:source.page};
            });
            const values = [...new Set(sources.map(source => JSON.stringify(source.value)))];
            const expectedStatus = values.length === 0 ? 'missing' : values.length === 1 ? 'unreviewed' : 'conflict';
            const expectedValue = values.length === 1 ? values[0] : 'null';
            if (field.status !== expectedStatus || JSON.stringify(field.value) !== expectedValue) fail();
            return {key:field.key,label:field.label,unit:field.unit,value:field.value,status:field.status,sources};
        });
        if (data.documents !== undefined && (!Array.isArray(data.documents) || data.documents.length > 2)) fail();
        const documents = (data.documents || []).map(document => {
            if (!document || !['SLD','E8','E9'].includes(document.type) || !string(document.filename)) fail();
            return {type:document.type, filename:document.filename};
        });
        if (data.warnings !== undefined && (!Array.isArray(data.warnings) ||
            data.warnings.length > 1000 || !data.warnings.every(string))) fail();
        const warnings = [...new Set([...(data.warnings || []),
            'Aus lokaler Datei geöffnet. Dokumentquellen und Ergänzungen sind nicht erneut geprüft.'])];
        let result = {schema_version:1,status:'DRAFT',deployable:false,fields,documents,warnings,
            notice:'Importierter, ungeprüfter Entwurf. Keine Freigabe und keine Geräteübertragung.'};
        if (data.manual_overrides !== undefined && !Array.isArray(data.manual_overrides)) fail();
        const edited = new Set();
        for (const entry of data.manual_overrides || []) {
            if (!entry || edited.has(entry.key)) fail();
            edited.add(entry.key);
            result = annotate(result, entry.key, entry.value, entry.note);
        }
        return result;
    }
    if (typeof module !== 'undefined' && module.exports) module.exports = {annotate, restore};
    else root.PcuDraftEditor = {annotate, restore};
})(typeof window === 'undefined' ? globalThis : window);
