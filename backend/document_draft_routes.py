from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool
from backend.auth import require_viewer
from backend.document_draft import build_draft
from edge.ocr_engine import ocr_engine

router = APIRouter()
MAX_BYTES = 15 * 1024 * 1024


@router.get('/pcu-draft')
async def draft_page():
    return FileResponse(Path(__file__).parent / 'static' / 'pcu-draft.html')


@router.post('/api/pcu/document-draft')
async def document_draft(sld_file: UploadFile = File(...), grid_doc_file: UploadFile = File(...),
                         grid_doc_type: str = Form(...), user=Depends(require_viewer)):
    if grid_doc_type not in ('E8', 'E9'):
        raise HTTPException(422, 'Bitte E8 oder E9 auswählen')
    documents = []
    for kind, upload in [('SLD', sld_file), (grid_doc_type, grid_doc_file)]:
        data = await upload.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise HTTPException(413, 'Maximal 15 MB je Dokument')
        if not data.startswith(b'%PDF-'):
            raise HTTPException(422, 'Bitte gültige PDF-Dokumente hochladen')
        name = (upload.filename or kind + '.pdf').replace('\\', '/').split('/')[-1]
        extracted = await run_in_threadpool(ocr_engine.extract_document, data, name)
        documents.append(dict(type=kind, filename=name, extraction=extracted))
    return build_draft(documents, ocr_engine._extract_grid_entities)
