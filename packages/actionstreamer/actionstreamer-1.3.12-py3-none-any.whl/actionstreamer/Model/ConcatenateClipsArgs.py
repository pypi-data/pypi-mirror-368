import json


class ConcatenateClipsArgs:

    def __init__(
        self,
        device_id: int,
        device_name: str,
        start_epoch: int,
        end_epoch: int,
        upload_url: str,
        postback_url: str,
        video_clips: list,
        **kwargs
    ):
        self.device_id = device_id
        self.device_name = device_name
        self.start_epoch = start_epoch
        self.end_epoch = end_epoch
        self.upload_url = upload_url
        self.postback_url = postback_url
        self.video_clips = video_clips

        camel_to_snake = {
            "deviceID": "device_id",
            "deviceName": "device_name",
            "startEpoch": "start_epoch",
            "endEpoch": "end_epoch",
            "uploadURL": "upload_url",
            "postbackURL": "postback_url",
            "videoClips": "video_clips"
        }

        for camel_key, snake_key in camel_to_snake.items():
            if camel_key in kwargs:
                setattr(self, snake_key, kwargs.pop(camel_key))

        self.extra_fields = kwargs

        if kwargs:
            print(f"Extra fields: {kwargs}")

    def to_dict(self):
        return {
            "deviceID": self.device_id,
            "deviceName": self.device_name,
            "startEpoch": self.start_epoch,
            "endEpoch": self.end_epoch,
            "uploadURL": self.upload_url,
            "postbackURL": self.postback_url,
            "videoClips": self.video_clips
        }

    def to_json(self):
        return json.dumps(self.to_dict())
