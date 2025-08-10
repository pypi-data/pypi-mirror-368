"""File with communication class for GryfApi."""

import asyncio
import logging
import re
from datetime import datetime , timedelta

from .rs232 import RS232Handler
from .tcp import TCPClientHandler
from .feedback import Feedback
from .gryf_expert import GryfExpert
from .const import (
    BAUDRATE,
    PORT,
    DriverFunctions,
    DriverActions,
)

_LOGGER = logging.getLogger(__name__)

class _GryfCommunicationApiBase():
    """Communication class for GryfApi."""
    
    _writer: RS232Handler | TCPClientHandler
    _module_count = 1
    _gryf_expert: GryfExpert
    feedback: Feedback
    _update_state_enable = True


    def __init__(
            self,
            port,
            callback=None
        ) -> None:
        """Initialise GryfCommunication."""

        self.port = port
        self._connection_task = None
        self._update_task = None
        self.feedback = Feedback(callback=callback)
        self._input_message_subscribers = []
        self._output_message_subscribers = []

        ipv4_patern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        serial_port_patern = r"/dev/tty\S*"

        if re.search(ipv4_patern , port):
            self._writer = TCPClientHandler(port , PORT)
        elif re.search(serial_port_patern , port):
            self._writer = RS232Handler(port , BAUDRATE)

    async def send_data(
            self,
            command
        ) -> None:
        """Send data."""

        for subscribers in self._output_message_subscribers:
            await subscribers(command)

        await self._writer.send_data(command)

    def set_callback(
            self,
            callback
        ) -> None:
        """Set callback for GryfApi data struct."""

        self.feedback.callback = callback

    def set_module_count(
            self,
            count: int,
            ) -> None:
        """Set module count for GryfApi."""

        self._module_count = count


    def subscribe_input_message(
            self,
            func,
        ) -> None:
        """Subscribe Input messages from GryfApi."""

        self._input_message_subscribers.append(func)

    def subscribe_output_message(
            self,
            func,
            ) -> None:
        """Subscribe Output messages to GryfApi."""

        self._output_message_subscribers.append(func)

    async def sending_data_to_gryf_expert(
            self,
            message: str,
        ) -> None:
        """Send data to gryf expert server."""

        if self._gryf_expert.enable == True:
            await self._gryf_expert.send_data(message)

    async def stop_connection(self) -> None:
        """Stop connection with drivers."""

        if self._connection_task:
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                _LOGGER.debug("Connection task was cancelled.")
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                _LOGGER.debug("Update task was cancelled.")
        await self._writer.close_connection()
        _LOGGER.debug("Connection closed.")

    async def __connection_task(self) -> None:
        """Connection task."""
        try:
            while True:
                line = await self._writer.read_data()
                if line:
                    commands = line.splitlines()

                    for cmd in commands:
                        await self.feedback.input_data(cmd)
                        if self._input_message_subscribers:
                            for subscribers in self._input_message_subscribers:
                                await subscribers(cmd)
        except asyncio.CancelledError:
            _LOGGER.info("Connection task cancelled.")
            await self._writer.close_connection()
            raise
        except Exception as e:
            _LOGGER.error(f"Error in connection task: {e}")
            await self._writer.close_connection()
            raise

    async def start_connection(self) -> None:
        """Start connection with drivers."""

        await self._writer.open_connection()
        self._connection_task = asyncio.create_task(self.__connection_task())
        _LOGGER.info("Connection task started.")

    def start_update_interval(
            self,
            time: int
            ) -> None:
        """Start interval update drivers state."""

        if not self._update_task:
            self._update_task = asyncio.create_task(self.__states_update_interval(time))
            _LOGGER.info("Update interval task started.")

    async def __states_update_interval(
            self,
            time: int
        ) -> None:
        """States update interval."""

        try:
            while True:

                for i in range(self._module_count):
                    try:
                        if not self._update_state_enable:
                            await asyncio.sleep(20)
                            self._update_state_enable = True

                        command = f"{DriverActions.GET_IN_STATE}={i + 1}\n\r"
                        await self.send_data(command)
                        await asyncio.sleep(0.1)

                        if not self._update_state_enable:
                            await asyncio.sleep(5)
                            self._update_state_enable = True

                        command = f"{DriverActions.GET_OUT_STATE}={i + 1}\n\r"
                        await self.send_data(command)
                        await asyncio.sleep(5)
                    except Exception as e:
                        _LOGGER.error(f"Error updating module {i + 1}: {e}")

                    await asyncio.sleep(time)
        except asyncio.CancelledError:
            _LOGGER.info("Update interval task cancelled.")
        except Exception as e:
            _LOGGER.error(f"Error in update interval: {e}")


    def available_driver(
            self, 
            id: int,
        ) -> bool:
        """Check driver available."""

        last_call = self.feedback.data.pongs.get(id , None)
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        if last_call == None:
            return False

        now_dt = datetime.strptime(current_time , "%H:%M")
        last_dt = datetime.strptime(last_call , "%H:%M")

        if now_dt - last_dt < timedelta(minutes=2):
            return True
        return False
