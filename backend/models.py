"""
Pydantic schema models for coneza Central Backend.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "VIEWER"  # SUPER_ADMIN, ENGINEER, VIEWER

class UserLogin(BaseModel):
    username: str
    password: str

class UserRoleUpdate(BaseModel):
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

class DeviceRegister(BaseModel):
    device_id: str
    name: str
    local_ip: str
    os_platform: Optional[str] = None
    controller_host: Optional[str] = "127.0.0.1"
    controller_port: Optional[int] = 5502

class DeviceHeartbeat(BaseModel):
    device_id: str
    local_ip: str
    controller_connected: bool
    controller_state: str
    telemetry: Optional[Dict[str, Any]] = None

class DeviceResponse(BaseModel):
    device_id: str
    name: str
    local_ip: str
    os_platform: Optional[str]
    controller_host: Optional[str]
    controller_port: Optional[int]
    status: str
    controller_state: str
    last_heartbeat: Optional[str]
    telemetry: Optional[Dict[str, Any]]

class DocumentResponse(BaseModel):
    id: str
    device_id: Optional[str]
    doc_type: str
    filename: str
    created_at: str
    ocr_entities: Optional[Dict[str, Any]]

class AnalysisTrigger(BaseModel):
    device_id: str
    document_ids: List[str]

class ConfigApproval(BaseModel):
    config_id: str
    approved: bool

class ConfigDeployRequest(BaseModel):
    config_id: str
    target_device_id: str
