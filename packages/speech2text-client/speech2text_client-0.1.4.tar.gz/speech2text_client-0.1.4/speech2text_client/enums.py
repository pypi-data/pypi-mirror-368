from enum import Enum


class Formats(str, Enum):
    RAW = "raw"
    TXT = "txt"
    SRT = "srt"
    VTT = "vtt"
    JSON = "json"
    XML = "xml"


class ListStages(str, Enum):
    COMPLETE = "complete"
    ERRORS = "errors"
    PROCESSING = "processing"
