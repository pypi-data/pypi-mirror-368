from datetime import datetime, timezone

import boto3


def link_dynamo_table(
    table: str,
    access_key: str,
    secret_key: str,
    endpoint_url: str = "",
    region: str = "cn-northwest-1",
):
    """Link to a DynamoDB table."""
    dynamodb_kwargs = {
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "region_name": region,
    }
    if endpoint_url:
        dynamodb_kwargs["endpoint_url"] = endpoint_url
    dynamodb = boto3.resource(
        "dynamodb",
        **dynamodb_kwargs,
    )
    return dynamodb.Table(table)


class LogTimeHelper:
    @classmethod
    def current_month(cls):
        return f"{datetime.now(timezone.utc):%Y-%m}"

    @classmethod
    def current_day(cls):
        return f"{datetime.now(timezone.utc):%Y-%m-%d}"

    @classmethod
    def current_time(cls):
        return f"{datetime.now(timezone.utc):%H:%M:%S:%f}"
