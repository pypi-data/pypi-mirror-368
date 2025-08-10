from datetime import datetime

from .typing import GryfData

import logging
_LOGGER = logging.getLogger(__name__)

class Parser:

    _data: GryfData

    def __init__(self, feedback):
        self._feedback = feedback

        self._data = feedback._data

    async def parse_metod_1(self , parsed_states , line: str , function: str):
        if len(parsed_states) not in {7 , 9}:
            raise ValueError(f"Invalid number of arguments: {line}")

        id = int(parsed_states[0])
        if id not in self._data[function]:
            self._data[function][id] = {}

        for i in range(1, len(parsed_states)):
            if parsed_states[i] not in {"0" , "1"}:
                raise ValueError(f"Wrong parameter value: {line}")

            self._data[function][id][i] = int(parsed_states[i])                   
        try:
            await self._feedback.handle_subscribtion(function, id=id)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def parse_metod_2(self , parsed_states , line: str , function: str , prefix: int):
        if parsed_states[1] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
            raise ValueError(f"Argument out of scope: {line}")

        pin = int(parsed_states[1])
        id = int(parsed_states[0])

        if id not in self._data[function]:
            self._data[function][id] = [0] * 20
        self._data[function][id][pin] = prefix
        try:
            await self._feedback.handle_subscribtion(function, id=id)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")
            
    async def parse_metod_3(self , parsed_states , line: str , function: str):
        if parsed_states[0] not in {"1" , "2" , "3" , "4" , "5" , "6" , "7" , "8"}:
            raise ValueError(f"Argument out of scope: {line}")

        pin = int(parsed_states[1])
        id = int(parsed_states[0])
        if id not in self._data[function]:
            self._data[function][id] = {}
        self._data[function][id][pin] = parsed_states[2]
        try:
            await self._feedback.handle_subscribtion(function, id, pin)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def parse_cover(self , parsed_states , line: str , function: str):
        if len(parsed_states) != 5:
            raise ValueError(f"Invalid number of arguments: {line}")

        for i in range(1, len(parsed_states)):
            if parsed_states[i] not in {"0" , "1" , "2"}:
                raise ValueError(f"Wrong parameter value: {line}")

            pin = int(parsed_states[0])
            if pin not in self._data[function]:
                self._data[function][pin] = {}
            self._data[function][pin][i] = int(parsed_states[i])                   
        try:
            await self._feedback.handle_subscribtion(function, id, pin)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def parse_temp(self , parsed_states , line: str):
        pin = int(parsed_states[1])
        id = int(parsed_states[0])
        if id not in self._data.temps:
            self._data.temps[id] = {}
        self._data.temps[id][pin] = float(f"{parsed_states[2]}.{parsed_states[3]}")
        try:
            await self._feedback.handle_temp_subscribtion(id , pin)
        except Exception as e:
            _LOGGER.error(f"Error subscriber {e}")

    async def parse_find(self , parsed_states):
        id = int(parsed_states[0])
        self._data.update_model(id, parsed_states[1], parsed_states[2])
        self._data.update_pong(int(parsed_states[0]))

    async def parse_pong(self , parsed_states):
        self._data.update_pong(int(parsed_states[0]))
