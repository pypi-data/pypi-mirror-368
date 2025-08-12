from mlgame.core.communication import TransitionCommManager
from mlgame.core.model import MLGameDataType
from mlgame.executor.interface import ExecutorInterface
from mlgame.utils.logger import logger
from mlgame.view.view import PygameView


import traceback


class DisplayExecutor(ExecutorInterface):
    """current not used """
    def __init__(self, display_comm: TransitionCommManager, scene_init_data):
        # super().__init__(name="ws")
        logger.info("             display_process_init ")
        self._proc_name = "display"
        self._comm_manager = display_comm
        self._recv_data_func = self._comm_manager.recv_from_game
        self._scene_init_data = scene_init_data

    def run(self):
        self.game_view = PygameView(self._scene_init_data)
        self._comm_manager.start_recv_obj_thread()
        try:
            while (game_data := self._recv_data_func()).type != MLGameDataType.GAME_RESULT:

                if game_data.type == MLGameDataType.GAME_PROGRESS:
                    # print(game_data)
                    self.game_view.draw(game_data.data)
                    pass
        except Exception as e:
            # exception = TransitionProcessError(self._proc_name, traceback.format_exc())
            self._comm_manager.send_exception(f"exception on {self._proc_name}")
            # catch connection error
            print("except", e)
            logger.exception(traceback.format_exc())

        finally:
            print("end display process")