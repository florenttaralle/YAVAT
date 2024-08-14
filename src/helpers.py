from PyQt6.QtMultimedia import QMediaPlayer

def media_status_str(status: int):
    match status:
        case QMediaPlayer.NoMedia:          return "NoMedia"
        case QMediaPlayer.LoadingMedia:     return "LoadingMedia"
        case QMediaPlayer.LoadedMedia:      return "LoadedMedia"
        case QMediaPlayer.StalledMedia:     return "StalledMedia"
        case QMediaPlayer.BufferingMedia:   return "BufferingMedia"
        case QMediaPlayer.BufferedMedia:    return "BufferedMedia"
        case QMediaPlayer.EndOfMedia:       return "EndOfMedia"
        case QMediaPlayer.InvalidMedia:     return "InvalidMedia"
    raise ValueError()


def media_state_str(state: int):
    match state:
        case QMediaPlayer.StoppedState:     return "StoppedState"
        case QMediaPlayer.PlayingState:     return "PlayingState"
        case QMediaPlayer.PausedState:      return "PausedState"
    raise ValueError()
