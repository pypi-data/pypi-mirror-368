__all__ = []

from typing import Collection

from emath import IVector2

from ._type import SdlDisplayId
from ._type import SdlDisplayOrientation
from ._type import SdlEventType
from ._type import SdlGamepadAxis
from ._type import SdlGamepadBindingType
from ._type import SdlGamepadButton
from ._type import SdlGamepadButtonLabel
from ._type import SdlGamepadType
from ._type import SdlGlContext
from ._type import SdlHat
from ._type import SdlJoystickId
from ._type import SdlMouseButton
from ._type import SdlScancode
from ._type import SdlWindow
from ._window_icon import WindowIcon

# sdl core
def initialize_sdl() -> None: ...
def deinitialize_sdl() -> None: ...

# window
def center_sdl_window(sdl_window: SdlWindow, /) -> None: ...
def create_sdl_window(
    gl_major_version: int, gl_minor_version: int, /
) -> tuple[SdlWindow, int, int]: ...
def delete_sdl_window(sdl_window: SdlWindow, /) -> None: ...
def disable_sdl_window_text_input(sdl_window: SdlWindow, /) -> None: ...
def enable_sdl_window_text_input(
    sdl_window: SdlWindow, x: int, y: int, w: int, h: int, cursor_position: int, /
) -> None: ...
def hide_sdl_window(sdl_window: SdlWindow, /) -> None: ...
def set_sdl_window_size(sdl_window: SdlWindow, size: IVector2, /) -> None: ...
def show_sdl_window(sdl_window: SdlWindow, /) -> None: ...
def swap_sdl_window(sdl_window: SdlWindow, synchronization: int, /) -> None: ...
def set_sdl_window_border(sdl_window: SdlWindow, is_bordered: bool, /) -> None: ...
def set_sdl_window_resizeable(sdl_window: SdlWindow, is_resizeable: bool, /) -> None: ...
def set_sdl_window_always_on_top(sdl_window: SdlWindow, is_always_on_top: bool, /) -> None: ...
def set_sdl_window_fullscreen(
    sdl_window: SdlWindow,
    sdl_display_id: SdlDisplayId,
    width: int,
    height: int,
    refresh_rate: float,
    /,
) -> None: ...
def set_sdl_window_not_fullscreen(sdl_window: SdlWindow) -> None: ...
def set_sdl_window_position(sdl_window: SdlWindow, position: IVector2, /) -> None: ...
def set_sdl_window_title(sdl_window: SdlWindow, title: str, /) -> None: ...
def set_sdl_window_icon(
    sdl_window: SdlWindow, icon: WindowIcon, /, *alternatives: WindowIcon
) -> None: ...
def maximize_sdl_window(sdl_window: SdlWindow, /) -> None: ...

# gl context
def create_sdl_gl_context(sdl_window: SdlWindow, /) -> SdlGlContext: ...
def delete_sdl_gl_context(sdl_gl_context: SdlGlContext, /) -> None: ...
def get_gl_attrs() -> tuple[int, int, int, int, int, int]: ...

# clipboard
def get_clipboard() -> str: ...
def set_clipboard(text: str) -> None: ...

# mouse
def hide_cursor() -> None: ...
def show_cursor() -> None: ...

SDL_BUTTON_LEFT: SdlMouseButton
SDL_BUTTON_MIDDLE: SdlMouseButton
SDL_BUTTON_RIGHT: SdlMouseButton
SDL_BUTTON_X1: SdlMouseButton
SDL_BUTTON_X2: SdlMouseButton

# event
def get_sdl_event() -> tuple | None: ...
def clear_sdl_events() -> None: ...

