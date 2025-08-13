import json


class ClearFlagQueueArgs:

    def __init__(self, flag_queue_name: str = '', **kwargs):
        self.flag_queue_name = flag_queue_name

        if "flagQueueName" in kwargs:
            self.flag_queue_name = kwargs.pop("flagQueueName")

        self.extra_fields = kwargs

        if kwargs:
            print(f"Extra fields: {kwargs}")

    def to_dict(self):
        return {
            "flagQueueName": self.flag_queue_name
        }

    def to_json(self):
        return json.dumps(self.to_dict())
