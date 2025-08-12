from typing import List, Optional

from .enums import ListStages
from .task import Task
from .options import RecognizeOptions


class Recognitions:

    def __init__(self, api):
        self.api = api

    def list(self, page: int = 1, limit: int = 20, stage: Optional[ListStages] = None) -> List[Task]:
        if stage:
            path = f"/recognitions/{stage}"
        else:
            path = f"/recognitions"
        path = f"{path}?page={page}&per-page={limit}"
        response = self.api.request("GET", path).json()
        return [Task(api=self.api, id_=item["id"], data=item) for item in response['list']]

    def task(self, id_: str) -> Task:
        return Task(api=self.api, id_=id_).update()

    def count(self, stage: Optional[ListStages] = None) -> int:
        if stage:
            path = f"/recognitions/{stage}"
        else:
            path = f"/recognitions"
        path = f"{path}?page=1&per-page=1"
        response = self.api.request("GET", path).json()
        return response['count']

    def send_file(self, path: str, options: RecognizeOptions) -> Task:
        files = {"file": open(path, "rb")}
        data = options.to_dict()
        response = self.api.request("POST", "/recognitions/task/file", files=files, data=data).json()
        return Task(api=self.api, id_=response['id'], data=response)

    def send_link(self, url: str, options: RecognizeOptions) -> Task:
        data = options.to_dict()
        data["url"] = url
        response = self.api.request("POST", "/recognitions/task/link", data=data).json()
        return Task(api=self.api, id_=response['id'], data=response)
