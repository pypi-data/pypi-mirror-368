from typing import TypeVar, Generic
from datetime import date
from itertools import product

from pydantic import BaseModel

from .field import Field
from .panel import DataPanel
from .base_delegate import BaseDelegate

from ..logger import logger
from ..configure import config, Config

SettingType = TypeVar('SettingType', bound=BaseModel)


class BaseAPI(Generic[SettingType]):
    setting_class: type[BaseModel]
    delegate_classes: list[type[BaseDelegate[SettingType]]]

    def __init_subclass__(cls, **kwargs):
        assert hasattr(cls, "setting_class"), \
            f"{cls.__name__}必须实现类属性setting_class"

        assert issubclass(cls.setting_class, BaseModel), \
            f"{cls.__name__}类属性setting_class必须为BaseModel子类, 实际为{cls.setting_class}"

        assert hasattr(cls, "delegate_classes"), \
            f"{cls.__name__}必须实现类属性delegate_classes"

        assert isinstance(cls.delegate_classes, list), \
            f"{cls.__name__}类属性delegate_classes必须为列表, 实际为{type(cls.delegate_classes)}"

        for delegate_class in cls.delegate_classes:
            assert issubclass(delegate_class, BaseDelegate), \
                f"{cls.__name__}类属性delegate_classes的元素必须为BaseDelegate子类, 实际为{delegate_class}"

    def __init__(self):
        self.config = config
        self.setting: SettingType = self.setting_class.model_validate(config.model_dump())
        self.delegates = self.initialize_delegates()

    def initialize_delegates(self):
        return [i(self.config, self.setting) for i in self.delegate_classes]

    def query(self, start_date: date, end_date: date, fields: list[Field], **kwargs):
        fields_delegation: dict[BaseDelegate[SettingType], list[Field]] = {}

        picked = []
        for delegate, field in product(self.delegates, fields):
            if field in picked:
                continue

            if not delegate.has_field(field, **kwargs):
                continue

            if not fields_delegation.get(delegate):
                fields_delegation[delegate] = []

            fields_delegation[delegate].append(field)
            picked.append(field)

        omitted = set(fields) - set(picked)
        if omitted:
            logger.warning(f"无法查询的字段: {omitted}")

        res = DataPanel()

        for delegate, fields in fields_delegation.items():
            panel = delegate.execute(start_date, end_date, fields, **kwargs)
            res <<= panel

        return res

    def __repr__(self):
        return f"<API {self.__class__.__name__}>"

    __str__ = __repr__


class BaseCombinedAPI(BaseAPI):
    setting_class = Config
    delegate_classes = []

    api_classes: list[type[BaseAPI]]

    def __init_subclass__(cls, **kwargs):
        assert hasattr(cls, "api_classes"), \
            f"{cls.__name__}必须实现类属性api_classes"

        for api_class in cls.api_classes:
            assert issubclass(api_class, BaseAPI), \
                f"{cls.__name__}类属性delegate_classes元素必须为BaseAPI子类, 实际为{api_class}"

    def initialize_delegates(self):
        delegates = []

        for api_class in self.api_classes:
            delegates += api_class().delegates

        return delegates

    def __repr__(self):
        return f"<CombinedAPI {'|'.join(map(lambda x: x.__name__, self.api_classes))}>"

    __str__ = __repr__


__all__ = ["BaseAPI", "BaseCombinedAPI"]