SDL_EVENT_QUIT: SdlEventType
SDL_EVENT_MOUSE_MOTION: SdlEventType
SDL_EVENT_MOUSE_WHEEL: SdlEventType
SDL_EVENT_MOUSE_BUTTON_DOWN: SdlEventType
SDL_EVENT_MOUSE_BUTTON_UP: SdlEventType
SDL_EVENT_KEY_DOWN: SdlEventType
SDL_EVENT_KEY_UP: SdlEventType
SDL_EVENT_TEXT_INPUT: SdlEventType
SDL_EVENT_WINDOW_RESIZED: SdlEventType
SDL_EVENT_WINDOW_SHOWN: SdlEventType
SDL_EVENT_WINDOW_HIDDEN: SdlEventType
SDL_EVENT_WINDOW_MOVED: SdlEventType
SDL_EVENT_WINDOW_FOCUS_GAINED: SdlEventType
SDL_EVENT_WINDOW_FOCUS_LOST: SdlEventType
SDL_EVENT_DISPLAY_ADDED: SdlEventType
SDL_EVENT_DISPLAY_REMOVED: SdlEventType
SDL_EVENT_DISPLAY_ORIENTATION: SdlEventType
SDL_EVENT_DISPLAY_MOVED: SdlEventType
SDL_EVENT_DISPLAY_CURRENT_MODE_CHANGED: SdlEventType
SDL_EVENT_JOYSTICK_ADDED: SdlEventType
SDL_EVENT_JOYSTICK_REMOVED: SdlEventType
SDL_EVENT_JOYSTICK_AXIS_MOTION: SdlEventType
SDL_EVENT_JOYSTICK_BUTTON_DOWN: SdlEventType
SDL_EVENT_JOYSTICK_BUTTON_UP: SdlEventType
SDL_EVENT_JOYSTICK_HAT_MOTION: SdlEventType
SDL_EVENT_WINDOW_MAXIMIZED: SdlEventType
SDL_EVENT_WINDOW_RESTORED: SdlEventType

