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
    totp_code: Optional[str] = None

class TwoFactorVerifyLogin(BaseModel):
    temp_token: str
    totp_code: str

class TwoFactorEnableRequest(BaseModel):
    totp_code: str

class TwoFactorDisableRequest(BaseModel):
    password: str
    totp_code: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    new_password: str
    old_password: Optional[str] = None
    temp_token: Optional[str] = None

class UserRoleUpdate(BaseModel):
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_2fa_enabled: Optional[int] = 0
    must_change_password: Optional[int] = 0


class DeviceRegister(BaseModel):
    device_id: str
    name: str
    local_ip: str
    plant_id: Optional[str] = None
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
    plant_id: Optional[str] = None
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
    plant_id: Optional[str] = None
    device_id: Optional[str] = None
    doc_type: str
    filename: str
    created_at: str
    ocr_entities: Optional[Dict[str, Any]] = None

class PlantCreate(BaseModel):
    name: str
    site_type: str = "PV"  # PV, BESS, WIND, HYBRID
    grid_operator: str = "Bayernwerk Netz GmbH"
    voltage_level: str = "MS_4110"  # MS_4110, HS_4120, NS_4105
    installed_capacity_kw: float = 0.0
    grid_connection_point: Optional[str] = None
    location: Optional[str] = None
    commissioning_date: Optional[str] = None
    status: Optional[str] = "PLANNING"
    notes: Optional[str] = None
    initial_device_id: Optional[str] = None

class PlantUpdate(BaseModel):
    name: Optional[str] = None
    site_type: Optional[str] = None
    grid_operator: Optional[str] = None
    voltage_level: Optional[str] = None
    installed_capacity_kw: Optional[float] = None
    grid_connection_point: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class PlantAssignDevice(BaseModel):
    device_id: str

class PlantResponse(BaseModel):
    id: str
    name: str
    site_type: str
    grid_operator: str
    voltage_level: str
    installed_capacity_kw: float
    grid_connection_point: Optional[str]
    location: Optional[str]
    commissioning_date: Optional[str]
    status: str
    notes: Optional[str]
    created_by: Optional[str]
    created_at: str
    device_count: int = 0
    document_count: int = 0

class AnalysisTrigger(BaseModel):
    device_id: str
    document_ids: List[str]
    plant_id: Optional[str] = None

class ConfigApproval(BaseModel):
    config_id: str
    approved: bool

class ConfigDeployRequest(BaseModel):
    config_id: str
    target_device_id: str

