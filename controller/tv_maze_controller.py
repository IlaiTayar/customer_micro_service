from fastapi import APIRouter

from api.external_api.tv_maze import tv_maze_api
from api.external_api.tv_maze.model.tv_maze_show_response import TvMazeShowResponse

router: APIRouter = APIRouter(prefix="/tv_maze",
                              tags=["tv_maze"],)

@router.get("/get/show-{show_id}", response_model=TvMazeShowResponse, status_code=200)
async def get_show_by_id(show_id: int) -> TvMazeShowResponse:
    result: TvMazeShowResponse = await tv_maze_api.get_show_by_id(show_id)

    return result