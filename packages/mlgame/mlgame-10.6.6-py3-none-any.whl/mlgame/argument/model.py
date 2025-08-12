import datetime
import os
from enum import Enum
from pathlib import Path
from typing import Union, List, Optional

from pydantic import AnyUrl, BaseModel, FilePath, DirectoryPath, field_validator, model_validator

from mlgame.core.env import FPS_MAX
from mlgame.utils.io import check_folder_existed_and_readable_or_create
from mlgame.utils.logger import logger


class GroupEnum(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    O = "O"


class AINameEnum(str, Enum):
    P1 = "1P"
    P2 = "2P"
    P3 = "3P"
    P4 = "4P"
    P5 = "5P"
    P6 = "6P"
    P7 = "7P"
    P8 = "8P"

class GroupAI(BaseModel):
    group:GroupEnum
    ai_name:AINameEnum
    ai_path: FilePath
    ai_label:str = ""
    
    @model_validator(mode="after")
    def set_ai_label_if_empty(self):
        if not self.ai_label:
            self.ai_label = self.ai_name
        return self


class MLGameArgument(BaseModel):
    """
    Data Entity to handle parsed cli arguments
    """
    fps: int = 30
    progress_frame_frequency: int = 300
    one_shot_mode: bool = False
    # ai_clients: Optional[List[FilePath]] = None
    is_manual: bool = False
    no_display: bool = True
    ws_url: Optional[AnyUrl] = None
    az_upload_url: Optional[AnyUrl] = None
    game_folder: DirectoryPath
    game_params: List[str]
    output_folder: Union[Path, None] = None
    record_folder: Union[Path, None] = None
    is_sound_on : bool = True
    is_debug: bool = False
    group_ai_orig: Optional[List[str]] = None
    labeled_ai_orig: Optional[List[str]] = None
    

    @property
    def group_ai(self)-> List[GroupAI]:
        group_ai = []
        if self.group_ai_orig:
            for entry in self.group_ai_orig:
                group, ai_name, ai_path,ai_label = entry.split(",")
                group_ai.append(GroupAI(group=group, ai_name=ai_name, ai_path=Path(ai_path), ai_label=ai_label))
        elif self.labeled_ai_orig:
            for i,ai_client_str in enumerate(self.labeled_ai_orig,start=1):
                if "," in ai_client_str:
                    ai_path,ai_label = ai_client_str.split(",")
                else:
                    ai_path = Path(ai_client_str)
                    ai_label = AINameEnum(f"{i}P")
                # group, ai_name, ai_path = entry.split(",")
                group_ai.append(GroupAI(group=GroupEnum.O, ai_name=AINameEnum(f"{i}P"), ai_path=Path(ai_path),ai_label=ai_label))
        return group_ai


    @field_validator('is_manual', mode='before')
    def update_manual(cls, v, values) -> bool:
        return not ("ai_clients" in values or "group_ai_orig" in values)

    @field_validator('output_folder', 'record_folder', mode='before')
    def update_folder(cls, v, values):
        if v is None:
            return None
        path = os.path.join(
            str(v),
            datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        )
        if check_folder_existed_and_readable_or_create(path):
            return path

    @field_validator('fps', mode='before')
    def clamp_fps(cls, v):
        fps_max = FPS_MAX
        fps_min = 1
        try:
            v = int(v)
            if v< fps_min or v> fps_max:
                logger.warning(
                    f"FPS should be between {fps_min} and {fps_max}, system will automatically clamp the fps"
                )
        except Exception:
            return 30  # fallback to default if not int
        return max(fps_min, min(fps_max, v))


class UserNumConfig(BaseModel):
    """
    Data Entity to handle user_num in game_config.json
    """
    min: int
    max: int

    @model_validator(mode="after")
    def max_should_be_larger_than_min(cls,values):
        assert values.min <= values.max
        return values
