from pygryfsmart import GryfApi
from .base import _GryfDevice

class GryfInputLine(_GryfDevice):

    def __init__(self,
                 name: str,
                 api: GryfApi,
                 ) -> None:
        super().__init__(name, 
                         0, 
                         0, 
                         api)

        self._attributes = {}

    def subscribe(self , update_fun_ptr):
        self._api.subscribe_input_message(update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"

