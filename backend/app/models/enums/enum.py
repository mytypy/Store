from enum import StrEnum


class OrderEnum(StrEnum):
    ERROR = 'error'
    PROCESS = 'process'
    COMPLETE = 'complete'