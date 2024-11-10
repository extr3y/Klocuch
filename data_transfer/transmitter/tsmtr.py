#BT transmitter
import sys

import aioble
import bluetooth
import machine
import uasyncio as asyncio
from micropython import const

from machine import Pin, SPI
from time import sleep, sleep_ms
from mcp3008 import MCP3008

"""Lines 15-109 work magically and shall be left untouched"""
def uid():
    """ Return the unique id of the device as a string """
    return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
        *machine.unique_id())

MANUFACTURER_ID = const(0x02A29)
MODEL_NUMBER_ID = const(0x2A24)
SERIAL_NUMBER_ID = const(0x2A25)
HARDWARE_REVISION_ID = const(0x2A26)
BLE_VERSION_ID = const(0x2A28)

button_a = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)

led = machine.Pin("LED", machine.Pin.OUT)

_ENV_SENSE_UUID = bluetooth.UUID(0x180A)
_GENERIC = bluetooth.UUID(0x1848)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x1800)
_BUTTON_UUID = bluetooth.UUID(0x2A6E)

_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)

# Advertising frequency
ADV_INTERVAL_MS = 250_000

device_info = aioble.Service(_ENV_SENSE_UUID)

connection = None

# Create characteristics for device info
aioble.Characteristic(device_info, bluetooth.UUID(MANUFACTURER_ID), read=True, initial="klocuch_remote")
aioble.Characteristic(device_info, bluetooth.UUID(MODEL_NUMBER_ID), read=True, initial="1.0")
aioble.Characteristic(device_info, bluetooth.UUID(SERIAL_NUMBER_ID), read=True, initial=uid())
aioble.Characteristic(device_info, bluetooth.UUID(HARDWARE_REVISION_ID), read=True, initial=sys.version)
aioble.Characteristic(device_info, bluetooth.UUID(BLE_VERSION_ID), read=True, initial="1.0")

remote_service = aioble.Service(_GENERIC)

button_characteristic = aioble.Characteristic(
    remote_service, _BUTTON_UUID, read=True, notify=True
)

print('registering services')
aioble.register_services(remote_service, device_info)

connected = False

async def remote_task():
    """ Send the event to the connected device """

    while True:
        #read voltages from chip channels
        message_list = chip.read_all(channel_list)
        #convert to message
        msg_str = nums_to_msg(message_list)
        print(f"sending {msg_str}") #for testing only
        if not connected:
            print('not connected')
            await asyncio.sleep_ms(1000)
            continue
        else:
            #send message
            button_characteristic.write(msg_str.encode())
        await asyncio.sleep_ms(500)
            
#serially wait for connections. Don't advertise while a central is connected.    
async def peripheral_task():
    print('peripheral task started')
    global connected, connection
    while True:
        connected = False
        async with await aioble.advertise(
            ADV_INTERVAL_MS, 
            name="klocuch", 
            appearance=_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL, 
            services=[_ENV_SENSE_TEMP_UUID]
        ) as connection:
            print("Connection from", connection.device)
            connected = True
            print(f"connected: {connected}")
            await connection.disconnected()
            print(f'disconnected')
        
"""
add trailing zeros to a calculated int value and convert to string
"""
def int_to_string(num):
    num_len = len(str(num))
    zero_wagon = ""
    while num_len < 3:
        zero_wagon += "0"
        num_len += 1
        
    return zero_wagon + str(num)

"""
merge 6 'string' type instructions into complete message
"""
def nums_to_msg(message):
    total_msg = ""
    for i in message:
        total_msg += int_to_string(i)
    
    return total_msg
        
"""
async main body
"""
async def main():
    tasks = [
        asyncio.create_task(peripheral_task()),
        asyncio.create_task(remote_task()),
    ]
    await asyncio.gather(*tasks)
    
"""
main body
"""
spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4), baudrate=500000)
cs = Pin(5, Pin.OUT)

#disable chip at start
cs.value(1)
#adc expansion
chip = MCP3008(spi, cs)
#used channels (on the mcp3008)
channel_list = [0, 1, 2, 3, 4, 5]

asyncio.run(main())

