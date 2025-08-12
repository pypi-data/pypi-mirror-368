from pathlib import Path
from typing import Literal

import pydantic
from pydantic import AnyHttpUrl, BaseModel, Field


class MusicInitSchema(BaseModel):
    type: Literal["music"] = Field(default="music")
    music_id: str
    file_path: Path  # This will ensure the path is valid
    url: AnyHttpUrl



class SoundInitSchema(BaseModel):
    type: Literal["sound"] = Field(default="sound")
    sound_id: str
    file_path: Path  # This will ensure the path is valid
    url: AnyHttpUrl




class SoundProgressSchema(pydantic.BaseModel):
    type: Literal["sound"] = Field(default="sound")
    sound_id: str




class MusicProgressSchema(pydantic.BaseModel):
    type: Literal["music"] = Field(default="music")  # Default and required
    music_id: str




def create_music_init_data(music_id: str, file_path: str, github_raw_url: str):
    # assert file_path is valid
    return {
        "type": "music",
        "music_id": music_id,
        "file_path": file_path,
        "url": github_raw_url,
    }


def create_sound_init_data(sound_id: str, file_path: str, github_raw_url: str):
    # assert file_path is valid
    return {
        "type": "sound",
        "sound_id": sound_id,
        "file_path": file_path,
        "url": github_raw_url,
    }
