from enum import Enum
from PyQt6.QtGui import QIcon

# https://www.iconfinder.com/search/icons?family=unicons-line

class Icons(Enum):
    __ICON_FOLDER__ = "assets/icons/"
    Yavat           = "yavat.png"
    YavatTemplate   = "yavat_template.png"
    Close           = "close.png"
    Quit            = "quit.png"

    ColorDelete     = "error.png"

    MenuV           = "menu_v.png"
    MenuH           = "menu_v.png"
    Mute            = "mute.png"
    Sound           = "sound.png"
    Play            = "play.png"
    Pause           = "pause.png"
    Forward         = "forward.png"
    ForwardStep     = "forward_step.png"
    BackwardStep    = "backward_step.png"
    Backward        = "backward.png"
    Goto            = "goto.png"

    ZoomIn          = "zoom_in.png"
    ZoomOut         = "zoom_out.png"
    ZoomReset       = "zoom_reset.png"

    MoveUp          = "arrow_up.png"
    MoveDown        = "arrow_down.png"

    Event           = "event.png"
    EventAdd        = "event_add.png"
    EventInfo       = "event_info.png"
    EventRem        = "event_rem.png"

    Timeline        = "timeline.png"
    TimelineAdd     = "timeline_add.png"
    TimelineRem     = "timeline_rem.png"

    Timeseries      = "timeseries.png"
    
    ArrowFromLeft   = "arrow_from_left.png"
    ArrowFromRight  = "arrow_from_right.png"
    ArrowToLeft     = "arrow_to_left.png"
    ArrowToRight    = "arrow_to_right.png"

    Load            = "download.png"
    Import          = "import.png"
    Save            = "upload.png"
    Edit            = "edit.png"
    
    Visible         = "visible.png"
    Hidden          = "hidden.png"
    
    MessageOk       = "ok.png"
    MessageInfo     = "info.png"
    MessageWarning  = "warning.png"
    MessageError    = "error.png"
    
    Ignored         = "ignored.png"
    XValueClock     = "xvalue_clock.png"
    XValueCalendar  = "xvalue_calendar.png"
    YValueTS        = "yvalue_timeseries.png"
    YValueTL1       = "yvalue_timeline_1.png"
    YValueTLN       = "yvalue_timeline_n.png"
    
    def icon(self) -> QIcon:
        return QIcon(self.__ICON_FOLDER__ + self.value)
