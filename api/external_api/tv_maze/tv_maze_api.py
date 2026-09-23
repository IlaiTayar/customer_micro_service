from typing import Optional
from api.external_api.tv_maze.model.tv_maze_show_response import TvMazeShowResponse
import httpx
from database import config


async def get_show_by_id(show_id: int) -> Optional[TvMazeShowResponse]:
    url = f"{config.TV_MAZE_BASE_URL}/shows/{show_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        data = response.json()
        tv_show_response = TvMazeShowResponse(tv_show_id=data["id"],
                                              tv_show_name=data["name"],
                                              tv_show_url=data["officialSite"],
                                              tv_show_language=data["language"],
                                              tv_show_description=data["summary"],
                                              tv_show_image_original_url=data["image"]["original"])

        return tv_show_response