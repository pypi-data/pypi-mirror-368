from typing import Union, List, Tuple


class RecognizeOptions:
    def __init__(self, lang: str = None, speakers: Union[int, Tuple[int, int], List[int]] = None, stereo: bool = False):
        self.lang = lang
        if isinstance(speakers, int) or speakers is None:
            self.speakers = speakers
        elif isinstance(speakers, (list, tuple)) and len(speakers) == 2:
            self.speakers = (int(speakers[0]), int(speakers[1]))
        else:
            raise ValueError("speakers должен быть числом или массивом [min,max]")
        self.stereo = bool(stereo)

    def to_dict(self) -> dict:
        options = {
            "lang": self.lang,
            "stereo": self.stereo,
        }
        if isinstance(self.speakers, int):
            options["speakers"] = self.speakers
        elif isinstance(self.speakers, (list, tuple)) and len(self.speakers) == 2:
            options["min_speakers"] = self.speakers[0],
            options["max_speakers"] = self.speakers[1]

        return options
