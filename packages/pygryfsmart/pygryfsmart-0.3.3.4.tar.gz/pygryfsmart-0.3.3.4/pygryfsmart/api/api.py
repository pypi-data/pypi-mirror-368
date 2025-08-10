"""Main api class function."""

from .functions import _GryfFunctionsApiBase
from .gryf_expert import GryfExpert
from .const import(
    CONF_ID,
    CONF_PIN,
    CONF_PTR,
    CONF_FUNCTION,
    DriverFunctions,
    subscriptable_function,
        )
import logging
_LOGGER = logging.getLogger(__name__)

class GryfApi(_GryfFunctionsApiBase):
    """Base pygryfsmart class."""

    _gryf_expert: GryfExpert
    
    def __init__(self,
                 port: str,
                 callback=None
        ) -> None:
        """Init pygryfsmart."""

        super().__init__(port , callback)

        self._gryf_expert = GryfExpert(self)

    async def start_gryf_expert(self) -> None: 
        """Start gryf expert server."""
        await self._gryf_expert.start_server()

    async def stop_gryf_expert(self) -> None:
        """Stop gryf expert server."""
        await self._gryf_expert.stop_server()

    def subscribe(
            self,
            id: int, 
            pin: int,
            func: str | DriverFunctions,
            ptr
        ) -> None:
        """Subscribe feedback from drivers."""

        if func in subscriptable_function:

            data = {
                CONF_ID: id,
                CONF_PIN: pin,
                CONF_FUNCTION: func,
                CONF_PTR: ptr
            }
            if func != DriverFunctions.TEMP:
                self.feedback.subscribe(data)
            else:
                self.feedback.subscribe_temp(data)
        else:
            _LOGGER.error(f"Bad function to subscribe: {func}")

    def realize_function_from_arguments(
        self,
        function: str,
        id: int,
        extra: int,
        state: int,
    ) -> None:
        pass

