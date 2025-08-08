__all__ = [
    "connect_controller",
    "Controller",
    "ControllerAnalogInput",
    "ControllerAnalogInputChanged",
    "ControllerBinaryInput",
    "ControllerBinaryInputChanged",
    "ControllerButton",
    "ControllerButtonChanged",
    "ControllerButtonName",
    "ControllerConnectionChanged",
    "ControllerDirectionalInput",
    "ControllerDirectionalInputChanged",
    "ControllerDirectionalInputValue",
    "ControllerDisconnectedError",
    "ControllerStick",
    "ControllerStickChanged",
    "ControllerStickName",
    "ControllerTrigger",
    "ControllerTriggerChanged",
    "ControllerTriggerName",
    "ControllerType",
    "controller_change_axis",
    "controller_change_button",
    "controller_change_hat",
    "disconnect_controller",
    "discover_controllers",
    "forget_controllers",
    "get_controllers",
]

from enum import IntFlag
from enum import StrEnum
from logging import getLogger
from typing import ClassVar
from typing import Collection
from typing import Final
from typing import Generator
from typing import Generic
from typing import Literal
from typing import Mapping
from typing import NamedTuple
from typing import TypeAlias
from typing import TypedDict
from typing import TypeVar
from uuid import UUID

from eevent import Event
from emath import DVector2

from . import _eplatform
from ._eplatform import SDL_GAMEPAD_BINDTYPE_AXIS
from ._eplatform import SDL_GAMEPAD_BINDTYPE_BUTTON
from ._eplatform import SDL_GAMEPAD_BINDTYPE_HAT
from ._eplatform import close_sdl_joystick
from ._eplatform import get_sdl_joysticks
from ._eplatform import open_sdl_joystick
from ._type import SdlGamepadAxis
from ._type import SdlGamepadButton
from ._type import SdlGamepadButtonLabel
from ._type import SdlGamepadType
from ._type import SdlHat
from ._type import SdlJoystickId

_N = TypeVar("_N", bound=str)


log = getLogger("eplatform.controller")


class ControllerDisconnectedError(RuntimeError):
    pass


class _ControllerInput(Generic[_N]):
    _controller: "Controller | None"

    def __init__(self, name: _N):
        self._controller = None
        self._name = name

    def __repr__(self) -> str:
        if self._controller is None:
            return f"<{self.__class__.__name__}>"
        return f"<{self.__class__.__name__} '{self._name}'>"

    @property
    def is_connected(self):
        return self._controller is not None

    @property
    def controller(self) -> "Controller":
        if self._controller is None:
            raise ControllerDisconnectedError()
        return self._controller

    @property
    def name(self) -> _N:
        if self._controller is None:
            raise ControllerDisconnectedError()
        return self._name


class ControllerAnalogInputChanged(TypedDict):
    analog_input: "ControllerAnalogInput"
    value: float


class ControllerAnalogInput(_ControllerInput[str]):
    _value: float

    changed: Event[ControllerAnalogInputChanged] = Event()

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.changed = Event()

    @property
    def value(self) -> float:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._value

    def _set_value(self, value: float) -> bool:
        if self._value == value:
            return False

        self._value = value

        data: ControllerAnalogInputChanged = {"analog_input": self, "value": value}
        ControllerAnalogInput.changed(data)
        self.changed(data)

        return True

    def _calculate_mapping_value(
        self, input_min: float, input_max: float, output_min: float, output_max: float
    ) -> float | None:
        cmp_min = input_min
        cmp_max = input_max
        if cmp_max < cmp_min:
            cmp_min, cmp_max = cmp_max, cmp_min
        if self._value >= cmp_min and self._value <= cmp_max:
            v = (self._value - input_min) / (input_max - input_min)
            return output_min + v * (output_max - output_min)
        return None


class ControllerBinaryInputChanged(TypedDict):
    binary_input: "ControllerBinaryInput"
    value: bool


class ControllerBinaryInput(_ControllerInput[str]):
    _value: bool

    changed: Event[ControllerBinaryInputChanged] = Event()

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.changed = Event()

    @property
    def value(self) -> bool:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._value

    def _set_value(self, value: bool) -> bool:
        if self._value == value:
            return False

        self._value = value

        data: ControllerBinaryInputChanged = {"binary_input": self, "value": value}
        ControllerBinaryInput.changed(data)
        self.changed(data)

        return True


