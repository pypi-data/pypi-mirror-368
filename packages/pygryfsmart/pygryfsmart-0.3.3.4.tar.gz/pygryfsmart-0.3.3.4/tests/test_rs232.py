import pytest
from unittest.mock import AsyncMock, patch
from pygryfsmart.rs232 import RS232Handler

@pytest.fixture
def rs232_handler():
    return RS232Handler(port="/dev/ttyUSB0", baudrate=115200)
pytest.mark.asyncio
@patch("serial_asyncio.open_serial_connection")
async def test_open_connection(mock_open_serial):
    mock_reader = AsyncMock()
    mock_writer = AsyncMock()
    mock_open_serial.return_value = (mock_reader, mock_writer)

    rs232_handler = RS232Handler(port="/dev/ttyUSB0", baudrate=115200)

    await rs232_handler.open_connection()

    mock_open_serial.assert_called_once_with(url="/dev/ttyUSB0", baudrate=115200)
    mock_writer = AsyncMock()
    rs232_handler.writer = mock_writer

    await rs232_handler.close_connection()

    mock_writer.close.assert_called_once()
    await mock_writer.wait_closed()

@pytest.mark.asyncio
async def test_send_data(rs232_handler):
    mock_writer = AsyncMock()
    rs232_handler.writer = mock_writer

    await rs232_handler.send_data("Test data")

    mock_writer.write.assert_called_once_with(b"Test data")
    await mock_writer.drain()

@pytest.mark.asyncio
async def test_read_data(rs232_handler):
    mock_reader = AsyncMock()
    mock_reader.readuntil = AsyncMock(return_value=b"Test data\n")
    rs232_handler.reader = mock_reader

    data = await rs232_handler.read_data()

    assert data == "Test data"
    mock_reader.readuntil.assert_called_once_with(b"\n")
