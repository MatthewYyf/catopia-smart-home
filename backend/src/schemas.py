from pydantic import BaseModel
from typing import Optional, Dict

class Command(BaseModel):
    id: str
    type: str
    params: Optional[Dict] = None

class Telemetry(BaseModel):
    sensor: Optional[Dict] = None
    state: Optional[Dict] = None