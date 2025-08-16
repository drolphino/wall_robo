from fastapi import APIRouter, HTTPException
from app.database import crud
from app.planner import create_grid, zigzag_path

router = APIRouter()

@router.get("/calculate_trajectory/{wall_id}")
def calculate_trajectory(wall_id: int, brush_size: int = 5):
    """
    Calculate trajectory for each section.
    Returns total cells traversed, total painting time, and section paths.
    """
    # Get wall
    wall = crud.get_latest_wall()
    if not wall or wall["wall_id"] != wall_id:
        raise HTTPException(status_code=404, detail="No wall found")

    sections = wall["rectangles"]
    section_paths = []

    # Processing sectionwise
    for sec in sections:
        sec_grid = create_grid(sec["width"], sec["height"], [])

        # Compute zigzag path
        path = zigzag_path(sec_grid)

        # Adjust section coordinates to wall coordinates
        adjusted_path = [(x + sec["x"], y + sec["y"]) for x, y in path]

        
        crud.save_section_trajectory(sec["id"], adjusted_path)
        section_paths.append({"section_id": sec["id"], "path": adjusted_path})

    # Step 3: Calculate total cells and painting time
    all_points = [p for s in section_paths for p in s["path"]]
    total_cells = len(all_points)

    # assumption  1 unit of time to paint 2 cells
    total_time = total_cells / 2

    return {
        "total_cells_traversed": total_cells,
        "total_time_units": total_time,
        "section_paths": section_paths
    }
