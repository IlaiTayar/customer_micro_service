import httpx
from typing import Any, Dict

from fastapi import HTTPException

from api.external_api.tv_maze.model.tv_maze_show_response import TvMazeShowResponse
from database import config


async def _get_from_tv_maze(url: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)

    except (httpx.ConnectError, httpx.TimeoutException) as err:
        raise HTTPException(
            status_code=503,
            detail=f"TVmaze service unavailable: {err}"
        )

    except httpx.HTTPError as err:
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with TVmaze: {err}"
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="TVmaze resource not found"
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail="TVmaze returned an error"
        )

    return response.json()


async def get_show_by_id(show_id: int) -> TvMazeShowResponse:
    url = f"{config.TV_MAZE_BASE_URL}/shows/{show_id}"
    data = await _get_from_tv_maze(url)

    image = data.get("image") or {}

    return TvMazeShowResponse(
        tv_show_id=data["id"],
        tv_show_name=data["name"],
        tv_show_url=data.get("officialSite"),
        tv_show_language=data.get("language"),
        tv_show_description=data.get("summary"),
        tv_show_image_original_url=image.get("original"),
    )