class ControllerDirectionalInputValue(IntFlag):
    NEUTRAL = 0
    UP = _eplatform.SDL_HAT_UP
    RIGHT = _eplatform.SDL_HAT_RIGHT
    DOWN = _eplatform.SDL_HAT_DOWN
    LEFT = _eplatform.SDL_HAT_LEFT
    UP_RIGHT = _eplatform.SDL_HAT_UP | _eplatform.SDL_HAT_RIGHT
    UP_LEFT = _eplatform.SDL_HAT_UP | _eplatform.SDL_HAT_LEFT
    DOWN_RIGHT = _eplatform.SDL_HAT_DOWN | _eplatform.SDL_HAT_RIGHT
    DOWN_LEFT = _eplatform.SDL_HAT_DOWN | _eplatform.SDL_HAT_LEFT
    LEFT_RIGHT = _eplatform.SDL_HAT_LEFT | _eplatform.SDL_HAT_RIGHT
    UP_DOWN = _eplatform.SDL_HAT_UP | _eplatform.SDL_HAT_DOWN
    ALL = (
        _eplatform.SDL_HAT_UP
        | _eplatform.SDL_HAT_DOWN
        | _eplatform.SDL_HAT_LEFT
        | _eplatform.SDL_HAT_RIGHT
    )


class ControllerDirectionalInputChanged(TypedDict):
    directional_input: "ControllerDirectionalInput"
    value: ControllerDirectionalInputValue


class ControllerDirectionalInput(_ControllerInput[str]):
    _value: ControllerDirectionalInputValue

    changed: Event[ControllerDirectionalInputChanged] = Event()

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.changed = Event()

    @property
    def value(self) -> ControllerDirectionalInputValue:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._value

    def _set_value(self, value: ControllerDirectionalInputValue) -> bool:
        if self._value == value:
            return False

        self._value = value

        data: ControllerDirectionalInputChanged = {"directional_input": self, "value": self._value}
        ControllerDirectionalInput.changed(data)
        self.changed(data)

        return True


class ControllerButtonChanged(TypedDict):
    button: "ControllerButton"
    is_pressed: bool


class ControllerButtonName(StrEnum):
    SOUTH = "south button"
    EAST = "east button"
    WEST = "west button"
    NORTH = "north button"
    BACK = "back button"
    GUIDE = "guide button"
    START = "start button"
    LEFT_STICK = "left stick button"
    RIGHT_STICK = "right stick button"
    LEFT_SHOULDER = "left shoulder button"
    RIGHT_SHOULDER = "right shoulder button"
    UP = "up button"
    DOWN = "down button"
    LEFT = "left button"
    RIGHT = "right button"
    RIGHT_PADDLE_1 = "right paddle 1 button"
    LEFT_PADDLE_1 = "left paddle 1 button"
    RIGHT_PADDLE_2 = "right paddle 2 button"
    LEFT_PADDLE_2 = "left paddle 2 button"
    TOUCHPAD = "touchpad button"
    A = "a button"
    B = "b button"
    X = "x button"
    Y = "y button"
    CROSS = "cross button"
    CIRCLE = "circle button"
    SQUARE = "square button"
    TRIANGLE = "triangle button"


class ControllerButton(_ControllerInput[ControllerButtonName]):
    _is_pressed: bool = False

    _analog_input_affectors: tuple[tuple[ControllerAnalogInput, float, float], ...] = ()
    _binary_input_affectors: tuple[ControllerBinaryInput, ...] = ()
    _directional_input_affectors: tuple[
        tuple[ControllerDirectionalInput, ControllerDirectionalInputValue], ...
    ] = ()

    changed: Event[ControllerButtonChanged] = Event()
    pressed: Event[ControllerButtonChanged] = Event()
    released: Event[ControllerButtonChanged] = Event()

    analog_mapping_threshold: float = 0.3

    def __init__(self, name: ControllerButtonName) -> None:
        super().__init__(name)
        self.changed = Event()
        self.pressed = Event()
        self.released = Event()

    def _get_mapped_is_pressed(self) -> bool:
        for analog_input, input_min, input_max in self._analog_input_affectors:
            v = analog_input._calculate_mapping_value(input_min, input_max, -1.0, 1.0)
            if v is not None:
                v = abs(v)
                if v > (1.0 - self.analog_mapping_threshold):
                    return True
                elif v < self.analog_mapping_threshold:
                    return False
        for binary_input in self._binary_input_affectors:
            if binary_input.value:
                return True
        for directional_input, directional_input_mask in self._directional_input_affectors:
            if (directional_input.value & directional_input_mask) != 0:
                return True
        return False

    def _map(self) -> None:
        is_pressed = self._get_mapped_is_pressed()

        if is_pressed == self._is_pressed:
            return

        self._is_pressed = is_pressed

        data: ControllerButtonChanged = {"button": self, "is_pressed": is_pressed}
        ControllerButton.changed(data)
        self.changed(data)
        if is_pressed:
            ControllerButton.pressed(data)
            self.pressed(data)
        else:
            ControllerButton.released(data)
            self.released(data)

    @property
    def is_pressed(self) -> bool:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._is_pressed


