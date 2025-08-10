from serial_asyncio import open_serial_connection
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

class RS232Handler:
    def __init__(self, port, baudrate, reconnect_delay=5):
        self.port = port
        self.baudrate = baudrate
        self.reconnect_delay = reconnect_delay
        self.reader = None
        self.writer = None
        self._lock = asyncio.Lock()

    async def open_connection(self):
        async with self._lock:
            if self.writer and self.reader:  
                return
            try:
                self.reader, self.writer = await open_serial_connection(url=self.port, baudrate=self.baudrate)
                _LOGGER.info(f"Connection opened on port {self.port} with baudrate {self.baudrate}")

                if not self.reader or not self.writer:
                    await self.ensure_connection()
                    raise ConnectionError("Failed to initialize reader/writer.")

            except Exception as e:
                _LOGGER.error(f"Failed to open connection on port {self.port}: {e}")
                self.reader, self.writer = None, None

    async def close_connection(self):
        async with self._lock:
            if self.writer:
                try:
                    self.writer.close()
                    await self.writer.wait_closed()
                    _LOGGER.info("Connection closed successfully.")
                except Exception as e:
                    _LOGGER.error(f"Error while closing connection: {e}")
                finally:
                    self.reader, self.writer = None, None
            else:
                _LOGGER.warning("Connection was already closed or not initialized.")

    async def ensure_connection(self):
        """Ensure there is a valid connection, try to reconnect if needed."""
        attempt = 0
        if self.writer is None or self.reader is None:
            _LOGGER.warning("No connection. Attempting to reconnect...")
            while True:
                try:
                    await self.open_connection()

                    if self.writer is None or self.reader is None:
                        await self.ensure_connection()

                    return
                except Exception:
                    attempt += 1
                    _LOGGER.warning(f"Reconnect attempt {attempt + 1} failed. Retrying in {self.reconnect_delay}s...")
                    await asyncio.sleep(self.reconnect_delay)

    async def send_data(self, data):
        await self.ensure_connection()
        if self.writer:
            try:
                self.writer.write(data.encode())
                await self.writer.drain()
                _LOGGER.debug(f"Sent data: {data}")
            except Exception as e:
                _LOGGER.error(f"Error while sending data: {e}")
                error_msg = str(e)
                if "device reports readiness to read but returned no data" in error_msg:
                    _LOGGER.error("Detected device disconnection or multiple access. Closing connection.")
                    await self.close_connection()
                    await self.ensure_connection()
        else:
            _LOGGER.warning("Cannot send data: Writer is not initialized.")

    async def read_data(self):
        await self.ensure_connection()
        if self.reader:
            try:
                data = await self.reader.readuntil(b"\n")
                decoded = data.decode(errors="replace").strip()
                _LOGGER.debug(f"Read data: {decoded}")
                return decoded
            except asyncio.IncompleteReadError as e:
                _LOGGER.error(f"Incomplete read error: {e}")
                return None
            except Exception as e:
                _LOGGER.error(f"Error while reading data: {e}")
                return None
        else:
            _LOGGER.warning("Cannot read data: Reader is not initialized.")
            return None

