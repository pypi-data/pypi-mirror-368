from pygryfsmart import GryfApi
from pygryfsmart import GryfExpert

from .base import _GryfDevice

class _GryfExpert(_GryfDevice):

    _expert: GryfExpert

    def __init__(self , api: GryfApi) -> None:
        super().__init__("Gryf Expert" , 0 , 0 , api)

    async def start(self):

        self._expert = GryfExpert(self._api)
        await self._expert.start_server()

    async def stop(self):

        await self._expert.stop_server()
        self._attributes = {
        }