# keyboard
#    number
SDL_SCANCODE_0: SdlScancode
SDL_SCANCODE_1: SdlScancode
SDL_SCANCODE_2: SdlScancode
SDL_SCANCODE_3: SdlScancode
SDL_SCANCODE_4: SdlScancode
SDL_SCANCODE_5: SdlScancode
SDL_SCANCODE_6: SdlScancode
SDL_SCANCODE_7: SdlScancode
SDL_SCANCODE_8: SdlScancode
SDL_SCANCODE_9: SdlScancode
#    function
SDL_SCANCODE_F1: SdlScancode
SDL_SCANCODE_F2: SdlScancode
SDL_SCANCODE_F3: SdlScancode
SDL_SCANCODE_F4: SdlScancode
SDL_SCANCODE_F5: SdlScancode
SDL_SCANCODE_F6: SdlScancode
SDL_SCANCODE_F7: SdlScancode
SDL_SCANCODE_F8: SdlScancode
SDL_SCANCODE_F9: SdlScancode
SDL_SCANCODE_F10: SdlScancode
SDL_SCANCODE_F11: SdlScancode
SDL_SCANCODE_F12: SdlScancode
SDL_SCANCODE_F13: SdlScancode
SDL_SCANCODE_F14: SdlScancode
SDL_SCANCODE_F15: SdlScancode
SDL_SCANCODE_F16: SdlScancode
SDL_SCANCODE_F17: SdlScancode
SDL_SCANCODE_F18: SdlScancode
SDL_SCANCODE_F19: SdlScancode
SDL_SCANCODE_F20: SdlScancode
SDL_SCANCODE_F21: SdlScancode
SDL_SCANCODE_F22: SdlScancode
SDL_SCANCODE_F23: SdlScancode
SDL_SCANCODE_F24: SdlScancode
#    letters
SDL_SCANCODE_A: SdlScancode
SDL_SCANCODE_B: SdlScancode
SDL_SCANCODE_C: SdlScancode
SDL_SCANCODE_D: SdlScancode
SDL_SCANCODE_E: SdlScancode
SDL_SCANCODE_F: SdlScancode
SDL_SCANCODE_G: SdlScancode
SDL_SCANCODE_H: SdlScancode
SDL_SCANCODE_I: SdlScancode
SDL_SCANCODE_J: SdlScancode
SDL_SCANCODE_K: SdlScancode
SDL_SCANCODE_L: SdlScancode
SDL_SCANCODE_M: SdlScancode
SDL_SCANCODE_N: SdlScancode
SDL_SCANCODE_O: SdlScancode
SDL_SCANCODE_P: SdlScancode
SDL_SCANCODE_Q: SdlScancode
SDL_SCANCODE_R: SdlScancode
SDL_SCANCODE_S: SdlScancode
SDL_SCANCODE_T: SdlScancode
SDL_SCANCODE_U: SdlScancode
SDL_SCANCODE_V: SdlScancode
SDL_SCANCODE_W: SdlScancode
SDL_SCANCODE_X: SdlScancode
SDL_SCANCODE_Y: SdlScancode
SDL_SCANCODE_Z: SdlScancode
#    symbols/operators
SDL_SCANCODE_APOSTROPHE: SdlScancode
SDL_SCANCODE_BACKSLASH: SdlScancode
SDL_SCANCODE_COMMA: SdlScancode
SDL_SCANCODE_DECIMALSEPARATOR: SdlScancode
SDL_SCANCODE_EQUALS: SdlScancode
SDL_SCANCODE_GRAVE: SdlScancode
SDL_SCANCODE_LEFTBRACKET: SdlScancode
SDL_SCANCODE_MINUS: SdlScancode
SDL_SCANCODE_NONUSBACKSLASH: SdlScancode
SDL_SCANCODE_NONUSHASH: SdlScancode
SDL_SCANCODE_PERIOD: SdlScancode
SDL_SCANCODE_RIGHTBRACKET: SdlScancode
SDL_SCANCODE_RSHIFT: SdlScancode
SDL_SCANCODE_SEMICOLON: SdlScancode
SDL_SCANCODE_SEPARATOR: SdlScancode
SDL_SCANCODE_SLASH: SdlScancode
SDL_SCANCODE_SPACE: SdlScancode
SDL_SCANCODE_TAB: SdlScancode
SDL_SCANCODE_THOUSANDSSEPARATOR: SdlScancode
#    actions
SDL_SCANCODE_AGAIN: SdlScancode
SDL_SCANCODE_ALTERASE: SdlScancode
SDL_SCANCODE_APPLICATION: SdlScancode
SDL_SCANCODE_BACKSPACE: SdlScancode
SDL_SCANCODE_CANCEL: SdlScancode
SDL_SCANCODE_CAPSLOCK: SdlScancode
SDL_SCANCODE_CLEAR: SdlScancode
SDL_SCANCODE_CLEARAGAIN: SdlScancode
SDL_SCANCODE_COPY: SdlScancode
SDL_SCANCODE_CRSEL: SdlScancode
SDL_SCANCODE_CURRENCYSUBUNIT: SdlScancode
SDL_SCANCODE_CURRENCYUNIT: SdlScancode
SDL_SCANCODE_CUT: SdlScancode
SDL_SCANCODE_DELETE: SdlScancode
SDL_SCANCODE_END: SdlScancode
SDL_SCANCODE_ESCAPE: SdlScancode
SDL_SCANCODE_EXECUTE: SdlScancode
SDL_SCANCODE_EXSEL: SdlScancode
SDL_SCANCODE_FIND: SdlScancode
SDL_SCANCODE_HELP: SdlScancode
SDL_SCANCODE_HOME: SdlScancode
SDL_SCANCODE_INSERT: SdlScancode
SDL_SCANCODE_LALT: SdlScancode
SDL_SCANCODE_LCTRL: SdlScancode
SDL_SCANCODE_LGUI: SdlScancode
SDL_SCANCODE_LSHIFT: SdlScancode
SDL_SCANCODE_MENU: SdlScancode
SDL_SCANCODE_MODE: SdlScancode
SDL_SCANCODE_NUMLOCKCLEAR: SdlScancode
SDL_SCANCODE_OPER: SdlScancode
SDL_SCANCODE_OUT: SdlScancode
SDL_SCANCODE_PAGEDOWN: SdlScancode
SDL_SCANCODE_PAGEUP: SdlScancode
SDL_SCANCODE_PASTE: SdlScancode
SDL_SCANCODE_PAUSE: SdlScancode
SDL_SCANCODE_POWER: SdlScancode
SDL_SCANCODE_PRINTSCREEN: SdlScancode
SDL_SCANCODE_PRIOR: SdlScancode
SDL_SCANCODE_RALT: SdlScancode
SDL_SCANCODE_RCTRL: SdlScancode
SDL_SCANCODE_RETURN: SdlScancode
SDL_SCANCODE_RETURN2: SdlScancode
SDL_SCANCODE_RGUI: SdlScancode
SDL_SCANCODE_SCROLLLOCK: SdlScancode
SDL_SCANCODE_SELECT: SdlScancode
SDL_SCANCODE_SLEEP: SdlScancode
SDL_SCANCODE_STOP: SdlScancode
SDL_SCANCODE_SYSREQ: SdlScancode
SDL_SCANCODE_UNDO: SdlScancode
SDL_SCANCODE_VOLUMEDOWN: SdlScancode
SDL_SCANCODE_VOLUMEUP: SdlScancode
SDL_SCANCODE_MUTE: SdlScancode
#    media
SDL_SCANCODE_MEDIA_SELECT: SdlScancode
SDL_SCANCODE_MEDIA_EJECT: SdlScancode
SDL_SCANCODE_MEDIA_FAST_FORWARD: SdlScancode
SDL_SCANCODE_MEDIA_NEXT_TRACK: SdlScancode
SDL_SCANCODE_MEDIA_PLAY: SdlScancode
SDL_SCANCODE_MEDIA_PREVIOUS_TRACK: SdlScancode
SDL_SCANCODE_MEDIA_REWIND: SdlScancode
SDL_SCANCODE_MEDIA_STOP: SdlScancode
#    ac
SDL_SCANCODE_AC_BACK: SdlScancode
SDL_SCANCODE_AC_BOOKMARKS: SdlScancode
SDL_SCANCODE_AC_FORWARD: SdlScancode
SDL_SCANCODE_AC_HOME: SdlScancode
SDL_SCANCODE_AC_REFRESH: SdlScancode
SDL_SCANCODE_AC_SEARCH: SdlScancode
SDL_SCANCODE_AC_STOP: SdlScancode
#    arrows
SDL_SCANCODE_DOWN: SdlScancode
SDL_SCANCODE_LEFT: SdlScancode
SDL_SCANCODE_RIGHT: SdlScancode
SDL_SCANCODE_UP: SdlScancode
#    international
SDL_SCANCODE_INTERNATIONAL1: SdlScancode
SDL_SCANCODE_INTERNATIONAL2: SdlScancode
SDL_SCANCODE_INTERNATIONAL3: SdlScancode
SDL_SCANCODE_INTERNATIONAL4: SdlScancode
SDL_SCANCODE_INTERNATIONAL5: SdlScancode
SDL_SCANCODE_INTERNATIONAL6: SdlScancode
SDL_SCANCODE_INTERNATIONAL7: SdlScancode
SDL_SCANCODE_INTERNATIONAL8: SdlScancode
SDL_SCANCODE_INTERNATIONAL9: SdlScancode
#    numpad numbers
SDL_SCANCODE_KP_0: SdlScancode
SDL_SCANCODE_KP_00: SdlScancode
SDL_SCANCODE_KP_000: SdlScancode
SDL_SCANCODE_KP_1: SdlScancode
SDL_SCANCODE_KP_2: SdlScancode
SDL_SCANCODE_KP_3: SdlScancode
SDL_SCANCODE_KP_4: SdlScancode
SDL_SCANCODE_KP_5: SdlScancode
SDL_SCANCODE_KP_6: SdlScancode
SDL_SCANCODE_KP_7: SdlScancode
SDL_SCANCODE_KP_8: SdlScancode
SDL_SCANCODE_KP_9: SdlScancode
#    numpad letters
SDL_SCANCODE_KP_A: SdlScancode
SDL_SCANCODE_KP_B: SdlScancode
SDL_SCANCODE_KP_C: SdlScancode
SDL_SCANCODE_KP_D: SdlScancode
SDL_SCANCODE_KP_E: SdlScancode
SDL_SCANCODE_KP_F: SdlScancode
#    numpad symbols/operators
SDL_SCANCODE_KP_AMPERSAND: SdlScancode
SDL_SCANCODE_KP_AT: SdlScancode
SDL_SCANCODE_KP_COLON: SdlScancode
SDL_SCANCODE_KP_COMMA: SdlScancode
SDL_SCANCODE_KP_DBLAMPERSAND: SdlScancode
SDL_SCANCODE_KP_DBLVERTICALBAR: SdlScancode
SDL_SCANCODE_KP_DECIMAL: SdlScancode
SDL_SCANCODE_KP_DIVIDE: SdlScancode
SDL_SCANCODE_KP_ENTER: SdlScancode
SDL_SCANCODE_KP_EQUALS: SdlScancode
SDL_SCANCODE_KP_EQUALSAS400: SdlScancode
SDL_SCANCODE_KP_EXCLAM: SdlScancode
SDL_SCANCODE_KP_GREATER: SdlScancode
SDL_SCANCODE_KP_HASH: SdlScancode
SDL_SCANCODE_KP_LEFTBRACE: SdlScancode
SDL_SCANCODE_KP_LEFTPAREN: SdlScancode
SDL_SCANCODE_KP_LESS: SdlScancode
SDL_SCANCODE_KP_MINUS: SdlScancode
SDL_SCANCODE_KP_MULTIPLY: SdlScancode
SDL_SCANCODE_KP_PERCENT: SdlScancode
SDL_SCANCODE_KP_PERIOD: SdlScancode
SDL_SCANCODE_KP_PLUS: SdlScancode
SDL_SCANCODE_KP_PLUSMINUS: SdlScancode
SDL_SCANCODE_KP_POWER: SdlScancode
SDL_SCANCODE_KP_RIGHTBRACE: SdlScancode
SDL_SCANCODE_KP_RIGHTPAREN: SdlScancode
SDL_SCANCODE_KP_SPACE: SdlScancode
SDL_SCANCODE_KP_TAB: SdlScancode
SDL_SCANCODE_KP_VERTICALBAR: SdlScancode
SDL_SCANCODE_KP_XOR: SdlScancode
#    numpad actions
SDL_SCANCODE_KP_BACKSPACE: SdlScancode
SDL_SCANCODE_KP_BINARY: SdlScancode
SDL_SCANCODE_KP_CLEAR: SdlScancode
SDL_SCANCODE_KP_CLEARENTRY: SdlScancode
SDL_SCANCODE_KP_HEXADECIMAL: SdlScancode
SDL_SCANCODE_KP_OCTAL: SdlScancode
#    memory
SDL_SCANCODE_KP_MEMADD: SdlScancode
SDL_SCANCODE_KP_MEMCLEAR: SdlScancode
SDL_SCANCODE_KP_MEMDIVIDE: SdlScancode
SDL_SCANCODE_KP_MEMMULTIPLY: SdlScancode
SDL_SCANCODE_KP_MEMRECALL: SdlScancode
SDL_SCANCODE_KP_MEMSTORE: SdlScancode
SDL_SCANCODE_KP_MEMSUBTRACT: SdlScancode
#    language
SDL_SCANCODE_LANG1: SdlScancode
SDL_SCANCODE_LANG2: SdlScancode
SDL_SCANCODE_LANG3: SdlScancode
SDL_SCANCODE_LANG4: SdlScancode
SDL_SCANCODE_LANG5: SdlScancode
SDL_SCANCODE_LANG6: SdlScancode
SDL_SCANCODE_LANG7: SdlScancode
SDL_SCANCODE_LANG8: SdlScancode
SDL_SCANCODE_LANG9: SdlScancode

