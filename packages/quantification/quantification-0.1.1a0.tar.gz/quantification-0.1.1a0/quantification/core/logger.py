import sys
from datetime import datetime

from loguru import logger as _logger
from pydantic import BaseModel
from loguru._datetime import datetime as _datetime

from .env import EnvGetter
from .configure import config


class Record(BaseModel):
    file: str
    func: str
    line: int
    level: str
    message: str


class Logger(EnvGetter):
    def __init__(self):
        super().__init__()

        _logger.remove()
        _logger.add(
            sink=self.sink,
            colorize=True,  # 在支持颜色的终端显示彩色日志
            backtrace=True,  # 记录异常堆栈
            diagnose=True,  # 显示变量值
            level=config.log_level,
            format=(
                "<g>{time:YYYY-MM-DD HH:mm:ss}</g> "
                "[<lvl>{level:^7}</lvl>] "
                "|函数 <r><u>{function}</u></r>: <c>{line}</c>行| "
                "{message}"
            ),
        )

        self.records: dict[str, list[Record]] = {}

    def sink(self, message):
        if not self.env:
            return

        sys.stdout.write(message)
        sys.stdout.flush()

        datetime_str = message.record["time"].isoformat()
        if datetime_str not in self.records:
            self.records[datetime_str] = []

        self.records[datetime_str].append(Record(
            file=message.record["file"].name,
            func=message.record["function"],
            line=message.record["line"],
            level=message.record["level"].name,
            message=message.record["message"]
        ))

    def hijack(self):
        if env := self.env:
            current = datetime.combine(env.date, env.time)
        else:
            current = datetime.now()
        return _logger.opt(depth=1).patch(lambda r: r.update(time=_datetime(
            year=current.year,
            month=current.month,
            day=current.day,
            hour=current.hour,
            minute=current.minute,
        )))

    def trace(self, msg):
        self.hijack().trace(msg)

    def debug(self, msg):
        self.hijack().debug(msg)

    def success(self, msg):
        self.hijack().success(msg)

    def info(self, msg):
        self.hijack().info(msg)

    def warning(self, msg):
        self.hijack().warning(msg)

    def error(self, msg):
        self.hijack().error(msg)


logger = Logger()

__all__ = ["logger", "Record"]
