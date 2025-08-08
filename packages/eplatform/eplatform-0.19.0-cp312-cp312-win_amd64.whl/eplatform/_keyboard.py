__all__ = ["change_key", "Keyboard", "KeyboardKey", "KeyboardKeyChanged", "KeyboardKeyLocation"]

from enum import IntFlag
from enum import StrEnum
from enum import auto
from inspect import get_annotations
from typing import Final
from typing import Literal
from typing import Mapping
from typing import TypeAlias
from typing import TypedDict
from typing import get_args

from eevent import Event

from . import _eplatform
from ._type import SdlScancode


class KeyboardModifier(IntFlag):
    CONTROL = auto()
    ALT = auto()
    SHIFT = auto()
    NONE = 0


class KeyboardKeyLocation(StrEnum):
    ZERO = "zero key location"
    ONE = "one key location"
    TWO = "two key location"
    THREE = "three key location"
    FOUR = "four key location"
    FIVE = "five key location"
    SIX = "six key location"
    SEVEN = "seven key location"
    EIGHT = "eight key location"
    NINE = "nine key location"
    F1 = "f1 key location"
    F2 = "f2 key location"
    F3 = "f3 key location"
    F4 = "f4 key location"
    F5 = "f5 key location"
    F6 = "f6 key location"
    F7 = "f7 key location"
    F8 = "f8 key location"
    F9 = "f9 key location"
    F10 = "f10 key location"
    F11 = "f11 key location"
    F12 = "f12 key location"
    F13 = "f13 key location"
    F14 = "f14 key location"
    F15 = "f15 key location"
    F16 = "f16 key location"
    F17 = "f17 key location"
    F18 = "f18 key location"
    F19 = "f19 key location"
    F20 = "f20 key location"
    F21 = "f21 key location"
    F22 = "f22 key location"
    F23 = "f23 key location"
    F24 = "f24 key location"
    A = "a key location"
    B = "b key location"
    C = "c key location"
    D = "d key location"
    E = "e key location"
    F = "f key location"
    G = "g key location"
    H = "h key location"
    I = "i key location"
    J = "j key location"
    K = "k key location"
    L = "l key location"
    M = "m key location"
    N = "n key location"
    O = "o key location"
    P = "p key location"
    Q = "q key location"
    R = "r key location"
    S = "s key location"
    T = "t key location"
    U = "u key location"
    V = "v key location"
    W = "w key location"
    X = "x key location"
    Y = "y key location"
    Z = "z key location"
    APOSTROPHE = "apostrophe key location"
    BACKSLASH = "backslash key location"
    COMMA = "comma key location"
    DECIMAL_SEPARATOR = "decimal separator key location"
    EQUALS = "equals key location"
    GRAVE = "grave key location"
    LEFT_BRACKET = "left bracket key location"
    MINUS = "minus key location"
    NON_US_BACKSLASH = "non us backslash key location"
    NON_US_HASH = "non us hash key location"
    PERIOD = "period key location"
    RIGHT_BRACKET = "right bracket key location"
    RIGHT_SHIFT = "right shift key location"
    SEMICOLON = "semicolon key location"
    SEPARATOR = "separator key location"
    SLASH = "slash key location"
    SPACE = "space key location"
    TAB = "tab key location"
    THOUSANDS_SEPARATOR = "thousands separator key location"
    AGAIN = "again key location"
    ALT_ERASE = "alt erase key location"
    CONTEXT_MENU = "context menu key location"
    BACKSPACE = "backspace key location"
    CANCEL = "cancel key location"
    CAPSLOCK = "capslock key location"
    CLEAR = "clear key location"
    CLEAR_AGAIN = "clear again key location"
    COPY = "copy key location"
    CRSEL = "crsel key location"
    CURRENCY_SUB_UNIT = "currency sub unit key location"
    CURRENCY_UNIT = "currency unit key location"
    CUT = "cut key location"
    DELETE = "delete key location"
    END = "end key location"
    ESCAPE = "escape key location"
    EXECUTE = "execute key location"
    EXSEL = "exsel key location"
    FIND = "find key location"
    HELP = "help key location"
    HOME = "home key location"
    INSERT = "insert key location"
    LEFT_ALT = "left alt key location"
    LEFT_CONTROL = "left control key location"
    LEFT_SPECIAL = "left special key location"
    LEFT_SHIFT = "left shift key location"
    MENU = "menu key location"
    MODE = "mode key location"
    MUTE = "mute key location"
    NUMLOCK_CLEAR = "numlock clear key location"
    OPER = "oper key location"
    OUT = "out key location"
    PAGE_DOWN = "page down key location"
    PAGE_UP = "page up key location"
    PASTE = "paste key location"
    PAUSE = "pause key location"
    POWER = "power key location"
    PRINT_SCREEN = "print screen key location"
    PRIOR = "prior key location"
    RIGHT_ALT = "right alt key location"
    RIGHT_CONTROL = "right control key location"
    ENTER = "enter key location"
    ENTER_2 = "enter 2 key location"
    RIGHT_SPECIAL = "right special key location"
    SCROLL_LOCK = "scroll lock key location"
    SELECT = "select key location"
    SLEEP = "sleep key location"
    STOP = "stop key location"
    SYSTEM_REQUEST = "system request key location"
    UNDO = "undo key location"
    VOLUME_DOWN = "volume down key location"
    VOLUME_UP = "volume up key location"
    MEDIA_EJECT = "media eject key location"
    MEDIA_FAST_FORWARD = "media fast forward key location"
    MEDIA_NEXT_TRACK = "media next track key location"
    MEDIA_PLAY = "media play key location"
    MEDIA_PREVIOUS_TRACK = "media previous track key location"
    MEDIA_REWIND = "media rewind key location"
    MEDIA_SELECT = "media select key location"
    MEDIA_STOP = "media stop key location"
    AC_BACK = "ac back key location"
    AC_BOOKMARKS = "ac bookmarks key location"
    AC_FORWARD = "ac forward key location"
    AC_HOME = "ac home key location"
    AC_REFRESH = "ac refresh key location"
    AC_SEARCH = "ac search key location"
    AC_STOP = "ac stop key location"
    DOWN = "down key location"
    LEFT = "left key location"
    RIGHT = "right key location"
    UP = "up key location"
    INTERNATIONAL_1 = "international 1 key location"
    INTERNATIONAL_2 = "international 2 key location"
    INTERNATIONAL_3 = "international 3 key location"
    INTERNATIONAL_4 = "international 4 key location"
    INTERNATIONAL_5 = "international 5 key location"
    INTERNATIONAL_6 = "international 6 key location"
    INTERNATIONAL_7 = "international 7 key location"
    INTERNATIONAL_8 = "international 8 key location"
    INTERNATIONAL_9 = "international 9 key location"
    NUMPAD_0 = "numpad 0 key location"
    NUMPAD_00 = "numpad 00 key location"
    NUMPAD_000 = "numpad 000 key location"
    NUMPAD_1 = "numpad 1 key location"
    NUMPAD_2 = "numpad 2 key location"
    NUMPAD_3 = "numpad 3 key location"
    NUMPAD_4 = "numpad 4 key location"
    NUMPAD_5 = "numpad 5 key location"
    NUMPAD_6 = "numpad 6 key location"
    NUMPAD_7 = "numpad 7 key location"
    NUMPAD_8 = "numpad 8 key location"
    NUMPAD_9 = "numpad 9 key location"
    NUMPAD_A = "numpad a key location"
    NUMPAD_B = "numpad b key location"
    NUMPAD_C = "numpad c key location"
    NUMPAD_D = "numpad d key location"
    NUMPAD_E = "numpad e key location"
    NUMPAD_F = "numpad f key location"
    NUMPAD_AMPERSAND = "numpad ampersand key location"
    NUMPAD_AT = "numpad at key location"
    NUMPAD_COLON = "numpad colon key location"
    NUMPAD_COMMA = "numpad comma key location"
    NUMPAD_AND = "numpad and key location"
    NUMPAD_OR = "numpad or key location"
    NUMPAD_DECIMAL = "numpad decimal key location"
    NUMPAD_DIVIDE = "numpad divide key location"
    NUMPAD_ENTER = "numpad enter key location"
    NUMPAD_EQUALS = "numpad equals key location"
    NUMPAD_AS400_EQUALS = "numpad as400 equals key location"
    NUMPAD_BANG = "numpad bang key location"
    NUMPAD_GREATER = "numpad greater key location"
    NUMPAD_HASH = "numpad hash key location"
    NUMPAD_LEFT_BRACE = "numpad left brace key location"
    NUMPAD_LEFT_PARENTHESIS = "numpad left parenthesis key location"
    NUMPAD_LESS = "numpad less key location"
    NUMPAD_MINUS = "numpad minus key location"
    NUMPAD_MULTIPLY = "numpad multiply key location"
    NUMPAD_PERCENT = "numpad percent key location"
    NUMPAD_PERIOD = "numpad period key location"
    NUMPAD_PLUS = "numpad plus key location"
    NUMPAD_PLUS_MINUS = "numpad plus minus key location"
    NUMPAD_POWER = "numpad power key location"
    NUMPAD_RIGHT_BRACE = "numpad right brace key location"
    NUMPAD_RIGHT_PARENTHESIS = "numpad right parenthesis key location"
    NUMPAD_SPACE = "numpad space key location"
    NUMPAD_TAB = "numpad tab key location"
    NUMPAD_PIPE = "numpad pipe key location"
    NUMPAD_XOR = "numpad xor key location"
    NUMPAD_BACKSPACE = "numpad backspace key location"
    NUMPAD_BINARY = "numpad binary key location"
    NUMPAD_CLEAR = "numpad clear key location"
    NUMPAD_CLEAR_ENTRY = "numpad clear entry key location"
    NUMPAD_HEXADECIMAL = "numpad hexadecimal key location"
    NUMPAD_OCTAL = "numpad octal key location"
    NUMPAD_MEMORY_ADD = "numpad memory add key location"
    NUMPAD_MEMORY_CLEAR = "numpad memory clear key location"
    NUMPAD_MEMORY_DIVIDE = "numpad memory divide key location"
    NUMPAD_MEMORY_MULTIPLY = "numpad memory multiply key location"
    NUMPAD_MEMORY_RECALL = "numpad memory recall key location"
    NUMPAD_MEMORY_STORE = "numpad memory store key location"
    NUMPAD_MEMORY_SUBTRACT = "numpad memory subtract key location"
    LANGUAGE_1 = "language 1 key location"
    LANGUAGE_2 = "language 2 key location"
    LANGUAGE_3 = "language 3 key location"
    LANGUAGE_4 = "language 4 key location"
    LANGUAGE_5 = "language 5 key location"
    LANGUAGE_6 = "language 6 key location"
    LANGUAGE_7 = "language 7 key location"
    LANGUAGE_8 = "language 8 key location"
    LANGUAGE_9 = "language 9 key location"


