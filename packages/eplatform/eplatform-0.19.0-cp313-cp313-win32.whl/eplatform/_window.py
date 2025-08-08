from __future__ import annotations

__all__ = [
    "blur_window",
    "close_window",
    "delete_window",
    "focus_window",
    "get_sdl_window",
    "hide_window",
    "input_window_text",
    "maximize_window",
    "move_window",
    "resize_window",
    "show_window",
    "unmaximize_window",
    "Window",
    "WindowBufferSynchronization",
    "WindowDestroyedError",
    "WindowMoved",
    "WindowResized",
    "WindowTextInputted",
    "WindowVisibilityChanged",
]

from contextlib import contextmanager
from enum import Enum
from typing import Collection
from typing import Generator
from typing import TypedDict

from eevent import Event
from egeometry import IRectangle
from emath import FMatrix4
from emath import FVector4
from emath import IVector2

from ._display import Display
from ._display import DisplayMode
from ._display import get_sdl_display_id
from ._eplatform import center_sdl_window
from ._eplatform import create_sdl_window
from ._eplatform import delete_sdl_window
from ._eplatform import disable_sdl_window_text_input
from ._eplatform import enable_sdl_window_text_input
from ._eplatform import hide_sdl_window
from ._eplatform import maximize_sdl_window
from ._eplatform import set_sdl_window_always_on_top
from ._eplatform import set_sdl_window_border
from ._eplatform import set_sdl_window_fullscreen
from ._eplatform import set_sdl_window_icon
from ._eplatform import set_sdl_window_not_fullscreen
from ._eplatform import set_sdl_window_position
from ._eplatform import set_sdl_window_resizeable
from ._eplatform import set_sdl_window_size
from ._eplatform import set_sdl_window_title
from ._eplatform import show_sdl_window
from ._eplatform import swap_sdl_window
from ._type import SdlWindow
from ._window_icon import WindowIcon


class WindowBufferSynchronization(Enum):
    IMMEDIATE = 0
    VSYNC = 1
    ADAPTIVE_VSYNC = -1


class WindowTextInputted(TypedDict):
    text: str


class WindowResized(TypedDict):
    size: IVector2
    is_maximized: bool


class WindowMoved(TypedDict):
    position: IVector2


class WindowVisibilityChanged(TypedDict):
    is_visible: bool


class WindowDestroyedError(RuntimeError):
    pass


