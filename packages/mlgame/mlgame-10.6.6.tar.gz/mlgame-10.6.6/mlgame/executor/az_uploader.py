
from mlgame.core.communication import TransitionCommManager
from mlgame.core.model import MLGameDataType, MLGameEntityWrapperSchema
from mlgame.executor.interface import ExecutorInterface
from mlgame.utils.azure import upload_data_to_azure_blob
from mlgame.utils.logger import logger


class AzureUploader(ExecutorInterface):
    _count_bias_list = [15, 15, 30, 30, 60,60,90,90,120]
    def __init__(self, pl_comm: TransitionCommManager, az_blob_url: str):
        # super().__init__(name="ws")
        self._proc_name = "azure_uploader"
        self._comm_manager = pl_comm
        self._recv_data_func = self._comm_manager.recv_from_game
        self._file_count = 0
        self._progress_data = []
        self._prev_count = 0
        self._post_count = self._get_next_count_bias()
        self._progress_count = -1
        self._az_url = str(az_blob_url)
    def run(self):
        self._comm_manager.start_recv_obj_thread()
        handlers = {
            MLGameDataType.GAME_PROGRESS: self._handle_progress,
            MLGameDataType.GAME_RESULT: self._handle_result,
            MLGameDataType.GAME_ERROR: self._handle_error,
            MLGameDataType.SYSTEM_MSG: self._handle_system_msg,
            MLGameDataType.GAME_INFO: self._handle_game_info
        }
        try:
            while game_data := self._recv_data_func():
                logger.info(f"AzureUploader received data: {game_data}")
                handler = handlers.get(game_data.type)
                if handler:
                    handler(game_data)
                else:
                    logger.warning(f"No handler found for {game_data.type}")

                if game_data.type == MLGameDataType.GAME_RESULT or game_data.type == MLGameDataType.NONE:
                    break

        except Exception as e:
            self._comm_manager.send_exception(f"Exception on {self._proc_name}")
            logger.exception(e)
        finally:
            logger.info("AzureUploader finished")
    def _handle_game_info(self, game_data: MLGameEntityWrapperSchema) -> None:
        """Handle game information data"""
        try:
            self._filename = "init.json"
            upload_data = [game_data.model_dump(mode='json')]
            upload_data_to_azure_blob(self._az_url, self._filename, upload_data)
                
        except Exception as e:
            logger.error(f"Error handling game info data: {str(e)}")
            raise

    def _handle_progress(self, game_data: MLGameEntityWrapperSchema) -> None:
        """Handle game progress data"""
        try:
            self._progress_data.append(game_data.data)
            if len(self._progress_data) > self._post_count:
                self._filename = f"{self._file_count}.json"
                upload_data = [obj.model_dump(mode='json') for obj in self._progress_data[self._prev_count:self._post_count]]
                upload_data_to_azure_blob(self._az_url, self._filename, upload_data)
                self._prev_count = self._post_count
                self._post_count += self._get_next_count_bias()
                self._file_count += 1
        except Exception as e:
            logger.exception(e)
            
    def _get_next_count_bias(self):
        if self._file_count >=len(self._count_bias_list):
            return self._count_bias_list[-1]
        return self._count_bias_list[self._file_count]
    def _handle_result(self, game_data: MLGameEntityWrapperSchema) -> None:
        """Handle game result data"""
        try:
            if self._progress_data:
                self._filename = f"{self._file_count}-end.json"
                upload_data = [obj.model_dump(mode='json') for obj in self._progress_data[self._prev_count:]]
                upload_data_to_azure_blob(self._az_url, self._filename, upload_data)
                self._prev_count = len(self._progress_data)
                self._post_count = len(self._progress_data)
                self._file_count += 1
            if game_data:
                self._filename = "result.json"
                upload_data = [game_data.model_dump(mode='json')]
                upload_data_to_azure_blob(self._az_url, self._filename, upload_data)

            logger.info(f"Game result received: {game_data.data}")
        except Exception as e:
            logger.error(f"Error handling result data: {str(e)}")
            raise

    def _handle_error(self, game_data: MLGameEntityWrapperSchema) -> None:
        """Handle game error data"""
        try:
            error_msg = game_data.data

            logger.error(
                f"Game error received - Message: {error_msg}"
            )
        except Exception as e:
            logger.error(f"Error handling error data: {str(e)}")
            raise

    def _handle_system_msg(self, game_data: MLGameEntityWrapperSchema) -> None:
        """Handle system message data"""
        try:
            message = game_data.data
            logger.info(f"System message received: {message}")
        except Exception as e:
            logger.error(f"Error handling system message: {str(e)}")
            raise
