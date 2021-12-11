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
    face_angle: int
    weapon_angle: float
    shooting: bool
    weapon_shooting: bool
    last_update: datetime.datetime
    bullet_delay: datetime.datetime



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
        arcade.key.SPACE: False,
        arcade.key.F: False
    }

@dataclass_json
@dataclass
class ItemState:
    x_loc: int
    y_loc: int
    rand_power_up: int
    present: bool
    item_delay: datetime.datetime

@dataclass_json
@dataclass
class GameState:
    player_states: Dict[str, PlayerState]
    item: ItemState
