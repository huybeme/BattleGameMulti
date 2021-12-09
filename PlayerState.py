import datetime
import arcade
from typing import Dict
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json     # the order of @ imports are important
@dataclass
class PlayerState:
    x_loc: float
    y_loc: float
    weapon_angle: float
    points: int
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
        arcade.key.SPACE: False
    }

    def __str__(self):
        return f"UP: {self.keys[arcade.key.UP]}, Down: {self.keys[arcade.key.DOWN]}" \
               f", Left: {self.keys[arcade.key.LEFT]}, Right: {self.keys[arcade.key.RIGHT]}, "


# @dataclass
# @dataclass_json
# class TargetState:
#     x_loc: int
#     y_loc: int


@dataclass_json
@dataclass
class GameState:
    player_states: Dict[str, PlayerState]
    # target: TargetState
