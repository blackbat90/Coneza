import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.auth import require_viewer
from backend.document_draft_routes import router


class DraftRouteTests(unittest.TestCase):
    def setUp(self):
        self.app=FastAPI()
        self.app.include_router(router)
        self.client=TestClient(self.app)

    def test_authentication_required(self):
        response=self.client.post('/api/pcu/document-draft')
        self.assertIn(response.status_code,(401,403))

    def test_upload_extracts_both_sources(self):
        self.app.dependency_overrides[require_viewer]=lambda: {'role':'VIEWER'}
        extraction={'success':True,'pages':[{'page_number':1,'text':'Wirkleistung: 75 kW'}]}
        with patch('backend.document_draft_routes.ocr_engine.extract_document',return_value=extraction) as extract:
            response=self.client.post('/api/pcu/document-draft',data={'grid_doc_type':'E9'},files={
                'sld_file':('SLD.pdf',b'%PDF-test','application/pdf'),
                'grid_doc_file':('E9.pdf',b'%PDF-test','application/pdf')})
        self.assertEqual(response.status_code,200)
        self.assertEqual(extract.call_count,2)
        self.assertFalse(response.json()['deployable'])
        self.assertEqual(response.json()['fields'][0]['sources'][1]['document_type'],'E9')

    def test_non_pdf_rejected_before_extraction(self):
        self.app.dependency_overrides[require_viewer]=lambda: {'role':'VIEWER'}
        with patch('backend.document_draft_routes.ocr_engine.extract_document') as extract:
            response=self.client.post('/api/pcu/document-draft',data={'grid_doc_type':'E8'},files={
                'sld_file':('SLD.pdf',b'not pdf'), 'grid_doc_file':('E8.pdf',b'not pdf')})
        self.assertEqual(response.status_code,422)
        extract.assert_not_called()

    def test_page_is_available(self):
        response=self.client.get('/pcu-draft')
        self.assertEqual(response.status_code,200)
        self.assertIn('PCU-Konfiguration',response.text)
