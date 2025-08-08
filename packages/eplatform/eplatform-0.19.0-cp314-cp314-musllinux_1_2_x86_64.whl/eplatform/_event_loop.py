__all__ = ["idle", "EventLoop"]

from asyncio import SelectorEventLoop
from selectors import SelectSelector
from time import time
from typing import Any
from typing import Callable
from typing import Collection
from typing import Final
from typing import Mapping
from typing import get_args

from eevent import Event
from emath import IVector2

from . import _eplatform
from ._controller import connect_controller
from ._controller import controller_change_axis
from ._controller import controller_change_button
from ._controller import controller_change_hat
from ._controller import disconnect_controller
from ._display import change_display_orientation
from ._display import change_display_position
from ._display import change_display_refresh_rate
from ._display import change_display_size
from ._display import connect_display
from ._display import disconnect_display
from ._eplatform import get_sdl_event
from ._keyboard import KeyboardKeyLocation
from ._keyboard import change_key
from ._mouse import change_mouse_button
from ._mouse import change_mouse_position
from ._mouse import scroll_mouse_wheel
from ._platform import get_keyboard
from ._platform import get_mouse
from ._platform import get_window
from ._type import SdlDisplayId
from ._type import SdlDisplayOrientation
from ._type import SdlEventType
from ._type import SdlHat
from ._type import SdlJoystickId
from ._type import SdlMouseButton
from ._type import SdlScancode
from ._window import blur_window
from ._window import close_window
from ._window import focus_window
from ._window import hide_window
from ._window import input_window_text
from ._window import maximize_window
from ._window import move_window
from ._window import resize_window
from ._window import show_window
from ._window import unmaximize_window

idle: Event[None] = Event()


class EventLoop(SelectorEventLoop):
    def __init__(self) -> None:
        selector = _Selector()
        super().__init__(selector)
        # _ready is an implementation detail of asyncio.base_events.BaseEventLoop
        # it's the only way of determining if there are callbacks ready to be processed or if
        # the "idle" event can be sent
        selector._ready_callbacks = self._ready  # type: ignore


