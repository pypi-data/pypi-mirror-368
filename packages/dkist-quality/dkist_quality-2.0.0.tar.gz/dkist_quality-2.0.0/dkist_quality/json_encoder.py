"""
Encoder and Decoder for JSON serialization
"""
import json
from datetime import datetime


class DatetimeEncoder(json.JSONEncoder):
    """
    A JSON encoder which encodes datetime(s) as iso formatted strings.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return {"iso_date": obj.isoformat("T")}
        return super().default(obj)


def datetime_json_object_hook(obj: dict):
    """
    Convert object being json decoded into a datetime object if
    in the format {"iso_date":"<iso formatted string>"} like those produced by
    the DatetimeEncoder
    :param obj: Dict of the object being json decoded
    :return: Datetime object
    """
    # extract date string if present in the object dict
    iso_date = obj.get("iso_date")
    if iso_date is not None:
        return datetime.fromisoformat(iso_date)
    return obj
