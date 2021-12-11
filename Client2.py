import datetime
import arcade
import threading
import asyncio
import socket
import json
import PlayerState
import math
from typing import List
from random import randint
import pathlib

CLIENT_ADDR = None
SERVER_ADDR = None
SERVER_PORT = None

# ----@@@@--    CONSTANTS    --@@@@-------------------------------------------------//

# TITLE
SCREEN_TITLE = "Project 2 - Battle Ships"

# PIXEL SIZES & MULTIPLIERS
SPRITE_IMAGE_SIZE = 32
SPRITE_SCALING_PLAYER = 0.75
SPRITE_SCALING_ENEMY = 1
SPRITE_SCALING_TILES = 2
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

# SCREEN DIMENSIONS in BLOCKS
SCREEN_GRID_WIDTH = 35
SCREEN_GRID_HEIGHT = 25

# PIXEL SIZE of SCREEN
SCREEN_WIDTH = SCREEN_GRID_WIDTH * SPRITE_IMAGE_SIZE
SCREEN_HEIGHT = SCREEN_GRID_HEIGHT * SPRITE_IMAGE_SIZE

# PHYSICS CONSTANTS
PLAYER_MOV_SPEED = 1.3
PLAYER_SHOOT_SPEED = 10

# ELEMENT LAYERS TO BE USED
LAYER_WATER = "Water"
LAYER_BACKGROUND = "Background"
LAYER_PLAYER = "Player"
LAYER_ENEMIES = "Enemies"
LAYER_SHOTS = "Shots"
LAYER_MOVEABLES = "Moveables"
LAYER_ITEMS = "Items"


class WeaponSprite(arcade.Sprite):
    def __init__(self, img_path: str, scale: float):
        super().__init__(img_path)
        self.scale = scale

    def update(self):
        self.angle += self.change_angle


class BulletSprite(arcade.Sprite):
    def __init__(self, img_path: str, speed: int, scale: float, game_window):
        super().__init__(img_path)
        self.speed = speed
        self.scale = scale
        self.game = game_window
        self.player_id = 0


class SpriteSheet(arcade.Sprite):
    def __init__(
            self,
            folder: str,
            fn: str,
            x_px: int,
            y_px: int,
            col: int,
            num_sprites: int,
            num_files,
    ):
        super().__init__()
        self.folder = folder
        self.filename = fn
        self.x_px = x_px
        self.y_px = y_px
        self.col = col
        self.num_sprites = num_sprites
        self.num_files = num_files


# <><><>----- PLAYER CLASS  -------------------------------------------------------------------------<><><>
class Player(arcade.Sprite):
    def __init__(
            self, img_path: str, scale: float, lives: int, id: int, sheet: SpriteSheet, face: int
    ):
        super().__init__(img_path)
        self.score = 0
        self.scale = scale
        self.num_bullets = 3
        self.player_id = id
        self.lives = lives
        self.level_reset = False
        self.is_shooting = False
        self.is_cannon_shooting = False
        self.face_angle = face  # since we start off facing up
        self.weapon = WeaponSprite("./Assets/Player/cannon.png", 0.25)

        # facing directions
        self.direction = [False, False, False, False]  # up, left, down, right
        self.spritesheet = None

        self.sheet = sheet
        self.sheet_0 = []
        self.sheet_45 = []
        self.sheet_90 = []
        self.sheet_135 = []
        self.sheet_180 = []
        self.sheet_225 = []
        self.sheet_270 = []
        self.sheet_315 = []
        for sprites in range(self.sheet.num_files):
            self.sheet_0.append(
                arcade.load_spritesheet(
                    f"Assets/Player/{self.sheet.folder}/{self.sheet.filename}_{sprites}.png",
                    self.sheet.x_px,
                    self.sheet.y_px,
                    self.sheet.col,
                    self.sheet.num_sprites,
                )[2]
            )
            self.sheet_45.append(
                arcade.load_spritesheet(
                    f"Assets/Player/{self.sheet.folder}/{self.sheet.filename}_{sprites}.png",
                    self.sheet.x_px,
                    self.sheet.y_px,
                    self.sheet.col,
                    self.sheet.num_sprites,
                )[3]
            )
            self.sheet_90.append(
                arcade.load_spritesheet(
                    f"Assets/Player/{self.sheet.folder}/{self.sheet.filename}_{sprites}.png",
                    self.sheet.x_px,
                    self.sheet.y_px,
                    self.sheet.col,
                    self.sheet.num_sprites,
                )[4]
            )
            self.sheet_135.append(
                arcade.load_spritesheet(
                    f"Assets/Player/{self.sheet.folder}/{self.sheet.filename}_{sprites}.png",
                    self.sheet.x_px,
                    self.sheet.y_px,
                    self.sheet.col,
                    self.sheet.num_sprites,
                )[5]
            )
            self.sheet_180.append(
                arcade.load_spritesheet(
                    f"Assets/Player/{self.sheet.folder}/{self.sheet.filename}_{sprites}.png",
                    self.sheet.x_px,
                    self.sheet.y_px,
                    self.sheet.col,
                    self.sheet.num_sprites,
                )[6]
            )
            self.sheet_225.append(
                arcade.load_spritesheet(
                    f"Assets/Player/{self.sheet.folder}/{self.sheet.filename}_{sprites}.png",
                    self.sheet.x_px,
                    self.sheet.y_px,
                    self.sheet.col,
                    self.sheet.num_sprites,
                )[7]
            )
            self.sheet_270.append(
                arcade.load_spritesheet(
                    f"Assets/Player/{self.sheet.folder}/{self.sheet.filename}_{sprites}.png",
                    self.sheet.x_px,
                    self.sheet.y_px,
                    self.sheet.col,
                    self.sheet.num_sprites,
                )[0]
            )
            self.sheet_315.append(
                arcade.load_spritesheet(
                    f"Assets/Player/{self.sheet.folder}/{self.sheet.filename}_{sprites}.png",
                    self.sheet.x_px,
                    self.sheet.y_px,
                    self.sheet.col,
                    self.sheet.num_sprites,
                )[1]
            )
        self.current_texture = 0

    def update_animation(self, delta_time: float = 1 / 60):
        update_per_frame = 2

        if self.change_x < 0 and self.change_y > 0:  # up left
            self.face_angle = 135
            self.animation(self.sheet_135, update_per_frame)
        elif self.change_x > 0 and self.change_y > 0:  # up right
            self.face_angle = 45
            self.animation(self.sheet_45, update_per_frame)
        elif self.change_x < 0 and self.change_y < 0:  # down left
            self.face_angle = 225
            self.animation(self.sheet_225, update_per_frame)
        elif self.change_x > 0 and self.change_y < 0:  # down right
            self.face_angle = 315
            self.animation(self.sheet_315, update_per_frame)
        elif self.change_x == 0 and self.change_y > 0:  # up
            self.face_angle = 90
            self.animation(self.sheet_90, update_per_frame)
        elif self.change_x < 0 and self.change_y == 0:  # left
            self.face_angle = 180
            self.animation(self.sheet_180, update_per_frame)
        elif self.change_x == 0 and self.change_y < 0:  # down
            self.face_angle = 270
            self.animation(self.sheet_270, update_per_frame)
        elif self.change_x > 0 and self.change_y == 0:  # right
            self.face_angle = 0
            self.animation(self.sheet_0, update_per_frame)

        if self.face_angle == 135:  # up left
            self.animation(self.sheet_135, update_per_frame)
        elif self.face_angle == 45:  # up right
            self.animation(self.sheet_45, update_per_frame)
        elif self.face_angle == 225:  # down left
            self.animation(self.sheet_225, update_per_frame)
        elif self.face_angle == 315:  # down right
            self.animation(self.sheet_315, update_per_frame)
        elif self.face_angle == 90:  # up
            self.animation(self.sheet_90, update_per_frame)
        elif self.face_angle == 180:  # left
            self.animation(self.sheet_180, update_per_frame)
        elif self.face_angle == 270:  # down
            self.animation(self.sheet_270, update_per_frame)
        elif self.face_angle == 0:  # right
            self.animation(self.sheet_0, update_per_frame)


    def animation(self, sheet, update):
        self.current_texture += 1
        if self.current_texture > 7 * update:
            self.current_texture = 0
        frame = self.current_texture // 5
        self.texture = sheet[frame]


