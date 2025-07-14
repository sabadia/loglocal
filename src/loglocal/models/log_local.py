import os

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing_extensions import ClassVar


class LogConfig(BaseSettings):
    level: str = Field(default="DEBUG")
    file_rotation: str = Field(default="30 days")
    file_retention: str = Field(default="90 days")
    serialize: bool = Field(default=True)
    enqueue: bool = Field(default=True)
    diagnose: bool = Field(default=False)  # avoid leaking vars in production

class LogLocal(BaseModel):
    log_path: str = os.path.join(os.path.expanduser("~"), ".local", "loglocal")
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message} | {extra}"
    log_level: str = "DEBUG"
    log_config: LogConfig = LogConfig()
