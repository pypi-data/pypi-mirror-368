import types
import inspect
import functools
from typing import Callable, Any

from pydantic import ValidationError, create_model, ConfigDict
from pydantic_core import PydanticUndefined


def to_str(x: Callable[..., Any]) -> str:
    """Convert a callable object to a descriptive string representation.

    Args:
        x: Any callable object (function, lambda, partial, class, method, etc.)

    Returns:
        A string representation of the callable.
    """
    # 1. Handle functools.partial objects
    if isinstance(x, functools.partial):
        func_str = to_str(x.func)
        args = [repr(a) for a in x.args]
        keywords = [f"{k}={repr(v)}" for k, v in x.keywords.items()]
        all_args = ", ".join(args + keywords)
        return f"functools.partial({func_str}, {all_args})"

    # 2. Handle classes (since classes are callable)
    if inspect.isclass(x):
        return f"{x.__module__}.{x.__qualname__}"

    # 3. Handle bound methods (instance methods and class methods)
    if isinstance(x, (types.MethodType, types.BuiltinMethodType)):
        method_name = x.__name__
        owner = x.__self__

        if inspect.isclass(owner):
            owner_str = owner.__qualname__
            return f"<bound method {owner_str}.{method_name}>"

        class_name = owner.__class__.__qualname__
        return f"<bound method {class_name}.{method_name} of {repr(owner)}>"

    if isinstance(x, (types.FunctionType, types.BuiltinFunctionType)):
        module = x.__module__
        qualname = x.__qualname__

        if qualname == '<lambda>':
            try:
                source = inspect.getsource(x).strip()
                if '\n' in source:
                    return f"<lambda at {module}:{x.__code__.co_firstlineno}>"
                return source
            except (OSError, TypeError):
                return "<lambda>"

        return f"{module}.{qualname}"

    # Fallback: Use standard string representation
    return str(x)


def get_function_location(func) -> str:
    """获取函数的定义位置（文件路径和行号）"""
    try:
        # 尝试获取函数的源文件和行号
        source_file = inspect.getsourcefile(func)
        lines, start_line = inspect.getsourcelines(func)
        end_line = start_line + len(lines) - 1

        # 如果是lambda函数，使用特殊格式
        if func.__name__ == '<lambda>':
            return f"lambda at {source_file}:{start_line}"

        return f"{source_file}:{start_line}-{end_line}"
    except Exception:
        # 如果无法获取位置信息，返回默认值
        return "<unknown location>"


def format_arg_type(value) -> str:
    """格式化参数类型信息，特别处理类对象"""
    if inspect.isclass(value):
        # 对于类对象，显示类名而不是元类
        return f"<class '{value.__module__}.{value.__qualname__}'>"
    return str(type(value))


def format_annotations(params) -> str:
    """格式化参数注解信息"""
    lines = []
    for name, param in params.items():
        # 跳过可变关键字参数
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            continue

        # 获取类型注解
        ann = param.annotation
        ann_str = ann.__name__ if ann is not param.empty else "Any"

        # 添加默认值信息
        default = ""
        if param.default is not param.empty:
            default = f" (默认值: {repr(param.default)})"

        # 添加参数类型标记
        kind = ""
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            kind = " [keyword-only]"
        elif param.kind == inspect.Parameter.POSITIONAL_ONLY:
            kind = " [positional-only]"

        lines.append(f"  - {name}: {ann_str}{default}{kind}")
    return "\n".join(lines)


def inject(func, **kwargs) -> Any:
    sig = inspect.signature(func)
    params = sig.parameters

    model_fields = {}
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            continue

        annotation = param.annotation
        if annotation is param.empty:
            annotation = Any

        default = PydanticUndefined
        if param.default is not param.empty:
            default = param.default

        model_fields[name] = (annotation, default)

    func_name = to_str(func)

    model = create_model(
        f"{func_name}_Params",
        __config__=ConfigDict(
            extra="allow",
            arbitrary_types_allowed=True,
            coerce_numbers_to_str=True
        ),
        **model_fields
    )

    try:
        validated = model(**kwargs)
    except ValidationError as e:
        errors = []
        for error in e.errors():
            loc = ".".join(map(str, error["loc"]))
            expected_type = " | ".join(error.get("ctx", {}).get("expected", ["未知类型"]))
            actual_type = type(kwargs.get(loc, "<missing>")).__name__
            msg = f"无法将类型 {actual_type} 转换为函数定义的类型 {expected_type}"
            input_value = error.get("input", "<missing>")

            errors.append(f"  - {loc}: {msg} (输入值: {input_value})")

        arg_types = "\n".join([
            f"  - {k}: {format_arg_type(v)}"
            for k, v in kwargs.items()
        ])

        raise TypeError(
            f"🚫 参数类型与可用参数不兼容，且强制转换失败，请检查 {func_name} 的定义:\n"
            f"📋 定义的参数:\n{format_annotations(params)}\n"
            f"📤 可用的全部参数(正确标准):\n{arg_types}\n"
            f"❌ 参数类型不匹配且转换失败:\n{"\n".join(errors)}\n"
            f"📍 函数定义位置: {get_function_location(func)}\n"
        )

    validated_data = validated.model_dump()

    if any((name for name, param in params.items() if param.kind == inspect.Parameter.VAR_KEYWORD)):
        return func(**validated_data)

    return func(**{p.name: validated_data[p.name] for p in params.values()})


__all__ = ["inject"]
