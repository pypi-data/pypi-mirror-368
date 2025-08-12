from enum import Enum, auto

class Scope(Enum):
    CONTENT = auto()
    LOCATION = auto()
    NAME = auto()
    OWNERSHIP = auto()
    PERMISSIONS = auto()
    SYMLINK_TARGET = auto()
    TIMESTAMPS = auto()