class ControllerStickName(StrEnum):
    LEFT = "left stick"
    RIGHT = "right stick"


class ControllerStickChanged(TypedDict):
    stick: "ControllerStick"
    vector: DVector2


class ControllerStick(_ControllerInput[ControllerStickName]):
    _vector: DVector2 = DVector2(0)

    _analog_input_affectors: tuple[
        tuple[ControllerAnalogInput, float, float, float, float, int], ...
    ] = ()
    _binary_input_affectors: tuple[tuple[ControllerBinaryInput, float, float, int], ...] = ()
    _directional_input_affectors: tuple[
        tuple[ControllerDirectionalInput, ControllerDirectionalInputValue, float, float, int], ...
    ] = ()

    changed: Event[ControllerStickChanged] = Event()

    def __init__(self, name: ControllerStickName) -> None:
        super().__init__(name)
        self.changed = Event()

    def _get_mapped_vector(self) -> DVector2:
        value = [0.0, 0.0]
        for analog_input, *calc_args, component in self._analog_input_affectors:
            v = analog_input._calculate_mapping_value(*calc_args)
            if v is not None:
                value[component] += v
        for (
            directional_input,
            directional_input_mask,
            output_min,
            output_max,
            component,
        ) in self._directional_input_affectors:
            if (directional_input.value & directional_input_mask) != 0:
                value[component] += output_max
            else:
                value[component] += output_min
        for binary_input, output_min, output_max, component in self._binary_input_affectors:
            if binary_input.value:
                value[component] += output_max
            else:
                value[component] += output_min
        return DVector2(max(-1.0, min(value[0], 1.0)), max(-1.0, min(value[1], 1.0)))

    def _map(self) -> None:
        vector = self._get_mapped_vector()

        if vector == self._vector:
            return

        self._vector = vector

        data: ControllerStickChanged = {"stick": self, "vector": vector}
        ControllerStick.changed(data)
        self.changed(data)

    @property
    def vector(self) -> DVector2:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._vector


class ControllerTriggerName(StrEnum):
    LEFT = "left trigger"
    RIGHT = "right trigger"


class ControllerTriggerChanged(TypedDict):
    trigger: "ControllerTrigger"
    position: float


class ControllerTrigger(_ControllerInput[ControllerTriggerName]):
    _position: float = 0.0

    _analog_input_affectors: tuple[
        tuple[ControllerAnalogInput, float, float, float, float], ...
    ] = ()
    _binary_input_affectors: tuple[tuple[ControllerBinaryInput, float, float], ...] = ()
    _directional_input_affectors: tuple[
        tuple[ControllerDirectionalInput, ControllerDirectionalInputValue, float, float], ...
    ] = ()

    changed: Event[ControllerTriggerChanged] = Event()

    def __init__(self, name: ControllerTriggerName) -> None:
        super().__init__(name)
        self.changed = Event()

    def _get_mapped_position(self) -> float:
        value = 0.0
        for analog_input, *calc_args in self._analog_input_affectors:
            v = analog_input._calculate_mapping_value(*calc_args)
            if v is not None:
                value += v
        for (
            directional_input,
            directional_input_mask,
            output_min,
            output_max,
        ) in self._directional_input_affectors:
            if (directional_input.value & directional_input_mask) != 0:
                value += output_max
            else:
                value += output_min
        for binary_input, output_min, output_max in self._binary_input_affectors:
            if binary_input.value:
                value += output_max
            else:
                value += output_min
        return max(0.0, min(value, 1.0))

    def _map(self) -> None:
        position = self._get_mapped_position()
        if position == self._position:
            return

        self._position = position

        data: ControllerTriggerChanged = {"trigger": self, "position": position}
        ControllerTrigger.changed(data)
        self.changed(data)

    @property
    def position(self) -> float:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._position


