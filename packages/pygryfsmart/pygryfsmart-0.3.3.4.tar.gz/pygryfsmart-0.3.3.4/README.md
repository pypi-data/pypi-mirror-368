# GryfSmart

**GryfSmart** is a system that enables control of Gryf smart system devices via an RS232 serial port. The core of the system is the `pygryfsmart.api.GryfApi` class, which provides functionalities for managing devices, such as sending commands, controlling device states, monitoring device statuses, and resetting devices.

## Installation

To use **GryfSmart**, you need to install the necessary dependencies and import the `pygryfsmart.api.GryfApi` class.

### Install Dependencies

```bash
pip install pygryfsmart
```

## Device Class

### Constructor: `GryfApi(port, callback=None)`

Creates a new `Device` object that connects to the device via the RS232 serial port.

- **port**: The serial port to which the device is connected (e.g., `'COM1'`, `'/dev/ttyUSB0'`).
- **callback**: An optional callback function that will process data returned by the device.

### Methods of the `Device` Class

#### `set_callback(callback)`

Sets the callback function that will be called when data is received from the device.

- **callback**: The function to invoke when data is received.

#### `stop_connection()`

Stops the connection to the device. It cancels active tasks related to the connection and state updates.

#### `start_connection()`

Starts the connection to the device by creating a task responsible for receiving data.

#### `send_data(data)`

Sends data to the device via the RS232 serial port.

- **data**: The command or data to be sent to the device.

#### `set_out(id: int, pin: int, state: OUTPUT_STATES | int)`

Sets the output state of the device. This can include turning on or off various output pins.

- **id**: The device ID.
- **pin**: The pin number (1 to 6).
- **state**: The output state (e.g., `ON`, `OFF`, `TOGGLE`).
    -  you can import OUTPUT_STATES enum from pygryfsmart.const

#### `set_key_time(ps_time: int, pl_time: int, id: int, pin: int, type: KEY_MODE | int)`

Sets the key press time for the device.

- **ps_time**: The short press time in milliseconds * 10.
- **pl_time**: The long press time in milliseconds * 10.
- **id**: The device ID.
- **pin**: The pin number (1 to 6).
- **type**: The type of the key.
  -  you can import KEY_MODES enum from pygryfsmart.const
#### `search_module(id: int)`

Retrieves information about the device model and assigns an ID.

- **id**: The device ID.

#### `search_modules(last_module: int)`

same for multiple devices, starting from 1 to `last_module`.

- **last_module**: The number of devices to be searched.

#### `ping(module_id: int)`

Sends a ping to a device to check if it is responsive.

- **module_id**: The device ID to ping.

#### `set_pwm(id: int, pin: int, level: int)`

Sets the PWM level for a specific pin on the device.

- **id**: The device ID.
- **pin**: The pin number (1 to 6).
- **level**: The PWM level (0 to 100).

#### `set_cover(id: int, pin: int, time: int, operation: SCHUTTER_STATES | int)`

Controls the cover state for a specific pin on the device.

- **id**: The device ID.
- **pin**: The pin number (1 to 4).
- **time**: The time in milliseconds for the operation.
- **operation**: The operation to perform (e.g., `OPEN`, `CLOSE`, `STOP`, `STEP_MODE`).
    -  you can import SCHUTTER_STATES from pygryfsmart.const

#### `reset(module_id: int, update_states: bool)`

Resets the device. Optionally, updates the states after reset.

- **module_id**: The device ID.
- **update_states**: Whether to update the states after reset.

#### `start_update_interval(time: int)`

Starts the task that periodically updates the device states.

- **time**: The interval time in seconds between updates.

## Subscribe metods:

#### `subscribe input messages(fun_ptr)`

- **fun_ptr**: Function to handle new messages from controllers.

#### `subscribe output messages(fun_ptr)`

- **fun_ptr**: Function to handle all sending messages.

#### 'subscribe(id , pin , func , fun_ptr`

- **id**: The device ID.
- **pin**: The pin number.
- **func**: selected function, for example DriverFunctions.INPUTS, you can import this from pygryfsmart.const.
- **fun_ptr**: handle function
