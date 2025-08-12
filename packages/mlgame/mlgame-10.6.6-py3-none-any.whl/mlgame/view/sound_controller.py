import pygame
from loguru import logger

from mlgame.view.audio_model import MusicInitSchema, SoundInitSchema


def mixer_enabled(func):
    def wrapper(self, *args, **kwargs):
        if self._is_mixer_enabled:
            return func(self, *args, **kwargs)

    return wrapper


class SoundController:
    def __init__(self, is_sound_on: bool, music_objs: list[MusicInitSchema], sound_objs: [SoundInitSchema]):
        self._is_mixer_enabled = is_sound_on

        self._music_path_dict = {}
        self._sound_dict = {}
        self._current_music_id = ''
        self._is_paused = False
        self._volume = 1
        try:
            if self._is_mixer_enabled:
                pygame.mixer.init()
                pygame.mixer.music.set_volume(1)
                # store music obj
                for music in music_objs:
                    self._music_path_dict[music.music_id] = music.file_path
                    # self.play_music(music.music_id)

                # store sound obj
                for sound in sound_objs:
                    self._sound_dict[sound.sound_id] = pygame.mixer.Sound(sound.file_path)

        except Exception as e:
            logger.error(e)
            self._is_mixer_enabled = False

    @mixer_enabled
    def toggle_sound(self):
        if self._volume == 0:
            self._volume = 1
        else:
            self._volume = 0
        pygame.mixer.music.set_volume(self._volume)
        
        

    @mixer_enabled
    def play_music(self, music_id: str):
        music_path = self._music_path_dict.get(music_id, None)
        #  music_id is playing , dont change

        if self._current_music_id != music_id and music_path:
            self._current_music_id = music_id
            pygame.mixer.music.load(self._music_path_dict[music_id])
            pygame.mixer.music.play(-1)

        pass

    @mixer_enabled
    def play_sound(self, sound_id):
        sound_obj = self._sound_dict.get(sound_id, None)
        if sound_obj and self._volume:
            self._sound_dict[sound_id].play()
        pass

    @mixer_enabled
    def pause(self):
        if not self._is_paused :
            pygame.mixer.music.pause()
            self._is_paused = True

    @mixer_enabled
    def unpause(self):
        if self._is_paused :
            pygame.mixer.music.unpause()
            self._is_paused = False