class ControllerConnectionChanged(TypedDict):
    controller: "Controller"
    is_connected: bool


_AffectorInput: TypeAlias = (
    ControllerAnalogInput | ControllerBinaryInput | ControllerDirectionalInput
)
_AffecteeInput: TypeAlias = ControllerButton | ControllerStick | ControllerTrigger


class ControllerType(StrEnum):
    UNKNOWN = "unknown"
    GAMEPAD = "gamepad"
    XBOX_360 = "xbox 360"
    XBOX_ONE = "xbox one"
    PLAYSTATION_3 = "playstation 3"
    PLAYSTATION_4 = "playstation 4"
    PLAYSTATION_5 = "playstation 5"
    NINTENDO_SWITCH_PRO = "nintendo switch pro"
    NINTENDO_SWITCH_JOYCON_LEFT = "nintendo switch joycon left"
    NINTENDO_SWITCH_JOYCON_RIGHT = "nintendo switch joycon left"
    NINTENDO_SWITCH_JOYCONS = "nintendo switch joycons"


class Controller:
    _sdl_joystick: SdlJoystickId | None = None
    _name: str = ""
    _uuid: UUID = UUID(bytes=b"\x00" * 16)
    _serial: str = ""
    _player_index: int | None = None
    _type: ControllerType = ControllerType.UNKNOWN

    _input_affects: dict[_AffectorInput, tuple[_AffecteeInput, ...]] = {}
    _input_affected_by: dict[_AffecteeInput, tuple[_AffectorInput, ...]] = {}

    _inputs: dict[
        str,
        ControllerAnalogInput
        | ControllerBinaryInput
        | ControllerDirectionalInput
        | ControllerButton
        | ControllerStick
        | ControllerTrigger,
    ] = {}
    _analog_inputs: tuple[ControllerAnalogInput, ...] = ()
    _binary_inputs: tuple[ControllerBinaryInput, ...] = ()
    _directional_inputs: tuple[ControllerDirectionalInput, ...] = ()
    _buttons: tuple[ControllerButton, ...] = ()
    _sticks: tuple[ControllerStick, ...] = ()
    _triggers: tuple[ControllerTrigger, ...] = ()

    connection_changed: Event[ControllerConnectionChanged] = Event()
    connected: ClassVar[Event[ControllerConnectionChanged]] = Event()
    disconnected: Event[ControllerConnectionChanged] = Event()

    def __init__(self) -> None:
        self.connection_changed = Event()
        self.disconnected = Event()

    def __repr__(self) -> str:
        if self._sdl_joystick is None:
            return "<Controller>"
        id = self._uuid.hex
        if self._serial:
            id = f"{id} {self._serial}"
        if self._player_index is not None:
            id = f"(Player {self._player_index}) {id}"
        return f"<Controller {self._name!r} {id}>"

    def _update_mapped_inputs(self, affector: _AffectorInput) -> None:
        try:
            affectees = self._input_affects[affector]
        except KeyError:
            return
        for affectee in affectees:
            affectee._map()

    def get_input(
        self, name: str
    ) -> (
        ControllerAnalogInput
        | ControllerBinaryInput
        | ControllerDirectionalInput
        | ControllerButton
        | ControllerStick
        | ControllerTrigger
    ):
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._inputs[str(name)]

    def get_analog_input(self, name: str) -> ControllerAnalogInput:
        input = self.get_input(name)
        if not isinstance(input, ControllerAnalogInput):
            raise KeyError(name)
        return input

    def get_binary_input(self, name: str) -> ControllerBinaryInput:
        input = self.get_input(name)
        if not isinstance(input, ControllerBinaryInput):
            raise KeyError(name)
        return input

    def get_directional_input(self, name: str) -> ControllerDirectionalInput:
        input = self.get_input(name)
        if not isinstance(input, ControllerDirectionalInput):
            raise KeyError(name)
        return input

    def get_button(self, name: ControllerButtonName) -> ControllerButton:
        input = self.get_input(name)
        if not isinstance(input, ControllerButton):
            raise KeyError(name)
        return input

    def get_stick(self, name: ControllerStickName) -> ControllerStick:
        input = self.get_input(name)
        if not isinstance(input, ControllerStick):
            raise KeyError(name)
        return input

    def get_trigger(self, name: ControllerTriggerName) -> ControllerTrigger:
        input = self.get_input(name)
        if not isinstance(input, ControllerTrigger):
            raise KeyError(name)
        return input

    @property
    def analog_inputs(self) -> Collection[ControllerAnalogInput]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._analog_inputs

    @property
    def binary_inputs(self) -> Collection[ControllerBinaryInput]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._binary_inputs

    @property
    def directional_inputs(self) -> Collection[ControllerDirectionalInput]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._directional_inputs

    @property
    def buttons(self) -> Collection[ControllerButton]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._buttons

    @property
    def sticks(self) -> Collection[ControllerStick]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._sticks

    @property
    def triggers(self) -> Collection[ControllerTrigger]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._triggers

    @property
    def is_connected(self) -> bool:
        return self._sdl_joystick is not None

    @property
    def name(self) -> str:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._name

    @property
    def type(self) -> ControllerType:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._type

    @property
    def uuid(self) -> UUID:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._uuid


