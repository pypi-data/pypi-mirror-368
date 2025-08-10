import pytest
from unittest.mock import AsyncMock
from pygryfsmart.feedback import Feedback
from pygryfsmart.const import (
    COMMAND_FUNCTION_IN,
    COMMAND_FUNCTION_OUT,
    COMMAND_FUNCTION_PWM,
    COMMAND_FUNCTION_COVER,
    COMMAND_FUNCTION_FIND,
    COMMAND_FUNCTION_PONG,
    COMMAND_FUNCTION_PRESS_SHORT,
    COMMAND_FUNCTION_PRESS_LONG,
    COMMAND_FUNCTION_TEMP,
)


@pytest.fixture
def feedback():
    return Feedback()


@pytest.mark.asyncio
async def test_parse_metod_1(feedback):
    line = "IN=1,1,0,1,0,1,0,1;"
    parsed_states = ["1", "1", "0", "1", "0", "1", "0", "1" , "1"]
    await feedback._Feedback__parse_metod_1(parsed_states, line, COMMAND_FUNCTION_IN)

    assert feedback.data[COMMAND_FUNCTION_IN][1] == {1: 1, 2: 0, 3: 1, 4: 0, 5: 1, 6: 0, 7: 1, 8: 1}


@pytest.mark.asyncio
async def test_parse_metod_2(feedback):
    line = "PS=2,3;"
    parsed_states = ["2", "3"]
    await feedback._Feedback__parse_metod_2(parsed_states, line, COMMAND_FUNCTION_PRESS_SHORT, 2)
    
    assert feedback.data[COMMAND_FUNCTION_PRESS_SHORT][2][3] == 2


@pytest.mark.asyncio
async def test_parse_metod_3(feedback):
    line = "PWM=3,2,255;"
    parsed_states = ["3", "2", "255"]
    await feedback._Feedback__parse_metod_3(parsed_states, line, COMMAND_FUNCTION_PWM)

    assert feedback.data[COMMAND_FUNCTION_PWM][3][2] == "255" 


@pytest.mark.asyncio
async def test_parse_cover(feedback):
    line = "COVER=4,1,0,1,0;"
    parsed_states = ["4", "1", "0", "1", "0"]
    await feedback._Feedback__parse_cover(parsed_states, line, COMMAND_FUNCTION_COVER)

    assert feedback.data[COMMAND_FUNCTION_COVER][4] == {1: 1, 2: 0, 3: 1, 4: 0}


@pytest.mark.asyncio
async def test_parse_temp(feedback):
    line = "TEMP=5,2,25,5;"
    parsed_states = ["5", "2", "25", "5"]
    await feedback._Feedback__parse_temp(parsed_states, line)

    assert feedback.data[COMMAND_FUNCTION_TEMP][5] == {2: 25.5}


@pytest.mark.asyncio
async def test_parse_find(feedback):
    parsed_states = ["6", "123", "45"]
    await feedback._Feedback__parse_find(parsed_states)

    assert feedback.data[COMMAND_FUNCTION_FIND][6] == 123.45

@pytest.mark.asyncio
async def test_input_data_valid(feedback):
    callback = AsyncMock()
    feedback.callback = callback

    line = "IN=1,1,0,1,0,1,0,1;"
    await feedback.input_data(line)

    assert feedback.data == {
        COMMAND_FUNCTION_IN: {},
        COMMAND_FUNCTION_OUT: {},
        COMMAND_FUNCTION_PWM: {},
        COMMAND_FUNCTION_COVER: {},
        COMMAND_FUNCTION_FIND: {},
        COMMAND_FUNCTION_PONG: {},
        COMMAND_FUNCTION_TEMP: {},
        COMMAND_FUNCTION_PRESS_SHORT: {},
        COMMAND_FUNCTION_PRESS_LONG: {},
    }

@pytest.mark.asyncio
async def test_input_data_invalid_command(feedback):
    line = "INVALID=1,1,0,1;"
    await feedback.input_data(line)

    # Brak zmian w danych, ponieważ komenda jest nieznana
    assert feedback.data == {
        COMMAND_FUNCTION_IN: {},
        COMMAND_FUNCTION_OUT: {},
        COMMAND_FUNCTION_PWM: {},
        COMMAND_FUNCTION_COVER: {},
        COMMAND_FUNCTION_FIND: {},
        COMMAND_FUNCTION_PONG: {},
        COMMAND_FUNCTION_TEMP: {},
        COMMAND_FUNCTION_PRESS_SHORT: {},
        COMMAND_FUNCTION_PRESS_LONG: {},
    }

