# 🧱 Wall Coverage Planner

This project is a **coverage planning system** that:

- Defines walls, obstacles
- Calculate sections for a given wall
- Generates trajectories to cover the wall, sectionwise
- Logs API requests for monitoring

---

## 🚀 Setup Instructions

### 1. Create and activate virtual environment

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

Now visit 👉 [http://127.0.0.1:8000/static](http://127.0.0.1:8000/static)

### 4. Run tests

```bash
pytest -m tests/test_api.py
```

---

## 🗄 Database Schema

### Tables Overview

- **walls** → Stores wall dimensions
- **obstacles** → Linked to walls
- **wall_sections** → Divides walls into smaller sections
- **section_trajectories** → Stores trajectory points for each section
- **api_logs** → Tracks API usage

---

## 📊 ER Diagram

```
   ┌─────────────┐
   │    walls    │
   │ id (PK)     │
   │ width       │
   │ height      │
   │ created_at  │
   └──────┬──────┘
          │ 1-to-many
 ┌────────┴───────────┐
 │                    │
 ▼                    ▼
┌─────────────┐   ┌───────────────┐
│  obstacles  │   │ wall_sections │
│ id (PK)     │   │ id (PK)       │
│ wall_id (FK)│   │ wall_id (FK)  │
│ x,y,width,h │   │ x,y,width,h   │
└─────────────┘   └──────┬────────┘
                         │ 1-to-many
                         ▼
                  ┌───────────────────────┐
                  │ section_trajectories  │
                  │ id (PK)               │
                  │ section_id (FK)       │
                  │ seq, x, y             │
                  └───────────────────────┘


  ┌─────────────┐
  │  api_logs   │  (separate, for monitoring API calls)
  │ id (PK)     │
  │ endpoint    │
  │ method      │
  │ request_time│
  │ created_at  │
  └─────────────┘
```

---

## 🔄 End-to-End Flow

### A) Add a wall

1. Client → `/add_wall` with `{width, height, obstacles[]}`.
2. Server builds binary grid:
   - Initialize grid[h][w] = 1.
   - For each obstacle rectangle → mark covered cells = 0.
3. Find free rectangles:
   - Scan grid row by row, left → right.
   - On unvisited free cell, extend right for width, then down for height.
   - Mark rectangle as visited and save as section.
4. Persist to DB: `walls`, `obstacles`, `wall_sections`.
5. Return → `{"message": "Wall added successfully", "wall_id": ...}`.

### B) Fetch the latest wall

1. Query → `SELECT * FROM walls ORDER BY id DESC LIMIT 1` (fast PK lookup).
2. Load obstacles and wall_sections via `wall_id`.
3. Return → wall dimensions + sections + obstacles.

### C) Calculate trajectory for each section

1. Client → `/calculate_trajectory/{wall_id}`.
2. Load wall, sections, obstacles.
3. For each section:
   - Create local grid (width × height).
   - Subtract overlapping obstacles (global → local transform).
   - Run **snake_cover** algorithm.
   - Transform local path back to global coordinates.
   - Persist path in `section_trajectories`.
4. Compute metrics:
   - `total_cells_traversed` = sum of section paths.
   - `total_time_taken` = total_cells_traversed/2 (assumption robo covers 2 cells per unit time).
5. Return → trajectories + metrics.

---

## 🧮 Algorithmic Core (Math + Intuition)

### 1) Grid construction

- Wall = 2D grid of size `height × width`.
- Free cells = 1, Obstacle cells = 0.
- Complexity: **O(W×H + obstacle_area)**

### 2) Free-rectangle decomposition

- Start at free unvisited cell → expand right for width.
- Expand downward as long as rows match.
- Mark rectangle visited.
- Complexity: **O(W×H)** (each cell visited once).

### 3) Snake (boustrophedon) coverage

- Traverse section row by row:
  - Row 0: left → right
  - Row 1: right → left
  - Row 2: left → right …
- Guarantees full coverage with minimal turns.
- Complexity: **O(w×h)** per section.

### 4) Indices & query performance

- `walls` PK index → fast latest wall fetch.
- `obstacles(wall_id)` & `wall_sections(wall_id)` → **O(log n)** lookups.
- `section_trajectories(section_id, seq)` → fast ordered retrieval.

---
