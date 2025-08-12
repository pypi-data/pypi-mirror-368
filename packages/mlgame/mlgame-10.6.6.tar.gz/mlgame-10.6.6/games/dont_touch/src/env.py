from os import path

from .version import version

PPM = 16.0  # pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS

'''width and height'''
WIDTH = 800
HEIGHT = 640
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
GRAY = "#cccccc"
WHITE = "#ffffff"
BLACK = "#000000"
RED = "#C3305b"
YELLOW = "#f5d750"
BLUE = "#3a84c1"
LIGHT_BLUE = "#061c42"
PAIA_B = "#0c3997"
GREEN = "#50aa82"
SENSOR_Y = "#ffff83"
SENSOR_R = "#ed2323"
SENSOR_B = "#1d92fe"
CAR_COLOR = [RED, BLUE, GREEN, YELLOW]

'''object size'''
car_size = (60, 30)

'''data path'''
ASSET_IMAGE_DIR = path.join(path.dirname(__file__), "../asset/image")
IMAGE_DIR = path.join(path.dirname(__file__), 'image')
SOUND_DIR = path.join(path.dirname(__file__), '../asset/sound')
MUSIC_DIR = path.join(path.dirname(__file__), '../asset/music')
MAP_DIR = path.join(path.dirname(__file__), "map")
IMAGE_URL = f"https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/dont_touch/{version}/asset/image/"
SOUND_URL = f"https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/dont_touch/{version}/asset/sound/"
MUSIC_URL = f"https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/dont_touch/{version}/asset/music/"
'''image'''
BG_IMG = "bg.png"
BG_URL = f"{IMAGE_URL}bg.png"

L_BG_IMG = "bg_light.png"
L_BG_URL = f"{IMAGE_URL}bg_light.png"

LOGO = "logo.png"
LOGO_URL = f"{IMAGE_URL}logo.png"
TARGET = "target.png"
TARGET_PATH = path.join(ASSET_IMAGE_DIR, TARGET)
TARGET_URL = f"{IMAGE_URL}target.png"
BAR_IMG = "bar.png"
BAR_URL = f"{IMAGE_URL}bar.png"

BGM_PATH = path.join(MUSIC_DIR, "BGM.mp3")
BGM_URL = MUSIC_URL + "BGM.mp3"
BOMB_PATH = path.join(SOUND_DIR, "bomb.mp3")
BOMB_URL = SOUND_URL + "bomb.mp3"
HELP_TXT_STYLE = "16px Arial BOLD"
HELP_TXT_COLOR = "#43A047"
