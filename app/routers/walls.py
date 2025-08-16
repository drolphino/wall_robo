from fastapi import APIRouter, HTTPException
from app.models import WallInput
from app.planner import create_grid, find_free_rectangles
from app.database import crud

router = APIRouter()

@router.post("/add_wall")
def add_wall(data: WallInput):
    grid = create_grid(data.width, data.height, [ob.dict() for ob in data.obstacles])
    sections = find_free_rectangles(grid)
    wall_id = crud.insert_wall(data.width, data.height, [ob.dict() for ob in data.obstacles], sections)
    return {"message": "Wall added successfully", "wall_id": wall_id}

@router.get("/latest_wall")
def latest_wall():
    wall = crud.get_latest_wall()
    if not wall:
        raise HTTPException(status_code=404, detail="No wall found")
    return wall
