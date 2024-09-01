from __future__ import annotations
from PyQt6.QtCore import QObject
import re

class VersionModel(QObject):
    """ Semantic versioning """
    def __init__(self, major: int, minor: int=0, patch: int=0, parent: QObject|None=None):
        QObject.__init__(self, parent)
        self.major = major  # breaking updates
        self.minor = minor  # non-breaking major updates
        self.patch = patch  # non-breaking minor updates
        
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {str(self)}>"
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @classmethod
    def from_str(cls, value: str, parent: QObject|None=None) -> VersionModel:
        match = re.match("(\d+)\.(\d+)\.(\d+)", value)
        assert match is not None, f"Invalid Version Format: '{value}'"
        return cls(int(match[1]), int(match[2]), int(match[3]), parent)
    
    def compatible(self, other: VersionModel|int) -> bool:
        return self.major == (other.major if isinstance(other, VersionModel) else other)
