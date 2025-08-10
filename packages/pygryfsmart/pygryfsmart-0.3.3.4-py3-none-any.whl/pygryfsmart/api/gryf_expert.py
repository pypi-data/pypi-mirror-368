"""File with GryfExpert server class."""

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class GryfExpert:
    """GryfExpert class."""

    def __init__(
            self,
            api,
            host='127.0.0.1', 
            port=4210
        ) -> None:
        """Initialise GryfExpert class."""

        self.host = host
        self.port = port

        self.writer = None
        self.server = None
        self._enable = False
        self._api = api
        self.active_clients = set()
        self.server_task = None

    async def handle_client(
            self,
            reader, 
            writer
        ) -> None:
        """Handle new server client."""

        addr = writer.get_extra_info('peername')
        _LOGGER.debug(f"Connected with: {addr}")
        self.active_clients.add(writer)

        try:
            message = "hello"
            writer.write(message.encode())
            await writer.drain()
            while True:
                data = await reader.read(1024)
                if not data:
                    _LOGGER.error(f"Client: {addr} stop connection")
                    break

                message = data.decode().strip() + "\n\r"
                _LOGGER.debug(f"message from {addr}: {message}")

                await self._api.send_data(f"{message}\n\r")
        except asyncio.CancelledError:
            _LOGGER.error(f"Client: {addr} stop connection")
        except Exception as e:
            _LOGGER.error(f"ocurred error from {addr}: {e}")
        finally:
            _LOGGER.debug(f"Closing connection with {addr}")
            writer.close()
            self.writer = None
            self.active_clients.remove(writer)
            await writer.wait_closed()
            return

    async def send_data(
            self,
            message
        ) -> None:
        """Sending data to GryfExpert."""

        if self.active_clients:
            try:
                message += "\n"
                for client in self.active_clients:
                    client.write(message.encode())
                    await client.drain()
            except Exception as e:
                _LOGGER.error(f"Unable to send message: {message}, error: {e}")
            finally:
                return

    async def stop_server(self) -> None:
        """Stop GryfExpert server."""
        if self.server:
            _LOGGER.debug("Stopping the server")
            self.server.close()
            await self.server.wait_closed()
            _LOGGER.debug("Server stopped")
        else:
            _LOGGER.error("Server is not running")

        self._enable = False

    async def start_server(self) -> None:
        """Start GryfExpert server."""
        self._api.subscribe_input_message(self.send_data)
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )

        addr = self.server.sockets[0].getsockname()
        _LOGGER.info(f"Server started on {addr}")

        self._enable = True
        self.server_task = asyncio.create_task(self.server.serve_forever())

    @property
    def enable(self):
        """Return is server enable."""
        return self._enable