class _Selector(SelectSelector):
    _ready_callbacks: Any = None

    def select(self, timeout: float | None = None) -> Any:
        start = time()
        if self._poll_sdl_events():
            return []
        result = super().select(-1)
        if (
            not self._ready_callbacks
            and not result
            and not (timeout is not None and time() - start > timeout)
        ):
            idle(None)
        return result

    def _poll_sdl_events(self) -> bool:
        while True:
            event = get_sdl_event()
            if event is None:
                return False
            if self._handle_sdl_event(*event):
                return True

    def _handle_sdl_event(self, event_type: SdlEventType, *args: Any) -> bool:
        try:
            handler = self._SDL_EVENT_DISPATCH[event_type]
        except KeyError:
            return False
        return handler(self, *args)

    def _handle_sdl_event_quit(self) -> bool:
        close_window(get_window())
        return True

    def _handle_sdl_event_mouse_motion(self, position: IVector2, delta: IVector2) -> bool:
        mouse = get_mouse()
        change_mouse_position(mouse, position, delta)
        return True

    def _handle_sdl_event_mouse_wheel(self, delta: IVector2) -> bool:
        mouse = get_mouse()
        scroll_mouse_wheel(mouse, delta)
        return True

    def _handle_sdl_event_mouse_button_changed(
        self, button: SdlMouseButton, is_pressed: bool
    ) -> bool:
        mouse = get_mouse()
        change_mouse_button(mouse, button, is_pressed)
        return True

    def _handle_sdl_event_key_changed(
        self, key: SdlScancode, is_pressed: bool, is_repeat: bool
    ) -> bool:
        return change_key(get_keyboard(), key, is_pressed, is_repeat)

    def _handle_sdl_event_text_input(self, text: str) -> bool:
        input_window_text(get_window(), text)
        return True

    def _handle_sdl_event_window_resized(self, size: IVector2) -> bool:
        resize_window(get_window(), size)
        return True

    def _handle_sdl_event_window_shown(self) -> bool:
        show_window(get_window())
        return True

    def _handle_sdl_event_window_hidden(self) -> bool:
        hide_window(get_window())
        return True

    def _handle_sdl_event_window_moved(self, position: IVector2) -> bool:
        move_window(get_window(), position)
        return True

    def _handle_sdl_event_display_added(self, sdl_display: SdlDisplayId) -> bool:
        connect_display(sdl_display)
        return True

    def _handle_sdl_event_display_removed(self, sdl_display: SdlDisplayId) -> bool:
        disconnect_display(sdl_display)
        return True

    def _handle_sdl_event_display_orientation(
        self, sdl_display: SdlDisplayId, sdl_display_orientation: SdlDisplayOrientation
    ) -> bool:
        change_display_orientation(sdl_display, sdl_display_orientation)
        return True

    def _handle_sdl_event_display_moved(
        self, sdl_display: SdlDisplayId, position: IVector2
    ) -> bool:
        change_display_position(sdl_display, position)
        return True

    def _handle_sdl_event_current_mode_changed(
        self, sdl_display: SdlDisplayId, size: IVector2, refresh_rate: float
    ) -> bool:
        change_display_size(sdl_display, size)
        change_display_refresh_rate(sdl_display, refresh_rate)
        return True

    def _handle_sdl_event_window_focus_gained(self) -> bool:
        focus_window(get_window())
        return True

    def _handle_sdl_event_window_focus_lost(self) -> bool:
        blur_window(get_window())
        return True

    def _handle_sdl_event_joystick_added(self, sdl_joystick: SdlJoystickId) -> bool:
        connect_controller(sdl_joystick)
        return True

    def _handle_sdl_event_joystick_removed(self, sdl_joystick: SdlJoystickId) -> bool:
        disconnect_controller(sdl_joystick)
        return True

    def _handle_sdl_event_joystick_axis_motion(
        self, sdl_joystick: SdlJoystickId, axis_index: int, value: float
    ) -> bool:
        return controller_change_axis(sdl_joystick, axis_index, value)

    def _handle_sdl_event_joystick_button_down(
        self, sdl_joystick: SdlJoystickId, button_index: int
    ) -> bool:
        return controller_change_button(sdl_joystick, button_index, True)

    def _handle_sdl_event_joystick_button_up(
        self, sdl_joystick: SdlJoystickId, button_index: int
    ) -> bool:
        return controller_change_button(sdl_joystick, button_index, False)

    def _handle_sdl_event_joystick_hat_motion(
        self, sdl_joystick: SdlJoystickId, hat_index: int, value: SdlHat
    ) -> bool:
        return controller_change_hat(sdl_joystick, hat_index, value)

    def _handle_sdl_event_window_maximized(self):
        maximize_window(get_window())
        return True

    def _handle_sdl_event_window_restored(self):
        unmaximize_window(get_window())
        return True

    _SDL_EVENT_DISPATCH: Final[Mapping[SdlEventType, Callable[..., bool]]] = {
        _eplatform.SDL_EVENT_QUIT: _handle_sdl_event_quit,
        _eplatform.SDL_EVENT_MOUSE_MOTION: _handle_sdl_event_mouse_motion,
        _eplatform.SDL_EVENT_MOUSE_WHEEL: _handle_sdl_event_mouse_wheel,
        _eplatform.SDL_EVENT_MOUSE_BUTTON_DOWN: _handle_sdl_event_mouse_button_changed,
        _eplatform.SDL_EVENT_MOUSE_BUTTON_UP: _handle_sdl_event_mouse_button_changed,
        _eplatform.SDL_EVENT_KEY_DOWN: _handle_sdl_event_key_changed,
        _eplatform.SDL_EVENT_KEY_UP: _handle_sdl_event_key_changed,
        _eplatform.SDL_EVENT_TEXT_INPUT: _handle_sdl_event_text_input,
        _eplatform.SDL_EVENT_WINDOW_RESIZED: _handle_sdl_event_window_resized,
        _eplatform.SDL_EVENT_WINDOW_SHOWN: _handle_sdl_event_window_shown,
        _eplatform.SDL_EVENT_WINDOW_HIDDEN: _handle_sdl_event_window_hidden,
        _eplatform.SDL_EVENT_WINDOW_MOVED: _handle_sdl_event_window_moved,
        _eplatform.SDL_EVENT_WINDOW_FOCUS_GAINED: _handle_sdl_event_window_focus_gained,
        _eplatform.SDL_EVENT_WINDOW_FOCUS_LOST: _handle_sdl_event_window_focus_lost,
        _eplatform.SDL_EVENT_DISPLAY_ADDED: _handle_sdl_event_display_added,
        _eplatform.SDL_EVENT_DISPLAY_REMOVED: _handle_sdl_event_display_removed,
        _eplatform.SDL_EVENT_DISPLAY_ORIENTATION: _handle_sdl_event_display_orientation,
        _eplatform.SDL_EVENT_DISPLAY_MOVED: _handle_sdl_event_display_moved,
        _eplatform.SDL_EVENT_DISPLAY_CURRENT_MODE_CHANGED: _handle_sdl_event_current_mode_changed,
        _eplatform.SDL_EVENT_JOYSTICK_ADDED: _handle_sdl_event_joystick_added,
        _eplatform.SDL_EVENT_JOYSTICK_REMOVED: _handle_sdl_event_joystick_removed,
        _eplatform.SDL_EVENT_JOYSTICK_AXIS_MOTION: _handle_sdl_event_joystick_axis_motion,
        _eplatform.SDL_EVENT_JOYSTICK_BUTTON_DOWN: _handle_sdl_event_joystick_button_down,
        _eplatform.SDL_EVENT_JOYSTICK_BUTTON_UP: _handle_sdl_event_joystick_button_up,
        _eplatform.SDL_EVENT_JOYSTICK_HAT_MOTION: _handle_sdl_event_joystick_hat_motion,
        _eplatform.SDL_EVENT_WINDOW_MAXIMIZED: _handle_sdl_event_window_maximized,
        _eplatform.SDL_EVENT_WINDOW_RESTORED: _handle_sdl_event_window_restored,
    }
