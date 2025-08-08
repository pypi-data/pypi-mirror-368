from pydantic import BaseModel
from typing import Any, Dict

class FaceAuthResponse(BaseModel):
    user_id: int
    is_new_user: bool
    custom_fields: Dict[str, Any] | None = None