class KeyboardKey:
    changed: Event["KeyboardKeyChanged"] = Event()
    pressed: Event["KeyboardKeyChanged"] = Event()
    released: Event["KeyboardKeyChanged"] = Event()

    def __init__(self, location: KeyboardKeyLocation):
        self.location = location
        self.is_pressed = False

        self.changed = Event()
        self.pressed = Event()
        self.released = Event()

    def __repr__(self) -> str:
        return f"<KeyboardKey {self.location.value!r}>"


class Keyboard:
    _keys_by_location: Mapping[KeyboardKeyLocation, KeyboardKey]

    def __init__(self) -> None:
        self._keys_by_location = {l: KeyboardKey(l) for l in KeyboardKeyLocation}
        self._left_control = self._keys_by_location[KeyboardKeyLocation.LEFT_CONTROL]
        self._right_control = self._keys_by_location[KeyboardKeyLocation.RIGHT_CONTROL]
        self._left_shift = self._keys_by_location[KeyboardKeyLocation.LEFT_SHIFT]
        self._right_shift = self._keys_by_location[KeyboardKeyLocation.RIGHT_SHIFT]
        self._left_alt = self._keys_by_location[KeyboardKeyLocation.LEFT_ALT]
        self._right_alt = self._keys_by_location[KeyboardKeyLocation.RIGHT_ALT]

    def get_key_by_location(self, location: KeyboardKeyLocation) -> KeyboardKey:
        return self._keys_by_location[location]

    @property
    def modifier(self) -> KeyboardModifier:
        modifier = KeyboardModifier.NONE
        if self._left_control.is_pressed or self._right_control.is_pressed:
            modifier |= KeyboardModifier.CONTROL
        if self._left_shift.is_pressed or self._right_shift.is_pressed:
            modifier |= KeyboardModifier.SHIFT
        if self._left_alt.is_pressed or self._right_alt.is_pressed:
            modifier |= KeyboardModifier.ALT
        return modifier


