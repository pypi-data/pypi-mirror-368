import time

from mlgame.argument.model import AINameEnum, GroupEnum
from mlgame.core.communication import MLCommManager
from mlgame.core.exceptions import ErrorEnum, GameError
from mlgame.executor.interface import ExecutorInterface
from mlgame.utils.logger import logger


import importlib
import os
import traceback


class AIClientExecutor(ExecutorInterface):
    def __init__(self,
                 # TODO insert GroupAI
                 ai_client_path: str,
                 ai_comm: MLCommManager,
                 ai_name:AINameEnum=AINameEnum.P1,
                 group:GroupEnum=GroupEnum.A,
                 game_params:dict=None,
                 ai_label:str=""
                 ):
        if game_params is None:
            game_params = {}
        self._frame_count = 0
        self.ai_comm = ai_comm
        self.ai_path = ai_client_path
        self._proc_name = ai_client_path
        # self._args_for_ml_play = args
        # self._kwargs_for_ml_play = kwargs
        self._ai_name = ai_name
        self._group = group
        self._ai_label = ai_label
        self.game_params = game_params

    def run(self):
        # self.ai_comm.start_recv_obj_thread()
        try:
            module_name = os.path.basename(self.ai_path)
            spec = importlib.util.spec_from_file_location(
                module_name, self.ai_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # set ai_name and group name
            ai_obj = module.MLPlay(ai_name=self._ai_name.value,
                                   # TODO ai_label
                                   group=self._group.value,
                                   game_params=self.game_params,
                                   ai_label=self._ai_label)

            # cmd = ai_obj.update({})
            logger.info(f"             AI Client({self._ai_name}) runs")
            self._ml_ready()
            while True:
                data = self.ai_comm.recv_from_game() # non-blocking
                # TODO add schema in ai client executor
                if data:
                    scene_info, keyboard_info,ai_enabled = data
                    if scene_info is None:
                        # game over
                        break
                else:
                    print(f"ai receive from game : {data}")
                    break

                # assert keyboard_info == "1"
                if ai_enabled:
                    # 遊戲暫停、delay 等等，都不會進到此條件，也因此確保了拿到的遊戲資訊是最新的
                    command = ai_obj.update(scene_info, keyboard_info)
                    if scene_info["status"] != "GAME_ALIVE" or command == "RESET":
                        ai_obj.reset()
                        # TODO 收到 reset 這裡會重置 frame_count ，應該要再多確認什麼情況要重置，什麼情況不用重置
                        self._frame_count = 0
                        self._ml_ready()
                        continue
                    if command is not None:
                        action_frame = scene_info['frame']
                        logger.debug(f"frame count in ai : {action_frame}")
                        self.ai_comm.send_to_game({
                            "frame": action_frame,
                            "command": command
                        })

                # time.sleep(0.01)
        except ModuleNotFoundError as e:
            failed_module_name = e.__str__().split("'")[1]
            logger.error(
                f"Module '{failed_module_name}' is not found in {self._proc_name}")
                        # send msg to game process
            ai_error = GameError(
                error_type=ErrorEnum.AI_INIT_ERROR, frame=self._frame_count,
                message="The process '{}' AI is not imported correctly. {}".format(
                    self._ai_name, traceback.format_exc())
            )

            self.ai_comm.send_to_game(ai_error)
            self._wait_for_exit()

        except FileNotFoundError as e:

            logger.error(f"{e} in {self._proc_name}")
            # send msg to game process
            ai_error = GameError(
                error_type=ErrorEnum.AI_INIT_ERROR, frame=self._frame_count,
                message=f"The process '{self._ai_name}' AI occurred file not found error. {e.__str__()}"
            )

            self.ai_comm.send_to_game(ai_error)
            self._wait_for_exit()

        except Exception as e:
            # handle ai other error

            logger.error(f"{e} in {self._proc_name}")
            ai_error = GameError(
                error_type=ErrorEnum.AI_EXEC_ERROR, frame=self._frame_count,
                message=f"The process '{self._ai_name}' is exited by itself. {traceback.format_exc()}"
            )

            self.ai_comm.send_to_game(ai_error)
            self._wait_for_exit()

        except SystemExit:  # Catch the exception made by 'sys.exit()'
            logger.error("             System exit at ai client process ")

            ai_error = GameError(
                error_type=ErrorEnum.AI_EXEC_ERROR, frame=self._frame_count,
                message=f"The process '{self._ai_name}' is exited by sys.exit. : {traceback.format_exc()}"
            )

            self.ai_comm.send_to_game(ai_error)

        if module == "mlgame.crosslang.ml_play":
            # TODO crosslang
            ai_obj.stop_client()
        logger.info(f"             AI Client({self._ai_name}) ends")

    def _ml_ready(self):
        """
        Send a "READY" command to the game process
        """
        self.ai_comm.send_to_game("READY")

    def _wait_for_exit(self):
        logger.warning(f"             AI Client({self._ai_name}) is broken , will return None until the end")

        while True:
            # mock AI client, will not return anything
            data = self.ai_comm.recv_from_game() # non-blocking
            if data:
                scene_info, keyboard_info,ai_enabled = data
                if scene_info is None:
                    # game over
                    break
            else:
                print(f"ai receive from game : {data}")
                break

            # assert keyboard_info == "1"
            if ai_enabled:
                # 遊戲暫停、delay 等等，都不會進到此條件，也因此確保了拿到的遊戲資訊是最新的
                if scene_info["status"] != "GAME_ALIVE" :
                    # ai_obj.reset()
                    self._ml_ready()
                    continue
                command = None
                action_frame = scene_info['frame']
                logger.debug(f"frame count in ai : {action_frame}")
                self.ai_comm.send_to_game({
                    "frame": action_frame,
                    "command": command
                })
            time.sleep(1)