class MoveableSprite(arcade.Sprite):
    def __init__(self, image: str, scale: float, center_x: int, center_y: int):
        super().__init__(image)
        self.scale = scale
        self.center_x = center_x
        self.center_y = center_y


class PowerUpSprite(arcade.Sprite):
    def __init__(
            self,
            image: str,
            scale: float,
            center_x: int,
            center_y: int,
            effect: str,
            color: arcade.color,
    ):
        super().__init__(image)
        self.scale = scale
        self.center_x = center_x
        self.center_y = center_y
        self.effect = effect
        self.color = color


# ------- MAIN GAME CLASS ----------------------------------------------------------------V
class TiledWindow(arcade.Window):
    def __init__(self, client_addr, server_addr, server_port):
        # Parent class call
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Multiplayer Networking
        self.ip_addr = client_addr
        self.server_address = server_addr
        self.server_port = server_port
        self.actions = PlayerState.PlayerMovement()
        #self.player_actions = PlayerState.PlayerState(
           # id=0, x_loc=0, y_loc=0, face_angle=0,weapon_angle=0,
            #shooting=False, weapon_shooting=False,
            #level_reset=False, last_update=datetime.datetime.now(),
            #bullet_delay=datetime.datetime.now())
        self.from_server = ""

        self.round = 1
        self.game_frame = 0
        self.restart_tick = 5

        layer_options = {
            "Water": {"use_spatial_hash": True},
            "Beach": {"use_spatial_hash": True},
            "Ice": {"use_spatial_hash": True},
            "Lower_Decorative": {"use_spatial_hash": True},
            "Solids": {"use_spatial_hash": True},
            "Upper_Decorative": {"use_spatial_hash": True},
        }

        self.map_1_location = pathlib.Path.cwd() / "Assets/Battle_Ships_Map_1.json"
        self.map_2_location = pathlib.Path.cwd() / "Assets/Battle_Ships_Map_2.json"
        self.map_3_location = pathlib.Path.cwd() / "Assets/Battle_Ships_Map_3.json"

        self.tile_map1 = arcade.load_tilemap(
            self.map_1_location,
            layer_options=layer_options,
            scaling=SPRITE_SCALING_TILES,
        )
        self.tile_map2 = arcade.load_tilemap(
            self.map_2_location,
            layer_options=layer_options,
            scaling=SPRITE_SCALING_TILES,
        )
        self.tile_map3 = arcade.load_tilemap(
            self.map_3_location,
            layer_options=layer_options,
            scaling=SPRITE_SCALING_TILES,
        )
        self.wall_list = self.tile_map1.sprite_lists["Solids"]
        self.beach_tile_list = self.tile_map1.sprite_lists["Beach"]
        self.water_tile_list = self.tile_map1.sprite_lists["Water"]

        self.map_scene = arcade.Scene.from_tilemap(self.tile_map1)

        # player setup
        player_1_ss = SpriteSheet("ship_sheets", "shipsheet", 128, 128, 4, 8, 7)
        self.player_1 = Player(
            "./Assets/Player/pirateship.png",
            SPRITE_SCALING_PLAYER,
            lives=5,
            id=1,
            sheet=player_1_ss,
            face=90
        )
        self.player_1.set_position(80, 80)
        self.physics_engine_wall_p1 = arcade.PhysicsEngineSimple(
            self.player_1, self.wall_list
        )
        self.player_1.weapon.set_position(
            self.player_1.center_x, self.player_1.center_y
        )

        player_2_ss = SpriteSheet("lapras_sheet", "lapras_sheet", 95, 95, 4, 8, 3)
        self.player_2 = Player(
            "./Assets/Player/lapras_start.png", 1, lives=5, id=2, sheet=player_2_ss,
            face=270
        )
        self.physics_engine_wall_p2 = arcade.PhysicsEngineSimple(
            self.player_2, self.wall_list
        )
        self.player_2.set_position(SCREEN_WIDTH - 64, SCREEN_HEIGHT - 64)
        self.player_2.weapon.set_position(
            self.player_2.center_x, self.player_2.center_y
        )

        # lists
        self.player_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.weapon_list = arcade.SpriteList()
        self.power_up_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.barrel_list = arcade.SpriteList()

        self.player_list.append(self.player_1)
        self.player_list.append(self.player_2)
        self.weapon_list.append(self.player_1.weapon)
        self.weapon_list.append(self.player_2.weapon)

        self.pre_whirlpool_list = arcade.SpriteList()
        # self.whirlpool_sprite = None
        self.post_whirlpool_list = arcade.SpriteList()
        self.post_whirlpool_sprite = None

        # MAP 1
        self.barrel_1 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=285,
            center_y=340,
        )
        self.barrel_2 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=SCREEN_WIDTH - 285,
            center_y=SCREEN_HEIGHT - 340,
        )
        self.barrel_3 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=560,
            center_y=660,
        )
        self.barrel_4 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=SCREEN_WIDTH - 560,
            center_y=SCREEN_HEIGHT - 660,
        )

        # MAP 2
        self.barrel_5 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=400,
            center_y=400,
        )
        self.barrel_6 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=SCREEN_WIDTH - 380,
            center_y=400,
        )
        self.barrel_7 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=200,
            center_y=300,
        )
        self.barrel_8 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=SCREEN_WIDTH - 200,
            center_y=SCREEN_HEIGHT - 300,
        )
        self.barrel_9 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=SCREEN_WIDTH - 100,
            center_y=100,
        )
        self.barrel_10 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=100,
            center_y=SCREEN_HEIGHT - 100,
        )

        # MAP 3
        self.barrel_11 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=384,
            center_y=160,
        )
        self.barrel_12 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=SCREEN_WIDTH - 384,
            center_y=SCREEN_HEIGHT - 160,
        )
        self.barrel_13 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=190,
            center_y=SCREEN_HEIGHT - 120,
        )
        self.barrel_14 = arcade.AnimatedTimeBasedSprite(
            "./Assets/World/Objects/Barrel/SPR_Barrel_0.png",
            1,
            center_x=SCREEN_WIDTH - 190,
            center_y=120,
        )

        # --- BARREL-----------------------------------------------------------------------------//
        barrel_sprite_path = "./Assets/World/Objects/Barrel/Barrel_Sprite_Sheet.png"
        barrel_frames: List[arcade.AnimationKeyframe] = []

        for row in range(2):
            for column in range(4):
                frame = arcade.AnimationKeyframe(
                    (column + 1) * (row + 1),
                    125,
                    arcade.load_texture(
                        str(barrel_sprite_path),
                        x=column * 40,
                        y=row * 50,
                        width=40,
                        height=50,
                    ),
                )
                barrel_frames.append(frame)

        self.barrel_1.frames = barrel_frames
        self.barrel_2.frames = barrel_frames
        self.barrel_3.frames = barrel_frames
        self.barrel_4.frames = barrel_frames

        # INITIAL MAP 1 ADD
        self.barrel_list.append(self.barrel_1)
        self.barrel_list.append(self.barrel_2)
        self.barrel_list.append(self.barrel_3)
        self.barrel_list.append(self.barrel_4)

        self.barrel_5.frames = barrel_frames
        self.barrel_6.frames = barrel_frames
        self.barrel_7.frames = barrel_frames
        self.barrel_8.frames = barrel_frames
        self.barrel_9.frames = barrel_frames
        self.barrel_10.frames = barrel_frames

        self.barrel_11.frames = barrel_frames
        self.barrel_12.frames = barrel_frames
        self.barrel_13.frames = barrel_frames
        self.barrel_14.frames = barrel_frames

        # --- WHIRLPOOL -----------------------------------------------------------------------------//
        self.whirlpool_list = arcade.SpriteList()
        self.whirlpool_sprite_path = (
            "./Assets/World/Hazards/Whirlpool/Whirlpool_Sprite_Sheet.png"
        )

        # --- POST-WHIRLPOOL -----------------------------------------------------------------------------//
        self.post_whirlpool_list = arcade.SpriteList()
        self.post_whirlpool_sprite_path = (
            "./Assets/World/Hazards/Whirlpool/Post_Whirlpool_Sprite_Sheet.png"
        )

        pre_whirlpool_sprite_path = (
            "./Assets/World/Hazards/Whirlpool/Pre_Whirlpool_SpriteSheet.png"
        )
        self.whirlpool_1 = arcade.AnimatedTimeBasedSprite(
            pre_whirlpool_sprite_path, 0.3, center_x=580, center_y=120
        )
        self.whirlpool_2 = arcade.AnimatedTimeBasedSprite(
            pre_whirlpool_sprite_path, 0.3, center_x=580, center_y=400
        )
        self.whirlpool_3 = arcade.AnimatedTimeBasedSprite(
            pre_whirlpool_sprite_path, 0.3, center_x=580, center_y=SCREEN_HEIGHT - 90
        )

        self.whirlpool_4 = arcade.AnimatedTimeBasedSprite(
            pre_whirlpool_sprite_path, 0.3, center_x=330, center_y=400
        )
        self.whirlpool_5 = arcade.AnimatedTimeBasedSprite(
            pre_whirlpool_sprite_path, 0.3, center_x=450, center_y=250
        )
        self.whirlpool_6 = arcade.AnimatedTimeBasedSprite(
            pre_whirlpool_sprite_path, 0.3, center_x=230, center_y=500
        )
        self.whirlpool_7 = arcade.AnimatedTimeBasedSprite(
            pre_whirlpool_sprite_path, 0.3, center_x=675, center_y=440
        )
        self.whirlpool_8 = arcade.AnimatedTimeBasedSprite(
            pre_whirlpool_sprite_path, 0.3, center_x=580, center_y=SCREEN_HEIGHT - 85
        )

        # --- PRE-WHIRLPOOL -------------------------------------------------------------------------//
        pre_whirlpool_sprite_path = (
            "./Assets/World/Hazards/Whirlpool/Pre_Whirlpool_SpriteSheet.png"
        )
        pre_whirlpool_frames: List[arcade.AnimationKeyframe] = []
        for row in range(3):
            for column in range(4):
                frame = arcade.AnimationKeyframe(
                    column * row,
                    52,
                    arcade.load_texture(
                        str(pre_whirlpool_sprite_path),
                        x=column * 312,
                        y=row * 309,
                        width=312,
                        height=309,
                    ),
                )
                pre_whirlpool_frames.append(frame)

        self.whirlpool_1.frames = pre_whirlpool_frames
        self.whirlpool_2.frames = pre_whirlpool_frames
        self.whirlpool_3.frames = pre_whirlpool_frames
        self.whirlpool_4.frames = pre_whirlpool_frames
        self.whirlpool_5.frames = pre_whirlpool_frames
        self.whirlpool_6.frames = pre_whirlpool_frames
        self.whirlpool_7.frames = pre_whirlpool_frames
        self.whirlpool_8.frames = pre_whirlpool_frames

        # Bitflags
        self.p1_invincibility_bool = True
        self.p2_invincibility_bool = True
        self.p1_pre_whirlpool_flag = False
        self.p2_pre_whirlpool_flag = False
        self.p1_whirlpool_flag = False
        self.p2_whirlpool_flag = False
        self.p1_post_whirlpool_flag = False
        self.p2_post_whirlpool_flag = False
        self.p1_hot_bullet = False
        self.p2_hot_bullet = False
        self.is_resetting = True
        self.clear_flag = False

        # Float Variables
        self.p1_movement_speed = PLAYER_MOV_SPEED
        self.p2_movement_speed = PLAYER_MOV_SPEED
        self.p1_total_movement_speed = PLAYER_MOV_SPEED
        self.p2_total_movement_speed = PLAYER_MOV_SPEED
        self.p1_invincibility_timer = 2
        self.p2_invincibility_timer = 2
        self.reset_timer = 1

        arcade.set_background_color(arcade.csscolor.SADDLE_BROWN)

        self.current_explosion_sprite = 0
        self.current_power_up_sprite = 0
        self.current_barrel_sprite = 0

        # -------- LOADING ANIMATION SPRITES ---------------------------------------------//

        # Heart Item
        self.heart_item = []
        for i in range(4):
            sprite = arcade.load_texture(f"Assets/World/Items/Item_2/SPR_Heart_{i}.png")
            self.heart_item.append(sprite)

        # Special Item 1
        self.power_up = []
        for i in range(16):
            sprite = arcade.load_texture(
                f"Assets/World/Items/Item_1/SPR_Special_Item_{i}.png"
            )
            self.power_up.append(sprite)

        # Explosion
        self.explosion = []
        for i in range(9):
            sprite = arcade.load_texture(f"Assets/World/Effects/SPR_Explosion_{i}.png")
            self.explosion.append(sprite)

        # -------- SOUND FX -------------------------------------------------------------V
        self.SFX_bubble = arcade.load_sound("Assets/SFX/Bubble.wav")
        self.SFX_chain_drop = arcade.load_sound("Assets/SFX/Chain_Drop.wav")
        self.SFX_magic_time = arcade.load_sound("Assets/SFX/Magic_Time.wav")

        # --- POWER-UPS -----------------------------------------------------------------------------//
        self.power_up_list = arcade.SpriteList()

        self.p1_movement_speed_extra = 0
        self.p2_movement_speed_extra = 0
        self.wait_between_powerups = 12
        self.p1_power_up_timer = 0
        self.p2_power_up_timer = 0



    # Initially sets up or restarts the game
    def setup(self):
        # Main Scene call
        self.game_frame = 0
        self.gameover = False
        self.round = 1
        self.SFX_chain_drop.play(0.9)

        self.physics_engine_wall_p1 = arcade.PhysicsEngineSimple(
            self.player_1, self.wall_list
        )

        self.physics_engine_wall = arcade.PhysicsEngineSimple(
            self.player_1, self.wall_list
        )

    def game_reset(self):

        if self.round < 3:
            self.player_1.lives = 5
            self.player_2.lives = 5
            self.player_1.num_bullets = 3
            self.player_2.num_bullets = 3
            self.clear_flag = True
            self.level_reset = True


        self.round += 1
        arcade.sound.play_sound(arcade.Sound("./Assets/SFX/Lip_Pop.wav"), 8)

        for post_whirlpool in self.post_whirlpool_list:
            post_whirlpool.remove_from_sprite_lists()
            self.post_whirlpool_list.update()

        if self.round == 1:

            self.barrel_1.remove_from_sprite_lists()
            self.barrel_2.remove_from_sprite_lists()
            self.barrel_3.remove_from_sprite_lists()
            self.barrel_4.remove_from_sprite_lists()

            self.barrel_11.remove_from_sprite_lists()
            self.barrel_12.remove_from_sprite_lists()
            self.barrel_13.remove_from_sprite_lists()
            self.barrel_14.remove_from_sprite_lists()

            self.barrel_list.append(self.barrel_1)
            self.barrel_list.append(self.barrel_2)
            self.barrel_list.append(self.barrel_3)
            self.barrel_list.append(self.barrel_4)

        elif self.round == 2:

            self.barrel_1.remove_from_sprite_lists()
            self.barrel_2.remove_from_sprite_lists()
            self.barrel_3.remove_from_sprite_lists()
            self.barrel_4.remove_from_sprite_lists()

            self.barrel_list.append(self.barrel_5)
            self.barrel_list.append(self.barrel_6)
            self.barrel_list.append(self.barrel_7)
            self.barrel_list.append(self.barrel_8)
            self.barrel_list.append(self.barrel_9)
            self.barrel_list.append(self.barrel_10)

            self.pre_whirlpool_list.append(self.whirlpool_1)
            self.pre_whirlpool_list.append(self.whirlpool_2)
            # self.pre_whirlpool_list.append(self.whirlpool_6)

            self.map_scene = arcade.Scene.from_tilemap(self.tile_map2)
            self.wall_list = self.tile_map2.sprite_lists["Solids"]
            self.beach_tile_list = self.tile_map2.sprite_lists["Beach"]
            self.water_tile_list = self.tile_map2.sprite_lists["Water"]

        elif self.round == 3:

            self.whirlpool_1.remove_from_sprite_lists()
            self.whirlpool_2.remove_from_sprite_lists()
            self.whirlpool_3.remove_from_sprite_lists()

            for pre_whirlpool in self.pre_whirlpool_list:
                pre_whirlpool.remove_from_sprite_lists()

            for whirlpool in self.whirlpool_list:
                whirlpool.remove_from_sprite_lists()

            for post_whirlpool in self.post_whirlpool_list:
                post_whirlpool.remove_from_sprite_lists()

            self.pre_whirlpool_list.append(self.whirlpool_4)
            self.pre_whirlpool_list.append(self.whirlpool_5)
            self.pre_whirlpool_list.append(self.whirlpool_6)
            self.pre_whirlpool_list.append(self.whirlpool_7)
            self.pre_whirlpool_list.append(self.whirlpool_8)

            # self.whirlpool_3.remove_from_sprite_lists()

            self.barrel_5.remove_from_sprite_lists()
            self.barrel_6.remove_from_sprite_lists()
            self.barrel_7.remove_from_sprite_lists()
            self.barrel_8.remove_from_sprite_lists()
            self.barrel_9.remove_from_sprite_lists()
            self.barrel_10.remove_from_sprite_lists()

            self.barrel_list.append(self.barrel_11)
            self.barrel_list.append(self.barrel_12)
            self.barrel_list.append(self.barrel_13)
            self.barrel_list.append(self.barrel_14)

            self.map_scene = arcade.Scene.from_tilemap(self.tile_map3)
            self.wall_list = self.tile_map3.sprite_lists["Solids"]
            self.beach_tile_list = self.tile_map3.sprite_lists["Beach"]
            self.water_tile_list = self.tile_map3.sprite_lists["Water"]

        self.gameover = True

        for power_up in self.power_up_list:
            power_up.remove_from_sprite_lists()

        for bullet in self.player_bullet_list:
            bullet.remove_from_sprite_lists()

        for explosion in self.explosion_list:
            explosion.remove_from_sprite_lists()

        self.p1_total_movement_speed = 0
        self.p1_movement_speed_extra = 0

        self.player_1.set_position(80, 80)

        self.player_1.weapon.set_position(
            self.player_1.center_x, self.player_1.center_y
        )
        self.physics_engine_wall_p1 = arcade.PhysicsEngineSimple(
            self.player_1, self.wall_list
        )

        self.p2_total_movement_speed = 0
        self.p2_movement_speed_extra = 0

        self.player_2.set_position(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 80)

        self.player_2.weapon.set_position(
            self.player_2.center_x, self.player_2.center_y
        )
        self.physics_engine_wall_p2 = arcade.PhysicsEngineSimple(
            self.player_2, self.wall_list
        )

    def check_game(self):
        if self.player_1.lives == 0 and self.round < 3:
            self.player_2.score += 1
            self.game_reset()
        elif self.player_2.lives == 0 and self.round < 3:
            self.player_1.score += 1
            self.game_reset()
        if self.restart_tick < 1:
            self.restart_tick = 5
            self.round = 0

            self.whirlpool_4.remove_from_sprite_lists()
            self.whirlpool_5.remove_from_sprite_lists()
            self.whirlpool_6.remove_from_sprite_lists()
            self.whirlpool_7.remove_from_sprite_lists()
            self.whirlpool_8.remove_from_sprite_lists()

            self.barrel_11.remove_from_sprite_lists()
            self.barrel_12.remove_from_sprite_lists()
            self.barrel_13.remove_from_sprite_lists()
            self.barrel_14.remove_from_sprite_lists()
            self.map_scene = arcade.Scene.from_tilemap(self.tile_map1)
            self.wall_list = self.tile_map1.sprite_lists["Solids"]
            self.beach_tile_list = self.tile_map1.sprite_lists["Beach"]
            self.water_tile_list = self.tile_map1.sprite_lists["Water"]
            self.barrel_list.append(self.barrel_1)
            self.barrel_list.append(self.barrel_2)
            self.barrel_list.append(self.barrel_3)
            self.barrel_list.append(self.barrel_4)
            self.player_1.score = 0
            self.player_2.score = 0

            self.game_reset()

    # ~~~~~~~ UPDATE LOOP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def on_update(self, delta_time):
        self.game_frame += 1
        self.check_game()

        self.physics_engine_wall_p1.update()
        self.physics_engine_wall_p2.update()

        if self.reset_timer > 0 and self.is_resetting:

            self.reset_timer -= delta_time
            if self.reset_timer <= 0:
                self.p1_total_movement_speed = PLAYER_MOV_SPEED
                self.p2_total_movement_speed = PLAYER_MOV_SPEED
                self.level_reset = False
                self.is_resetting = False

        if self.p1_power_up_timer > 0:
            self.p1_power_up_timer -= delta_time
            if self.p1_power_up_timer <= 0:
                self.p1_movement_speed_extra = 0

        if self.p2_power_up_timer > 0:
            self.p2_power_up_timer -= delta_time
            if self.p2_power_up_timer <= 0:
                self.p2_movement_speed_extra = 0

        if self.wait_between_powerups > 0 and len(self.power_up_list) < 1:
            self.wait_between_powerups -= delta_time
            if self.wait_between_powerups <= 0:
                self.wait_between_powerups = 12
                self.random_power_up()
                arcade.sound.play_sound(arcade.Sound("./Assets/SFX/Bottle_Up.wav"), 4)

        if self.p1_invincibility_bool:
            self.p1_invincibility_timer -= delta_time
            # print("TIMER: ", self.p1_invincibility_timer)
            if self.p1_invincibility_timer <= 0:
                self.p1_invincibility_bool = False
                # print(self.p1_invincibility_bool)
                self.p1_invincibility_timer = 1

        if self.p2_invincibility_bool:
            self.p2_invincibility_timer -= delta_time
            # print("TIMER: ", self.p1_invincibility_timer)
            if self.p2_invincibility_timer <= 0:
                self.p2_invincibility_bool = False
                # print(self.p1_invincibility_bool)
                self.p2_invincibility_timer = 1

        # BEACH COLLISION - ONLY SLOWS PLAYER DOWN WHILE ON IT, ALLOWS FIRING THROUGH IT

        p1_beach_collision = arcade.check_for_collision_with_list(
            self.player_1, self.beach_tile_list
        )
        p2_beach_collision = arcade.check_for_collision_with_list(
            self.player_2, self.beach_tile_list
        )

        if p1_beach_collision:
            self.p1_total_movement_speed = 0.4
        if p2_beach_collision:
            self.p2_total_movement_speed = 0.4

        p1_water_collision = arcade.check_for_collision_with_list(
            self.player_1, self.water_tile_list
        )
        p2_water_collision = arcade.check_for_collision_with_list(
            self.player_2, self.water_tile_list
        )

        if p1_water_collision and not p1_beach_collision:
            self.p1_total_movement_speed = PLAYER_MOV_SPEED
        if p2_water_collision and not p2_beach_collision:
            self.p2_total_movement_speed = PLAYER_MOV_SPEED

        self.player_1.weapon.set_position(
            self.player_1.center_x, self.player_1.center_y
        )
        self.player_2.weapon.set_position(
            self.player_2.center_x, self.player_2.center_y
        )

        if self.player_1.is_shooting and self.player_1.num_bullets > 0:
            self.player_shooting(self.player_1)

        if self.player_2.is_shooting and self.player_2.num_bullets > 0:
            self.player_shooting(self.player_2)

        # collision control for player bullets
        for bullet in self.player_bullet_list:
            hit_wall = arcade.check_for_collision_with_list(bullet, self.wall_list)
            hit_barrel = arcade.check_for_collision_with_list(bullet, self.barrel_list)
            hit_player = arcade.check_for_collision_with_list(bullet, self.player_list)

            if (
                    len(hit_wall) > 0
                    or len(hit_barrel) > 0
                    or len(hit_player) > 0
            ):
                explosion = arcade.Sprite("./Assets/World/Effects/SPR_Explosion_0.png")
                explosion.center_x = bullet.center_x
                explosion.center_y = bullet.center_y
                self.explosion_list.append(explosion)
                if bullet.player_id == 1:
                    self.player_1.num_bullets += 1
                    if arcade.check_for_collision(bullet, self.player_2):
                        if self.p1_hot_bullet:
                            self.player_2.lives -= 2
                            self.p1_hot_bullet = False
                        else:
                            self.player_2.lives -= 1
                if bullet.player_id == 2:
                    self.player_2.num_bullets += 1
                    if arcade.check_for_collision(bullet, self.player_1):
                        if self.p2_hot_bullet:
                            self.player_1.lives -= 2
                            self.p2_hot_bullet = False
                        else:
                            self.player_1.lives -= 1
                bullet.remove_from_sprite_lists()
                arcade.sound.play_sound(
                    arcade.sound.Sound("./Assets/SFX/Explode.wav"), 0.3
                )

        self.player_1.hit_box = [[-30, -30], [30, -30], [30, 30], [-30, 30]]
        self.player_2.hit_box = [[-30, -30], [30, -30], [30, 30], [-30, 30]]

        # PUSHABLE BARREL -----------------------------------------------------------------\\
        for barrel in self.barrel_list:
            barrel.hit_box = [[-20, -20], [20, -20], [20, 20], [-20, 20]]

            player_1_collision = arcade.check_for_collision(barrel, self.player_1)
            player_2_collision = arcade.check_for_collision(barrel, self.player_2)
            wall_collision = arcade.check_for_collision_with_list(
                barrel, self.wall_list
            )

            if player_1_collision:
                if not wall_collision:
                    # Moving RIGHT
                    if self.player_1.change_x > 0:
                        barrel.change_x = self.player_1.change_x + 0.5
                        # Moving LEFT
                    elif self.player_1.change_x < 0:
                        barrel.change_x = self.player_1.change_x - 0.5
                    elif self.player_1.change_x == 0:
                        barrel.change_x = 0

                    # Moving DOWN
                    if self.player_1.change_y > 0:
                        barrel.change_y = self.player_1.change_y + 0.5
                    # Moving UP
                    elif self.player_1.change_y < 0:
                        barrel.change_y = self.player_1.change_y - 0.5
                    elif self.player_1.change_y == 0:
                        barrel.change_y = 0

                    barrel.center_x += barrel.change_x
                    barrel.center_y += barrel.change_y

                else:
                    barrel.center_x -= barrel.change_x
                    barrel.center_y -= barrel.change_y

            if player_2_collision:
                if not wall_collision:
                    # Moving RIGHT
                    if self.player_2.change_x > 0:
                        barrel.change_x = self.player_2.change_x + 0.5
                        # Moving LEFT
                    elif self.player_2.change_x < 0:
                        barrel.change_x = self.player_2.change_x - 0.5
                    elif self.player_2.change_x == 0:
                        barrel.change_x = 0

                    # Moving DOWN
                    if self.player_2.change_y > 0:
                        barrel.change_y = self.player_2.change_y + 0.5
                    # Moving UP
                    elif self.player_2.change_y < 0:
                        barrel.change_y = self.player_2.change_y - 0.5
                    elif self.player_2.change_y == 0:
                        barrel.change_y = 0

                    barrel.center_x += barrel.change_x
                    barrel.center_y += barrel.change_y
                else:
                    barrel.center_x -= barrel.change_x
                    barrel.center_y -= barrel.change_y

        # PRE_WHIRLPOOL -----------------------------------------------------------------\\
        for pre_whirlpool in self.pre_whirlpool_list:
            pre_whirlpool.hit_box = [[-60, -60], [60, -60], [60, 60], [-60, 60]]

            player_1_collision = arcade.check_for_collision(
                pre_whirlpool, self.player_1
            )

            if player_1_collision:
                self.p1_pre_whirlpool_flag = True
                if self.player_1.change_x == 0 and self.player_1.change_y == 0:
                    # print("Player stopped on pre_whirlpool")
                    self.p1_invincibility_bool = True
                    self.p1_invincibility_timer = 2
                    self.spawn_whirlpool(pre_whirlpool)
            if not player_1_collision and self.p1_pre_whirlpool_flag == True:
                self.p1_pre_whirlpool_flag = False
                self.p1_invincibility_bool = True
                self.p1_invincibility_timer = 1.5
                self.spawn_whirlpool(pre_whirlpool)

            player_2_collision = arcade.check_for_collision(
                pre_whirlpool, self.player_2
            )

            if player_2_collision:
                self.p2_pre_whirlpool_flag = True
                if self.player_2.change_x == 0 and self.player_2.change_y == 0:
                    # print("Player stopped on pre_whirlpool")
                    self.p2_invincibility_bool = True
                    self.p2_invincibility_timer = 2
                    # self.spawn_whirlpool(pre_whirlpool)
            if not player_2_collision and self.p2_pre_whirlpool_flag == True:
                self.p2_pre_whirlpool_flag = False
                self.p2_invincibility_bool = True
                self.p2_invincibility_timer = 1.5
                self.spawn_whirlpool(pre_whirlpool)

        # WHIRLPOOL ----------------------------------------------------------------------\\
        for whirlpool in self.whirlpool_list:
            whirlpool.hit_box = [[-15, -15], [15, -15], [15, 15], [-15, 15]]

            player_1_collision = arcade.check_for_collision(whirlpool, self.player_1)

            if player_1_collision:
                if self.p1_invincibility_bool == False:
                    print("Player 1 - Whirlpool Damage - Life -1!")
                    self.player_1.lives -= 1
                    self.p1_invincibility_bool = True
                    self.p1_invincibility_timer = 1.5
                    self.spawn_post_whirlpool(whirlpool)
                    self.SFX_bubble.play(5)

            player_2_collision = arcade.check_for_collision(whirlpool, self.player_2)

            if player_2_collision:
                if self.p2_invincibility_bool == False:
                    print("Player 2 - Whirlpool Damage - Life -1!")
                    self.player_2.lives -= 1
                    self.p2_invincibility_bool = True
                    self.p2_invincibility_timer = 1.5
                    self.spawn_post_whirlpool(whirlpool)
                    self.SFX_bubble.play(5)

        # POST_WHIRLPOOL ----------------------------------------------------------------------\\
        for post_whirlpool in self.post_whirlpool_list:
            post_whirlpool.hit_box = [[-15, -15], [15, -15], [15, 15], [-15, 15]]

        player_1_collision = arcade.check_for_collision_with_list(
            self.player_1, self.post_whirlpool_list
        )
        if player_1_collision:
            self.p1_total_movement_speed = 0.4

        player_2_collision = arcade.check_for_collision_with_list(
            self.player_2, self.post_whirlpool_list
        )
        if player_2_collision:
            self.p2_total_movement_speed = 0.4

         # SPECIAL POWER_UPS -----------------------------------------------------------------\\
        for power_up in self.power_up_list:

            # Manual Animation
            power_up.texture = self.power_up[self.current_power_up_sprite]
            self.current_power_up_sprite += 1

            if self.current_power_up_sprite > 15:
                self.current_power_up_sprite = 0

            p1_power_up_collision = arcade.check_for_collision(power_up, self.player_1)
            p2_power_up_collision = arcade.check_for_collision(power_up, self.player_2)

            if p1_power_up_collision:
                # SPEED BOOSTER (BLUE)
                if power_up.color == arcade.color.BEAU_BLUE:
                    self.SFX_magic_time.play(3)
                    print("Player 1 - Speed Boost Activated!")
                    power_up.remove_from_sprite_lists()
                    self.p1_power_up_timer = 10
                    self.p1_movement_speed_extra = 1.5
                # HEALTH RESTORE (GREEN)
                elif power_up.color == arcade.color.ELECTRIC_GREEN:
                    self.SFX_magic_time.play(3)
                    print("Player 1 - Life +1!")
                    self.player_1.lives += 1
                    power_up.remove_from_sprite_lists()
                    self.p1_power_up_timer = 10
                # DAMAGE BOOSTER (RED)
                elif power_up.color == arcade.color.CANDY_APPLE_RED:
                    self.SFX_magic_time.play(3)
                    print("Player 1 - Extra Damage on Next Shot!")
                    self.p1_hot_bullet = True
                    power_up.remove_from_sprite_lists()
                    self.p1_power_up_timer = 10

            elif p2_power_up_collision:
                if power_up.color == arcade.color.BEAU_BLUE:
                    print("Player 2 - Speed Boost Activated!")
                    self.SFX_magic_time.play(3)
                    power_up.remove_from_sprite_lists()
                    self.p2_power_up_timer = 10
                    self.p2_movement_speed_extra = 1.5
                # HEALTH RESTORE (GREEN)
                elif power_up.color == arcade.color.ELECTRIC_GREEN:
                    print("Player 2 - Life +1!")
                    self.SFX_magic_time.play(3)
                    self.player_2.lives += 1
                    power_up.remove_from_sprite_lists()
                    self.p2_power_up_timer = 10
                # DAMAGE BOOSTER (RED)
                elif power_up.color == arcade.color.CANDY_APPLE_RED:
                    print("Player 2 - Extra Damage on Next Shot!")
                    self.SFX_magic_time.play(3)
                    self.p2_hot_bullet = True
                    power_up.remove_from_sprite_lists()
                    self.p2_power_up_timer = 10

        # HIT-EFFECT (EXPLOSION) -------------------------------------------------\\
        for explosion in self.explosion_list:
            explosion.texture = self.explosion[self.current_explosion_sprite]
            self.current_explosion_sprite += 1

            if self.current_explosion_sprite > 8:
                explosion.remove_from_sprite_lists()
                self.current_explosion_sprite = 0

            # PLAYER 1 MOVEMENT
            # UP
        if self.player_1.direction[0] == True:
            self.player_1.change_y = (
                    self.p1_total_movement_speed + self.p1_movement_speed_extra
            )
        # LEFT
        if self.player_1.direction[1] == True:
            self.player_1.change_x = (
                    -self.p1_total_movement_speed - self.p1_movement_speed_extra
            )
        # DOWN
        if self.player_1.direction[2] == True:
            self.player_1.change_y = (
                    -self.p1_total_movement_speed - self.p1_movement_speed_extra
            )
        # RIGHT
        if self.player_1.direction[3] == True:
            self.player_1.change_x = (
                    self.p1_total_movement_speed + self.p1_movement_speed_extra
            )

            # PLAYER 2 MOVEMENT
            # UP
        if self.player_2.direction[0] == True:
            self.player_2.change_y = (
                    self.p2_total_movement_speed + self.p2_movement_speed_extra
            )
        # LEFT
        if self.player_2.direction[1] == True:
            self.player_2.change_x = (
                    -self.p2_total_movement_speed - self.p2_movement_speed_extra
            )
        # DOWN
        if self.player_2.direction[2] == True:
            self.player_2.change_y = (
                    -self.p2_total_movement_speed - self.p2_movement_speed_extra
            )
        # RIGHT
        if self.player_2.direction[3] == True:
            self.player_2.change_x = (
                    self.p2_total_movement_speed + self.p2_movement_speed_extra
            )

        if self.clear_flag:
            for pre_whirlpool in self.pre_whirlpool_list:
                pre_whirlpool.remove_from_sprite_lists()
                self.pre_whirlpool_list.update()

            for whirlpool in self.whirlpool_list:
                self.whirlpool_list.remove(whirlpool)
                self.whirlpool_list.update()

            for post_whirlpool in self.post_whirlpool_list:
                post_whirlpool.remove_from_sprite_lists()
                self.post_whirlpool_list.update()
        self.clear_flag = False

        # UPDATE SPRITE LISTS --------------------------------------\\
        self.player_list.update()
        self.player_list.update_animation()
        self.player_bullet_list.update()
        self.weapon_list.update()
        self.explosion_list.update()
        self.whirlpool_list.update_animation()
        self.post_whirlpool_list.update()
        self.pre_whirlpool_list.update_animation()
        self.post_whirlpool_list.update_animation()
        self.pre_whirlpool_list.update()
        self.barrel_list.update_animation()

    # ---- DRAWING / RENDERING SCENE ---------------------------------------------------------------V
    def on_draw(self):
        arcade.start_render()
        self.map_scene.draw()
        # draw things after map scene

        arcade.draw_text(
            "Player 1 [score: "
            + str(self.player_1.score)
            + ", lives: "
            + str(self.player_1.lives)
            + "]",
            25,
            SCREEN_HEIGHT - 50,
            arcade.csscolor.WHITE,
            18,
        )

        arcade.draw_text(
            "Player 2 [score: "
            + str(self.player_2.score)
            + ", lives: "
            + str(self.player_2.lives)
            + "]",
            SCREEN_WIDTH - (SCREEN_WIDTH / 3),
            SCREEN_HEIGHT - 50,
            arcade.csscolor.WHITE,
            18,
        )

        arcade.draw_text(
            "Frame: " + str(self.game_frame), 25, 25, arcade.csscolor.WHITE, 18
        )

        self.barrel_list.draw()

        self.power_up_list.draw()
        self.explosion_list.draw()
        for explosion in self.explosion_list:
            explosion.draw()

        self.pre_whirlpool_list.draw()
        self.whirlpool_list.draw()
        self.post_whirlpool_list.draw()

        self.weapon_list.draw()
        self.player_list.draw()

        self.player_bullet_list.draw()

        if self.round >= 3 and (self.player_1.lives <= 0 or self.player_2.lives <= 0):
            if self.gameover:
                if self.player_1.lives <= 0:
                    arcade.sound.play_sound(
                        arcade.Sound("./Assets/SFX/Lapras_cry.wav"), 4
                    )
                else:
                    arcade.sound.play_sound(arcade.Sound("./Assets/SFX/arrr.wav"), 4)
                self.gameover = False
            if self.game_frame % 100 == 0:
                self.restart_tick -= 1
            if self.player_1.score > self.player_2.score:
                arcade.draw_text(
                    "Player 1 wins!!",
                    SCREEN_WIDTH / 2 - 200,
                    SCREEN_HEIGHT / 2,
                    arcade.csscolor.WHITE,
                    40,
                )
            else:
                arcade.draw_text(
                    "Player 2 wins!!",
                    SCREEN_WIDTH / 2 - 200,
                    SCREEN_HEIGHT / 2,
                    arcade.csscolor.WHITE,
                    40,
                )
            arcade.draw_text(
                "Game restarts in: " + str(self.restart_tick),
                SCREEN_WIDTH / 2 - 150,
                SCREEN_HEIGHT / 2 - 100,
                arcade.csscolor.WHITE,
                40,
            )


    def player_shooting(self, player):
        bullet = BulletSprite(
            "./Assets/Player/spike_ball/spike_ball.png", 5, 0.15, game_window=self
        )
        bullet.player_id = player.player_id
        dist_to_next_point = 10
        cf = 7
        if player.is_cannon_shooting:
            bullet.change_x = (
                    math.cos(math.radians(player.weapon.angle)) * dist_to_next_point
            )
            bullet.change_y = (
                    math.sin(math.radians(player.weapon.angle)) * dist_to_next_point
            )
        else:
            bullet.change_x = (
                    math.cos(math.radians(player.face_angle)) * dist_to_next_point
            )
            bullet.change_y = (
                    math.sin(math.radians(player.face_angle)) * dist_to_next_point
            )
        # set position has a correction so bullets dont collide with self, may not be suitable if we use other sprite sheets than the current ship one
        bullet.set_position(
            player.center_x + (cf * bullet.change_x),
            player.center_y + cf * bullet.change_y,
        )
        self.player_bullet_list.append(bullet)
        player.num_bullets -= 1
        arcade.sound.play_sound(
            arcade.sound.Sound("./Assets/SFX/bang-sfx/cannon_02.wav"), 0.3
        )
        player.is_shooting = False
        player.is_cannon_shooting = False

    # ----- Key DOWN Events -----------------------------
    def on_key_press(self, key, modifiers):
        if (key in self.actions.keys):
            self.actions.keys[key] = True

    # ----- Key UP Events--------------------------------
    def on_key_release(self, key, modifiers):
        if (key in self.actions.keys):
            self.actions.keys[key] = False

    def random_power_up(self):
        random_x = randint(16, SCREEN_WIDTH - 16)
        random_y = randint(16, SCREEN_HEIGHT - 16)
        rand_power_up = randint(0, 2)

        power_up = arcade.Sprite("./Assets/World/Items/Item_1/SPR_Special_Item_0.png")
        power_up.center_x = random_x
        power_up.center_y = random_y
        power_up.scale = 2

        if rand_power_up == 0:
            power_up.color = arcade.color.BEAU_BLUE
        elif rand_power_up == 1:
            power_up.color = arcade.color.ELECTRIC_GREEN
        elif rand_power_up == 2:
            power_up.color = arcade.color.CANDY_APPLE_RED

        self.power_up_list.append(power_up)

        # Making sure item does not spawn on top of specific entities
        for item in self.power_up_list:
            water_collision = arcade.check_for_collision_with_list(
                item, self.water_tile_list
            )
            wall_collision = arcade.check_for_collision_with_list(item, self.wall_list)

            # Recursive call to keep trying to spawn item only in navigatable water tiles
            if not water_collision or wall_collision:
                item.remove_from_sprite_lists()
                self.random_power_up()

    def spawn_whirlpool(self, pre_whirlpool):
        self.whirlpool_sprite = arcade.AnimatedTimeBasedSprite(
            self.whirlpool_sprite_path,
            2.5,
            center_x=pre_whirlpool.center_x,
            center_y=pre_whirlpool.center_y,
        )
        whirlpool_frames: List[arcade.AnimationKeyframe] = []
        for row in range(2):
            for column in range(2):
                frame = arcade.AnimationKeyframe(
                    column * row,
                    42,
                    arcade.load_texture(
                        str(self.whirlpool_sprite_path),
                        x=column * 64,
                        y=row * 64,
                        width=64,
                        height=64,
                    ),
                )
                whirlpool_frames.append(frame)
        self.whirlpool_sprite.frames = whirlpool_frames
        self.whirlpool_list.append(self.whirlpool_sprite)
        pre_whirlpool.remove_from_sprite_lists()

    def spawn_post_whirlpool(self, whirlpool):
        self.p1_invincibility_bool = True
        self.p1_invincibility_timer = 0.5
        self.post_whirlpool_sprite = arcade.AnimatedTimeBasedSprite(
            self.post_whirlpool_sprite_path,
            2.25,
            center_x=whirlpool.center_x,
            center_y=whirlpool.center_y,
        )
        post_whirlpool_frames: List[arcade.AnimationKeyframe] = []
        for row in range(2):
            for column in range(2):
                frame = arcade.AnimationKeyframe(
                    column * row,
                    140,
                    arcade.load_texture(
                        str(self.post_whirlpool_sprite_path),
                        x=column * 64,
                        y=row * 64,
                        width=64,
                        height=64,
                    ),
                )
                post_whirlpool_frames.append(frame)
        self.post_whirlpool_sprite.frames = post_whirlpool_frames
        self.post_whirlpool_list.append(self.post_whirlpool_sprite)
        whirlpool.remove_from_sprite_lists()

