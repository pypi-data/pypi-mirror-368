from pydantic import Field, BaseModel


class TuShareSetting(BaseModel):
    tushare_token: str = Field(description='TuShare接口Token')
