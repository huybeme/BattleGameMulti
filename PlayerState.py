import datetime
import arcade
from typing import Dict
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json  # the order of @ imports are important
@dataclass
class PlayerState:
    id: int
    x_loc: float
    y_loc: float
    points: int
    face_angle: int
    weapon_angle: float
    shooting: bool
    last_update: datetime.datetime



@dataclass_json
@dataclass
class PlayerMovement:
    keys = {
        arcade.key.UP: False,
        arcade.key.DOWN: False,
        arcade.key.LEFT: False,
        arcade.key.RIGHT: False,

        arcade.key.W: False,
        arcade.key.S: False,
        arcade.key.A: False,
        arcade.key.D: False,
        arcade.key.E: False,
        arcade.key.SPACE: False
    }

    def __str__(self):
        return f"UP: {self.keys[arcade.key.UP]}, Down: {self.keys[arcade.key.DOWN]}" \
               f", Left: {self.keys[arcade.key.LEFT]}, Right: {self.keys[arcade.key.RIGHT]}, "


@dataclass_json
@dataclass
class GameState:
    player_states: Dict[str, PlayerState]
    # target: TargetState