_SDL_GAMEPAD_TYPE_CONTROLLER_TYPE: Final[Mapping[SdlGamepadType, ControllerType]] = {
    _eplatform.SDL_GAMEPAD_TYPE_UNKNOWN: ControllerType.UNKNOWN,
    _eplatform.SDL_GAMEPAD_TYPE_STANDARD: ControllerType.GAMEPAD,
    _eplatform.SDL_GAMEPAD_TYPE_XBOX360: ControllerType.XBOX_360,
    _eplatform.SDL_GAMEPAD_TYPE_XBOXONE: ControllerType.XBOX_ONE,
    _eplatform.SDL_GAMEPAD_TYPE_PS3: ControllerType.PLAYSTATION_3,
    _eplatform.SDL_GAMEPAD_TYPE_PS4: ControllerType.PLAYSTATION_4,
    _eplatform.SDL_GAMEPAD_TYPE_PS5: ControllerType.PLAYSTATION_5,
    _eplatform.SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_PRO: ControllerType.NINTENDO_SWITCH_PRO,
    _eplatform.SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_LEFT: ControllerType.NINTENDO_SWITCH_JOYCON_LEFT,
    _eplatform.SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_RIGHT: ControllerType.NINTENDO_SWITCH_JOYCON_RIGHT,
    _eplatform.SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_PAIR: ControllerType.NINTENDO_SWITCH_JOYCONS,
}

_SDL_GAMEPAD_BUTTON_NAME: Final[Mapping[SdlGamepadButton, ControllerButtonName]] = {
    _eplatform.SDL_GAMEPAD_BUTTON_SOUTH: ControllerButtonName.SOUTH,
    _eplatform.SDL_GAMEPAD_BUTTON_EAST: ControllerButtonName.EAST,
    _eplatform.SDL_GAMEPAD_BUTTON_WEST: ControllerButtonName.WEST,
    _eplatform.SDL_GAMEPAD_BUTTON_NORTH: ControllerButtonName.NORTH,
    _eplatform.SDL_GAMEPAD_BUTTON_BACK: ControllerButtonName.BACK,
    _eplatform.SDL_GAMEPAD_BUTTON_GUIDE: ControllerButtonName.GUIDE,
    _eplatform.SDL_GAMEPAD_BUTTON_START: ControllerButtonName.START,
    _eplatform.SDL_GAMEPAD_BUTTON_LEFT_STICK: ControllerButtonName.LEFT_STICK,
    _eplatform.SDL_GAMEPAD_BUTTON_RIGHT_STICK: ControllerButtonName.RIGHT_STICK,
    _eplatform.SDL_GAMEPAD_BUTTON_LEFT_SHOULDER: ControllerButtonName.LEFT_SHOULDER,
    _eplatform.SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER: ControllerButtonName.RIGHT_SHOULDER,
    _eplatform.SDL_GAMEPAD_BUTTON_DPAD_UP: ControllerButtonName.UP,
    _eplatform.SDL_GAMEPAD_BUTTON_DPAD_DOWN: ControllerButtonName.DOWN,
    _eplatform.SDL_GAMEPAD_BUTTON_DPAD_LEFT: ControllerButtonName.LEFT,
    _eplatform.SDL_GAMEPAD_BUTTON_DPAD_RIGHT: ControllerButtonName.RIGHT,
    _eplatform.SDL_GAMEPAD_BUTTON_RIGHT_PADDLE1: ControllerButtonName.RIGHT_PADDLE_1,
    _eplatform.SDL_GAMEPAD_BUTTON_LEFT_PADDLE1: ControllerButtonName.LEFT_PADDLE_1,
    _eplatform.SDL_GAMEPAD_BUTTON_RIGHT_PADDLE2: ControllerButtonName.RIGHT_PADDLE_2,
    _eplatform.SDL_GAMEPAD_BUTTON_LEFT_PADDLE2: ControllerButtonName.LEFT_PADDLE_2,
    _eplatform.SDL_GAMEPAD_BUTTON_TOUCHPAD: ControllerButtonName.TOUCHPAD,
}

