import math
from abc import ABCMeta, abstractmethod
from typing import Any, Type

from quantification import inject, Field

factor_cache: dict[Type["BaseFactor"], Any] = {}


class OP:
    @staticmethod
    def _create_combined_class(operands, func):
        combined_fields: list[Field] = []
        for operand in operands:
            if isinstance(operand, type) and issubclass(operand, BaseFactor):
                combined_fields += operand.fields

        class CombinedFactor(BaseFactor):
            fields = list(set(combined_fields))

            @classmethod
            def run(cls, **kwargs):
                if not factor_cache.get(cls):
                    factor_cache[cls] = cls.calculate(**kwargs)

                return factor_cache[cls]

            @classmethod
            def calculate(cls, **kwargs):
                # 解析操作数为实际值
                resolved_operands = []
                for op in operands:
                    if isinstance(op, type) and issubclass(op, BaseFactor):
                        resolved_operands.append(op.run(**kwargs))
                    else:
                        resolved_operands.append(op)

                # 执行运算函数
                return func(*resolved_operands)

        return CombinedFactor

    @staticmethod
    def add(left, right):
        return OP._create_combined_class([left, right], lambda a, b: a + b)

    @staticmethod
    def sub(left, right):
        return OP._create_combined_class([left, right], lambda a, b: a - b)

    @staticmethod
    def mul(left, right):
        return OP._create_combined_class([left, right], lambda a, b: a * b)

    @staticmethod
    def div(left, right):
        return OP._create_combined_class([left, right], lambda a, b: a / b)

    @staticmethod
    def pow(left, right):
        return OP._create_combined_class([left, right], lambda a, b: a ** b)

    @staticmethod
    def rpow(left, right):
        return OP._create_combined_class([left, right], lambda a, b: b ** a)

    @staticmethod
    def sin(factor):
        return OP._create_combined_class([factor], lambda a: math.sin(a))

    @staticmethod
    def cos(factor):
        return OP._create_combined_class([factor], lambda a: math.cos(a))

    @staticmethod
    def tan(factor):
        return OP._create_combined_class([factor], lambda a: math.tan(a))

    @staticmethod
    def exp(factor):
        return OP._create_combined_class([factor], lambda a: math.exp(a))

    @staticmethod
    def ln(factor):
        return OP._create_combined_class([factor], lambda a: math.log(a))

    @staticmethod
    def log(factor, base=math.e):
        return OP._create_combined_class([factor, base], lambda a, b: math.log(a, b))

    @staticmethod
    def sqrt(factor):
        return OP._create_combined_class([factor], lambda a: math.sqrt(a))

    @staticmethod
    def abs(factor):
        return OP._create_combined_class([factor], lambda a: abs(a))

    @staticmethod
    def neg(factor):
        return OP._create_combined_class([factor], lambda a: -a)


class FactorMeta(ABCMeta):
    def __add__(cls, other):
        return OP.add(cls, other)

    def __sub__(cls, other):
        return OP.sub(cls, other)

    def __mul__(cls, other):
        return OP.mul(cls, other)

    def __truediv__(cls, other):
        return OP.div(cls, other)

    def __pow__(cls, other):
        return OP.pow(cls, other)

    def __radd__(cls, other):
        return OP.add(other, cls)

    def __rsub__(cls, other):
        return OP.sub(other, cls)

    def __rmul__(cls, other):
        return OP.mul(other, cls)

    def __rtruediv__(cls, other):
        return OP.div(other, cls)

    def __rpow__(cls, other):
        return OP.rpow(other, cls)

    def __neg__(cls):
        return OP.neg(cls)

    def sin(cls):
        return OP.sin(cls)

    def cos(cls):
        return OP.cos(cls)

    def tan(cls):
        return OP.tan(cls)

    def exp(cls):
        return OP.exp(cls)

    def ln(cls):
        return OP.ln(cls)

    def sqrt(cls):
        return OP.sqrt(cls)

    def abs(cls):
        return OP.abs(cls)

    def neg(cls):
        return OP.neg(cls)

    def log(cls, base=math.e):
        return OP.log(cls, base)

    def pow(cls, exponent):
        return OP.pow(cls, exponent)

    def __repr__(self):
        return self.__name__

    __str__ = __repr__


class BaseFactor(metaclass=FactorMeta):
    fields: list[Field]

    def __init_subclass__(cls, **kwargs):
        assert hasattr(cls, 'fields'), \
            f"{cls.__name__}必须实现类属性fields"

        for field in cls.fields:
            assert isinstance(field, Field), \
                f"{cls.__name__}类属性fields元素必须为Field, 实际为{type(field)}"

    @classmethod
    def run(cls, **kwargs):
        kwargs["data"] = kwargs["query"](fields=cls.fields, stock=kwargs["stock"])
        if not factor_cache.get(cls):
            factor_cache[cls] = inject(cls.calculate, **kwargs)

        return factor_cache[cls]

    @classmethod
    @abstractmethod
    def calculate(cls, **kwargs):
        """计算因子值，子类需要重写此方法"""
        raise NotImplementedError("因子必须实现calculate方法")


def clear_cache():
    global factor_cache
    factor_cache.clear()


__all__ = ["BaseFactor", "OP", "clear_cache"]
