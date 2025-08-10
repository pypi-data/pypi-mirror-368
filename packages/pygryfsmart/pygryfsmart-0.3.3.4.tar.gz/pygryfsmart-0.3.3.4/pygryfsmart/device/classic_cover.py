import asyncio

from pygryfsmart import GryfApi
from pygryfsmart.const import ShutterStates, DriverFunctions

from .base import _GryfDevice

class GryfCover(_GryfDevice):

    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        time: int,
        api: GryfApi,
        fun_ptr=None,
    ):
        super().__init__(name,
                         id,
                         pin,
                         api)

        self._time = time

        self._attributes = {
            "id": id,
            "pin": pin,
            "time": time
        }

        self._fun_ptr = fun_ptr
        self._api.subscribe(self._id , self._pin, DriverFunctions.COVER , self.__async_update)
        self._shutter_state = 0
        self._feedback_update = 1

    def subscribe(self , update_fun_ptr):
        self._fun_ptr = update_fun_ptr

    async def __async_update(self, state):
        self._feedback_update = 1
        self._shutter_state = state

        if self._fun_ptr:
            await self._fun_ptr(state)

    @property
    def name(self):
        return f"{self._name}"

    async def turn_on(self):
        for k in range(10):
            self._feedback_update = 0
            await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.OPEN)
            for i in range(10):
                if self._feedback_update:
                    break;

                await asyncio.sleep(k * 10)

            if self._shutter_state == 1:
                break
        

    async def turn_off(self):
        for k in range(10):
            self._feedback_update = 0
            await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.CLOSE)
            for i in range(10):
                if self._feedback_update:
                    break;

                await asyncio.sleep(k * 10)

            if self._shutter_state == 0:
                break

    async def toggle(self):
        await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.STEP_MODE)

    async def stop(self):
        await self._api.set_cover(self._id , self._pin , self._time , ShutterStates.STOP)
