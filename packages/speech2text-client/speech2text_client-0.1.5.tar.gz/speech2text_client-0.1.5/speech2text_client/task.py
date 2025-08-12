import time
from typing import Optional
from .enums import Formats
from .options import RecognizeOptions


class TaskStatus:
    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description


class FileMeta:
    def __init__(self, config: dict):
        self.duration = config['duration'] if 'duration' in config and isinstance(config['duration'], str) else None
        self.format = config['format'] if 'format' in config and isinstance(config['format'], str) else None
        self.channels = config['channels'] if 'channels' in config and isinstance(config['channels'], int) else None
        self.audio_format = config['audio_format'] if 'audio_format' in config and isinstance(config['audio_format'],
                                                                                              str) else None
        self.mime = config['mime'] if 'mime' in config and isinstance(config['mime'], str) else None


class Task:
    def __init__(self, api, id_: str, data: Optional[dict] = None):
        self.__api = api
        self.__id = id_
        if data is not None:
            self.__load_data(data)

    def update(self):
        resp = self.__api.request("GET", f"/recognitions/{self.__id}").json()
        self.__load_data(resp)
        return self

    def id(self) -> str:
        return self.__id

    def status(self) -> TaskStatus:
        return self.__status

    def meta(self) -> FileMeta:
        return self.__meta

    def recognize_options(self) -> RecognizeOptions:
        return self.__recognize_options

    def isPaid(self) -> bool:
        return self.__payment

    def source_type(self) -> str:
        return self.__resource['type'] if self.__resource['type'] is not None else None

    def source_file_name(self) -> str:
        return self.__resource['name'] if self.__resource is not None and self.__resource['type'] == 'file' else None

    def source_url(self) -> str:
        return self.__resource['url'] if self.__resource is not None and self.__resource['type'] == 'link' else None

    def wait(self, timeout: int = 120, interval: int = 5):
        start = time.time()
        while time.time() - start < timeout:
            st = self.update().status()
            if st.code != 100:  # 100 = processing
                break
            time.sleep(interval)
        return self

    def result(self, format_: Formats = 'txt'):
        if isinstance(format_, Formats):
            format_ = format_.value
        response = self.__api.request("GET", f"/recognitions/{self.__id}/result/{format_}").text
        return response

    def cancel(self) -> bool:
        response = self.__api.request("DELETE", f"/recognitions/{self.__id}")
        return response.get("success", False) if isinstance(response, dict) else True

    def __load_data(self, data):
        if 'file_meta' in data:
            self.__meta = FileMeta(data['file_meta'])
        if 'created' in data:
            self.__created = data['created']
        if 'status' in data:
            self.__status = TaskStatus(code=data['status']['code'], description=data['status']['description'])
        if 'resource' in data:
            self.__resource = data['resource']
        self.__payment = True if 'payment' in data and 'price' in data['payment'] and data['payment'][
            'price'] == 1 else False
        self.__recognize_options = RecognizeOptions()
        if 'options' in data:
            speakers = None
            if 'speakers' in data['options']:
                speakers = data['options']['speakers']
            elif 'min_speakers' in data['options'] or 'max_speakers' in data['options']:
                speakers = [
                    data['options']['min_speakers'] if 'min_speakers' in data['options'] and isinstance(
                        data['options']['min_speakers'], int) else None,
                    data['options']['max_speakers'] if 'max_speakers' in data['options'] and isinstance(
                        data['options']['max_speakers'], int) else None,
                ]
            self.__recognize_options.lang = data['options']['lang'] if 'lang' in data['options'] else None
            self.__recognize_options.stereo = data['options']['multi_channel'] if 'multi_channel' in data['options'] and \
                                                                                  data['options'][
                                                                                      'multi_channel'] == 1 else None
            self.__recognize_options.speakers = speakers
