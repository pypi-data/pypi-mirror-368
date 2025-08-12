from mlgame.core.communication import GameCommManager
from mlgame.executor.interface import ExecutorInterface
from mlgame.game.generic import quit_or_esc
from mlgame.game.paia_game import PaiaGame
from mlgame.utils.logger import logger
from mlgame.view.view import PygameViewInterface


import pandas as pd


import time
import traceback


class GameManualExecutor(ExecutorInterface):
    # TODO deprecated
    def __init__(self, game: PaiaGame,
                 game_view: PygameViewInterface,
                 game_comm: GameCommManager,
                 fps=30,
                 one_shot_mode=False, ):
        self.game_view = game_view
        self.frame_count = 0
        self.game = game
        self.game_comm = game_comm
        self._ml_delayed_frames = {}
        self._ml_execution_time = 1 / fps
        self._fps = fps
        self._ml_delayed_frames = {}
        # self._recorder = get_recorder(self._execution_cmd, self._ml_names)
        self._frame_count = 0
        self.one_shot_mode = one_shot_mode
        self._proc_name = self.game.__class__.__str__

    def run(self):
        game = self.game
        game_view = self.game_view
        self.game_comm.send_to_others(game_view.scene_init_data)

        try:
            while not quit_or_esc():
                cmd_dict = game.get_keyboard_command()
                # self._recorder.record(scene_info_dict, cmd_dict)
                result = game.update(cmd_dict)
                self._frame_count += 1
                view_data = game.get_scene_progress_data()
                self.game_comm.send_to_others(view_data)
                game_view.draw(view_data)
                time.sleep(self._ml_execution_time)
                # Do reset stuff
                if result == "RESET" or result == "QUIT":
                    game_result = game.get_game_result()
                    attachments = game_result['attachment']
                    print(pd.DataFrame(attachments).to_string())
                    if self.one_shot_mode or result == "QUIT":
                        game_result['frame_used']=self._frame_count
                        self.game_comm.send_to_others(game_result)
                        break
                    game.reset()
                    game_view.reset()
                    # self._frame_count = 0

        except Exception as e:
            # handle unknown exception
            # send to es
            logger.exception(
                f"Some errors happened in game process. {e.__str__()}")
            traceback.print_exc()

        logger.info("manual executor end.")