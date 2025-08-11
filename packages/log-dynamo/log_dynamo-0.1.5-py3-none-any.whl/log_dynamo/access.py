from dataclasses import dataclass

from log_dynamo.utils import link_dynamo_table, LogTimeHelper

@dataclass
class LogAccess:
    project: str = "app"
    access_key: str = ""
    secret_key: str = ""
    endpoint_url: str = ""
    table_name: str = "log_access"

    def __post_init__(self):
        self.table = link_dynamo_table(
            self.table_name,
            self.access_key,
            self.secret_key,
            self.endpoint_url,
        )

    def increase(self, app: str = "app", action: str = "GET /", func: str = "func"):
        month = LogTimeHelper.current_month()
        pk = f"{self.project}#{month}"
        self.table.update_item(
            Key={"pk": pk, "action": action},
            UpdateExpression="""
            SET 
                #c = if_not_exists(#c, :start) + :inc,
                #a = :app,
                #f = :func,
                #m = :month,
                #p = :project
        """,
            ExpressionAttributeNames={
                "#c": "count",
                "#a": "app",
                "#f": "func",
                "#m": "month",
                "#p": "project",
            },
            ExpressionAttributeValues={
                ":start": 0,
                ":inc": 1,
                ":app": app,
                ":func": func,
                ":month": month,
                ":project": self.project,
            },
            ReturnValues="UPDATED_NEW",
        )
