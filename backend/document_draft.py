"""Source-linked PCU draft. No defaults, approval, persistence or device writes."""
import math

# Application configuration fields, not a verified manufacturer's register map.
FIELDS = [
    ('rated_active_power_kw', 'Wirkleistung der Anlage', 'kW', 'active_power_kw'),
    ('rated_apparent_power_kva', 'Scheinleistung der Anlage', 'kVA', 'apparent_power_kva'),
    ('grid_voltage_nominal_volts', 'Nennspannung am Netzanschluss', 'V', 'grid_voltage_v'),
    ('grid_frequency_nominal_hz', 'Nennfrequenz', 'Hz', None),
    ('p_max_feed_in_limit_kw', 'Zulässige Einspeiseleistung', 'kW', None),
    ('p_setpoint_kw', 'Wirkleistungssollwert', 'kW', None),
    ('p_ramp_rate_kw_per_sec', 'Wirkleistungsrampe', 'kW/s', None),
    ('q_control_mode', 'Blindleistungsverfahren', '', 'reactive_mode'),
    ('cos_phi_setpoint', 'Leistungsfaktor-Sollwert', '', 'cos_phi'),
    ('q_setpoint_kvar', 'Blindleistungssollwert', 'kvar', None),
    *[(f'q_u_curve.{k}{i}_percent', f'Q(U) Punkt {i}: {label}', '%', None)
      for i in range(1, 5) for k, label in [('u', 'Spannung'), ('q', 'Blindleistung')]],
    ('p_f_droop.overfreq_start_hz', 'P(f): Beginn Überfrequenz', 'Hz', None),
    ('p_f_droop.overfreq_droop_percent', 'P(f): Statik Überfrequenz', '%', None),
    ('p_f_droop.underfreq_start_hz', 'P(f): Beginn Unterfrequenz', 'Hz', None),
    ('p_f_droop.underfreq_droop_percent', 'P(f): Statik Unterfrequenz', '%', None),
    *[(f'protection.{key}', label, unit, None) for key, label, unit in [
        ('u_max_percent', 'Obere Spannungsgrenze', '%'), ('u_max_trip_ms', 'Verzögerung Überspannung', 'ms'),
        ('u_min_percent', 'Untere Spannungsgrenze', '%'), ('u_min_trip_ms', 'Verzögerung Unterspannung', 'ms'),
        ('f_max_hz', 'Obere Frequenzgrenze', 'Hz'), ('f_min_hz', 'Untere Frequenzgrenze', 'Hz')]],
    ('grid_operator', 'Netzbetreiber', '', None), ('connection_point', 'Netzanschlusspunkt', '', None),
    ('equipment', 'Geräte und Zuordnung', '', 'detected_equipment_tags'),
    ('meter_mapping', 'Messgerät, Wandler und Vorzeichen', '', None),
    ('communications', 'Adressen und Kommunikationsparameter', '', None),
    ('failure_behavior', 'Verhalten bei Kommunikationsausfall', '', None),
    ('pcu_interface', 'PCU-Modell, Firmware und Registerversion', '', None),
]


def build_draft(documents, extract_entities):
    if len(documents) != 2 or documents[0]['type'] != 'SLD' or documents[1]['type'] not in ('E8', 'E9'):
        raise ValueError('SLD und E8 oder E9 erforderlich')
    observations = []
    warnings = []
    for doc in documents:
        if not doc['extraction'].get('success'):
            warnings.append(f"{doc['filename']}: Dokument konnte nicht gelesen werden")
        for page in doc['extraction'].get('pages', []):
            text = page.get('text', '')
            observations.append((doc, page.get('page_number'), extract_entities(text, doc['type'])))
            # The legacy extractor returns the first match per entity. Inspect
            # individual lines too, preserving page-wide extraction for wrapped values.
            for line in text.splitlines():
                if line.strip() and line.strip() != text.strip():
                    observations.append((doc, page.get('page_number'), extract_entities(line, doc['type'])))
        if not any(p.get('text', '').strip() for p in doc['extraction'].get('pages', [])):
            warnings.append(f"{doc['filename']}: Kein auswertbarer Text; OCR oder manuelle Ergänzung erforderlich")
    rows = []
    for key, label, unit, entity in FIELDS:
        candidates = []
        for doc, page, entities in observations:
            value = entities.get(entity) if entity else None
            if value is None or value == '' or value == []:
                continue
            if isinstance(value, float) and not math.isfinite(value):
                continue
            candidate = dict(value=value, document=doc['filename'], document_type=doc['type'], page=page)
            if candidate not in candidates:
                candidates.append(candidate)
        unique = []
        for candidate in candidates:
            if candidate['value'] not in unique:
                unique.append(candidate['value'])
        state = 'missing' if not unique else 'conflict' if len(unique) > 1 else 'unreviewed'
        rows.append(dict(key=key, label=label, unit=unit, status=state,
                         value=unique[0] if len(unique) == 1 else None, sources=candidates))
    return dict(status='DRAFT', deployable=False, fields=rows, warnings=warnings,
                documents=[dict(type=d['type'], filename=d['filename']) for d in documents],
                notice='Dokumentenentwurf: erkannte Angaben prüfen. Keine Freigabe, keine Übertragung. '
                       'Felder entsprechen dem Softwaremodell; keine vollständige Phoenix-Registerkompatibilität bestätigt.')
