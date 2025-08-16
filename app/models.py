from pydantic import BaseModel
from typing import List

class Obstacle(BaseModel):
    x:      int
    y:      int
    width:  int
    height: int


class WallInput(BaseModel):
    width:     int
    height:    int
    obstacles: List[Obstacle]