import machine
import time
import math

class Servo:
    def __init__(self, gpio, invert=False):
        self.angle = 180
        self.gpio = gpio
        self.invert = invert
        self.resolution = self.pwm_set_freq_duty(50, 0)
        self.pwm_set_dutyH(1250)
        self.max_speed = 250  # 330
        self.min_speed = 25
        self.speed = 0
        self.on = False

        self.pwm = machine.PWM(machine.Pin(self.gpio, machine.Pin.OUT))
        self.pwm.freq(50)
        self.pwm.duty_u16(0)

    def pwm_get_wrap(self):
        return 65535

    def pwm_set_freq_duty(self, f, d):
        clk = 125000000
        divider16 = clk // f // 4096 + (clk % (f * 4096) != 0)
        if divider16 // 16 == 0:
            divider16 = 16

        wrap = clk * 16 // divider16 // f - 1

        self.pwm.freq(f)
        self.pwm.duty_u16(int(wrap * d / 100))
        return wrap

    def pwm_set_dutyH(self, d):
        wrap = self.pwm_get_wrap()
        self.pwm.duty_u16(int(wrap * d / 10000))

    def on(self):
        self.on = True

    def off(self):
        self.pwm.duty_u16(0)
        self.on = False

    def set_position(self, angle):
        per = ((2400 - 400) / 180 * angle + 400) / 20000 * 10000
        self.pwm_set_dutyH(int(per))

    def control(self):
        if self.speed > 0:
            if self.angle < 180:
                self.angle += 1
            else:
                return
        elif self.speed < 0:
            if self.angle > 0:
                self.angle -= 1
            else:
                return
        else:
            return

        dt = 1000.0 / self.speed
        del_t = int(abs(dt))
        time.sleep_ms(del_t)

class Joy:
    def __init__(self, x_0, y_0, dead_zone):
        self.x_0 = x_0
        self.y_0 = y_0
        self.dead_zone = dead_zone

        self.x = self.x_0
        self.y = self.y_0

    def value(self, x_bt_value, y_bt_value):
        bt_scaling_factor = 65535.0 / 1000 
        conversion_factor = 1.0 / 4096

        x_value = x_bt_value * bt_scaling_factor * conversion_factor
        if self.x_0 - self.dead_zone < x_value < self.x_0 + self.dead_zone:
            self.x = self.x_0
        else:
            self.x = x_value

        y_value = y_bt_value * bt_scaling_factor * conversion_factor
        if self.y_0 - self.dead_zone < y_value < self.y_0 + self.dead_zone:
            self.y = self.y_0
        else:
            self.y = y_value

    def set_velocity(self, servo, xy):
        a = 1 / (1 - (0.5 + self.dead_zone)) ** 2

        if xy == 0:
            if self.x < self.x_0 - self.dead_zone:
                servo.speed = -a * (self.x - (self.x_0 - self.dead_zone)) ** 2 * servo.max_speed
            elif self.x > self.x_0 + self.dead_zone:
                servo.speed = a * (self.x - (self.x_0 + self.dead_zone)) ** 2 * servo.max_speed
            else:
                servo.speed = 0

            if abs(servo.speed) > servo.min_speed or servo.speed == 0:
                return
            else:
                if servo.speed > 0:
                    servo.speed = servo.min_speed
                else:
                    servo.speed = -servo.min_speed
        elif xy == 1:
            if self.y < self.y_0 - self.dead_zone:
                servo.speed = -a * (self.y - (self.y_0 - self.dead_zone)) ** 2 * servo.max_speed
            elif self.y > self.y_0 + self.dead_zone:
                servo.speed = a * (self.y - (self.y_0 + self.dead_zone)) ** 2 * servo.max_speed
            else:
                servo.speed = 0

            if abs(servo.speed) > servo.min_speed or servo.speed == 0:
                return
            else:
                if servo.speed > 0:
                    servo.speed = servo.min_speed
                else:
                    servo.speed = -servo.min_speed
        else:
            print("invalid char value")