_SDL_GAMEPAD_BUTTON_LABEL_NAME: Final[Mapping[SdlGamepadButtonLabel, ControllerButtonName]] = {
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_A: ControllerButtonName.A,
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_B: ControllerButtonName.B,
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_X: ControllerButtonName.X,
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_Y: ControllerButtonName.Y,
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_CROSS: ControllerButtonName.CROSS,
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_CIRCLE: ControllerButtonName.CIRCLE,
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_SQUARE: ControllerButtonName.SQUARE,
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_TRIANGLE: ControllerButtonName.TRIANGLE,
}

_SDL_GAMEPAD_AXIS_STICK_NAME: Final[
    Mapping[SdlGamepadAxis, tuple[ControllerStickName, Literal[0, 1]]]
] = {
    _eplatform.SDL_GAMEPAD_AXIS_LEFTX: (ControllerStickName.LEFT, 0),
    _eplatform.SDL_GAMEPAD_AXIS_LEFTY: (ControllerStickName.LEFT, 1),
    _eplatform.SDL_GAMEPAD_AXIS_RIGHTX: (ControllerStickName.RIGHT, 0),
    _eplatform.SDL_GAMEPAD_AXIS_RIGHTY: (ControllerStickName.RIGHT, 1),
}

_SDL_GAMEPAD_AXIS_TRIGGER_NAME: Final[Mapping[SdlGamepadAxis, ControllerTriggerName]] = {
    _eplatform.SDL_GAMEPAD_AXIS_LEFT_TRIGGER: ControllerTriggerName.LEFT,
    _eplatform.SDL_GAMEPAD_AXIS_RIGHT_TRIGGER: ControllerTriggerName.RIGHT,
}


_controllers: dict[SdlJoystickId, Controller] = {}


def get_controllers() -> Generator[Controller, None, None]:
    yield from _controllers.values()


