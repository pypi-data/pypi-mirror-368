from pygryfsmart import GryfApi
from .base import _GryfDevice

class GryfOutputLine(_GryfDevice):

    def __init__(self,
                 name: str,
                 api: GryfApi,
                 ) -> None:
        self._attributes = {}

        super().__init__(name, 
                         0, 
                         0, 
                         api)

    def subscribe(self , update_fun_ptr):
        self._api.subscribe_output_message(update_fun_ptr)

    @property
    def name(self):
        return f"{self._name}"
