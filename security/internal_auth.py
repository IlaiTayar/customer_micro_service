from typing import Optional

from fastapi import Header, HTTPException

from database import config


async def verify_internal_api_key(x_internal_api_key: Optional[str] = Header(default=None)) -> None:
    if x_internal_api_key != config.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: internal endpoint")
