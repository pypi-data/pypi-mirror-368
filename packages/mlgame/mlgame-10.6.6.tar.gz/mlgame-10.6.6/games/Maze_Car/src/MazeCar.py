import math

import pygame

from mlgame.game.paia_game import PaiaGame
from mlgame.utils.enum import get_ai_name
from mlgame.view.audio_model import create_music_init_data, MusicProgressSchema
from mlgame.view.decorator import check_game_progress, check_game_result
from mlgame.view.view_model import create_text_view_data, create_asset_init_data, create_image_view_data, \
    create_line_view_data, Scene, create_polygon_view_data, create_rect_view_data, create_scene_progress_data
from .env import *
from .mazeMode import MazeMode
from .points import Check_point

'''need some fuction same as arkanoid which without dash in the name of fuction'''


class MazeCar(PaiaGame):
    def __init__(self, user_num, map_num, time_to_play, map_file=None, *args, **kwargs):
        super().__init__(user_num=user_num)
        # self.game_type = game_type
        self.user_num = user_num
        self.is_single = False
        if self.user_num == 1:
            self.is_single = True
        # self.maze_id = map_num - 1
        self.game_end_time = time_to_play
        # self.sensor_num = sensor_num
        self.sensor_num = 5

        if map_file is None:
            map_file = path.join(MAP_FOLDER, f"map_{map_num}.json")
        self.map_file = map_file
        self.game_mode = MazeMode(self.user_num, self.map_file, self.game_end_time, self.sensor_num)
        # self.game_mode.sound_controller.play_music()
        self.is_running = self.isRunning()
        self.map_width = self.game_mode.map.width
        self.map_height = self.game_mode.map.height
        self.scene = Scene(WIDTH, HEIGHT, BG_COLOR)
        self.origin_car_pos = [0, 0]

    # self.origin_car_pos = self.game_mode.car_info[0]["center"]

    def update(self, cmd_dict):
        # self.game_mode.ticks()
        self.frame_count += 1
        self.game_mode.handle_event()
        self.game_mode.update_sprite(cmd_dict)
        if not self.isRunning():
            self.is_running = False
            return "RESET"
        for car in self.game_mode.cars:
            if self.origin_car_pos != [0, 0]:
                break
            self.origin_car_pos = car.get_info()["center"]

    def get_data_from_game_to_player(self):
        scene_info = self.get_scene_info
        player_info = {}
        for car in self.game_mode.car_info:
            # type of car is dictionary
            player_info[get_ai_name(int(car["id"]))] = {"frame": scene_info["frame"],
                                                        "status": car["status"],
                                                        "x": car["coordinate"][0],
                                                        "y": car["coordinate"][1],
                                                        "angle": (car["angle"] * 180 / math.pi) % 360,
                                                        "R_sensor": car["r_sensor_value"]["distance"],
                                                        "L_sensor": car["l_sensor_value"]["distance"],
                                                        "F_sensor": car["f_sensor_value"]["distance"],
                                                        "L_T_sensor": car["l_t_sensor_value"]["distance"],
                                                        "R_T_sensor": car["r_t_sensor_value"]["distance"],
                                                        "end_x": self.game_mode.end_point.get_info()["coordinate"][0],
                                                        "end_y": self.game_mode.end_point.get_info()["coordinate"][1],
                                                        }
        return player_info

    def reset(self):
        self.frame_count = 0
        self.game_mode = MazeMode(self.user_num, self.map_file, self.game_end_time, self.sensor_num)
        # self.game_mode.sound_controller.play_music()

    def isRunning(self):
        return self.game_mode.isRunning()

    @property
    def get_scene_info(self):
        """
        Get the scene information
        """
        scene_info = {
            "frame": self.game_mode.frame,
        }

        for car in self.game_mode.car_info:
            # type of car is dictionary
            scene_info[str(car["id"]) + "P_position"] = car["topleft"]
        return scene_info

    def get_scene_init_data(self) -> dict:
        """
        Get the scene and object information for drawing on the web
        """
        game_info = {
            "scene": self.scene.__dict__,
            "background": [],
            "assets": [],
            "map_width": self.game_mode.map.tileWidth * 20,
            "map_height": self.game_mode.map.tileHeight * 20
        }
        game_info["assets"].append(create_asset_init_data("info", 300, 700, INFO_PATH, INFO_URL))
        game_info["assets"].append(create_asset_init_data("bg_img", 1000, 700, BG_PATH, BG_URL))

        game_info["assets"].append(create_asset_init_data("endpoint", 60, 60, ENDPOINT_PATH, ENDPOINT_URL))
        game_info["assets"].append(create_asset_init_data("checkpoint", 60, 60, CHECKPOINT_PATH, CHECKPOINT_URL))
        game_info["assets"].append(create_asset_init_data("checkpoint_2", 60, 60, CHECKPOINT2_PATH, CHECKPOINT_URL))

        for car in self.game_mode.car_info:
            file_path = path.join(ASSET_IMAGE_DIR, CARS_NAME[car["id"]])
            url = CARS_URL[car["id"]]
            car_init_info = create_asset_init_data("car_0" + str(car["id"] + 1), 50, 40, file_path, url)
            game_info["assets"].append(car_init_info)

        for wall in self.game_mode.walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            vertices = [self.game_mode.trnsfer_box2d_to_pygame(v) for v in vertices]
            # game_info["background"].append(create_aapolygon_view_data("wall", vertices, WHITE))
            game_info["background"].append(create_polygon_view_data("wall", vertices, WALL_COLOR))
            # game_info["background"].append(
            #     create_text_view_data(f"({vertices[0][0]},{vertices[0][1]})",
            #                           vertices[0][0]-32, vertices[0][1], "#0000FF",
            #                           "12px Arial BOLD"))
        for wall in self.game_mode.slant_walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            vertices = [self.game_mode.trnsfer_box2d_to_pygame(v) for v in vertices]
            game_info["background"].append(create_polygon_view_data("wall", vertices, WALL_COLOR))

        # add coordinate p0 p1 p2 p3
        p0 = (16, 16)
        p1 = (656, 16)
        p2 = (656, 656)
        p3 = (16, 656)

        game_info["background"].append(
            create_text_view_data(f"(0,0)",
                                  p0[0], p0[1] - 12, HELP_TXT_COLOR,
                                  "12px Arial BOLD"))
        game_info["background"].append(
            create_rect_view_data(f"P0",
                                  p0[0], p0[1], 2, 2, HELP_TXT_COLOR))

        game_info["background"].append(
            create_text_view_data(f"(200,0)",
                                  p1[0] - 16, p1[1] - 12, HELP_TXT_COLOR,
                                  "12px Arial BOLD"))
        game_info["background"].append(
            create_rect_view_data(f"P1",
                                  p1[0], p1[1], 2, 2, HELP_TXT_COLOR))

        game_info["background"].append(
            create_text_view_data(f"(200,-200)",
                                  p2[0] - 16, p2[1] + 12, HELP_TXT_COLOR,
                                  "12px Arial BOLD"))
        game_info["background"].append(
            create_rect_view_data(f"P2",
                                  p2[0], p2[1], 2, 2, HELP_TXT_COLOR))

        game_info["background"].append(
            create_text_view_data(f"(0,-200)",
                                  p3[0], p3[1] + 12, HELP_TXT_COLOR,
                                  "12px Arial BOLD"))
        game_info["background"].append(
            create_rect_view_data(f"P3",
                                  p3[0], p3[1], 2, 2, HELP_TXT_COLOR))

        for p in self.game_mode.all_points:
            point_data = p.get_progress_data()
            game_info["background"].append(point_data)
            game_info["background"].append(
                create_text_view_data(f"({p.get_info()['coordinate'][0]},{p.get_info()['coordinate'][1]})",
                                      point_data['x'] - 12, point_data['y'] + 50,
                                      HELP_TXT_COLOR,
                                      "12px Arial BOLD"))
        game_info["musics"] = [
            create_music_init_data("bgm", file_path=BGM_PATH, github_raw_url=BGM_URL),
        ]
        return game_info

    @check_game_progress
    def get_scene_progress_data(self) -> dict:
        """
        Get the position of game objects for drawing on the web
        """
        background = []
        object_list = []
        toggle = []
        toggle_with_bias = []

        # if self.is_single:
        #     # 讓鏡頭跟著
        #     game_progress["game_sys_info"] = {"view_center_coordinate": [250 - self.game_mode.car_info[0]["center"][0],
        #                                                                  240 - self.game_mode.car_info[0]["center"][1]]}
        # else:
        #     # 鏡頭固定在車子出生的位置
        #     game_progress["game_sys_info"] = {"view_center_coordinate": [250 - self.origin_car_pos[0],
        #                                                                  240 - self.origin_car_pos[1]]}
        for p in self.game_mode.all_points:
            if isinstance(p, Check_point):
                point_data = p.get_progress_data()
                object_list.append(point_data)

        # end point
        object_list.append(self.game_mode.end_point.get_progress_data())
        # rect
        # game_progress["background"].append(create_image_view_data("bg_img", 0, 0, 860, 560))
        background.append(create_image_view_data("info", 700, 0, 300, 700))
        # game_progress["toggle"].append(create_image_view_data("bg_img", 0, 0, 860, 560))
        p = self.game_mode.trnsfer_box2d_to_pygame((0, 0))
        # for x in range(TILE_LEFTTOP[0], TILE_WIDTH + TILE_LEFTTOP[0]+1, TILESIZE):
        #     game_progress["toggle_with_bias"].append(create_line_view_data("x", x, TILE_LEFTTOP[1], x, TILE_HEIGHT+TILE_LEFTTOP[1], "#8c8c8c"))
        #
        # for y in range(TILE_LEFTTOP[1], TILE_HEIGHT + TILE_LEFTTOP[1]+1, TILESIZE):
        #     game_progress["toggle_with_bias"].append(create_line_view_data("y", TILE_LEFTTOP[0], y, TILE_WIDTH+TILE_LEFTTOP[0], y, "#8c8c8c"))
        # object_list.append(create_rect_view_data("rect", p[0], p[1], 10, 10, "#356425"))
        # info
        # game_progress["toggle"].append(create_image_view_data("info", 525, 40, 327, 480))
        # car

        # text
        background.append(
            create_text_view_data(f"{self.frame_count:4d}", 800, 40, WHITE, font_style="40px Arial"))
        background.append(create_text_view_data("frames", 815, 100, WHITE, font_style="20px Arial"))
        # game_progress["toggle"].append(create_text_view_data("{0:05d} frames".format(self.frame_count), 750, 100, WHITE, font_style="36px Arial"))
        for car in self.game_mode.car_info:
            y = 170
            x = 845
            # sensor_label = 'L'
            if car["is_running"]:
                background.append(
                    create_text_view_data(f"{'L  ':<9}{car['l_sensor_value']['distance']:0>5.1f}cm",
                                          x,
                                          y + 130 * (car["id"]), YELLOW,
                                          "15px Arial BOLD")
                )
                background.append(
                    create_text_view_data(f"{'LF':<8}{car['l_t_sensor_value']['distance']:0>5.1f}cm",
                                          x,
                                          y + 16 + 130 * (car["id"]), YELLOW,
                                          "15px Arial BOLD")
                )
                background.append(
                    create_text_view_data(f"{'F  ':<9}{car['f_sensor_value']['distance']:0>5.1f}cm",
                                          x,
                                          y + 32 + 130 * (car["id"]), RED,
                                          "15px Arial BOLD")
                )
                background.append(
                    create_text_view_data(f"{'R  ':<9}{car['r_sensor_value']['distance']:0>5.1f}cm",
                                          x,
                                          y + 48 + 130 * (car["id"]), BLUE,
                                          "15px Arial BOLD")
                )
                toggle_with_bias.append(
                    create_text_view_data(f"{'RF':<8}{car['r_t_sensor_value']['distance']:0>5.1f}cm",
                                          x,
                                          y + 64 + 130 * (car["id"]), BLUE,
                                          "15px Arial BOLD")
                )

                object_list.append(
                    create_line_view_data("l_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["l_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["l_sensor_value"]["coordinate"])[1],
                                          YELLOW, 3))

                object_list.append(
                    create_line_view_data("l_top_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["l_t_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["l_t_sensor_value"]["coordinate"])[1],
                                          YELLOW, 3))

                object_list.append(
                    create_line_view_data("r_top_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["r_t_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["r_t_sensor_value"]["coordinate"])[1],
                                          BLUE, 3))
                object_list.append(
                    create_line_view_data("r_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["r_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["r_sensor_value"]["coordinate"])[1],
                                          BLUE, 3))
                object_list.append(
                    create_line_view_data("f_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["f_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["f_sensor_value"]["coordinate"])[1],
                                          RED, 3))
            else:
                object_list.append(create_text_view_data("{0:4d} frames".format(car["end_frame"]),
                                                         x,
                                                         y + 32 + 130 * (car["id"]),
                                                         WHITE,
                                                         "18px Arial BOLD"))
        for car in self.game_mode.car_info:
            object_list.append(
                create_image_view_data("car_0" + str(car["id"] + 1), car["topleft"][0], car["topleft"][1],
                                       car['size'][0], car['size'][1],
                                       car["angle"])
            )
            toggle_with_bias.append(
                create_text_view_data(f"({car['coordinate'][0]},{car['coordinate'][1]})",
                                      car["topleft"][0] - 30, car["topleft"][1] + 30, CAR_COLOR[car['id']],
                                      "18px Arial BOLD"))
            """
            "x": car["coordinate"][0],
            "y": car["coordinate"][1],
            "angle": (car["angle"] * 180 / math.pi) % 360,
            """
        game_progress = create_scene_progress_data(
            frame=self.frame_count,
            background=background,
            object_list=object_list,
            foreground=[],
            toggle=toggle,
            toggle_with_bias=toggle_with_bias,
            musics=[MusicProgressSchema(music_id=f"bgm").__dict__],
            sounds=[]
        )
        return game_progress

    @check_game_result
    def get_game_result(self):
        """
        Get the game result for the web

        same_rank = {"玩家編號": str(user.car_no + 1) + "P",
        "單局排名": self.game_mode.ranked_user.index(ranking) + 1,
        "使用總幀數": user.end_frame,
        "遊戲總幀數限制":self.game_end_time,
        "使用時間百分比":round(user.end_frame/self.game_end_time,5)*100,
        "檢查點總數量":self.game_mode.check_point_num,
        "玩家通過檢查點數量": user.check_point,
        "玩家未通過檢查點數量": remain_point,
        "檢查點通過率": pass_percent,
        "檢查點未通過率": remain_percent,
        }

        """
        scene_info = self.get_scene_info
        result = self.game_mode.result
        rank = []
        for user in self.game_mode.ranked_user:
            if self.game_mode.check_point_num:

                pass_percent = round(user.check_point / self.game_mode.check_point_num, 5) * 100
                remain_point = self.game_mode.check_point_num - user.check_point
                remain_percent = 100 - pass_percent
            else:
                pass_percent = 0
                remain_point = 0
                remain_percent = 0

            same_rank = {
                "player_num": str(user.car_no + 1) + "P",
                "rank": user.rank,
                "used_frame": user.end_frame,
                "frame_limit": self.game_end_time,
                "frame_percent": round(user.end_frame / self.game_end_time * 100, 3),
                "total_checkpoints": self.game_mode.check_point_num,
                "check_points": user.check_point,
                "remain_points": remain_point,
                "pass_percent": pass_percent,
                "remain_percent": remain_percent,
                "score": user.score
            }
            rank.append(same_rank)

        return {"frame_used": scene_info["frame"],
                "status": self.game_mode.state,
                "attachment": rank,
                }

        pass

    def get_keyboard_command(self):
        """
        Get the command according to the pressed keys
        """
        if not self.isRunning():
            return {"1P": "RESET",
                    "2P": "RESET",
                    "3P": "RESET",
                    "4P": "RESET",
                    "5P": "RESET",
                    "6P": "RESET",
                    }
        key_pressed_list = pygame.key.get_pressed()
        cmd_1P = {"left_PWM": 0, "right_PWM": 0}
        cmd_2P = {"left_PWM": 0, "right_PWM": 0}
        cmd_3P = {"left_PWM": 0, "right_PWM": 0}
        cmd_4P = {"left_PWM": 0, "right_PWM": 0}
        cmd_5P = {"left_PWM": 0, "right_PWM": 0}
        cmd_6P = {"left_PWM": 0, "right_PWM": 0}

        if key_pressed_list[pygame.K_UP]:
            cmd_1P["left_PWM"] = 100
            cmd_1P["right_PWM"] = 100
        elif key_pressed_list[pygame.K_DOWN]:
            cmd_1P["left_PWM"] = -100
            cmd_1P["right_PWM"] = -100
        if key_pressed_list[pygame.K_LEFT]:
            cmd_1P["right_PWM"] += 100
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd_1P["left_PWM"] += 100

        if key_pressed_list[pygame.K_w]:
            cmd_2P["left_PWM"] = 100
            cmd_2P["right_PWM"] = 100
        elif key_pressed_list[pygame.K_s]:
            cmd_2P["left_PWM"] = -100
            cmd_2P["right_PWM"] = -100
        elif key_pressed_list[pygame.K_a]:
            cmd_2P["right_PWM"] += 100
        elif key_pressed_list[pygame.K_d]:
            cmd_2P["left_PWM"] += 100

        return {"1P": cmd_1P,
                "2P": cmd_2P,
                "3P": cmd_3P,
                "4P": cmd_4P,
                "5P": cmd_5P,
                "6P": cmd_6P}

    def trnsfer_box2d_to_pygame(self, coordinate):
        '''
        :param coordinate: vertice of body of box2d object
        :return: center of pygame rect
        '''
        return (
            (coordinate[0] - self.game_mode.pygame_point[0]) * PPM,
            (self.game_mode.pygame_point[1] - coordinate[1]) * PPM)
