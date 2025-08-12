from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Union

from pydantic import BaseModel, model_validator

from mlgame.core.exceptions import ErrorEnum


class MLGameDataType(str, Enum):
    """Data type enum for MLGame"""

    GAME_PROGRESS = "game_progress"
    GAME_ERROR = "game_error"
    GAME_RESULT = "game_result"
    SYSTEM_MSG = "system_message"
    DEFAULT = "not_yet_set"
    GAME_INFO = "game_info"
    NONE = "none"
    END = "end"

class GameProgressSchema(BaseModel):
    """Data structure for game progress"""

    frame: int
    background: List[Dict[str, Any]] = []
    object_list: List[Dict[str, Any]] = []
    toggle: List[Dict[str, Any]] = []
    toggle_with_bias: List[Dict[str, Any]] = []
    foreground: List[Dict[str, Any]] = []
    game_sys_info: Dict[str, Any] = {}
    musics: List[Dict[str, Any]] = []
    sounds: List[Dict[str, Any]] = []



class GameInfoSchema(BaseModel):
    """Data structure for game initialization"""

    scene: Dict[str, Any]
    assets: List[Dict[str, Any]] = []
    background: List[Dict[str, Any]] = []
    musics: List[Dict[str, Any]] = []
    sounds: List[Dict[str, Any]] = []

class GameResultSchema(BaseModel):
    """Data structure for game result"""
    frame_used:int
    status:str
    attachment:List[Dict[str, Any]]

class GameErrorSchema(BaseModel):
    """Data structure for game errors"""

    error_type: ErrorEnum
    message: str = ""
    frame: int
    time_stamp: datetime = datetime.now(timezone.utc)


    class Config:
        arbitrary_types_allowed = True

class SystemMsgSchema(BaseModel):
    """Data structure for system messages"""

    message: str = ""


    class Config:
        arbitrary_types_allowed = True
    def __dict__(self):
        return {"message": self.message}


class MLGameEntityWrapperSchema(BaseModel):
    """Base schema for MLGame data exchange"""

    type: MLGameDataType = MLGameDataType.DEFAULT
    data: Union[GameProgressSchema, GameInfoSchema,GameResultSchema, GameErrorSchema,SystemMsgSchema,Dict[str, Any]]={}

    @model_validator(mode="after")
    def update_type_from_data(self):
        """Update the `type` field after the model is fully validated."""
        if isinstance(self.data, GameProgressSchema):
            self.type = MLGameDataType.GAME_PROGRESS
        elif isinstance(self.data, GameInfoSchema):
            self.type = MLGameDataType.GAME_INFO
        elif isinstance(self.data, GameResultSchema):
            self.type = MLGameDataType.GAME_RESULT
        elif isinstance(self.data, GameErrorSchema):
            self.type = MLGameDataType.GAME_ERROR
        elif isinstance(self.data, SystemMsgSchema):
            self.type = MLGameDataType.SYSTEM_MSG
        

        return self

    # class Config:
    #     arbitrary_types_allowed = True