# joystick
def get_sdl_joysticks() -> Collection[SdlJoystickId]: ...
def open_sdl_joystick(
    sdl_joystick: SdlJoystickId, /
) -> tuple[
    str,
    str,
    str | None,
    int,
    tuple[tuple[float], ...],
    tuple[tuple[bool], ...],
    tuple[tuple[int], ...],
    tuple[tuple[tuple[tuple, tuple], ...], SdlGamepadType] | None,
]: ...
def close_sdl_joystick(sdl_joystick: SdlJoystickId, /) -> None: ...
def connect_virtual_joystick(name: str, /) -> SdlJoystickId: ...
def disconnect_virtual_joystick(sdl_joystick: SdlJoystickId, /) -> None: ...

SDL_GAMEPAD_BINDTYPE_BUTTON: SdlGamepadBindingType
SDL_GAMEPAD_BINDTYPE_AXIS: SdlGamepadBindingType
SDL_GAMEPAD_BINDTYPE_HAT: SdlGamepadBindingType

SDL_GAMEPAD_BUTTON_LABEL_A: SdlGamepadButtonLabel
SDL_GAMEPAD_BUTTON_LABEL_B: SdlGamepadButtonLabel
SDL_GAMEPAD_BUTTON_LABEL_X: SdlGamepadButtonLabel
SDL_GAMEPAD_BUTTON_LABEL_Y: SdlGamepadButtonLabel
SDL_GAMEPAD_BUTTON_LABEL_CROSS: SdlGamepadButtonLabel
SDL_GAMEPAD_BUTTON_LABEL_CIRCLE: SdlGamepadButtonLabel
SDL_GAMEPAD_BUTTON_LABEL_SQUARE: SdlGamepadButtonLabel
SDL_GAMEPAD_BUTTON_LABEL_TRIANGLE: SdlGamepadButtonLabel

