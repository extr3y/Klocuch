"""
BT receiver, motor control
"""

#high and low level BT libraries
import aioble
import bluetooth
#controlling hardware, asynchronous code execution
import machine
import uasyncio as asyncio

from machine import Pin, ADC, PWM
import time
#reduntant
import utime
import math
from servo_bt import Joy, Servo


MAX_U16 = 65535
BOTTOM_THRESHOLD = 32000
UPPER_THRESHOLD = 34000
#assumption: providing 100% of voltage leads to bad stuff happening
MAGIC_CONSTANT = 65020 * 0.75

JOYSTICK_THRESHOLD = 50
#defining motor pins
"""
MOTOR PAIR 1
"""
#motor 1a
In1=Pin(6,Pin.OUT)
In2=Pin(7,Pin.OUT)
EN_A=PWM(Pin(8))
#motor 1b
In3=Pin(4,Pin.OUT)
In4=Pin(3,Pin.OUT)
EN_B=PWM(Pin(2))

#defining frequency for enable pins
EN_A.freq(1500)
EN_B.freq(1500)
"""
MOTOR PAIR 2
"""
#motor 2a
In5=Pin(13,Pin.OUT)
In6=Pin(14,Pin.OUT)
EN_C=PWM(Pin(15))
#motor 2b
In7=Pin(12,Pin.OUT)
In8=Pin(11,Pin.OUT)
EN_D=PWM(Pin(10))

#defining frequency for enable pins
EN_C.freq(1500)
EN_D.freq(1500)

"""
the two functions might work in opposition to their names; fine tuning needed
"""
#drive forward
def move_forward():
    In1.low()
    In2.high()
    In3.low()
    In4.high()
    In5.low()
    In6.high()
    In7.low()
    In8.high()
    
#drive backward
def move_backward():
    In1.high()
    In2.low()
    In3.high()
    In4.low()
    In5.high()
    In6.low()
    In7.high()
    In8.low()
        
#stop; all voltages down
def stop():
    In1.low()
    In2.low()
    In3.low()
    In4.low()
    In5.low()
    In6.low()
    In7.low()
    In8.low()
    
"""
TO DO
"""
def left():
    In1.low()
    In2.high()
    In3.high()
    In4.low()
    In5.low()
    In6.high()
    In7.high()
    In8.low()

def right():
    In1.high()
    In2.low()
    In3.low()
    In4.high()
    In5.high()
    In6.low()
    In7.low()
    In8.high()

"""
args: 
- 'x': received and processed integer joystick value [0, 999]
returns:
- values {-1, 0, 1} indicating moving backwards, forwards and halting

JOYSTICK_THRESHOLD is the value of joystick's deadzone expressed as a fraction of x [0, 500]
"""
def calculate_direction(x):
    if x < 500 - JOYSTICK_THRESHOLD:
        return -1
    elif x > 500 + JOYSTICK_THRESHOLD:
        return 1
    else:
        return 0
    
"""
args:
- 'x': received and processed integer joystick value [0, 999]
returns:
- arbitrarily chosen PWM integer values [0, 65535] indicating different 'gears'
"""
def gearbox(x):
    #deviation from neutral position, 500
    relative_speed = abs(500 - x)

    if relative_speed > 450:
        return 60000
    elif relative_speed > 300:
        return 40000
    elif relative_speed > 150:
        return 30000
    else:
        return 22000

"""
args:
- 'msg': a 'bytes' object containing the received BT message
returns:
- list of signed ints containing PWM values. Positive for forward movement and vice versa
"""
def decode_msg(msg):
    msg = str(msg)[2:-1]
    coordinates = [int(msg[3*i:3*i+3]) for i in range(6)]
    directions = [calculate_direction(coordinate) for coordinate in coordinates]
    speeds = [gearbox(coordinate) for coordinate in coordinates]
    drive_data = [direction * speed for direction, speed in zip(directions, speeds)]
    return drive_data

"""
args:
- 'pwm_instructions': a list of signed integer PWM values.
    Positive for forward movement and vice versa  
"""
def drive(pwm_instructions):
    duty_cycle = pwm_instructions[0]

    #calculate engine speed
    EN_A.duty_u16(int(abs(duty_cycle)))
    EN_B.duty_u16(int(abs(duty_cycle)))
    EN_C.duty_u16(int(abs(duty_cycle)))
    EN_D.duty_u16(int(abs(duty_cycle)))

    #calculate direction
    if duty_cycle > 0:
        move_backward()
    elif duty_cycle < 0:
        move_forward()
    #if 0
    else:
        stop()
        
_REMOTE_UUID = bluetooth.UUID(0x1848)
_ENV_SENSE_UUID = bluetooth.UUID(0x1800) 
_REMOTE_CHARACTERISTICS_UUID = bluetooth.UUID(0x2A6E)

led = machine.Pin("LED", machine.Pin.OUT)
led_ext = machine.Pin(0, machine.Pin.OUT)
led_ext.value(True)
connected = False
alive = False
blinking = False

async def find_remote():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:

            # See if it matches our name
            if result.name() == "klocuch":
                print("Found klocuch")
                for item in result.services():
                    print (item)
                if _ENV_SENSE_UUID in result.services():
                    print("Found Robot Remote Service")
                    return result.device
            
    return None


async def peripheral_task():
    print('starting peripheral task')
    global connected
    connected = False
    device = await find_remote()
    if not device:
        print("Robot Remote not found")
        return
    try:
        print("Connecting to", device)
        connection = await device.connect()
        
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
      
    # funkcja 'async with' upewnia się, że połączenie zostanie
    # poprawnie zamknięte w przypadku wystąpienia błędu w bloku
    # poniżej
    async with connection:
        print("Connected")
        connected = True
        alive = True
        while alive:
            try:
                robot_service = await connection.service(_REMOTE_UUID)
                print(robot_service)
                control_characteristic = await robot_service.characteristic(_REMOTE_CHARACTERISTICS_UUID)
                print(control_characteristic)
            except asyncio.TimeoutError:
                print("Timeout discovering services/characteristics")
                return
            while True:
                if control_characteristic != None:
                    try:
                        command = await control_characteristic.read()
                        all_info = decode_msg(command)
                        drive(all_info)
                        move_servo(all_info)

                    except TypeError:
                        print(f'something went wrong; remote disconnected?')
                        connected = False
                        alive = False
                        return
                    except asyncio.TimeoutError:
                        print(f'something went wrong; timeout error?')
                        connected = False
                        alive = False
                        return
                    except aioble.GattError:
                        print(f'something went wrong; Gatt error - did the remote die?')
                        connected = False
                        alive = False
                        return
                else:
                    print('no characteristic')
                await asyncio.sleep_ms(100)

"""
SERVO DECLARATIONS
"""
j = Joy(0.49, 0.49, 0.015)

adc_1 = ADC(Pin(26))
adc_2 = ADC(Pin(27))

s_1 = Servo(gpio=0, invert = False)
s_2 = Servo(gpio=1, invert = False)
s_1.on()
s_2.on()

    
def move_servo(pwm_instructions):
    bt_x_value = pwm_instructions[4]
    bt_y_value = pwm_instructions[5]
    j.value(bt_x_value, bt_y_value)

    j.set_velocity(s_1, 0)
    j.set_velocity(s_2, 1)
    s_1.control()
    s_2.control()
    s_1.set_position(s_1.angle)
    s_2.set_position(s_2.angle)

async def main():
    tasks = []
    tasks = [
        asyncio.create_task(peripheral_task())
    ]
    await asyncio.gather(*tasks)

"""
Main function
"""
while True:
    asyncio.run(main())



