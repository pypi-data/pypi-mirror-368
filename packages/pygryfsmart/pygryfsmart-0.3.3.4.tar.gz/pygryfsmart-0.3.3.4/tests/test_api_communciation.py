import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from pygryfsmart.api import GryfApi
from pygryfsmart.const import DriverFunctions

@pytest.mark.asyncio
async def test_init():
    """Test inicjalizacji klasy."""
    with patch("mypackage.gryf_communication.RS232Handler"), \
         patch("mypackage.gryf_communication.TCPClientHandler"), \
         patch("pygryfsmart.gryf_communication.Feedback"):
        
        api = GryfApi("192.168.1.100")
        assert api.feedback is not None
        assert api._writer is not None


@pytest.mark.asyncio
async def test_detect_connection_type():
    """Test wykrywania IP oraz portu szeregowego."""
    with patch("pygryfsmart.gryf_communication.RS232Handler"), \
         patch("pygryfsmart.gryf_communication.TCPClientHandler"):
        
        api_ip = GryfApi("192.168.1.100")
        assert isinstance(api_ip._writer, AsyncMock)  

        api_serial = GryfApi("/dev/ttyUSB0")
        assert isinstance(api_serial._writer, AsyncMock)  


@pytest.mark.asyncio
async def test_send_data():
    """Test wysyłania danych przez send_data()."""
    with patch("pygryfsmart.gryf_communication.RS232Handler") as mock_serial:
        mock_writer = mock_serial.return_value
        mock_writer.send_data = AsyncMock()

        api = GryfApi("/dev/ttyUSB0")
        await api.send_data("TEST_COMMAND")

        mock_writer.send_data.assert_called_once_with("TEST_COMMAND")


@pytest.mark.asyncio
async def test_subscribe_messages():
    """Test subskrypcji wiadomości."""
    with patch("mypackage.gryf_communication.RS232Handler"):
        api = GryfApi("/dev/ttyUSB0")

        def test_callback(data):
            return data

        api.subscribe_input_message(test_callback)
        api.subscribe_output_message(test_callback)

        assert test_callback in api._input_message_subscribers
        assert test_callback in api._output_message_subscribers


@pytest.mark.asyncio
async def test_start_stop_connection():
    """Test uruchamiania i zatrzymywania połączenia."""
    with patch("mypackage.gryf_communication.RS232Handler") as mock_serial:
        mock_writer = mock_serial.return_value
        mock_writer.open_connection = AsyncMock()
        mock_writer.close_connection = AsyncMock()

        api = GryfApi("/dev/ttyUSB0")

        await api.start_connection()
        assert api._connection_task is not None
        mock_writer.open_connection.assert_called_once()

        await api.stop_connection()
        assert api._connection_task is None
        mock_writer.close_connection.assert_called_once()


@pytest.mark.asyncio
async def test_available_driver():
    """Test dostępności drivera."""
    with patch("mypackage.gryf_communication.RS232Handler"):
        api = GryfApi("/dev/ttyUSB0")

        now = datetime.now().strftime("%H:%M")
        api.feedback.data = {DriverFunctions.PONG: {1: now}}

        assert api.available_driver(1) == True  
        assert api.available_driver(2) == False
