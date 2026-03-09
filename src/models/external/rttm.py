from __future__ import annotations
from typing import List, Mapping
import os
from enum import Enum
import attr


class RTTMType(str, Enum):
    SEGMENT = "SEGMENT"
    SPEAKER = "SPEAKER"
    NOSCORE = "NOSCORE"
    NO_RT_METADATA = "NO_RT_METADATA"
    LEXEME = "LEXEME"
    NON_LEX = "NON-LEX"
    NON_SPEECH = "NON-SPEECH"
    SPKR_INFO = "SPKR-INFO"
    FILLER = "FILLER"
    EDIT = "EDIT"
    IP = "IP"
    SU = "SU"
    CB = "CB"


@attr.define(frozen=True)
class RTTMEntry:
    entry_type: RTTMType
    file_id: str
    channel: str
    start_s: float
    duration_s: float
    orthography: str
    speaker_type: str
    speaker_name: str
    confidence: str
    signal_lookahead_time: str

    @property
    def stop_s(self) -> float:
        return self.start_s + self.duration_s

    @property
    def label(self) -> str:
        return self.speaker_name

    def data(self) -> Mapping[str, object]:
        return {
            "type": self.entry_type.value,
            "file_id": self.file_id,
            "channel": self.channel,
            "start_s": self.start_s,
            "duration_s": self.duration_s,
            "stop_s": self.stop_s,
            "orthography": self.orthography,
            "speaker_type": self.speaker_type,
            "speaker_name": self.speaker_name,
            "confidence": self.confidence,
            "signal_lookahead_time": self.signal_lookahead_time,
        }

    @staticmethod
    def parse_value(value, dst_type=str):
        return None if value == "<NA>" else dst_type(value)

    @classmethod
    def parse(cls, line: str) -> RTTMEntry:
        parts = line.split()
        if len(parts) != 10:
            raise ValueError(f"Invalid RTTM line (expected 10 fields, got {len(parts)}): {line}")

        try:
            entry_type = RTTMType(parts[0])
        except ValueError as what:
            supported = ", ".join([member.value for member in RTTMType])
            raise ValueError(f"Unsupported RTTM type: {parts[0]}. Supported types: {supported}") from what


        return cls(
            entry_type=entry_type,
            file_id=cls.parse_value(parts[1]),
            channel=cls.parse_value(parts[2]),
            start_s=cls.parse_value(parts[3], float),
            duration_s=cls.parse_value(parts[4], float),
            orthography=cls.parse_value(parts[5]),
            speaker_type=cls.parse_value(parts[6]),
            speaker_name=cls.parse_value(parts[7]),
            confidence=cls.parse_value(parts[8]),
            signal_lookahead_time=cls.parse_value(parts[9]),
        )


@attr.define
class RTTMModel:
    entries: List[RTTMEntry] = attr.Factory(list)
    path: str | None = None

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)

    def data(self):
        return [entry.data() for entry in self.entries]

    def by_file(self) -> Mapping[str, List[RTTMEntry]]:
        entries_by_file = {}
        for entry in self.entries:
            entries_by_file.setdefault(entry.file_id, []).append(entry)
        return entries_by_file

    def speakers(self) -> List[str]:
        return sorted({entry.speaker_name for entry in self.entries})

    @classmethod
    def load(cls, path: str) -> RTTMModel:
        assert os.path.exists(path), f"RTTM File Not Found: {path}"
        entries: List[RTTMEntry] = []
        with open(path, "rt") as rttm_file:
            for line_id, raw_line in enumerate(rttm_file, start=1):
                line = raw_line.strip()
                if (not line) or line.startswith("#"):
                    continue
                try:
                    entries.append(RTTMEntry.parse(line))
                except Exception as what:
                    raise ValueError(f"RTTM parse error at line {line_id}: {what}") from what
        return cls(entries=entries, path=path)
