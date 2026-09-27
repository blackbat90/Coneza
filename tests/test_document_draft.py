import unittest
from backend.document_draft import build_draft


class DraftTests(unittest.TestCase):
    def documents(self, a, b):
        return [dict(type=kind, filename=kind+'.pdf', extraction=dict(success=True,
            pages=[dict(page_number=1, text=text)])) for kind,text in [('SLD',a),('E8',b)]]

    def test_missing_values_are_not_defaulted(self):
        draft=build_draft(self.documents('', ''), lambda text, kind: {})
        self.assertFalse(draft['deployable'])
        self.assertTrue(all(f['value'] is None and f['status']=='missing' for f in draft['fields']))
        self.assertEqual(len(draft['warnings']), 2)

    def test_conflicting_sources_preserved_without_winner(self):
        draft=build_draft(self.documents('75','100'), lambda text,kind: {'active_power_kw':float(text)})
        field=draft['fields'][0]
        self.assertEqual(field['status'],'conflict')
        self.assertIsNone(field['value'])
        self.assertEqual([s['value'] for s in field['sources']],[75,100])

    def test_agreement_remains_unreviewed_and_source_linked(self):
        draft=build_draft(self.documents('75','75'), lambda text,kind: {'active_power_kw':float(text)})
        field=draft['fields'][0]
        self.assertEqual(field['value'],75)
        self.assertEqual(field['status'],'unreviewed')
        self.assertEqual(field['sources'][0]['page'],1)
        self.assertEqual(field['sources'][1]['document'],'E8.pdf')
        self.assertIsNone(next(f for f in draft['fields'] if f['key']=='p_setpoint_kw')['value'])

    def test_invalid_document_pair_rejected(self):
        with self.assertRaises(ValueError):build_draft([], lambda text,kind: {})
