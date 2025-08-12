from loguru import logger

from mlgame.argument.cmd_argument import parse_cmd_and_get_arg_obj
from mlgame.argument.model import GroupAI, GroupEnum
from .env import GAMES_PATH, AI_CLIENTS_PATH, OUTPUT_PATH, get_path


def test_parse_output_folder_arg():
    arg_str = f"-o {OUTPUT_PATH} -i {get_path(AI_CLIENTS_PATH, 'arkanoid/rule/ml_play.py')} {get_path(GAMES_PATH, 'arkanoid')} "
    args = parse_cmd_and_get_arg_obj(arg_str.split(' '))

    assert "var" in str(args.output_folder)
    assert isinstance(args.group_ai[0], GroupAI)
    assert not args.is_manual


def test_parse_input_ai_arg():
    arg_str = f"-i {get_path(AI_CLIENTS_PATH, 'arkanoid/rule/ml_play.py')} {get_path(GAMES_PATH, 'arkanoid')} "
    args = parse_cmd_and_get_arg_obj(arg_str.split(' '))

    assert isinstance(args.group_ai[0], GroupAI)
    assert args.group_ai[0].ai_label == "1P"

    ai_label = "ai_label"
    arg_str = f"-i {get_path(AI_CLIENTS_PATH, 'arkanoid/rule/ml_play.py')},{ai_label} {get_path(GAMES_PATH, 'arkanoid')} "
    args = parse_cmd_and_get_arg_obj(arg_str.split(' '))

    assert isinstance(args.group_ai[0], GroupAI)
    assert args.group_ai[0].ai_label == ai_label


# def test_parse_cmd_with_group_ai_and_input_ai():
#     arg_str = (f"--group_ai A,1P,{get_path(AI_CLIENTS_PATH, 'arkanoid/dev/ml_play.py')},kylin2 " +
#                f"--group_ai B,2P,{get_path(AI_CLIENTS_PATH, 'arkanoid/dev/ml_play.py')},kylin3 " +
#                f"--group_ai B,3P,{get_path(AI_CLIENTS_PATH, 'arkanoid/dev/ml_play.py')},kylin4 " +
#                f"{get_path(GAMES_PATH, 'arkanoid')} ")
#     args = parse_cmd_and_get_arg_obj(arg_str.split(' '))
#
#     assert len(args.group_ai) == 3
#     assert isinstance(args.group_ai[0], GroupAI)
#     assert not args.is_manual
#     logger.info(args.group_ai)

#
# def test_parse_group_ai_cmd():
#     arg_str = (f"--group_ai A,1P,{get_path(AI_CLIENTS_PATH, 'arkanoid/dev/ml_play.py')},ai_label_1 " +
#                f"--group_ai A,2P,{get_path(AI_CLIENTS_PATH, 'arkanoid/dev/ml_play.py')},ai_label_2 " +
#                f"--group_ai B,3P,{get_path(AI_CLIENTS_PATH, 'arkanoid/dev/ml_play.py')},ai_label_3 " +
#                f"--group_ai B,4P,{get_path(AI_CLIENTS_PATH, 'arkanoid/dev/ml_play.py')},ai_label_4 " +
#                f"{get_path(GAMES_PATH, 'arkanoid')} ")
#
#     args = parse_cmd_and_get_arg_obj(arg_str.split(' '))
#
#     assert len(args.group_ai) == 4
#     assert isinstance(args.group_ai[0], GroupAI)
#     assert not args.is_manual
#
#     logger.warning(args.group_ai)


def test_enum():
    group = "A"
    assert group == GroupEnum.A
    assert group == GroupEnum(group)
    assert group == GroupEnum.A.value
    assert group != str(GroupEnum.A)