SDL_GAMEPAD_BUTTON_SOUTH: SdlGamepadButton
SDL_GAMEPAD_BUTTON_EAST: SdlGamepadButton
SDL_GAMEPAD_BUTTON_WEST: SdlGamepadButton
SDL_GAMEPAD_BUTTON_NORTH: SdlGamepadButton
SDL_GAMEPAD_BUTTON_BACK: SdlGamepadButton
SDL_GAMEPAD_BUTTON_GUIDE: SdlGamepadButton
SDL_GAMEPAD_BUTTON_START: SdlGamepadButton
SDL_GAMEPAD_BUTTON_LEFT_STICK: SdlGamepadButton
SDL_GAMEPAD_BUTTON_RIGHT_STICK: SdlGamepadButton
SDL_GAMEPAD_BUTTON_LEFT_SHOULDER: SdlGamepadButton
SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER: SdlGamepadButton
SDL_GAMEPAD_BUTTON_DPAD_UP: SdlGamepadButton
SDL_GAMEPAD_BUTTON_DPAD_DOWN: SdlGamepadButton
SDL_GAMEPAD_BUTTON_DPAD_LEFT: SdlGamepadButton
SDL_GAMEPAD_BUTTON_DPAD_RIGHT: SdlGamepadButton
SDL_GAMEPAD_BUTTON_MISC1: SdlGamepadButton
SDL_GAMEPAD_BUTTON_RIGHT_PADDLE1: SdlGamepadButton
SDL_GAMEPAD_BUTTON_LEFT_PADDLE1: SdlGamepadButton
SDL_GAMEPAD_BUTTON_RIGHT_PADDLE2: SdlGamepadButton
SDL_GAMEPAD_BUTTON_LEFT_PADDLE2: SdlGamepadButton
SDL_GAMEPAD_BUTTON_TOUCHPAD: SdlGamepadButton
SDL_GAMEPAD_BUTTON_MISC2: SdlGamepadButton
SDL_GAMEPAD_BUTTON_MISC3: SdlGamepadButton
SDL_GAMEPAD_BUTTON_MISC4: SdlGamepadButton
SDL_GAMEPAD_BUTTON_MISC5: SdlGamepadButton
SDL_GAMEPAD_BUTTON_MISC6: SdlGamepadButton

