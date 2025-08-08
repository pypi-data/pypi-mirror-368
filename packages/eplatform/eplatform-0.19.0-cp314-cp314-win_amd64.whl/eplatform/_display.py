__all__ = [
    "change_display_orientation",
    "change_display_position",
    "change_display_refresh_rate",
    "change_display_size",
    "connect_display",
    "disconnect_display",
    "discover_displays",
    "Display",
    "DisplayConnectionChanged",
    "DisplayDisconnectedError",
    "DisplayMode",
    "DisplayMoved",
    "DisplayOrientation",
    "DisplayOrientationChanged",
    "DisplayRefreshRateChanged",
    "DisplayResized",
    "forget_displays",
    "get_displays",
    "get_sdl_display_id",
]

from enum import Enum
from typing import ClassVar
from typing import Collection
from typing import Generator
from typing import TypedDict

from eevent import Event
from egeometry import IRectangle
from emath import IVector2

from . import _eplatform
from ._eplatform import get_sdl_display_details
from ._eplatform import get_sdl_displays
from ._type import SdlDisplayId
from ._type import SdlDisplayOrientation


class DisplayDisconnectedError(RuntimeError):
    pass


class DisplayOrientation(Enum):
    NONE = _eplatform.SDL_ORIENTATION_UNKNOWN
    LANDSCAPE = _eplatform.SDL_ORIENTATION_LANDSCAPE
    LANDSCAPE_FLIPPED = _eplatform.SDL_ORIENTATION_LANDSCAPE_FLIPPED
    PORTRAIT = _eplatform.SDL_ORIENTATION_PORTRAIT
    PORTRAIT_FLIPPED = _eplatform.SDL_ORIENTATION_PORTRAIT_FLIPPED


class DisplayMode:
    def __init__(self, size: IVector2, refresh_rate: float) -> None:
        self._size = size
        self._refresh_rate = refresh_rate

    def __repr__(self) -> str:
        return (
            f"<DisplayMode "
            f"{self._size.x!r}x{self._size.y}px "
            f"@ {self._refresh_rate:.1f} hertz"
            f">"
        )

    @property
    def size(self) -> IVector2:
        return self._size

    @property
    def refresh_rate(self) -> float:
        return self._refresh_rate


class DisplayConnectionChanged(TypedDict):
    display: "Display"
    is_connected: bool


class DisplayOrientationChanged(TypedDict):
    display: "Display"
    orientation: DisplayOrientation


class DisplayMoved(TypedDict):
    display: "Display"
    position: IVector2


class DisplayResized(TypedDict):
    display: "Display"
    size: IVector2


class DisplayRefreshRateChanged(TypedDict):
    display: "Display"
    refresh_rate: float


class Display:
    _sdl_display: SdlDisplayId | None = None
    _name: str = ""
    _orientation: DisplayOrientation = DisplayOrientation.NONE
    _bounds: IRectangle = IRectangle(IVector2(0), IVector2(1))
    _refresh_rate: float | None = None
    _modes: tuple[DisplayMode, ...] = ()

    connection_changed: Event[DisplayConnectionChanged] = Event()
    connected: ClassVar[Event[DisplayConnectionChanged]] = Event()
    disconnected: Event[DisplayConnectionChanged] = Event()
    orientation_changed: Event[DisplayOrientationChanged] = Event()
    moved: Event[DisplayMoved] = Event()
    resized: Event[DisplayResized] = Event()
    refresh_rate_changed: Event[DisplayRefreshRateChanged] = Event()

    def __init__(self) -> None:
        self.connection_changed = Event()
        self.disconnected = Event()
        self.orientation_changed = Event()
        self.moved = Event()
        self.resized = Event()
        self.refresh_rate_changed = Event()

    def __repr__(self) -> str:
        if self._sdl_display is None:
            return "<Display>"
        return f"<Display {self._name!r}>"

    @property
    def is_connected(self) -> bool:
        return self._sdl_display is not None

    @property
    def is_primary(self) -> bool:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self.bounds.position == IVector2(0)

    @property
    def modes(self) -> Collection[DisplayMode]:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._modes

    @property
    def name(self) -> str:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._name

    @property
    def orientation(self) -> DisplayOrientation:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._orientation

    @property
    def bounds(self) -> IRectangle:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._bounds

    @property
    def refresh_rate(self) -> float | None:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._refresh_rate


def get_sdl_display_id(display: Display) -> SdlDisplayId:
    if not display.is_connected:
        raise DisplayDisconnectedError()
    assert display._sdl_display is not None
    return display._sdl_display


_displays: dict[SdlDisplayId, Display] = {}


def get_displays() -> Generator[Display, None, None]:
    yield from _displays.values()


def connect_display(sdl_display: SdlDisplayId) -> None:
    (
        display_name,
        display_orientation,
        display_x,
        display_y,
        display_w,
        display_h,
        display_refresh_rate,
        display_modes,
    ) = get_sdl_display_details(sdl_display)

    assert sdl_display not in _displays
    _displays[sdl_display] = display = Display()

    display._sdl_display = sdl_display
    display._name = display_name
    display._orientation = DisplayOrientation(display_orientation)
    display._bounds = IRectangle(IVector2(display_x, display_y), IVector2(display_w, display_h))
    display._refresh_rate = display_refresh_rate if display_refresh_rate > 0 else None
    display._modes = tuple(DisplayMode(IVector2(w, h), rr) for w, h, rr in display_modes)

    data: DisplayConnectionChanged = {"display": display, "is_connected": True}
    Display.connection_changed(data)
    Display.connected(data)


def disconnect_display(sdl_display: SdlDisplayId) -> None:
    display = _displays.pop(sdl_display)
    display._sdl_display = None

    data: DisplayConnectionChanged = {"display": display, "is_connected": False}
    Display.connection_changed(data)
    display.connection_changed(data)
    Display.disconnected(data)
    display.disconnected(data)


def discover_displays() -> None:
    for sdl_display in get_sdl_displays():
        connect_display(sdl_display)


def forget_displays() -> None:
    for display in list(_displays.keys()):
        disconnect_display(display)


def change_display_orientation(
    sdl_display: SdlDisplayId, sdl_display_orientation: SdlDisplayOrientation
) -> None:
    display = _displays[sdl_display]
    display._orientation = DisplayOrientation(sdl_display_orientation)

    data: DisplayOrientationChanged = {"display": display, "orientation": display._orientation}
    Display.orientation_changed(data)
    display.orientation_changed(data)


def change_display_position(sdl_display: SdlDisplayId, position: IVector2) -> None:
    display = _displays[sdl_display]
    display._bounds = IRectangle(position, display._bounds.size)

    data: DisplayMoved = {"display": display, "position": position}
    Display.moved(data)
    display.moved(data)


def change_display_size(sdl_display: SdlDisplayId, size: IVector2) -> None:
    display = _displays[sdl_display]
    display._bounds = IRectangle(display._bounds.position, size)

    data: DisplayResized = {"display": display, "size": size}
    Display.resized(data)
    display.resized(data)


def change_display_refresh_rate(sdl_display: SdlDisplayId, refresh_rate: float) -> None:
    display = _displays[sdl_display]
    display._refresh_rate = refresh_rate

    data: DisplayRefreshRateChanged = {"display": display, "refresh_rate": refresh_rate}
    Display.refresh_rate_changed(data)
    display.refresh_rate_changed(data)
