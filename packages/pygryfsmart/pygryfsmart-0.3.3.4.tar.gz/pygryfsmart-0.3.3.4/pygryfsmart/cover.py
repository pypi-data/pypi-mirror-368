import asyncio
import logging

from pygryfsmart.const import SCHUTTER_STATES
from pygryfsmart.api import GryfApi

_LOGGER = logging.getLogger(__name__)

class GryfCover:
    def __init__(self,
                 device: GryfApi,
                 id: int,
                 pin: int,
                 time: int) -> None:
        self._pin = pin
        self._id = id
        self._device = device
        self._time = time
        self._current_cover_position = 0
        self._position_to_move = 0
        self._direction = 0

    def get_time(self , postion_to_move: int):
        return (postion_to_move * self._time) // 100

    def update_current_position(self):
        postion_moved = 100 / self._time
        if self._direction == SCHUTTER_STATES.CLOSE:
            self._current_cover_position -= postion_moved
        elif self._direction == SCHUTTER_STATES.OPEN:
            self._current_cover_position += postion_moved
        _LOGGER.debug("postion: " , self._current_cover_position)
        

    async def __cover_task(self):
        while (self._direction == SCHUTTER_STATES.OPEN and self._current_cover_position >= self._position_to_move) or (self._direction == SCHUTTER_STATES.CLOSE and self._current_cover_position <= self._position_to_move):
            await asyncio.sleep(1)   
            self.update_current_position()
        self.__cover_task.cancel()

    async def set_cover_position(self , position: int):

        self._position_to_move = position
            
        if self._current_cover_position > position:
            self._direction = SCHUTTER_STATES.CLOSE
            time = self.get_time(self._current_cover_position - position)
            await self._device.set_cover(self._id , self._pin , time , SCHUTTER_STATES.CLOSE)
        elif self._current_cover_position < position:
            self._direction = SCHUTTER_STATES.CLOSE
            time = self.get_time(position - self._current_cover_position)
            await self._device.set_cover(self._id , self._pin , time , SCHUTTER_STATES.OPEN)

        if not self.__cover_task:
            self.__cover_task
            
