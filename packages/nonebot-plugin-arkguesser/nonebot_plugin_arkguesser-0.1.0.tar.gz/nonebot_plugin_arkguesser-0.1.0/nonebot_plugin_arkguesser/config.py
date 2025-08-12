from nonebot import get_plugin_config
from pydantic import BaseModel, Field

class Config(BaseModel):
    arkguesser_max_attempts: int = Field(10, alias="明日方舟最大尝试次数")
    arkguesser_default_rarity_range: str = Field("6", alias="明日方舟默认星级范围")
    arkguesser_default_mode: str = Field("大头", alias="明日方舟默认模式")

plugin_config = get_plugin_config(Config)