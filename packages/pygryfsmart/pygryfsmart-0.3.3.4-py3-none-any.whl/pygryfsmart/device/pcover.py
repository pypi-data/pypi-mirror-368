from pygryfsmart import GryfApi
from pygryfsmart.const import ShutterStates

import asyncio
import logging

from .base import _GryfDevice

_LOGGER = logging.getLogger(__name__)

class GryfPCover(_GryfDevice):

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 time: int,
                 api: GryfApi
                 ) -> None:
        self._attributes = {
            "id": id,
            "pin": pin,
            "time": time
        }

        super().__init__(
            name,
            id,
            pin,
            api,
        )

        self._opening_time = time
        self._current_postion = 0
        self._expected_postion = 0
        self._one_interval_position_move = 500 / time
        self._timer_en = False
        self._timer_task = None
        self._opening_postion = 0
        self._opening_postion_en = False
        self._operation = ShutterStates.STOP
        self._time_to_sleep = 0.0

    async def turn_on(self):
        await self._api.set_cover(self._id , self._pin , self._opening_time , ShutterStates.OPEN)

    async def turn_off(self):
        await self._api.set_cover(self._id , self._pin , self._opening_time , ShutterStates.CLOSE)

    async def toggle(self):
        await self._api.set_cover(self._id , self._pin , self._opening_time , ShutterStates.STEP_MODE)

    async def stop(self):
        await self._api.set_cover(self._id , self._pin , 0, ShutterStates.STOP)

    async def __timer(self):
        self._timer_en = True

        while abs(self._current_postion - self._expected_postion) > 1:

            if self._expected_postion > self._current_postion:
                self._current_postion += self._one_interval_position_move
            elif self._expected_postion < self._current_postion:
                self._current_postion -= self._one_interval_position_move

            _LOGGER.debug("%s" , self._current_postion)

            if not self._opening_postion_en:
                await self.__send_postion_to_move()
                self._opening_postion_en = True
                self._opening_postion = self._expected_postion

            if abs(self._expected_postion - self._opening_postion) > 2:
                if self._opening_postion > self._current_postion and self._current_postion > self._expected_postion:
                    await self.stop()
                    await self.__send_postion_to_move()
                elif self._expected_postion > self._current_postion and self._current_postion > self._opening_postion:
                    await self.stop()
                    await self.__send_postion_to_move()

            await asyncio.sleep(0.5)

        await asyncio.sleep(self._time_to_sleep)
        self._time_to_sleep = 0.0
        await self.stop()

        self._timer_en = False
        self._opening_postion_en = False

    async def __send_postion_to_move(self):
        self._operation = ShutterStates if self._current_postion < self._expected_postion else ShutterStates.CLOSE
        time_to_move = int((abs(self._current_postion - self._expected_postion) * self._opening_time) / 100)

        await self._api.set_cover(self._id , self._pin , time_to_move , self._operation)

        if time_to_move > 10:
            self._time_to_sleep += 0.5

    def set_current_postion(self , current_postion: int):
        self._current_postion = current_postion

    async def set_position(self , position: int):

        self._expected_postion = position

        if not self._timer_en:
            self._opening_postion = 0
            self._opening_postion_en = False
            self._timer_task = asyncio.create_task(self.__timer())
