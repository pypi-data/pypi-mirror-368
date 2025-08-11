from datetime import datetime


class JsonUtils:
    @staticmethod
    def serialize_datetime(obj):
        if isinstance(obj, dict):
            return {k: JsonUtils.serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [JsonUtils.serialize_datetime(i) for i in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj