import inspect
from dataclasses import dataclass
from typing import Optional

from log_dynamo.level import LogLevel
from log_dynamo.utils import link_dynamo_table, LogTimeHelper


@dataclass
class LogRecord:
    project: str = "app"
    app: str = "app"
    access_key: str = ""
    secret_key: str = ""
    endpoint_url: str = ""
    table_name: str = "log_record"

    def __post_init__(self):
        self.table = link_dynamo_table(
            self.table_name,
            self.access_key,
            self.secret_key,
            self.endpoint_url,
        )

    def write(self, log: str, level: LogLevel, user: Optional[int] = 0):
        func_name = [i.function for i in inspect.stack()][2]
        day = LogTimeHelper.current_day()
        pk = f"{self.project}#{day}"
        sk = f"{LogTimeHelper.current_time()}#{func_name}#{user}"
        self.table.put_item(
            Item={
                "pk": pk,
                "sk": sk,
                "app": self.app,
                "func": func_name,
                "level": level.value,
                "log": log,
                "user": user,
            }
        )

    def debug(self, text: str, user: int = 0):
        self.write(log=text, level=LogLevel.DEBUG, user=user)

    def info(self, text: str, user: int = 0):
        self.write(log=text, level=LogLevel.INFO, user=user)

    def warning(self, text: str, user: int = 0):
        self.write(log=text, level=LogLevel.WARNING, user=user)

    def error(self, text: str, user: int = 0):
        self.write(log=text, level=LogLevel.ERROR, user=user)
