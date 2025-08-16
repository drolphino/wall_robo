from .connection import get_connection

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS walls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        width INTEGER,
        height INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS obstacles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wall_id INTEGER NOT NULL,
        x INTEGER, y INTEGER, width INTEGER, height INTEGER,
        FOREIGN KEY(wall_id) REFERENCES walls(id)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_obstacles_wall ON obstacles(wall_id)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wall_sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wall_id INTEGER NOT NULL,
        x INTEGER, y INTEGER, width INTEGER, height INTEGER,
        FOREIGN KEY(wall_id) REFERENCES walls(id)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_wall ON wall_sections(wall_id)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS section_trajectories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_id INTEGER NOT NULL,
        seq INTEGER NOT NULL,
        x INTEGER NOT NULL,
        y INTEGER NOT NULL,
        FOREIGN KEY(section_id) REFERENCES wall_sections(id)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trajectories_section ON section_trajectories(section_id, seq)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT,
        method TEXT,
        request_time REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint)")

    conn.commit()
    conn.close()



if __name__ == "__main__":
    init_db()
    print("Database initialized!")
