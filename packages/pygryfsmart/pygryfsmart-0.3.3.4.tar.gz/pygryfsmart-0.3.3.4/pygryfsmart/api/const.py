from enum import IntEnum

BAUDRATE = 115200
PORT = 4510

class OutputActions(IntEnum):
    """Enum with Output states."""

    ON = 1
    OFF = 2
    TOGGLE = 3

class ShutterStates(IntEnum):
    """Enum with Shutter states."""

    CLOSE = 1
    OPEN = 2
    STOP = 3
    STEP_MODE = 4

class KeyModes(IntEnum):
    "Enum with key modes."

    NO = 0
    NC = 1

class DriverFunctions():
    """Enum with driver functions."""

    INPUTS = "I"
    OUTPUTS = "O"
    PWM = "LED"
    COVER = "R"
    TEMP = "T"
    FIND = "AT+FIND"
    PONG = "PONG"
    PRESS_LONG = "PL"
    PRESS_SHORT = "PS"

class DriverActions():
    SET_OUT = "AT+SetOut"
    SET_COVER = "AT+SetRol"
    SET_PWM = "SetLED"
    PING = "PING"
    RESET = "AT+RST"
    SEARCH = "AT+Search"
    
    GET_IN_STATE = "AT+StanIN"
    GET_OUT_STATE = "AT+StanOUT"

class ConfigurationFunctions():
    SET_PRESS_TIME = "AT+Key"

subscriptable_function = [
    DriverFunctions.INPUTS,
    DriverFunctions.OUTPUTS,
    DriverFunctions.TEMP,
    DriverFunctions.PWM,
    DriverFunctions.COVER,
]
#
# COMMAND_FUNCTION_IN = "I"
# COMMAND_FUNCTION_OUT = "O"
# COMMAND_FUNCTION_PWM = "LED"
# COMMAND_FUNCTION_COVER = "R"
# COMMAND_FUNCTION_FIND = "AT+FIND"
# COMMAND_FUNCTION_PONG = "PONG"
# COMMAND_FUNCTION_PRESS_SHORT = "PS"
# COMMAND_FUNCTION_PRESS_LONG = "PL"
# COMMAND_FUNCTION_TEMP = "T"
#
# COMMAND_FUNCTION_GET_IN_STATE = "AT+StanIN"
# COMMAND_FUNCTION_GET_OUT_STATE = "AT+StanOUT"
# COMMAND_FUNCTION_SET_OUT = "AT+SetOut"
# COMMAND_FUNCTION_SET_COVER = "AT+SetRol"
# COMMAND_FUNCTION_SET_PWM = "SetLED"
# COMMAND_FUNCTION_PING = "PING"
# COMMAND_FUNCTION_SET_PRESS_TIME = "AT+Key"
# COMMADN_FUNCTION_SEARCH_MODULE = "AT+Search"
# COMMAND_FUNCTION_RESET = "AT+RST"
#
CONF_ID = "id"
CONF_PIN = "pin"
CONF_PTR = "ptr"
CONF_FUNCTION = "fun"
CONF_TEMPERATURE = "temp"
CONF_OUT = "out"
