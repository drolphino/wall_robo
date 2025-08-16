from .connection import get_connection

def insert_wall(width: int, height: int, obstacles: list[dict], sections: list[dict]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO walls (width, height) VALUES (?, ?)", (width, height))
    wall_id = cursor.lastrowid

    for ob in obstacles:
        cursor.execute(
            "INSERT INTO obstacles (wall_id, x, y, width, height) VALUES (?, ?, ?, ?, ?)",
            (wall_id, ob["x"], ob["y"], ob["width"], ob["height"])
        )

    for sec in sections:
        cursor.execute(
            "INSERT INTO wall_sections (wall_id, x, y, width, height) VALUES (?, ?, ?, ?, ?)",
            (wall_id, sec["x"], sec["y"], sec["width"], sec["height"])
        )

    conn.commit()
    conn.close()
    return wall_id

def get_latest_wall()-> dict|None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM walls ORDER BY id DESC LIMIT 1")
    wall = cursor.fetchone()
    if not wall:
        conn.close()
        return None

    wall_id, width, height = wall["id"], wall["width"], wall["height"]

    cursor.execute("SELECT x, y, width, height FROM obstacles WHERE wall_id=?", (wall_id,))
    obstacles = [{"x": r["x"], "y": r["y"], "width": r["width"], "height": r["height"]} for r in cursor.fetchall()]

    cursor.execute("SELECT x, y, width, height, id FROM wall_sections WHERE wall_id=?", (wall_id,))
    sections = [{"x": r["x"], "y": r["y"], "width": r["width"], "height": r["height"], "id": r["id"]} for r in cursor.fetchall()]

    conn.close()
    return {"wall_id": wall_id, "width": width, "height": height, "obstacles": obstacles, "rectangles": sections}

def save_section_trajectory(section_id: int, path: list[tuple]):
    conn = get_connection()
    cursor = conn.cursor()
    for seq, (x, y) in enumerate(path):
        cursor.execute(
            "INSERT INTO section_trajectories (section_id, seq, x, y) VALUES (?, ?, ?, ?)",
            (section_id, seq, x, y)
        )
    conn.commit()
    conn.close()
