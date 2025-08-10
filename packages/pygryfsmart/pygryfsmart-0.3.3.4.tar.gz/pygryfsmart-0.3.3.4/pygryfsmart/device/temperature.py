from pygryfsmart import GryfApi
from pygryfsmart.const import DriverFunctions

from .base import _GryfDevice

class GryfTemperature(_GryfDevice):

    def __init__(self,
                 name: str,
                 id: int,
                 pin: int,
                 api: GryfApi,
                 callback=None
                 ) -> None:
        self._attributes = {
            "id": id,
            "pin": pin,
        }

        super().__init__(name, 
                         id, 
                         pin, 
                         api)
        if callback is not None:
            self._api.subscribe(self._id , self._pin , DriverFunctions.TEMP , callback)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe(self._id , self._pin, DriverFunctions.TEMP , update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"
