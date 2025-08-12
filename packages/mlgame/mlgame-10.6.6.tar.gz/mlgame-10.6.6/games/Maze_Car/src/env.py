from os import path
from .version import version
PPM = 16  # pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS

'''width and height'''
WIDTH = 1000
HEIGHT = 700
TILE_WIDTH = 540  # 大小
TILE_HEIGHT = 540

'''tile-base'''
TILESIZE = 16
TILE_LEFTTOP = 16, 16  # pixel
GRIDWIDTH = (TILE_WIDTH + TILE_LEFTTOP[0]) / TILESIZE
GRIDHEIGHT = (TILE_HEIGHT + TILE_LEFTTOP[1]) / TILESIZE

'''sensor set trans'''
sensor_trans = ((1, 0),
                (0, 1),
                (-1, 0),
                (0, -1))

'''environment data'''
FPS = 30

'''color'''
BLACK = (0, 0, 0)
WHITE = "#F5F5F5"
RED = "#ff0000"
YELLOW = "#FFF500"
GREEN = (0, 255, 0)
GREY = "#9E9E9E"
BLUE = "#0C55FF"
LIGHT_BLUE = "#03A9F4"
BROWN = "#795548"
PINK = "#E91E63"
MEDIUMPURPLE = "#9C27B0"
WALL_COLOR = "#D9D9D9"
CAR1_COLOR = "#FFC107"
CAR2_COLOR = "#FF80AB"
CAR3_COLOR = "#00E5FF"
CAR4_COLOR = "#B2FF59"
CAR_COLOR = [CAR1_COLOR, CAR2_COLOR, CAR3_COLOR, CAR4_COLOR]
'''object size'''
car_size = (50, 40)

'''data path'''
ASSET_IMAGE_DIR = path.join(path.dirname(__file__), "../asset/image")
IMAGE_DIR = path.join(path.dirname(__file__), 'image')
SOUND_DIR = path.join(path.dirname(__file__), '../asset/sound')

'''image'''
BG_IMG = "bg_img.png"
BG_URL = 'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/bg_img.png'
BG_PATH = path.join(ASSET_IMAGE_DIR, BG_IMG)
INFO_NAME = "info.png"
INFO_PATH = path.join(ASSET_IMAGE_DIR, INFO_NAME)
INFO_URL = 'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/info.png'

LOGO = "logo.png"
LOGO_URL = 'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/logo.png'

TMF_LOGO = "TMFlogo.png"
TMF_LOGO_URL = 'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/TMFlogo.png'
ENDPOINT_IMG = "endpoint.png"
ENDPOINT_URL = f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/{ENDPOINT_IMG}'
ENDPOINT_PATH = path.join(ASSET_IMAGE_DIR, ENDPOINT_IMG)

CHECKPOINT_IMG = "checkpoint.png"
CHECKPOINT_URL = f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/{CHECKPOINT_IMG}'
CHECKPOINT_PATH = path.join(ASSET_IMAGE_DIR, CHECKPOINT_IMG)
CHECKPOINT2_IMG = "checkpoint_2.png"
CHECKPOINT2_URL = f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/{CHECKPOINT2_IMG}'
CHECKPOINT2_PATH = path.join(ASSET_IMAGE_DIR, CHECKPOINT2_IMG)

CARS_NAME = ["car_01.png", "car_02.png", "car_03.png", "car_04.png", "car_05.png", "car_06.png", ]
CARS_URL = [f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/car_01.png',
            f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/car_02.png',
            f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/car_03.png',
            f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/car_04.png',
            f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/car_05.png',
            f'https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/Maze_Car/{version}/asset/image/car_06.png'
            ]

'''map_file'''
PRACTICE_MAPS = ["level_1.json", "level_2.json", "level_3.json", "level_4.json", "level_5.json", "level_6.json"]
NORMAL_MAZE_MAPS = ["normal_map_1.json", "normal_map_2.json", "normal_map_3.json", "normal_map_3.json",
                    "normal_map_3.json", "normal_map_3.json"]
MOVE_MAZE_MAPS = ["move_map_1.json", "move_map_2.json", "move_map_3.json", "move_map_4.json", "move_map_4.json",
                  "move_map_4.json"]
BG_COLOR = "#8493B1"
MAP_FOLDER = path.join(path.dirname(__file__), "map")
HELP_TXT_COLOR = "#0000FF"

BGM_FILE_NAME = "BGM.mp3"
MUSIC_PATH = path.join(path.dirname(__file__), "..", "asset", "music")
MUSIC_URL = f"https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/maze_car/{version}/asset/music/"

BGM_PATH = path.join(MUSIC_PATH, BGM_FILE_NAME)
BGM_URL = MUSIC_URL+BGM_FILE_NAME