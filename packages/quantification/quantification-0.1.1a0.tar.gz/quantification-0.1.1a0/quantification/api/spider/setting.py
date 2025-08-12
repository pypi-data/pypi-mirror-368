from pydantic import Field, BaseModel


class SpiderSetting(BaseModel):
    bduss: str = Field(description='百度cookie BDUSS')
