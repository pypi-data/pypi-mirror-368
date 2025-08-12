import json
from mlgame.core.communication import TransitionCommManager
from mlgame.core.model import GameProgressSchema, MLGameDataType
from mlgame.executor.interface import ExecutorInterface
from mlgame.utils.logger import logger




import os


class ProgressLogExecutor(ExecutorInterface):
    def __init__(self, progress_folder, progress_frame_frequency, pl_comm: TransitionCommManager):
        # super().__init__(name="ws")
        self._proc_name = f"progress_log({progress_folder}"
        self._progress_folder = progress_folder
        self._progress_frame_frequency = progress_frame_frequency
        self._comm_manager = pl_comm
        self._recv_data_func = self._comm_manager.recv_from_game
        self._filename = "{}.json"
        self._progress_data = []


    def save_json_and_init(self, path):
        with open(path, 'w') as f:
            data = json.dumps(self._progress_data, default=lambda o: o.model_dump() if hasattr(o, "model_dump") else o)
            # json.dump(self._progress_data, f)
            f.write(data)
        # Get the file size in kilobytes (1 KB = 1024 bytes)
        file_size_kb = os.path.getsize(path) / 1024
        # Print the file path and file size in KB
        print(f"File saved to: {path}, file size: {file_size_kb:.2f} KB")

        self._progress_data = []

    def run(self):
        self._comm_manager.start_recv_obj_thread()

        try:
            progress_count = -1
            # Process data until we receive the game result
            while True:
                game_data = self._recv_data_func()
                game_data = game_data
                if game_data.type == MLGameDataType.GAME_RESULT:
                    break
                    
                if game_data.type == MLGameDataType.GAME_PROGRESS:
                    
                    progress_data = GameProgressSchema.model_validate(game_data.data)
                    frame = progress_data.frame
                    # Check if we need to save the progress data
                    if (frame - 1) % self._progress_frame_frequency == 0 and frame != 1:
                        progress_count += 1
                        filepath = os.path.join(
                            self._progress_folder, 
                            self._filename.format(progress_count)
                        )
                        self.save_json_and_init(filepath)
                        
                    self._progress_data.append(progress_data)
            
            # Handle remaining progress data after the game is finished
            if self._progress_data:
                progress_count += 1
                filename = self._filename.format(str(progress_count) + '-end')
                filepath = os.path.join(self._progress_folder, filename)
                self.save_json_and_init(filepath)
                
        except Exception as e:
            # exception = TransitionProcessError(self._proc_name, traceback.format_exc())
            self._comm_manager.send_exception(
                f"exception on {self._proc_name}")
            # catch connection error
            logger.exception(e)
        finally:
            logger.info("end pl")
