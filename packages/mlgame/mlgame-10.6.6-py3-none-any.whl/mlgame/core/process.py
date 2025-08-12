import time
from multiprocessing import Process, Pipe

from mlgame.argument.model import GroupAI
from mlgame.executor.az_uploader import AzureUploader
from mlgame.executor.recorder import ProgressLogExecutor
from mlgame.executor.websocket_executor import WebSocketExecutor
from mlgame.core.communication import GameCommManager, MLCommManager, TransitionCommManager
from mlgame.core.env import TIMEOUT
from mlgame.executor.ai_client import AIClientExecutor
from mlgame.utils.logger import logger


def create_process_of_ws_and_start(game_comm: GameCommManager, ws_url) -> Process:
    recv_pipe_for_game, send_pipe_for_ws = Pipe(False)
    recv_pipe_for_ws, send_pipe_for_game = Pipe(False)
    ws_comm = TransitionCommManager(recv_pipe_for_ws, send_pipe_for_ws)
    game_comm.add_comm_to_others("ws", recv_pipe_for_game, send_pipe_for_game)
    ws_executor = WebSocketExecutor(ws_uri=ws_url, ws_comm=ws_comm)
    process = Process(target=ws_executor.run, name="ws")
    # process = ws_executor
    process.start()
    # time.sleep(0.1)
    return process


def create_process_of_ai_clients_and_start(
        game_comm: GameCommManager, ai_clients: list[GroupAI], game_params: dict) -> list:
    """
    return a process list to main process and bind pipes to `game_comm`
    """
    ai_process = []
    for index, ai_client in enumerate(ai_clients):
        ai_group = ai_client.group
        ai_name = ai_client.ai_name
        recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
        recv_pipe_for_ml, send_pipe_for_game = Pipe(False)
        game_comm.add_comm_to_ml(
            ai_name,
            recv_pipe_for_game, send_pipe_for_game)
        ai_comm = MLCommManager(ai_name)
        ai_comm.set_comm_to_game(
            recv_pipe_for_ml, send_pipe_for_ml)
        ai_executor = AIClientExecutor(
            str(ai_client.ai_path), ai_comm,
            ai_name=ai_name,group=ai_group, game_params=game_params,ai_label=ai_client.ai_label)
        process = Process(target=ai_executor.run,
                          name=ai_name)
        process.start()
        ai_process.append(process)
    return ai_process


def create_process_of_recorder_and_start(game_comm: GameCommManager, progress_folder,
                                             progress_frame_frequency) -> Process:
    recv_pipe_for_game, send_pipe_for_pl = Pipe(False)
    recv_pipe_for_pl, send_pipe_for_game = Pipe(False)
    pl_comm = TransitionCommManager(recv_pipe_for_pl, send_pipe_for_pl)
    game_comm.add_comm_to_others("pl", recv_pipe_for_game, send_pipe_for_game)
    pl_executor = ProgressLogExecutor(progress_folder=progress_folder,
                                      progress_frame_frequency=progress_frame_frequency, pl_comm=pl_comm)
    process = Process(target=pl_executor.run, name="pl")
    process.start()
    # time.sleep(0.1)
    return process


def create_process_of_az_uploader_and_start(game_comm: GameCommManager, az_url) -> Process:
    recv_pipe_for_game, send_pipe_for_pl = Pipe(False)
    recv_pipe_for_pl, send_pipe_for_game = Pipe(False)
    pl_comm = TransitionCommManager(recv_pipe_for_pl, send_pipe_for_pl)
    game_comm.add_comm_to_others("az", recv_pipe_for_game, send_pipe_for_game)
    az_excutor = AzureUploader(pl_comm=pl_comm, az_blob_url=az_url)
    process = Process(target=az_excutor.run, name="az")
    process.start()
    # time.sleep(0.1)
    return process

def terminate(game_comm: GameCommManager, ai_process: list, ws_proc: Process, progress_proc: Process,az_proc:Process):
    logger.debug("Main process will terminate ai process")
    # 5.terminate
    for ai_proc in ai_process:
        # Send stop signal to all alive ml processes
        if ai_proc.is_alive():
            game_comm.send_to_ml(
                None, ai_proc.name)
            ai_proc.terminate()
    logger.debug("Main process will terminate ws process")

    if ws_proc:
        timeout = time.time() + TIMEOUT
        logger.info(f"wait to close ws for timeout : {TIMEOUT} s")
        ws_proc.terminate()
        while ws_proc.is_alive():
            time.sleep(0.5)
            if time.time() > timeout:
                logger.info("Force to terminate ws proc ")
                ws_proc.kill()
                ws_proc.join()
                break

            logger.info("wait to close ws .")
        logger.info(f"use {time.time() - timeout + TIMEOUT} to close.")

    if progress_proc:
        timeout = time.time() + TIMEOUT
        logger.info(f"wait to close progress for timeout : {TIMEOUT} s")
        while True:
            time.sleep(0.5)
            progress_proc.terminate()
            if time.time() > timeout:
                print("Force to terminate progress_proc proc ")
                progress_proc.kill()
                progress_proc.join()
                break
            elif not progress_proc.is_alive():
                break
            logger.info("wait to close progress_proc .")
        logger.info(f"use {time.time() - timeout + TIMEOUT} to close.")
    if az_proc:
        timeout = time.time() + TIMEOUT
        logger.info(f"wait to close progress for timeout : {TIMEOUT} s")
        while True:
            time.sleep(0.5)
            az_proc.terminate()
            if time.time() > timeout:
                print("Force to terminate az_proc ")
                az_proc.kill()
                az_proc.join()
                break
            elif not az_proc.is_alive():
                break
            logger.info("wait to close az_proc .")
        logger.info(f"use {time.time() - timeout + TIMEOUT} to close.")
    logger.debug("Game is terminated")
