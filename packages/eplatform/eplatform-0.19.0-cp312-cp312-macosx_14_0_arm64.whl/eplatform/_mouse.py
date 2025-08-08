from __future__ import annotations

__all__ = [
    "change_mouse_button",
    "change_mouse_position",
    "Mouse",
    "MouseButton",
    "MouseButtonChanged",
    "MouseButtonLocation",
    "MouseMoved",
    "MouseScrolled",
    "MouseScrolledDirection",
    "scroll_mouse_wheel",
]

from enum import StrEnum
from typing import Final
from typing import Literal
from typing import Mapping
from typing import TypeAlias
from typing import TypedDict

from eevent import Event
from emath import IVector2

from . import _eplatform
from ._eplatform import hide_cursor
from ._eplatform import show_cursor
from ._platform import get_window
from ._type import SdlMouseButton


class MouseButtonLocation(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    FORWARD = "forward"
    BACK = "back"


class MouseButton:
    changed: Event[MouseButtonChanged] = Event()
    pressed: Event[MouseButtonChanged] = Event()
    released: Event[MouseButtonChanged] = Event()

    def __init__(self, location: MouseButtonLocation):
        self.location = location
        self.is_pressed = False

        self.changed = Event()
        self.pressed = Event()
        self.released = Event()

    def __repr__(self) -> str:
        return f"<MouseButton {self.location!r}>"


class Mouse:
    _buttons_by_location: Mapping[MouseButtonLocation, MouseButton]
    _position = IVector2(0)

    moved: Event[MouseMoved] = Event()

    scrolled: Event[MouseScrolled] = Event()
    scrolled_vertically: Event[MouseScrolledDirection] = Event()
    scrolled_up: Event[MouseScrolledDirection] = Event()
    scrolled_down: Event[MouseScrolledDirection] = Event()
    scrolled_horizontally: Event[MouseScrolledDirection] = Event()
    scrolled_left: Event[MouseScrolledDirection] = Event()
    scrolled_right: Event[MouseScrolledDirection] = Event()

    def __init__(self) -> None:
        self._buttons_by_location = {l: MouseButton(l) for l in MouseButtonLocation}

        self.moved = Event()

        self.scrolled = Event()
        self.scrolled_vertically = Event()
        self.scrolled_up = Event()
        self.scrolled_down = Event()
        self.scrolled_horizontally = Event()
        self.scrolled_left = Event()
        self.scrolled_right = Event()

    def get_button(self, location: MouseButtonLocation) -> MouseButton:
        return self._buttons_by_location[location]

    @property
    def position(self) -> IVector2:
        return self._position

    def show(self) -> None:
        show_cursor()

    def hide(self) -> None:
        hide_cursor()


_SDL_MOUSE_BUTTON_TO_LOCATION: Final[Mapping[SdlMouseButton, MouseButtonLocation]] = {
    _eplatform.SDL_BUTTON_LEFT: MouseButtonLocation.LEFT,
    _eplatform.SDL_BUTTON_MIDDLE: MouseButtonLocation.MIDDLE,
    _eplatform.SDL_BUTTON_RIGHT: MouseButtonLocation.RIGHT,
    _eplatform.SDL_BUTTON_X1: MouseButtonLocation.BACK,
    _eplatform.SDL_BUTTON_X2: MouseButtonLocation.FORWARD,
}


class MouseMoved(TypedDict):
    position: IVector2
    delta: IVector2


class MouseScrolled(TypedDict):
    delta: IVector2


class MouseScrolledDirection(TypedDict):
    delta: int


class MouseButtonChanged(TypedDict):
    button: MouseButton
    is_pressed: bool
    position: IVector2


def change_mouse_position(mouse: Mouse, position: IVector2, delta: IVector2) -> None:
    mouse._position = position
    event_data: MouseMoved = {"position": position, "delta": delta}
    Mouse.moved(event_data)
    mouse.moved(event_data)


def change_mouse_button(mouse: Mouse, sdl_mouse_button: SdlMouseButton, is_pressed: bool) -> None:
    button = mouse.get_button(_SDL_MOUSE_BUTTON_TO_LOCATION[sdl_mouse_button])
    button.is_pressed = is_pressed
    event_data: MouseButtonChanged = {
        "button": button,
        "is_pressed": is_pressed,
        "position": mouse.position,
    }
    MouseButton.changed(event_data)
    button.changed(event_data)
    if is_pressed:
        MouseButton.pressed(event_data)
        button.pressed(event_data)
    else:
        MouseButton.released(event_data)
        button.released(event_data)


def scroll_mouse_wheel(mouse: Mouse, delta: IVector2) -> None:
    scrolled_data: MouseScrolled = {"delta": delta}
    Mouse.scrolled(scrolled_data)
    mouse.scrolled(scrolled_data)
    if delta.y:
        y_data: MouseScrolledDirection = {"delta": delta.y}
        Mouse.scrolled_vertically(y_data)
        mouse.scrolled_vertically(y_data)
        if delta.y > 0:
            Mouse.scrolled_up(y_data)
            mouse.scrolled_up(y_data)
        else:
            assert delta.y < 0
            Mouse.scrolled_down(y_data)
            mouse.scrolled_down(y_data)
    if delta.x:
        x_data: MouseScrolledDirection = {"delta": delta.x}
        Mouse.scrolled_horizontally(x_data)
        mouse.scrolled_horizontally(x_data)
        if delta.x > 0:
            Mouse.scrolled_right(x_data)
            mouse.scrolled_right(x_data)
        else:
            assert delta.x < 0
            Mouse.scrolled_left(x_data)
            mouse.scrolled_left(x_data)