def connect_controller(sdl_joystick: SdlJoystickId) -> None:
    assert sdl_joystick not in _controllers
    _controllers[sdl_joystick] = controller = Controller()

    (name, guid, serial, player_index, axis_details, button_details, hat_details, gamepad_info) = (
        open_sdl_joystick(sdl_joystick)
    )
    controller._sdl_joystick = sdl_joystick
    controller._name = name
    controller._uuid = UUID(hex=guid)
    controller._serial = serial or ""
    controller._player_index = player_index if player_index >= 0 else None

    controller._inputs = {}

    analog_inputs: list[ControllerAnalogInput] = []
    binary_inputs: list[ControllerBinaryInput] = []
    directional_inputs: list[ControllerDirectionalInput] = []

    for i, (value,) in enumerate(axis_details):
        name = f"analog {i}"
        input = ControllerAnalogInput(name)
        input._controller = controller
        input._value = value
        analog_inputs.append(input)
        if name in controller._inputs:
            raise RuntimeError(f"{name} already in inputs")
        controller._inputs[name] = input

    for i, (value,) in enumerate(button_details):
        name = f"binary {i}"
        input = ControllerBinaryInput(name)
        input._controller = controller
        input._value = value
        binary_inputs.append(input)
        if name in controller._inputs:
            raise RuntimeError(f"{name} already in inputs")
        controller._inputs[name] = input

    for i, (value,) in enumerate(hat_details):
        name = f"directional {i}"
        input = ControllerDirectionalInput(name)
        input._controller = controller
        input._value = ControllerDirectionalInputValue(value)
        directional_inputs.append(input)
        if name in controller._inputs:
            raise RuntimeError(f"{name} already in inputs")
        controller._inputs[name] = input

    controller._analog_inputs = tuple(analog_inputs)
    controller._binary_inputs = tuple(binary_inputs)
    controller._directional_inputs = tuple(directional_inputs)

    if gamepad_info:
        mapping_details, sdl_gamepad_type = gamepad_info
        try:
            controller._type = _SDL_GAMEPAD_TYPE_CONTROLLER_TYPE[sdl_gamepad_type]
        except KeyError:
            pass

        input_affects: dict[_AffectorInput, list[_AffecteeInput]] = {}
        input_affected_by: dict[_AffecteeInput, list[_AffectorInput]] = {}

        buttons: dict[ControllerButtonName, ControllerButton] = {}
        sticks: dict[ControllerStickName, ControllerStick] = {}
        triggers: dict[ControllerTriggerName, ControllerTrigger] = {}
        for (input_type, *input_args), (output_type, *output_args) in mapping_details:
            input_directional_mask: float | None = None
            input_axis_min: float | None = None
            input_axis_max: float | None = None

            if input_type == SDL_GAMEPAD_BINDTYPE_BUTTON:
                input_button_index = input_args[0]
                try:
                    input = binary_inputs[input_button_index]
                except IndexError:
                    log.warning(
                        f"unable to map to binary input {input_button_index}, skipping mapping"
                    )
                    continue
            elif input_type == SDL_GAMEPAD_BINDTYPE_AXIS:
                input_analog_index, input_axis_min, input_axis_max = input_args
                try:
                    input = analog_inputs[input_analog_index]
                except IndexError:
                    log.warning(
                        f"unable to map to analog input {input_analog_index}, skipping mapping"
                    )
                    continue
            elif input_type == SDL_GAMEPAD_BINDTYPE_HAT:
                input_directional_index, input_directional_mask = input_args
                try:
                    input = directional_inputs[input_directional_index]
                except IndexError:
                    log.warning(
                        f"unable to map to directional input {directional_inputs}, skipping mapping"
                    )
                    continue
            else:
                log.warning(f"unexpected input type {input_type!r}, skipping mapping")
                continue

            if output_type == SDL_GAMEPAD_BINDTYPE_BUTTON:
                # map button
                sdl_button, sdl_button_label = output_args
                button_name = _SDL_GAMEPAD_BUTTON_NAME.get(sdl_button)
                button_label_name = _SDL_GAMEPAD_BUTTON_LABEL_NAME.get(sdl_button_label)
                if button_name is None and button_label_name is None:
                    log.warning(
                        f"unexpected button {sdl_button} and label {sdl_button_label}, "
                        f"skipping mapping"
                    )
                    continue

                true_button_name = button_label_name or button_name
                assert isinstance(true_button_name, str)
                try:
                    output = buttons[true_button_name]
                except KeyError:
                    output = ControllerButton(true_button_name)
                output._controller = controller

                if input_type == SDL_GAMEPAD_BINDTYPE_BUTTON:
                    output._binary_input_affectors += (input,)
                elif input_type == SDL_GAMEPAD_BINDTYPE_HAT:
                    assert input_directional_mask is not None
                    output._directional_input_affectors += (
                        (input, ControllerDirectionalInputValue(input_directional_mask)),
                    )
                elif input_type == SDL_GAMEPAD_BINDTYPE_AXIS:
                    assert isinstance(input, ControllerAnalogInput)
                    assert input_axis_min is not None
                    assert input_axis_max is not None
                    output._analog_input_affectors += ((input, input_axis_min, input_axis_max),)
                else:
                    log.warning(f"unexpected input type {input_type!r}, skipping mapping")
                    continue

                if button_label_name is not None:
                    buttons[button_label_name] = output
                if button_name is not None:
                    buttons[button_name] = output
            elif output_type == SDL_GAMEPAD_BINDTYPE_AXIS:
                sdl_axis, output_axis_min, output_axis_max = output_args
                try:
                    trigger_name = _SDL_GAMEPAD_AXIS_TRIGGER_NAME[sdl_axis]
                except KeyError:
                    trigger_name = None
                if trigger_name is None:
                    # map stick
                    try:
                        stick_name, stick_component = _SDL_GAMEPAD_AXIS_STICK_NAME[sdl_axis]
                    except KeyError:
                        log.warning(f"unexpected axis {sdl_axis}, skipping mapping")
                        continue
                    try:
                        output = sticks[stick_name]
                    except KeyError:
                        output = ControllerStick(stick_name)
                    output._controller = controller

                    if input_type == SDL_GAMEPAD_BINDTYPE_AXIS:
                        assert isinstance(input, ControllerAnalogInput)
                        assert input_axis_min is not None
                        assert input_axis_max is not None
                        output._analog_input_affectors += (
                            (
                                input,
                                input_axis_min,
                                input_axis_max,
                                output_axis_min,
                                output_axis_max,
                                stick_component,
                            ),
                        )
                    elif input_type == SDL_GAMEPAD_BINDTYPE_HAT:
                        assert input_directional_mask is not None
                        output._directional_input_affectors += (
                            (
                                input,
                                ControllerDirectionalInputValue(input_directional_mask),
                                output_axis_min,
                                output_axis_max,
                                stick_component,
                            ),
                        )
                    elif input_type == SDL_GAMEPAD_BINDTYPE_BUTTON:
                        output._binary_input_affectors += (
                            (input, output_axis_min, output_axis_max, stick_component),
                        )
                    else:
                        log.warning(f"unexpected input type {input_type!r}, skipping mapping")
                        continue

                    sticks[stick_name] = output
                else:
                    # map trigger
                    try:
                        output = triggers[trigger_name]
                    except KeyError:
                        output = ControllerTrigger(trigger_name)
                    output._controller = controller

                    if input_type == SDL_GAMEPAD_BINDTYPE_AXIS:
                        assert isinstance(input, ControllerAnalogInput)
                        assert input_axis_min is not None
                        assert input_axis_max is not None
                        output._analog_input_affectors += (
                            (
                                input,
                                input_axis_min,
                                input_axis_max,
                                output_axis_min,
                                output_axis_max,
                            ),
                        )
                    elif input_type == SDL_GAMEPAD_BINDTYPE_HAT:
                        assert input_directional_mask is not None
                        output._directional_input_affectors += (
                            (
                                input,
                                ControllerDirectionalInputValue(input_directional_mask),
                                output_axis_min,
                                output_axis_max,
                            ),
                        )
                    elif input_type == SDL_GAMEPAD_BINDTYPE_BUTTON:
                        output._binary_input_affectors += (
                            (input, output_axis_min, output_axis_max),
                        )
                    else:
                        log.warning(f"unexpected input type {input_type!r}, skipping mapping")
                        continue

                    triggers[trigger_name] = output
            else:
                log.warning(f"unexpected output type {output_type!r}, skipping mapping")
                continue

            input_affects.setdefault(input, []).append(output)
            input_affected_by.setdefault(output, []).append(input)

        for name, input in (*buttons.items(), *sticks.items(), *triggers.items()):
            if name in controller._inputs:
                raise RuntimeError(f"{name} already in inputs")
            controller._inputs[str(name)] = input

        controller._input_affects = {k: tuple(v) for k, v in input_affects.items()}
        controller._input_affected_by = {k: tuple(v) for k, v in input_affected_by.items()}
        controller._buttons = tuple(set(buttons.values()))
        controller._sticks = tuple(set(sticks.values()))
        controller._triggers = tuple(set(triggers.values()))

    data: ControllerConnectionChanged = {"controller": controller, "is_connected": True}
    Controller.connection_changed(data)
    Controller.connected(data)


