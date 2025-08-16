from typing import List, Dict, Tuple, Any

def create_grid(width: int, height: int,obstacles:List[Dict]) -> List[List[int]]:
    grid = []
    for _ in range(height):
        row = [1]*width
        grid.append(row)
    
    for obstacle in obstacles:
        ox,oy = obstacle['x'], obstacle['y']
        ow,oh = obstacle['width'], obstacle['height']

        y_start = max(0, oy)     
        y_end = min(height, oy + oh)
        x_start = max(0, ox)
        x_end = min(width, ox + ow)

        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                grid[y][x] = 0
    return grid

#function to find the zigzag path in a grid
def zigzag_path(grid: List[List[int]])-> List[Tuple[int,int]]:
    H, W = len(grid), len(grid[0])
    path = []
    for y in range(H):
        if y%2==0:
            x_range = range(W)
        else:
            x_range = range(W-1, -1, -1)
        for x in x_range:
            if grid[y][x] == 1:
                path.append((x, y))
    return path


#function to find free rectangles in a grid
def find_free_rectangles(grid:List[List[int]])-> List[Dict[str,int]]:
    rectangles = []
    H,W = len(grid), len(grid[0])
    visited = [[False]*W for _ in range(H)]

    for y in range(H):
        for x in range(W):
            if grid[y][x] ==1 and not visited[y][x]: 
                rect = {'x': x, 'y': y, 'width': 0, 'height': 0}
                # Find width
                while (x + rect['width'] < W and grid[y][x + rect['width']] == 1 and not visited[y][x + rect['width']]):
                    rect['width'] += 1
                # Find height
                while (y + rect['height'] < H and all(grid[y + rect['height']][x + w] == 1 and not visited[y + rect['height']][x + w] for w in range(rect['width']))):
                    rect['height'] += 1
                # Mark cells as visited
                for dy in range(rect['height']):
                    for dx in range(rect['width']):
                        visited[y + dy][x + dx] = True
            
                rectangles.append(rect)
    return rectangles

