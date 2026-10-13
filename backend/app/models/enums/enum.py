from enum import StrEnum


class OrderEnum(StrEnum):
    """
    Enum класс, который хранит виды статусов заказа
    """
    
    ERROR = 'error'
    PROCESS = 'process'
    COMPLETE = 'complete'