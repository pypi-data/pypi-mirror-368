from pygryfsmart.const import OutputActions, DriverFunctions
from pygryfsmart import GryfApi

from .base import _GryfDevice

import asyncio

class GryfOutput(_GryfDevice):
    _state = 0
    _feedback_update = 0

    _update_fun_ptr = None

    def __init__(
        self,
        name: str,
        id: int,
        pin: int,
        api: GryfApi,
        update_fun_ptr=None,
    ):
        self._attributes = {
            "id": id,
            "pin": pin,
        }

        super().__init__(name,
                         id,
                         pin,
                         api)

        self._api.subscribe(self._id , self._pin , DriverFunctions.OUTPUTS , self.__async_update)
        
        self._update_fun_ptr = update_fun_ptr

    def subscribe(self , update_fun_ptr):
        self._update_fun_ptr = update_fun_ptr

    async def __async_update(self, state):
        self._state = state
        self._feedback_update = 1

        if self._update_fun_ptr:
            await self._update_fun_ptr(state)

    @property
    def name(self):
        return f"{self._name}"

    @property
    def state(self):
        return self._state

    async def turn_on(self):
        for k in range(10):

            self._feedback_update = 0
            await self._api.set_out(self._id, self._pin, OutputActions.ON)

            for i in range(10):

                if self._feedback_update:
                    break
                
                await asyncio.sleep(k * 0.01)
            
            if self._state == 1:
                break

    async def turn_off(self):
        for k in range(10):

            self._feedback_update = 0
            await self._api.set_out(self._id, self._pin, OutputActions.OFF)

            for i in range(10):

                if self._feedback_update:
                    break
                
                await asyncio.sleep(k * 0.01)
            
            if self._state == 0:
                break

    async def toggle(self):
        await self._api.set_out(self._id, self._pin, OutputActions.TOGGLE)
