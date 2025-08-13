import json


class CameraMultiplexArgs:

    def __init__(
        self,
        height: int = 1920,
        width: int = 1080,
        fps: float = 30,
        device_id: int = 0,
        **kwargs
    ):
        self.height = height
        self.width = width
        self.fps = fps
        self.device_id = device_id

        if "deviceID" in kwargs:
            self.device_id = kwargs.pop("deviceID")

        self.extra_fields = kwargs

        if kwargs:
            print(f"Extra fields: {kwargs}")

    def to_dict(self):
        return {
            "height": self.height,
            "width": self.width,
            "fps": self.fps,
            "deviceID": self.device_id
        }

    def to_json(self):
        return json.dumps(self.to_dict())
