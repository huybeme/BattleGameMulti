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
    num_bullets: int
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
        arcade.key.F: False,
    }


@dataclass_json
@dataclass
class GameInformation:
    level_switch: bool
    level_num: int
    player1_lives: int
    player1_score: int
    player2_lives: int
    player2_score: int
    barrel_list: list[list[int, int]]


@dataclass_json
@dataclass
class GameState:
    player_states: Dict[str, PlayerState]
    game_state: GameInformation
