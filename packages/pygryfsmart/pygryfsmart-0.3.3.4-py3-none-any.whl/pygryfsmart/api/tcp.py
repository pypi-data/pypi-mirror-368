import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

class TCPClientHandler:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._reader = None
        self._writer = None
        self._reconnect_interval = 5

    @property
    def port(self):
        return self._port

    async def open_connection(self):
        while True:
            try:
                self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
                _LOGGER.info(f"Connection opened: {self._host}:{self._port}")
                return
            except Exception as e:
                _LOGGER.error(f"Error opening connection: {e}")
                await asyncio.sleep(self._reconnect_interval)

    async def close_connection(self):
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            _LOGGER.info("Connection closed.")
        else:
            _LOGGER.warning("No active connection to close.")

    async def send_data(self, data):
        if self._writer:
            try:
                self._writer.write(data.encode())
                await self._writer.drain()  
                _LOGGER.debug(f"Sent data: {data}")
            except Exception as e:
                _LOGGER.error(f"Error sending data: {e}")
                await self.reconnect()
        else:
            _LOGGER.warning("Cannot send data: No active connection.")

    async def read_data(self):
        if self._reader:
            try:
                data = await self._reader.read(1024)  
                if data:
                    decoded_data = data.decode().strip()
                    _LOGGER.debug(f"Received data: {decoded_data}")
                    return decoded_data
                else:
                    _LOGGER.warning("Connection closed by server.")
                    await self.reconnect()
                    return ""
            except Exception as e:
                _LOGGER.error(f"Error reading data: {e}")
                await self.reconnect()
                return ""
        else:
            _LOGGER.warning("Cannot read data: No active connection.")
            await self.reconnect()
            return ""

    async def reconnect(self):
        try: 
            self._writer = None
            self._reader = None
            await self.close_connection()
            await self.open_connection()
        except ConnectionResetError as e:
            _LOGGER.error("Connection error: %s", e)
            await asyncio.sleep(self._reconnect_interval)
            await self.reconnect()
