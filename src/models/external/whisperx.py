from pydantic import BaseModel

class WhisperXWordModel(BaseModel):
    word: str
    start: float
    end: float
    score: float
    speaker: str|None = None

class WhisperXSegmentModel(BaseModel):
    start: float
    end: float
    text: str
    speaker: str
    words: list[WhisperXWordModel]

class WhisperXModel(BaseModel):
    segments: list[WhisperXSegmentModel]
    word_segments: list[WhisperXWordModel]
    language: str