def get_ip_addresses(data):
    ip_addresses = []
    count = 1
    while count < len(data) - 1:
        if data[count] == '\"':
            count += 1
            ip = ""
            while data[count] != "\"":
                ip = ip + data[count]
                count += 1
            ip_addresses.append(ip)
        count += 1
    return ip_addresses

def find_ip_address():
    server_address = ""
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        connection.connect(('10.255.255.255', 1))  # dummy address that doesn't need to be reached
        server_address = connection.getsockname()[0]
    except IOError:
        server_address = '127.0.0.1'  # localhost loopback address
    finally:
        connection.close()
    return server_address

def setup_client_connection(client: TiledWindow):
    client_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(client_event_loop)
    client_event_loop.create_task(communication_with_server(client, client_event_loop))
    client_event_loop.run_forever()


async def communication_with_server(client: TiledWindow, event_loop):  # client pulls from TiledWindow class
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # send stuff to server to get player id for player determination
    keystate = json.dumps(client.actions.keys)
    level_state = json.dumps(client.player_actions.level_reset)
    UDPClientSocket.sendto(str.encode(keystate), (client.server_address, int(client.server_port)))
    UDPClientSocket.sendto(str.encode(level_state), (client.server_address, int(client.server_port)))
    data_packet = UDPClientSocket.recvfrom(1024)
    data = data_packet[0]
    decoded_data: PlayerState.GameState = PlayerState.GameState.from_json(data)
    player_dict = decoded_data.player_states

    # get list of ip addresses from server
    data_packet, serveraddr = UDPClientSocket.recvfrom(1024)
    decoded_addresses = data_packet.decode()
    ip_addresses = get_ip_addresses(decoded_addresses)
    print("ready to play")

    # sort out who is who
    player2_ip_addr = None
    if player_dict[client.ip_addr].id == 1:
        player = client.player_1
        player2 = client.player_2
        player2_ip_addr = ip_addresses[1]
    else:
        player = client.player_2
        player2 = client.player_1
        player2_ip_addr = ip_addresses[0]


    while True:
        keystate = json.dumps(client.actions.keys)
        level_state = json.dumps(client.player_actions.level_reset)
        UDPClientSocket.sendto(str.encode(keystate), (client.server_address, int(client.server_port)))
        UDPClientSocket.sendto(str.encode(level_state), (client.server_address, int(client.server_port)))
        data_packet = UDPClientSocket.recvfrom(1024)
        data = data_packet[0]   # get the encoded string
        decoded_data: PlayerState.GameState = PlayerState.GameState.from_json(data)

        player_dict = decoded_data.player_states    # will contain all_players


        player1_info: PlayerState.PlayerState = player_dict[client.ip_addr]  # get info of your ip


        if  player1_info.level_reset:
            print(player.level_reset)
            player.center_x = 80
            player.center_y = 80
            player.level_reset = False
        else:
            player.center_x = player1_info.x_loc
            player.center_y = player1_info.y_loc

        player.weapon.angle = player1_info.weapon_angle
        player.face_angle = player1_info.face_angle
        player.is_shooting = player1_info.shooting
        player.is_cannon_shooting = player1_info.weapon_shooting

        player2_info: PlayerState.PlayerState = player_dict[player2_ip_addr]
        player2.center_x = player2_info.x_loc
        player2.center_y = player2_info.y_loc
        player2.weapon.angle = player2_info.weapon_angle
        player2.face_angle = player2_info.face_angle
        player2.is_shooting = player2_info.shooting
        player2.is_cannon_shooting = player2_info.weapon_shooting



def main():

    SERVER_ADDR = "192.168.0.82"
    SERVER_PORT = "25001"

    CLIENT_ADDR = find_ip_address()
    # SERVER_ADDR = input("enter the IP address to the game server:\n")     # uncomment before submission
    # SERVER_PORT = input("enter the port to the game server:\n")

    window = TiledWindow(CLIENT_ADDR, SERVER_ADDR, SERVER_PORT)

    client_thread = threading.Thread(target=setup_client_connection, args=(window,), daemon=True)
    client_thread.start()
    arcade.run()


if __name__ == '__main__':
    main()
