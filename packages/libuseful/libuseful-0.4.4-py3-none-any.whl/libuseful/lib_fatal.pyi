from .lib_singleton import *
from .lib_logger import *

__all__ = ['CFatalErr']

class CFatalErr(Singleton):
    class KEY:
        ID: str
        TYPE: str
        MODE: str
        PC_STAMP: str
        MSG: str
    class TYPE:
        NONE: str
        ADB: str
    class MODE:
        BROKEN: str
        INFINITE_WAIT: str
        OFFLINE: str
    def get_infos(self, type: TYPE = ...) -> dict: ...
    def get_info(self, id: str) -> dict: ...
    def set_info(self, type: TYPE, mode: MODE, err: str) -> str: ...
    def __init__(self) -> None: ...
    def __del__(self) -> None: ...
