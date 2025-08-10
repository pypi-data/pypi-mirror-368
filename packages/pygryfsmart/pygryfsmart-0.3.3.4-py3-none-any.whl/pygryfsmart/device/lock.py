from pygryfsmart.const import OutputActions, DriverFunctions
from pygryfsmart import GryfApi

from .base import _GryfDevice

class GryfLock(_GryfDevice):
  def __init__(
    self,
    name: str,
    id: int,
    pin: int,
    in_id: int | None,
    in_pin: int | None,
    api: GryfApi,
    update_fun_ptr=None
  ):
    super().__init__(
      name,
      id,
      pin,
      api
    )

    self._name = name
    self.name = name
    self._id = id
    self._pin = pin

    if in_id is not None:
      self._attributes = {
        "id_out": id,
        "pin_out": pin,
        "id_in": in_id,
        "pin_in": in_pin,
      }

      self._in_id = in_id
      self._in_pin = in_pin
      self._in_en = True

    else:
      self._attributes = {
        "id": id,
        "pin": pin,
      }
      self._in_en = False

    self._open = False
    self._locked = True
    self._update_fun_ptr = None

  async def async_update_in(self, state):
    self._open = not state

    data = {
      "open": self._open,
      "locked": self._locked,
    }

    await self._update_fun_ptr(data)

  async def update_out(self, state):
    self._locked = state
  
    data = {
      "open": self._open,
      "locked": self._locked,
    }

    await self._update_fun_ptr(data)

  def subscribe(self, update_fun_ptr):
    self._update_fun_ptr = update_fun_ptr

    self._api.subscribe(self._id, self._pin, DriverFunctions.OUTPUTS, self.update_out)
    if self._in_en:
      self._api.subscribe(self._in_id, self._in_pin, DriverFunctions.INPUTS, self.async_update_in)

  @property
  def output_enable(self):
    return self._in_en

  async def turn_on(self):
    await self._api.set_out(self._id, self._pin, OutputActions.ON)

  async def turn_off(self):
    await self._api.set_out(self._id, self._pin, OUTPUT_STATES.OFF)
