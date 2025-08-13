import json


class StopReceiveActionSyncArgs:

    def __init__(self, sender_ip: str = '', sender_port: int = 0, **kwargs):
        self.sender_ip = sender_ip
        self.sender_port = sender_port

        if "senderIP" in kwargs:
            self.sender_ip = kwargs.pop("senderIP")

        if "senderPort" in kwargs:
            self.sender_port = kwargs.pop("senderPort")

        self.extra_fields = kwargs

        if kwargs:
            print(f"Extra fields: {kwargs}")

    def to_dict(self):
        return {
            "senderIP": self.sender_ip,
            "senderPort": self.sender_port
        }

    def to_json(self):
        return json.dumps(self.to_dict())
