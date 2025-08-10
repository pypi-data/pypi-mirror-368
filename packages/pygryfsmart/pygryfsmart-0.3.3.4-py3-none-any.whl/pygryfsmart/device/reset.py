from pygryfsmart import GryfApi

from .base import _GryfDevice

class GryfReset(_GryfDevice):

    def __init__(
        self,
        api: GryfApi,
    ) -> None:
        self._attributes = {}

        super().__init__("Gryf RST",
                         0,
                         0,
                         api)

    @property
    def name(self):
        return "Gryf RST"

    async def reset_all(self):
        await self._api.reset(0 , True)

    async def reset_single_module(self , module):
        await self._api.reset(module , True)
