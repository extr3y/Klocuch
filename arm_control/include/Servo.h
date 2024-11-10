#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/adc.h"

typedef struct
{
	int angle;
	uint gpio;
	uint slice;
	uint chan;
	uint resolution;
	float max_speed; // for our project 330 deg/s
	float min_speed; //90 deg/s
	float speed;
	bool on;
	bool invert;
} Servo;

typedef struct
{
	float x;
	float y;

	float x_0;
	float y_0;

	float dead_zone;

	uint gpio_x;
	uint gpio_y;

	uint adc_input_x;
	uint adc_input_y;

}Joy;

int getAngle();

uint32_t pwm_get_wrap(uint slice_num);
uint32_t pwm_set_freq_duty(uint slice_num, uint chan, uint32_t f, int d);

void pwm_set_dutyH(uint slice_num, uint chan, int d);
void ServoInit(Servo *s, uint gpio, bool invert);
void ServoOn(Servo *s);
void ServoOff(Servo *s);
void ServoPosition(Servo *s, int angle);
void ServoPosition2(Servo *s, int angle);
void controlServo_1(Servo *s_1, Servo *s_2);
void JoyInit(Joy* j, float x_0, float y_0, float dead_zone, uint gpio_x, uint gpio_y, uint adc_input_x, uint adc_input_y);
void JoyRealValue(Joy* j);
void JoyValue(Joy* j);
void adcSetVelocity(Servo* s, Joy* j, int xy); //char xy
void controlServo(Servo *s);

