import abc
from enum import Enum

from mlgame.argument.model import GroupAI
from mlgame.core.model import GameProgressSchema
from mlgame.utils.enum import get_ai_name
from mlgame.view.view_model import Scene


class GameResultState(str, Enum):
    """
    表示遊戲結束的狀態
    finish 表示遊戲有成功執行到最後，表示玩家通關，或是多個玩家至少一人通關
    fail 表示玩家闖關失敗，或是沒有任何一個玩家通關
    """
    FINISH = "finish"
    FAIL = "fail"
    NOT_YET = "not_yet"
    PASSED = "passed"
    UN_PASSED = "un_passed"
    RUNNING = "running"


class GameStatus():
    # TODO refactor
    """
        表示遊戲進行中的狀態
        GAME_ALIVE 表示遊戲進行中
        GAME_OVER 表示玩家闖關失敗，多人遊戲中，收到此狀態，表示輸掉此遊戲
        GAME_PASS 表示玩家闖關成功，多人遊戲中，收到此狀態，表示贏得此遊戲
    """
    GAME_ALIVE = "GAME_ALIVE"
    GAME_OVER = "GAME_OVER"
    GAME_PASS = "GAME_PASS"
    GAME_1P_WIN = "GAME_1P_WIN"
    GAME_2P_WIN = "GAME_2P_WIN"
    GAME_DRAW = "GAME_DRAW"


class PaiaGame(abc.ABC):
    def __init__(self, user_num: int=1,group_ai_list:list[GroupAI]=[], *args, **kwargs):
        self.scene = Scene(width=800, height=600, color="#4FC3F7", bias_x=0, bias_y=0)
        self.frame_count = 0
        self.game_result_state = GameResultState.FAIL
        self.status = GameStatus.GAME_ALIVE
        self.user_num = user_num
        self.game_mode = "NORMAL"
        self.ai_enabled = True
        self.game_state = None
        self.group_ai_list = group_ai_list
    @abc.abstractmethod
    def update(self, commands: dict):
        self.game_state.update(commands)
        self.frame_count += 1

    @abc.abstractmethod
    def get_data_from_game_to_player(self) -> dict:
        """
        send something to game AI
        we could send different data to different ai
        """
        data_to_player = {}
        data_to_1p = {
            "frame": self.frame_count,
            "status": self.status,
            "key": "value"

        }
        for i in range(self.user_num):
            data_to_player[get_ai_name(i)] = data_to_1p
        return data_to_player

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def get_scene_init_data(self) -> dict:
        # TODO add schema
        """
        Get the initial scene and object information for drawing on the web
        """
        # TODO add music or sound
        scene_init_data = {"scene": self.scene.__dict__,
                           "assets": [

                           ],
                           "background":[]
                           # "audios": {}
                           }
        return scene_init_data

    @abc.abstractmethod
    def get_scene_progress_data(self) -> GameProgressSchema:
        """
        Get the position of game objects for drawing on the web
        """

        scene_progress = {
            # background view data will be draw first
            "background": [],
            # game object view data will be draw on screen by order , and it could be shifted by WASD
            "object_list": [],
            "toggle": [],
            "toggle_with_bias": [],
            "foreground": [],
            # other information to display on web
            "user_info": [],
            # other information to display on web
            "game_sys_info": {}
        #     TODO add music and sound
        }
        return GameProgressSchema.model_validate(scene_progress)

    @abc.abstractmethod
    def get_game_result(self) -> dict:
        """
        send game result
        """
        return {"frame_used": self.frame_count,
                "result": {

                },

                }



class GameState(abc.ABC):
    def __init__(self,game:PaiaGame):
        self.game = game
        
    @abc.abstractmethod
    def update(self, *args, **kwargs):
        """
        Update the game state.
        """
        pass
    
    @abc.abstractmethod
    def get_scene_progress_data(self)->GameProgressSchema:
        """
        Get the scene progress data.
        """
        pass
    
    @abc.abstractmethod
    def reset(self):
        """
        Reset the game state.
        """
        pass


def get_paia_game_obj(game_cls, parsed_game_params: dict, user_num, group_ai_list:list[GroupAI]) -> PaiaGame:
    game = game_cls(user_num=user_num, **parsed_game_params, group_ai_list=group_ai_list)
    assert isinstance(game, PaiaGame), "Game " + str(game) + " should implement a abstract class : PaiaGame"
    return game
