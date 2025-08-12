import sys
import time

from mlgame.argument.cmd_argument import parse_cmd_and_get_arg_obj
from mlgame.argument.tool import revise_ai_clients
from mlgame.core.process import create_process_of_az_uploader_and_start
from mlgame.executor.game import GameExecutor
from mlgame.executor.manual import GameManualExecutor
from mlgame.game.paia_game import get_paia_game_obj
from mlgame.utils.logger import logger
from mlgame.view.audio_model import MusicInitSchema, SoundInitSchema
from mlgame.view.sound_controller import SoundController

if __name__ == "__main__":
    import os

    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

    # 1. parse command line
    arg_obj = parse_cmd_and_get_arg_obj(sys.argv[1:])

    # 2. get parsed_game_params
    from mlgame.argument.game_argument import GameConfig

    game_config = GameConfig(arg_obj.game_folder.__str__())
    parsed_game_params = game_config.parse_game_params(arg_obj.game_params)
    # TODO use group AI
    ai_clients = revise_ai_clients(arg_obj.group_ai, game_config.user_num_config)
    user_num = len(ai_clients)
    game = get_paia_game_obj(game_config.game_cls, parsed_game_params, user_num,group_ai_list=ai_clients)

    # TODO refactor , process should not be init here   
    ai_process = []
    ws_proc = None
    record_proc = None
    az_upload_proc = None

    logger.info("===========Game is started ===========")
    from mlgame.core.communication import GameCommManager
    from mlgame.core.process import (
        create_process_of_ai_clients_and_start,
        create_process_of_ws_and_start,
        create_process_of_recorder_and_start,
        terminate,
    )
    from mlgame.view.view import PygameView, DummyPygameView

    game_comm = GameCommManager()
    try:
        if arg_obj.is_debug:
            logger.remove()
            logger.add(sys.stdout, level="DEBUG",format="<green>{time:YYYY-MM-DD HH:mm:ss.SSSSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
            logger.add(
                "debug.log",
                level="DEBUG",
                rotation="10 MB",  # Rotate after the log file reaches 10 MB
                retention=1,  # Keep only the most recent rotated log file
                compression=None,  # Do not compress the log file
            )
            pass

        if arg_obj.ws_url:
            # prepare transmitter for game executor
            ws_proc = create_process_of_ws_and_start(game_comm, str(arg_obj.ws_url))

        if arg_obj.record_folder:
            # prepare transmitter for game executor
            record_proc = create_process_of_recorder_and_start(
                game_comm, arg_obj.record_folder, arg_obj.progress_frame_frequency
            )
        if arg_obj.az_upload_url:
            # prepare transmitter for game executor
            az_upload_proc = create_process_of_az_uploader_and_start(
                game_comm, arg_obj.az_upload_url
            )
        # 4. prepare ai_clients , create pipe, start ai_client process
        if arg_obj.is_manual:
            # only play in local and manual mode and will show view
            # TODO to deprecated and use ml_play_manual.py to alternate
            game_view = PygameView(
                game.get_scene_init_data(),
                caption=f"PAIA Game: {game_config.game_name} v{game_config.game_version}",
                icon=game_config.logo
            )
            game_executor = GameManualExecutor(
                game,
                game_view,
                game_comm,
                fps=arg_obj.fps,
                one_shot_mode=arg_obj.one_shot_mode,
            )

        else:
            init_data = game.get_scene_init_data()

            # set sound
            sound_controller = SoundController(
                is_sound_on=arg_obj.is_sound_on,
                music_objs=[
                    MusicInitSchema(**obj) for obj in init_data.get("musics", [])
                ],
                sound_objs=[
                    SoundInitSchema(**obj) for obj in init_data.get("sounds", [])
                ],
            )
            # play game with ai_clients
            if arg_obj.no_display:
                logger.warning("Game will not be displayed.")
                game_view = DummyPygameView(game.get_scene_init_data())
            else:
                game_view = PygameView(
                    game.get_scene_init_data(),
                    caption=f"PAIA Game: {game_config.game_name} v{game_config.game_version}",
                    icon=game_config.logo,
                    sound_controller=sound_controller,
                )
            ai_process = create_process_of_ai_clients_and_start(
                game_comm=game_comm,
                ai_clients=ai_clients,
                game_params=parsed_game_params,
            )

            # 5. run game in main process


            game_executor = GameExecutor(
                game,
                game_comm,
                game_view,
                # sound_controller=sound_controller,
                fps=arg_obj.fps,
                one_shot_mode=arg_obj.one_shot_mode,
                no_display=arg_obj.no_display,
                output_folder=arg_obj.output_folder,
            )

        time.sleep(0.1)
        game_executor.run()

    except Exception as e:
        # finally
        logger.exception(e)
        pass
    finally:
        # TODO refactor , process should not be init here
        terminate(game_comm, ai_process, ws_proc, record_proc,az_upload_proc)
    logger.info("===========All process is terminated ===========")
    pass