def change_key(
    keyboard: Keyboard, sdl_scancode: SdlScancode, is_pressed: bool, is_repeat: bool
) -> bool:
    try:
        key_location = _SDL_SCANCODE_TO_KEY_LOCATION[sdl_scancode]
    except KeyError:
        return False
    key = keyboard._keys_by_location[key_location]
    key.is_pressed = is_pressed
    data: KeyboardKeyChanged = {
        "key": key,
        "is_pressed": is_pressed,
        "is_repeat": is_repeat,
        "modifier": keyboard.modifier,
    }
    KeyboardKey.changed(data)
    key.changed(data)
    if is_pressed:
        KeyboardKey.pressed(data)
        key.pressed(data)
    else:
        KeyboardKey.released(data)
        key.released(data)
    return True


class KeyboardKeyChanged(TypedDict):
    key: KeyboardKey
    is_pressed: bool
    is_repeat: bool
    modifier: KeyboardModifier


_SDL_SCANCODE_TO_KEY_LOCATION: Final[Mapping[SdlScancode, KeyboardKeyLocation]] = {
    # number
    _eplatform.SDL_SCANCODE_0: KeyboardKeyLocation.ZERO,
    _eplatform.SDL_SCANCODE_1: KeyboardKeyLocation.ONE,
    _eplatform.SDL_SCANCODE_2: KeyboardKeyLocation.TWO,
    _eplatform.SDL_SCANCODE_3: KeyboardKeyLocation.THREE,
    _eplatform.SDL_SCANCODE_4: KeyboardKeyLocation.FOUR,
    _eplatform.SDL_SCANCODE_5: KeyboardKeyLocation.FIVE,
    _eplatform.SDL_SCANCODE_6: KeyboardKeyLocation.SIX,
    _eplatform.SDL_SCANCODE_7: KeyboardKeyLocation.SEVEN,
    _eplatform.SDL_SCANCODE_8: KeyboardKeyLocation.EIGHT,
    _eplatform.SDL_SCANCODE_9: KeyboardKeyLocation.NINE,
    # function
    _eplatform.SDL_SCANCODE_F1: KeyboardKeyLocation.F1,
    _eplatform.SDL_SCANCODE_F2: KeyboardKeyLocation.F2,
    _eplatform.SDL_SCANCODE_F3: KeyboardKeyLocation.F3,
    _eplatform.SDL_SCANCODE_F4: KeyboardKeyLocation.F4,
    _eplatform.SDL_SCANCODE_F5: KeyboardKeyLocation.F5,
    _eplatform.SDL_SCANCODE_F6: KeyboardKeyLocation.F6,
    _eplatform.SDL_SCANCODE_F7: KeyboardKeyLocation.F7,
    _eplatform.SDL_SCANCODE_F8: KeyboardKeyLocation.F8,
    _eplatform.SDL_SCANCODE_F9: KeyboardKeyLocation.F9,
    _eplatform.SDL_SCANCODE_F10: KeyboardKeyLocation.F10,
    _eplatform.SDL_SCANCODE_F11: KeyboardKeyLocation.F11,
    _eplatform.SDL_SCANCODE_F12: KeyboardKeyLocation.F12,
    _eplatform.SDL_SCANCODE_F13: KeyboardKeyLocation.F13,
    _eplatform.SDL_SCANCODE_F14: KeyboardKeyLocation.F14,
    _eplatform.SDL_SCANCODE_F15: KeyboardKeyLocation.F15,
    _eplatform.SDL_SCANCODE_F16: KeyboardKeyLocation.F16,
    _eplatform.SDL_SCANCODE_F17: KeyboardKeyLocation.F17,
    _eplatform.SDL_SCANCODE_F18: KeyboardKeyLocation.F18,
    _eplatform.SDL_SCANCODE_F19: KeyboardKeyLocation.F19,
    _eplatform.SDL_SCANCODE_F20: KeyboardKeyLocation.F20,
    _eplatform.SDL_SCANCODE_F21: KeyboardKeyLocation.F21,
    _eplatform.SDL_SCANCODE_F22: KeyboardKeyLocation.F22,
    _eplatform.SDL_SCANCODE_F23: KeyboardKeyLocation.F23,
    _eplatform.SDL_SCANCODE_F24: KeyboardKeyLocation.F24,
    # letters
    _eplatform.SDL_SCANCODE_A: KeyboardKeyLocation.A,
    _eplatform.SDL_SCANCODE_B: KeyboardKeyLocation.B,
    _eplatform.SDL_SCANCODE_C: KeyboardKeyLocation.C,
    _eplatform.SDL_SCANCODE_D: KeyboardKeyLocation.D,
    _eplatform.SDL_SCANCODE_E: KeyboardKeyLocation.E,
    _eplatform.SDL_SCANCODE_F: KeyboardKeyLocation.F,
    _eplatform.SDL_SCANCODE_G: KeyboardKeyLocation.G,
    _eplatform.SDL_SCANCODE_H: KeyboardKeyLocation.H,
    _eplatform.SDL_SCANCODE_I: KeyboardKeyLocation.I,
    _eplatform.SDL_SCANCODE_J: KeyboardKeyLocation.J,
    _eplatform.SDL_SCANCODE_K: KeyboardKeyLocation.K,
    _eplatform.SDL_SCANCODE_L: KeyboardKeyLocation.L,
    _eplatform.SDL_SCANCODE_M: KeyboardKeyLocation.M,
    _eplatform.SDL_SCANCODE_N: KeyboardKeyLocation.N,
    _eplatform.SDL_SCANCODE_O: KeyboardKeyLocation.O,
    _eplatform.SDL_SCANCODE_P: KeyboardKeyLocation.P,
    _eplatform.SDL_SCANCODE_Q: KeyboardKeyLocation.Q,
    _eplatform.SDL_SCANCODE_R: KeyboardKeyLocation.R,
    _eplatform.SDL_SCANCODE_S: KeyboardKeyLocation.S,
    _eplatform.SDL_SCANCODE_T: KeyboardKeyLocation.T,
    _eplatform.SDL_SCANCODE_U: KeyboardKeyLocation.U,
    _eplatform.SDL_SCANCODE_V: KeyboardKeyLocation.V,
    _eplatform.SDL_SCANCODE_W: KeyboardKeyLocation.W,
    _eplatform.SDL_SCANCODE_X: KeyboardKeyLocation.X,
    _eplatform.SDL_SCANCODE_Y: KeyboardKeyLocation.Y,
    _eplatform.SDL_SCANCODE_Z: KeyboardKeyLocation.Z,
    # symbols/operators
    _eplatform.SDL_SCANCODE_APOSTROPHE: KeyboardKeyLocation.APOSTROPHE,
    _eplatform.SDL_SCANCODE_BACKSLASH: KeyboardKeyLocation.BACKSLASH,
    _eplatform.SDL_SCANCODE_COMMA: KeyboardKeyLocation.COMMA,
    _eplatform.SDL_SCANCODE_DECIMALSEPARATOR: KeyboardKeyLocation.DECIMAL_SEPARATOR,
    _eplatform.SDL_SCANCODE_EQUALS: KeyboardKeyLocation.EQUALS,
    _eplatform.SDL_SCANCODE_GRAVE: KeyboardKeyLocation.GRAVE,
    _eplatform.SDL_SCANCODE_LEFTBRACKET: KeyboardKeyLocation.LEFT_BRACKET,
    _eplatform.SDL_SCANCODE_MINUS: KeyboardKeyLocation.MINUS,
    _eplatform.SDL_SCANCODE_NONUSBACKSLASH: KeyboardKeyLocation.NON_US_BACKSLASH,
    _eplatform.SDL_SCANCODE_NONUSHASH: KeyboardKeyLocation.NON_US_HASH,
    _eplatform.SDL_SCANCODE_PERIOD: KeyboardKeyLocation.PERIOD,
    _eplatform.SDL_SCANCODE_RIGHTBRACKET: KeyboardKeyLocation.RIGHT_BRACKET,
    _eplatform.SDL_SCANCODE_RSHIFT: KeyboardKeyLocation.RIGHT_SHIFT,
    _eplatform.SDL_SCANCODE_SEMICOLON: KeyboardKeyLocation.SEMICOLON,
    _eplatform.SDL_SCANCODE_SEPARATOR: KeyboardKeyLocation.SEPARATOR,
    _eplatform.SDL_SCANCODE_SLASH: KeyboardKeyLocation.SLASH,
    _eplatform.SDL_SCANCODE_SPACE: KeyboardKeyLocation.SPACE,
    _eplatform.SDL_SCANCODE_TAB: KeyboardKeyLocation.TAB,
    _eplatform.SDL_SCANCODE_THOUSANDSSEPARATOR: KeyboardKeyLocation.THOUSANDS_SEPARATOR,
    # actions
    _eplatform.SDL_SCANCODE_AGAIN: KeyboardKeyLocation.AGAIN,
    _eplatform.SDL_SCANCODE_ALTERASE: KeyboardKeyLocation.ALT_ERASE,
    _eplatform.SDL_SCANCODE_APPLICATION: KeyboardKeyLocation.CONTEXT_MENU,
    _eplatform.SDL_SCANCODE_BACKSPACE: KeyboardKeyLocation.BACKSPACE,
    _eplatform.SDL_SCANCODE_CANCEL: KeyboardKeyLocation.CANCEL,
    _eplatform.SDL_SCANCODE_CAPSLOCK: KeyboardKeyLocation.CAPSLOCK,
    _eplatform.SDL_SCANCODE_CLEAR: KeyboardKeyLocation.CLEAR,
    _eplatform.SDL_SCANCODE_CLEARAGAIN: KeyboardKeyLocation.CLEAR_AGAIN,
    _eplatform.SDL_SCANCODE_COPY: KeyboardKeyLocation.COPY,
    _eplatform.SDL_SCANCODE_CRSEL: KeyboardKeyLocation.CRSEL,
    _eplatform.SDL_SCANCODE_CURRENCYSUBUNIT: KeyboardKeyLocation.CURRENCY_SUB_UNIT,
    _eplatform.SDL_SCANCODE_CURRENCYUNIT: KeyboardKeyLocation.CURRENCY_UNIT,
    _eplatform.SDL_SCANCODE_CUT: KeyboardKeyLocation.CUT,
    _eplatform.SDL_SCANCODE_DELETE: KeyboardKeyLocation.DELETE,
    _eplatform.SDL_SCANCODE_END: KeyboardKeyLocation.END,
    _eplatform.SDL_SCANCODE_ESCAPE: KeyboardKeyLocation.ESCAPE,
    _eplatform.SDL_SCANCODE_EXECUTE: KeyboardKeyLocation.EXECUTE,
    _eplatform.SDL_SCANCODE_EXSEL: KeyboardKeyLocation.EXSEL,
    _eplatform.SDL_SCANCODE_FIND: KeyboardKeyLocation.FIND,
    _eplatform.SDL_SCANCODE_HELP: KeyboardKeyLocation.HELP,
    _eplatform.SDL_SCANCODE_HOME: KeyboardKeyLocation.HOME,
    _eplatform.SDL_SCANCODE_INSERT: KeyboardKeyLocation.INSERT,
    _eplatform.SDL_SCANCODE_LALT: KeyboardKeyLocation.LEFT_ALT,
    _eplatform.SDL_SCANCODE_LCTRL: KeyboardKeyLocation.LEFT_CONTROL,
    _eplatform.SDL_SCANCODE_LGUI: KeyboardKeyLocation.LEFT_SPECIAL,
    _eplatform.SDL_SCANCODE_LSHIFT: KeyboardKeyLocation.LEFT_SHIFT,
    _eplatform.SDL_SCANCODE_MENU: KeyboardKeyLocation.MENU,
    _eplatform.SDL_SCANCODE_MODE: KeyboardKeyLocation.MODE,
    _eplatform.SDL_SCANCODE_MUTE: KeyboardKeyLocation.MUTE,
    _eplatform.SDL_SCANCODE_NUMLOCKCLEAR: KeyboardKeyLocation.NUMLOCK_CLEAR,
    _eplatform.SDL_SCANCODE_OPER: KeyboardKeyLocation.OPER,
    _eplatform.SDL_SCANCODE_OUT: KeyboardKeyLocation.OUT,
    _eplatform.SDL_SCANCODE_PAGEDOWN: KeyboardKeyLocation.PAGE_DOWN,
    _eplatform.SDL_SCANCODE_PAGEUP: KeyboardKeyLocation.PAGE_UP,
    _eplatform.SDL_SCANCODE_PASTE: KeyboardKeyLocation.PASTE,
    _eplatform.SDL_SCANCODE_PAUSE: KeyboardKeyLocation.PAUSE,
    _eplatform.SDL_SCANCODE_POWER: KeyboardKeyLocation.POWER,
    _eplatform.SDL_SCANCODE_PRINTSCREEN: KeyboardKeyLocation.PRINT_SCREEN,
    _eplatform.SDL_SCANCODE_PRIOR: KeyboardKeyLocation.PRIOR,
    _eplatform.SDL_SCANCODE_RALT: KeyboardKeyLocation.RIGHT_ALT,
    _eplatform.SDL_SCANCODE_RCTRL: KeyboardKeyLocation.RIGHT_CONTROL,
    _eplatform.SDL_SCANCODE_RETURN: KeyboardKeyLocation.ENTER,
    _eplatform.SDL_SCANCODE_RETURN2: KeyboardKeyLocation.ENTER_2,
    _eplatform.SDL_SCANCODE_RGUI: KeyboardKeyLocation.RIGHT_SPECIAL,
    _eplatform.SDL_SCANCODE_SCROLLLOCK: KeyboardKeyLocation.SCROLL_LOCK,
    _eplatform.SDL_SCANCODE_SELECT: KeyboardKeyLocation.SELECT,
    _eplatform.SDL_SCANCODE_SLEEP: KeyboardKeyLocation.SLEEP,
    _eplatform.SDL_SCANCODE_STOP: KeyboardKeyLocation.STOP,
    _eplatform.SDL_SCANCODE_SYSREQ: KeyboardKeyLocation.SYSTEM_REQUEST,
    _eplatform.SDL_SCANCODE_UNDO: KeyboardKeyLocation.UNDO,
    _eplatform.SDL_SCANCODE_VOLUMEDOWN: KeyboardKeyLocation.VOLUME_DOWN,
    _eplatform.SDL_SCANCODE_VOLUMEUP: KeyboardKeyLocation.VOLUME_UP,
    # media
    _eplatform.SDL_SCANCODE_MEDIA_EJECT: KeyboardKeyLocation.MEDIA_EJECT,
    _eplatform.SDL_SCANCODE_MEDIA_FAST_FORWARD: KeyboardKeyLocation.MEDIA_FAST_FORWARD,
    _eplatform.SDL_SCANCODE_MEDIA_NEXT_TRACK: KeyboardKeyLocation.MEDIA_NEXT_TRACK,
    _eplatform.SDL_SCANCODE_MEDIA_PLAY: KeyboardKeyLocation.MEDIA_PLAY,
    _eplatform.SDL_SCANCODE_MEDIA_PREVIOUS_TRACK: KeyboardKeyLocation.MEDIA_PREVIOUS_TRACK,
    _eplatform.SDL_SCANCODE_MEDIA_REWIND: KeyboardKeyLocation.MEDIA_REWIND,
    _eplatform.SDL_SCANCODE_MEDIA_SELECT: KeyboardKeyLocation.MEDIA_SELECT,
    _eplatform.SDL_SCANCODE_MEDIA_STOP: KeyboardKeyLocation.MEDIA_STOP,
    # ac
    _eplatform.SDL_SCANCODE_AC_BACK: KeyboardKeyLocation.AC_BACK,
    _eplatform.SDL_SCANCODE_AC_BOOKMARKS: KeyboardKeyLocation.AC_BOOKMARKS,
    _eplatform.SDL_SCANCODE_AC_FORWARD: KeyboardKeyLocation.AC_FORWARD,
    _eplatform.SDL_SCANCODE_AC_HOME: KeyboardKeyLocation.AC_HOME,
    _eplatform.SDL_SCANCODE_AC_REFRESH: KeyboardKeyLocation.AC_REFRESH,
    _eplatform.SDL_SCANCODE_AC_SEARCH: KeyboardKeyLocation.AC_SEARCH,
    _eplatform.SDL_SCANCODE_AC_STOP: KeyboardKeyLocation.AC_STOP,
    # arrows
    _eplatform.SDL_SCANCODE_DOWN: KeyboardKeyLocation.DOWN,
    _eplatform.SDL_SCANCODE_LEFT: KeyboardKeyLocation.LEFT,
    _eplatform.SDL_SCANCODE_RIGHT: KeyboardKeyLocation.RIGHT,
    _eplatform.SDL_SCANCODE_UP: KeyboardKeyLocation.UP,
    # international
    _eplatform.SDL_SCANCODE_INTERNATIONAL1: KeyboardKeyLocation.INTERNATIONAL_1,
    _eplatform.SDL_SCANCODE_INTERNATIONAL2: KeyboardKeyLocation.INTERNATIONAL_2,
    _eplatform.SDL_SCANCODE_INTERNATIONAL3: KeyboardKeyLocation.INTERNATIONAL_3,
    _eplatform.SDL_SCANCODE_INTERNATIONAL4: KeyboardKeyLocation.INTERNATIONAL_4,
    _eplatform.SDL_SCANCODE_INTERNATIONAL5: KeyboardKeyLocation.INTERNATIONAL_5,
    _eplatform.SDL_SCANCODE_INTERNATIONAL6: KeyboardKeyLocation.INTERNATIONAL_6,
    _eplatform.SDL_SCANCODE_INTERNATIONAL7: KeyboardKeyLocation.INTERNATIONAL_7,
    _eplatform.SDL_SCANCODE_INTERNATIONAL8: KeyboardKeyLocation.INTERNATIONAL_8,
    _eplatform.SDL_SCANCODE_INTERNATIONAL9: KeyboardKeyLocation.INTERNATIONAL_9,
    # numpad numbers
    _eplatform.SDL_SCANCODE_KP_0: KeyboardKeyLocation.NUMPAD_0,
    _eplatform.SDL_SCANCODE_KP_00: KeyboardKeyLocation.NUMPAD_00,
    _eplatform.SDL_SCANCODE_KP_000: KeyboardKeyLocation.NUMPAD_000,
    _eplatform.SDL_SCANCODE_KP_1: KeyboardKeyLocation.NUMPAD_1,
    _eplatform.SDL_SCANCODE_KP_2: KeyboardKeyLocation.NUMPAD_2,
    _eplatform.SDL_SCANCODE_KP_3: KeyboardKeyLocation.NUMPAD_3,
    _eplatform.SDL_SCANCODE_KP_4: KeyboardKeyLocation.NUMPAD_4,
    _eplatform.SDL_SCANCODE_KP_5: KeyboardKeyLocation.NUMPAD_5,
    _eplatform.SDL_SCANCODE_KP_6: KeyboardKeyLocation.NUMPAD_6,
    _eplatform.SDL_SCANCODE_KP_7: KeyboardKeyLocation.NUMPAD_7,
    _eplatform.SDL_SCANCODE_KP_8: KeyboardKeyLocation.NUMPAD_8,
    _eplatform.SDL_SCANCODE_KP_9: KeyboardKeyLocation.NUMPAD_9,
    # numpad letters
    _eplatform.SDL_SCANCODE_KP_A: KeyboardKeyLocation.NUMPAD_A,
    _eplatform.SDL_SCANCODE_KP_B: KeyboardKeyLocation.NUMPAD_B,
    _eplatform.SDL_SCANCODE_KP_C: KeyboardKeyLocation.NUMPAD_C,
    _eplatform.SDL_SCANCODE_KP_D: KeyboardKeyLocation.NUMPAD_D,
    _eplatform.SDL_SCANCODE_KP_E: KeyboardKeyLocation.NUMPAD_E,
    _eplatform.SDL_SCANCODE_KP_F: KeyboardKeyLocation.NUMPAD_F,
    # numpad symbols/operators
    _eplatform.SDL_SCANCODE_KP_AMPERSAND: KeyboardKeyLocation.NUMPAD_AMPERSAND,
    _eplatform.SDL_SCANCODE_KP_AT: KeyboardKeyLocation.NUMPAD_AT,
    _eplatform.SDL_SCANCODE_KP_COLON: KeyboardKeyLocation.NUMPAD_COLON,
    _eplatform.SDL_SCANCODE_KP_COMMA: KeyboardKeyLocation.NUMPAD_COMMA,
    _eplatform.SDL_SCANCODE_KP_DBLAMPERSAND: KeyboardKeyLocation.NUMPAD_AND,
    _eplatform.SDL_SCANCODE_KP_DBLVERTICALBAR: KeyboardKeyLocation.NUMPAD_OR,
    _eplatform.SDL_SCANCODE_KP_DECIMAL: KeyboardKeyLocation.NUMPAD_DECIMAL,
    _eplatform.SDL_SCANCODE_KP_DIVIDE: KeyboardKeyLocation.NUMPAD_DIVIDE,
    _eplatform.SDL_SCANCODE_KP_ENTER: KeyboardKeyLocation.NUMPAD_ENTER,
    _eplatform.SDL_SCANCODE_KP_EQUALS: KeyboardKeyLocation.NUMPAD_EQUALS,
    _eplatform.SDL_SCANCODE_KP_EQUALSAS400: KeyboardKeyLocation.NUMPAD_AS400_EQUALS,
    _eplatform.SDL_SCANCODE_KP_EXCLAM: KeyboardKeyLocation.NUMPAD_BANG,
    _eplatform.SDL_SCANCODE_KP_GREATER: KeyboardKeyLocation.NUMPAD_GREATER,
    _eplatform.SDL_SCANCODE_KP_HASH: KeyboardKeyLocation.NUMPAD_HASH,
    _eplatform.SDL_SCANCODE_KP_LEFTBRACE: KeyboardKeyLocation.NUMPAD_LEFT_BRACE,
    _eplatform.SDL_SCANCODE_KP_LEFTPAREN: KeyboardKeyLocation.NUMPAD_LEFT_PARENTHESIS,
    _eplatform.SDL_SCANCODE_KP_LESS: KeyboardKeyLocation.NUMPAD_LESS,
    _eplatform.SDL_SCANCODE_KP_MINUS: KeyboardKeyLocation.NUMPAD_MINUS,
    _eplatform.SDL_SCANCODE_KP_MULTIPLY: KeyboardKeyLocation.NUMPAD_MULTIPLY,
    _eplatform.SDL_SCANCODE_KP_PERCENT: KeyboardKeyLocation.NUMPAD_PERCENT,
    _eplatform.SDL_SCANCODE_KP_PERIOD: KeyboardKeyLocation.NUMPAD_PERIOD,
    _eplatform.SDL_SCANCODE_KP_PLUS: KeyboardKeyLocation.NUMPAD_PLUS,
    _eplatform.SDL_SCANCODE_KP_PLUSMINUS: KeyboardKeyLocation.NUMPAD_PLUS_MINUS,
    _eplatform.SDL_SCANCODE_KP_POWER: KeyboardKeyLocation.NUMPAD_POWER,
    _eplatform.SDL_SCANCODE_KP_RIGHTBRACE: KeyboardKeyLocation.NUMPAD_RIGHT_BRACE,
    _eplatform.SDL_SCANCODE_KP_RIGHTPAREN: KeyboardKeyLocation.NUMPAD_RIGHT_PARENTHESIS,
    _eplatform.SDL_SCANCODE_KP_SPACE: KeyboardKeyLocation.NUMPAD_SPACE,
    _eplatform.SDL_SCANCODE_KP_TAB: KeyboardKeyLocation.NUMPAD_TAB,
    _eplatform.SDL_SCANCODE_KP_VERTICALBAR: KeyboardKeyLocation.NUMPAD_PIPE,
    _eplatform.SDL_SCANCODE_KP_XOR: KeyboardKeyLocation.NUMPAD_XOR,
    # numpad actions
    _eplatform.SDL_SCANCODE_KP_BACKSPACE: KeyboardKeyLocation.NUMPAD_BACKSPACE,
    _eplatform.SDL_SCANCODE_KP_BINARY: KeyboardKeyLocation.NUMPAD_BINARY,
    _eplatform.SDL_SCANCODE_KP_CLEAR: KeyboardKeyLocation.NUMPAD_CLEAR,
    _eplatform.SDL_SCANCODE_KP_CLEARENTRY: KeyboardKeyLocation.NUMPAD_CLEAR_ENTRY,
    _eplatform.SDL_SCANCODE_KP_HEXADECIMAL: KeyboardKeyLocation.NUMPAD_HEXADECIMAL,
    _eplatform.SDL_SCANCODE_KP_OCTAL: KeyboardKeyLocation.NUMPAD_OCTAL,
    # memory
    _eplatform.SDL_SCANCODE_KP_MEMADD: KeyboardKeyLocation.NUMPAD_MEMORY_ADD,
    _eplatform.SDL_SCANCODE_KP_MEMCLEAR: KeyboardKeyLocation.NUMPAD_MEMORY_CLEAR,
    _eplatform.SDL_SCANCODE_KP_MEMDIVIDE: KeyboardKeyLocation.NUMPAD_MEMORY_DIVIDE,
    _eplatform.SDL_SCANCODE_KP_MEMMULTIPLY: KeyboardKeyLocation.NUMPAD_MEMORY_MULTIPLY,
    _eplatform.SDL_SCANCODE_KP_MEMRECALL: KeyboardKeyLocation.NUMPAD_MEMORY_RECALL,
    _eplatform.SDL_SCANCODE_KP_MEMSTORE: KeyboardKeyLocation.NUMPAD_MEMORY_STORE,
    _eplatform.SDL_SCANCODE_KP_MEMSUBTRACT: KeyboardKeyLocation.NUMPAD_MEMORY_SUBTRACT,
    # language
    _eplatform.SDL_SCANCODE_LANG1: KeyboardKeyLocation.LANGUAGE_1,
    _eplatform.SDL_SCANCODE_LANG2: KeyboardKeyLocation.LANGUAGE_2,
    _eplatform.SDL_SCANCODE_LANG3: KeyboardKeyLocation.LANGUAGE_3,
    _eplatform.SDL_SCANCODE_LANG4: KeyboardKeyLocation.LANGUAGE_4,
    _eplatform.SDL_SCANCODE_LANG5: KeyboardKeyLocation.LANGUAGE_5,
    _eplatform.SDL_SCANCODE_LANG6: KeyboardKeyLocation.LANGUAGE_6,
    _eplatform.SDL_SCANCODE_LANG7: KeyboardKeyLocation.LANGUAGE_7,
    _eplatform.SDL_SCANCODE_LANG8: KeyboardKeyLocation.LANGUAGE_8,
    _eplatform.SDL_SCANCODE_LANG9: KeyboardKeyLocation.LANGUAGE_9,
}

assert len(_SDL_SCANCODE_TO_KEY_LOCATION) == len(KeyboardKeyLocation)