SDL_GAMEPAD_AXIS_LEFTX: SdlGamepadAxis
SDL_GAMEPAD_AXIS_LEFTY: SdlGamepadAxis
SDL_GAMEPAD_AXIS_RIGHTX: SdlGamepadAxis
SDL_GAMEPAD_AXIS_RIGHTY: SdlGamepadAxis
SDL_GAMEPAD_AXIS_LEFT_TRIGGER: SdlGamepadAxis
SDL_GAMEPAD_AXIS_RIGHT_TRIGGER: SdlGamepadAxis

SDL_HAT_UP: SdlHat
SDL_HAT_RIGHT: SdlHat
SDL_HAT_DOWN: SdlHat
SDL_HAT_LEFT: SdlHat

SDL_GAMEPAD_TYPE_UNKNOWN: SdlGamepadType
SDL_GAMEPAD_TYPE_STANDARD: SdlGamepadType
SDL_GAMEPAD_TYPE_XBOX360: SdlGamepadType
SDL_GAMEPAD_TYPE_XBOXONE: SdlGamepadType
SDL_GAMEPAD_TYPE_PS3: SdlGamepadType
SDL_GAMEPAD_TYPE_PS4: SdlGamepadType
SDL_GAMEPAD_TYPE_PS5: SdlGamepadType
SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_PRO: SdlGamepadType
SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_LEFT: SdlGamepadType
SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_RIGHT: SdlGamepadType
SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_PAIR: SdlGamepadType

# display

def get_sdl_displays() -> Collection[SdlDisplayId]: ...
def get_sdl_display_details(
    sdl_display_id: SdlDisplayId, /
) -> tuple[
    str, SdlDisplayOrientation, int, int, int, int, float, tuple[tuple[int, int, float]]
]: ...

SDL_ORIENTATION_UNKNOWN: SdlDisplayOrientation
SDL_ORIENTATION_LANDSCAPE: SdlDisplayOrientation
SDL_ORIENTATION_LANDSCAPE_FLIPPED: SdlDisplayOrientation
SDL_ORIENTATION_PORTRAIT: SdlDisplayOrientation
SDL_ORIENTATION_PORTRAIT_FLIPPED: SdlDisplayOrientation
