import os

TIMEOUT = int(os.getenv("WS_TIMEOUT", 60))
WS_WAIT_GAME_TIMEOUT = int(os.getenv("WS_WAIT_GAME_TIMEOUT", 15))
FPS_MAX = int(os.getenv("FPS_MAX", 300))