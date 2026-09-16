"""
coneza Linux Edge Webserver
Runs locally on industrial Linux edge devices (e.g. Phoenix Contact EPC / IPCs).
Receives E8, E9, and SLD documents, executes layout-robust OCR, syncs to backend,
and interacts directly with Phoenix Contact EZA controllers over Modbus TCP.
"""

import os
import io
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from edge.ocr_engine import ocr_engine
from edge.phoenix_eza.controller import PhoenixEZAControllerClient
from edge.phoenix_eza.simulator import PhoenixEZASimulator
from edge.backend_client import EdgeBackendClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("coneza_edge_server")

# Configuration from environment or defaults
CONTROLLER_HOST = os.getenv("EZA_CONTROLLER_HOST", "127.0.0.1")
CONTROLLER_PORT = int(os.getenv("EZA_CONTROLLER_PORT", "5502"))
BACKEND_URL = os.getenv("CONEZA_BACKEND_URL", "http://127.0.0.1:8080")
START_EMBEDDED_SIMULATOR = os.getenv("START_EMBEDDED_SIMULATOR", "true").lower() in ("true", "1", "yes")

# In-memory document store on edge
uploaded_documents: Dict[str, Any] = {}

# Instantiate services
controller_client = PhoenixEZAControllerClient(host=CONTROLLER_HOST, port=CONTROLLER_PORT)
backend_client = EdgeBackendClient(
    backend_url=BACKEND_URL,
    controller_host=CONTROLLER_HOST,
    controller_port=CONTROLLER_PORT
)
simulator = PhoenixEZASimulator(host="0.0.0.0", port=CONTROLLER_PORT) if START_EMBEDDED_SIMULATOR else None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting coneza edge webserver...")
    if simulator:
        logger.info(f"Starting built-in Phoenix Contact EZA Simulator on port {CONTROLLER_PORT}...")
        await simulator.start()
    
    backend_client.start()
    yield
    # Shutdown
    logger.info("Stopping coneza edge webserver...")
    await backend_client.stop()
    if simulator:
        await simulator.stop()

app = FastAPI(
    title="coneza Edge Webserver",
    description="Edge node webserver for receiving E8, E9, SLD files and controlling Phoenix Contact EZA-Regler",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory setup
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Request Models
class EZAConfigPayload(BaseModel):
    rated_active_power_kw: Optional[float] = None
    rated_apparent_power_kva: Optional[float] = None
    grid_voltage_nominal_volts: Optional[float] = None
    p_max_feed_in_limit_kw: Optional[float] = None
    p_setpoint_kw: Optional[float] = None
    p_ramp_rate_kw_per_sec: Optional[float] = None
    q_control_mode: Optional[int] = None
    cos_phi_setpoint: Optional[float] = None
    q_setpoint_kvar: Optional[float] = None
    q_u_curve: Optional[Dict[str, float]] = None
    p_f_droop: Optional[Dict[str, float]] = None
    protection: Optional[Dict[str, float]] = None
    verify: bool = True

@app.get("/api/device/info")
async def get_device_info():
    """Returns local edge gateway telemetry and system health."""
    conn_test = await controller_client.test_connection()
    return {
        "device_id": backend_client.device_id,
        "device_name": backend_client.device_name,
        "local_ip": backend_client.get_local_ip(),
        "backend_url": BACKEND_URL,
        "backend_sync_status": backend_client.last_sync_status,
        "controller_host": CONTROLLER_HOST,
        "controller_port": CONTROLLER_PORT,
        "controller_connected": conn_test.get("connected", False),
        "embedded_simulator_running": simulator is not None,
        "documents_cached_count": len(uploaded_documents)
    }

@app.post("/api/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type_hint: Optional[str] = Form(None)
):
    """
    Receives E8, E9, or SLD PDF documents, executes OCR layout extraction,
    and forwards to backend.
    """
    try:
        content = await file.read()
        filename = file.filename or "uploaded_document.pdf"
        
        # Execute OCR and layout extraction
        extracted_data = ocr_engine.extract_document(content, filename)
        if doc_type_hint and doc_type_hint in ("E8", "E9", "SLD"):
            extracted_data["detected_type"] = doc_type_hint

        doc_id = f"doc_{len(uploaded_documents) + 1}_{filename}"
        uploaded_documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "ocr_result": extracted_data,
            "synced_to_backend": False
        }

        # Background sync to backend
        async def sync_task():
            res = await backend_client.forward_document_to_backend(extracted_data, content, filename)
            if res:
                uploaded_documents[doc_id]["synced_to_backend"] = True
                uploaded_documents[doc_id]["backend_doc_id"] = res.get("id")

        background_tasks.add_task(sync_task)

        return {
            "status": "success",
            "document_id": doc_id,
            "filename": filename,
            "detected_type": extracted_data["detected_type"],
            "pages_processed": extracted_data["total_pages"],
            "extracted_entities": extracted_data["extracted_entities"],
            "backend_sync": "in_progress"
        }
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    """Lists locally processed E8, E9, and SLD documents."""
    return list(uploaded_documents.values())

@app.get("/api/controller/status")
async def get_controller_status():
    """Reads live measurements and operating state from Phoenix Contact EZA Controller."""
    try:
        telemetry = await controller_client.read_telemetry()
        return {"status": "success", "telemetry": telemetry}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/controller/config")
async def get_controller_configuration():
    """Reads active setpoints, Q(U) curves, and protection parameters from Phoenix Contact EZA."""
    try:
        config = await controller_client.read_active_configuration()
        return {"status": "success", "configuration": config}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/controller/configure")
async def configure_controller(payload: EZAConfigPayload):
    """
    Directly writes configuration parameters to Phoenix Contact EZA holding registers
    with read-back verification.
    """
    try:
        data = payload.model_dump(exclude_unset=True)
        verify = data.pop("verify", True)
        result = await controller_client.apply_configuration(data, verify=verify)
        return {"status": "success" if result["success"] else "verification_failed", "details": result}
    except Exception as e:
        logger.error(f"Configuration write failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/controller/trip")
async def emergency_trip_breaker():
    """Sends emergency trip command to circuit breaker via EZA controller."""
    try:
        from edge.phoenix_eza.register_map import HOLDING_REGISTERS
        await controller_client.write_holding_register(HOLDING_REGISTERS["REG_CMD_CIRCUIT_BREAKER"], 2)
        return {"status": "success", "command": "CIRCUIT_BREAKER_TRIPPED"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_edge_ui():
    """Serves the local edge control panel."""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    index_file = os.path.join(templates_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>coneza Edge Webserver Active</h1><p>Visit /docs for API schema.</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
