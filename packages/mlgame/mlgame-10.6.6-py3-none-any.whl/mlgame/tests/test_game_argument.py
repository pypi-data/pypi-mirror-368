import logging
import os.path

from os import path
from mlgame.argument.tool import get_data_from_json_file
from mlgame.argument.game_argument import parse_game_config_data, GameConfig


def test_create_game_config():
    game_folder = os.path.join(os.path.dirname(__file__), "..", "..", "games", "swimming_squid_battle")
    game_config = GameConfig(game_folder=game_folder)
    # game_config._config_to_create_parser
    assert hasattr(game_config, 'game_config_parser')
    assert hasattr(game_config, 'game_version')
    assert hasattr(game_config, 'game_cls')

    assert game_config.logo
    assert os.path.exists(game_config.logo)
    

    game_params = "--level 3 --game_times 3".split(' ')
    parsed_game_params = game_config.parse_game_params(game_params)
    assert isinstance(parsed_game_params, dict)


def test_parse_game_config_file():
    config_file = path.join(path.dirname(__file__), "test_data", "game_config.json")
    config_data = get_data_from_json_file(config_file)
    params = config_data["game_params"]

    result = parse_game_config_data(config_data)
    assert result
    assert "()" in result
    for param in params:
        assert param["name"] in result
    logging.info(result)
