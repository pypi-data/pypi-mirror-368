from pygryfsmart import GryfApi
from pygryfsmart.const import DriverFunctions

from .base import _GryfDevice

import asyncio

class GryfPwm(_GryfDevice):

    _last_level = 70
    _is_on: bool

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi,
                 callback=None,
                 ) -> None:
        self._attributes = {
            "id": id,
            "pin": pin,
        }

        super().__init__(name, 
                         id, 
                         pin, 
                         api)
        self._last_level = 0
        self._is_on = False
        if callback is not None:
            self._api.subscribe(self._id , self._pin , DriverFunctions.PWM , callback)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, DriverFunctions.PWM , update_fun_ptr)

    async def set_level(self , level: int):
        if level > 0:
            self._last_level = level
        await self._api.set_pwm(self._id , self._pin , level)
        await self._api.send_data(f"stateLED={self._id}\n\r")

    async def turn_on(self):
        await self._api.set_pwm(self._id , self._pin , self._last_level)
        self._is_on = True

    async def turn_off(self):
        await self._api.set_pwm(self._id , self._pin , 0)
        self._is_on = False

    async def toggle(self):
        if self._is_on:
            await self.turn_off()
        else:
            await self.turn_on()

    @property
    def name(self):
        return f"{self._name}"