def disconnect_controller(sdl_joystick: SdlJoystickId) -> None:
    controller = _controllers.pop(sdl_joystick)
    controller._sdl_joystick = None
    for input in controller._inputs.values():
        input._controller = None

    close_sdl_joystick(sdl_joystick)

    data: ControllerConnectionChanged = {"controller": controller, "is_connected": False}
    Controller.connection_changed(data)
    controller.connection_changed(data)
    Controller.disconnected(data)
    controller.disconnected(data)


def discover_controllers() -> None:
    for sdl_joystick in get_sdl_joysticks():
        connect_controller(sdl_joystick)


def forget_controllers() -> None:
    for sdl_joystick in list(_controllers.keys()):
        disconnect_controller(sdl_joystick)


def controller_change_axis(sdl_joystick: SdlJoystickId, axis_index: int, value: float) -> bool:
    controller = _controllers[sdl_joystick]
    input = controller._analog_inputs[axis_index]
    if input._set_value(value):
        controller._update_mapped_inputs(input)
        return True
    return False


def controller_change_button(
    sdl_joystick: SdlJoystickId, button_index: int, is_pressed: bool
) -> bool:
    controller = _controllers[sdl_joystick]
    input = controller._binary_inputs[button_index]
    if input._set_value(is_pressed):
        controller._update_mapped_inputs(input)
        return True
    return False


def controller_change_hat(sdl_joystick, hat_index, value: SdlHat) -> bool:
    controller = _controllers[sdl_joystick]
    input = controller._directional_inputs[hat_index]
    if input._set_value(ControllerDirectionalInputValue(value)):
        controller._update_mapped_inputs(input)
        return True
    return False