class Window:
    _sdl_window: SdlWindow | None = None

    moved: Event[WindowMoved] = Event()
    closed: Event[None] = Event()
    text_inputted: Event[WindowTextInputted] = Event()
    resized: Event[WindowResized] = Event()
    visibility_changed: Event[WindowVisibilityChanged] = Event()
    shown: Event[WindowVisibilityChanged] = Event()
    hidden: Event[WindowVisibilityChanged] = Event()
    focused: Event[None] = Event()
    blurred: Event[None] = Event()

    def __init__(self, gl_major_version: int, gl_minor_version: int) -> None:
        self._sdl_window, x, y = create_sdl_window(gl_major_version, gl_minor_version)

        self._title = ""

        self._position = IVector2(x, y)
        self.moved = Event()

        self.closed = Event()
        self.text_inputted = Event()

        self._size = IVector2(200, 200)
        self.resized = Event()

        self._is_visible = False
        self.visibility_changed = Event()
        self.shown = Event()
        self.hidden = Event()

        self._is_focused = False
        self.focused = Event()
        self.blurred = Event()

        self._is_resizeable = False
        self._is_bordered = True
        self._is_always_on_top = False
        self._is_fullscreen = False
        self._is_maximized = False

    def __del__(self) -> None:
        delete_window(self)

    def enable_text_input(self, rect: IRectangle, *, cursor_position: int = 0) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        enable_sdl_window_text_input(
            self._sdl_window,
            rect.position.x,
            rect.position.y,
            rect.size.x,
            rect.size.y,
            cursor_position,
        )

    def disable_text_input(self) -> None:
        if not self._sdl_window:
            return
        disable_sdl_window_text_input(self._sdl_window)

    @contextmanager
    def text_input(
        self, rect: IRectangle, *, cursor_position: int = 0
    ) -> Generator[None, None, None]:
        self.enable_text_input(rect, cursor_position=cursor_position)
        yield
        self.disable_text_input()

    def show(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        show_sdl_window(self._sdl_window)

    def hide(self) -> None:
        if not self._sdl_window:
            return
        hide_sdl_window(self._sdl_window)

    @property
    def is_visible(self) -> bool:
        return self._is_visible

    def center(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        center_sdl_window(self._sdl_window)

    def refresh(
        self, synchronization: WindowBufferSynchronization = WindowBufferSynchronization.IMMEDIATE
    ) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        swap_sdl_window(self._sdl_window, synchronization.value)

    def resize(self, value: IVector2) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_size(self._sdl_window, value)

    def move(self, value: IVector2) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_position(self._sdl_window, value)

    @property
    def position(self) -> IVector2:
        return self._position

    @property
    def size(self) -> IVector2:
        return self._size

    @property
    def is_bordered(self) -> bool:
        return self._is_bordered

    def show_border(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_border(self._sdl_window, True)
        self._is_bordered = True

    def hide_border(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_border(self._sdl_window, False)
        self._is_bordered = False

    @property
    def is_resizeable(self) -> bool:
        return self._is_resizeable

    def allow_resize(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_resizeable(self._sdl_window, True)
        self._is_resizeable = True

    def prevent_resize(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_resizeable(self._sdl_window, False)
        self._is_resizeable = False

    @property
    def is_always_on_top(self) -> bool:
        return self._is_always_on_top

    def force_always_on_top(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_always_on_top(self._sdl_window, True)
        self._is_always_on_top = True

    def allow_not_on_top(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_always_on_top(self._sdl_window, False)
        self._is_always_on_top = False

    @property
    def is_fullscreen(self) -> bool:
        return self._is_fullscreen

    def fullscreen(self, display: Display, mode: DisplayMode) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        sdl_display_id = get_sdl_display_id(display)
        set_sdl_window_fullscreen(
            self._sdl_window, sdl_display_id, mode.size.x, mode.size.y, mode.refresh_rate
        )
        self._is_fullscreen = True

    def window(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_not_fullscreen(self._sdl_window)
        self._is_fullscreen = False

    @property
    def is_focused(self) -> bool:
        return self._is_focused

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_title(self._sdl_window, value)
        self._title = value

    def set_icon(self, icon: WindowIcon, alternatives: Collection[WindowIcon]) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_icon(self._sdl_window, icon, *alternatives)

    @property
    def is_maximized(self) -> bool:
        return self._is_maximized

    def maximize(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        maximize_sdl_window(self._sdl_window)


def get_sdl_window(window: Window) -> SdlWindow:
    assert window._sdl_window is not None
    return window._sdl_window


def delete_window(window: Window) -> None:
    if window._sdl_window is None:
        return
    delete_sdl_window(window._sdl_window)
    window._sdl_window = None


def close_window(window: Window) -> None:
    Window.closed(None)
    window.closed(None)


def input_window_text(window: Window, text: str) -> None:
    data: WindowTextInputted = {"text": text}
    Window.text_inputted(data)
    window.text_inputted(data)


def show_window(window: Window) -> None:
    window._is_visible = True
    event_data: WindowVisibilityChanged = {"is_visible": True}
    Window.visibility_changed(event_data)
    window.visibility_changed(event_data)
    Window.shown(event_data)
    window.shown(event_data)


def hide_window(window: Window) -> None:
    window._is_visible = False
    event_data: WindowVisibilityChanged = {"is_visible": False}
    Window.visibility_changed(event_data)
    window.visibility_changed(event_data)
    Window.hidden(event_data)
    window.hidden(event_data)


def resize_window(window: Window, size: IVector2) -> None:
    window._size = size
    event_data: WindowResized = {"size": size, "is_maximized": window.is_maximized}
    Window.resized(event_data)
    window.resized(event_data)


def move_window(window: Window, position: IVector2) -> None:
    window._position = position
    event_data: WindowMoved = {"position": position}
    Window.moved(event_data)
    window.moved(event_data)


def focus_window(window: Window) -> None:
    window._is_focused = True
    Window.focused(None)
    window.focused(None)


def blur_window(window: Window) -> None:
    window._is_focused = False
    Window.blurred(None)
    window.blurred(None)


def maximize_window(window: Window) -> None:
    window._is_maximized = True
    event_data: WindowResized = {"size": window.size, "is_maximized": True}
    Window.resized(event_data)
    window.resized(event_data)


def unmaximize_window(window: Window) -> None:
    window._is_maximized = False
    event_data: WindowResized = {"size": window.size, "is_maximized": False}
    Window.resized(event_data)
    window.resized(event_data)
