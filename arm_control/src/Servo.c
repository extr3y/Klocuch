#include "Servo.h"


int getAngle()
{
		char userInput[4];
		fgets(userInput, sizeof(userInput), stdin);

		if(userInput[0] >= '0' && userInput[0] <= '9')
		{
			int uI = atoi(userInput);
			printf("%d\n",uI);
			return uI;
		}

}


uint32_t pwm_get_wrap(uint slice_num)
{
	valid_params_if(PWM, slice_num >= 0 && slice_num < NUM_PWM_SLICES);
	return pwm_hw->slice[slice_num].top;
}

uint32_t pwm_set_freq_duty(uint slice_num, uint chan, uint32_t f, int d)
{
	const uint32_t clk = 125000000;
	uint32_t divider16 = clk / f / 4096 + (clk % (f * 4096) != 0);

	if(divider16 / 16 == 0)
	{
		divider16 = 16;
	}

	uint32_t wrap = clk * 16 / divider16 / f - 1;

	pwm_set_clkdiv_int_frac(slice_num, divider16 / 16, divider16 & 0xF);
	pwm_set_wrap(slice_num, wrap);
	pwm_set_chan_level(slice_num, chan, wrap * d / 100);

	return wrap;
}

void pwm_set_dutyH(uint slice_num, uint chan, int d)
{
	pwm_set_chan_level(slice_num, chan, pwm_get_wrap(slice_num) * d / 10000);
}

void ServoInit(Servo *s, uint gpio, bool invert)
{
	gpio_set_function(gpio, GPIO_FUNC_PWM);
	s->gpio = gpio;
	s->slice = pwm_gpio_to_slice_num(gpio);
	s->chan = pwm_gpio_to_channel(gpio);

	pwm_set_enabled(s->slice, false);
	s->on = false;
	s->speed = 0;
	s->resolution = pwm_set_freq_duty(s->slice, s->chan, 50, 0);
	pwm_set_dutyH(s->slice, s->chan, 1250); // było 1250
	s->angle = 180;
	s->max_speed = 250;//330
	s->min_speed = 25;
/*
	if (s->chan)
	{
		pwm_set_output_polarity(s->slice, false, invert);
	}

	else
	{
		pwm_set_output_polarity(s->slice, invert, false);
	}
*/
		pwm_set_output_polarity(s->slice, true, true);
}

void ServoOn(Servo *s)
{
	pwm_set_enabled(s->slice, true);
	s->on = true;
}

void ServoOff(Servo *s)
{
	pwm_set_enabled(s->slice, false);
	s->on = false;
}

void ServoPosition(Servo *s, int angle)
{
	float per = ((2400 - 400)/180 * (float) angle + 400) / 20000 * 10000;
	int p = 0;
	p = (int) per;

	pwm_set_dutyH(s->slice, s->chan, p);
}

void ServoPosition2(Servo *s, int angle)
{
	float per = ((4000 - 6000)/180 * (float) angle + 6000) / 20000 * 10000;
	int p = 0;
	p = (int) per;

	pwm_set_dutyH(s->slice, s->chan, p);
}

void controlServo_1(Servo *s_1, Servo *s_2)
{
	char userInput = getchar();
	if(userInput == 'w')
	{
		s_1->angle = s_1->angle + 1;
	}

	else if(userInput == 's')
	{
		s_1->angle = s_1->angle - 1;
	}

	else if(userInput == 'a')
	{
		s_2->angle = s_2->angle + 3;
	}

	else if(userInput == 'd')
	{
		s_2->angle = s_2->angle - 3;
	}
}

void controlServo(Servo *s)
{
	if(s->speed > 0)
	{
		if(s->angle < 180)
		{
			s->angle = s->angle + 1;
			//printf("1:1\n");
		}
		else
		{
			//printf("1:2\n");
			return;
		}
	}

	else if(s->speed < 0)
	{
		if(s->angle > 0)
		{
			//printf("2:1\n");
			s->angle = s->angle - 1;
		}
		else
		{
			//printf("2:2\n");
			return;
		}
	}

	else
	{
		//printf("3:1\n");
		return;
	}

	float dt = 1000.0/s->speed; //mindfuck
	//printf("%f :", dt);
	uint del_t = (uint) abs(dt);
	//printf("%d :\n ", del_t);
	sleep_ms(del_t);
}

void JoyInit(Joy* j, float x_0, float y_0, float dead_zone, uint gpio_x, uint gpio_y, uint adc_input_x, uint adc_input_y)
{
	j->x_0 = x_0;
	j->y_0 = y_0;

	j->dead_zone = dead_zone;

	j->gpio_x = gpio_x;
	j->gpio_y = gpio_y;

	j->adc_input_x = adc_input_x;
	j->adc_input_y = adc_input_y;
}

void JoyRealValue(Joy* j)
{
	const float conversion_factor = 1.0f / (1 << 12);
	adc_select_input(j->adc_input_x);
	uint16_t result = adc_read();

	printf("x: %f ;", result * conversion_factor);

	adc_select_input(j->adc_input_y);
	result = adc_read();

	printf("y: %f\n", result * conversion_factor);
}

void JoyValue(Joy* j)
{
	const float conversion_factor = 1.0f / (1 << 12);

	adc_select_input(j->adc_input_x);
	uint16_t result = adc_read();

	if(j->x_0 - j->dead_zone < result * conversion_factor && result * conversion_factor < j->x_0 + j->dead_zone)
	{
		j->x = j->x_0;
	}

	else
	{
		j->x = result * conversion_factor;
	}

	adc_select_input(j->adc_input_y);
	result = adc_read();

	if(j->y_0 - j->dead_zone < result * conversion_factor && result * conversion_factor < j->y_0 + j->dead_zone)
	{
		j->y = j->y_0;
	}
	else
	{
		j->y = result * conversion_factor;
	}
}

void adcSetVelocity(Servo* s, Joy* j, int xy) //char xy
{
	float a = 1 / pow(1 - (0.5 + j->dead_zone), 2);
	if(xy == 0)
	{
		if(j->x < j->x_0 - j->dead_zone)
		{
			s->speed = - a * pow(j->x - (j->x_0 - j->dead_zone), 2) * s->max_speed;
		}
		else if(j->x > j->x_0 + j->dead_zone)
		{
			s->speed = a * pow(j->x - (j->x_0 + j->dead_zone), 2) * s->max_speed;
		}
		else //if(j->x == j->x_0)
		{
			s->speed = 0;
		}

		if(abs(s->speed) > s->min_speed || s->speed == 0)
		{
			return;
		}
		else
		{
			if(s->speed > 0)
			{
				s->speed = s->min_speed;
			}
			else
			{
				s->speed = -s->min_speed;
			}
		}
	}
	else if(xy == 1)
	{


		if(j->y < j->y_0 - j->dead_zone)
		{
			s->speed = - a * pow(j->y - (j->y_0 - j->dead_zone), 2) * s->max_speed;
		}
		else if(j->y > j->y_0 + j->dead_zone)
		{
			s->speed = a * pow(j->y - (j->y_0 + j->dead_zone), 2) * s->max_speed;
		}
		else //if(j->x == j->x_0)
		{
			s->speed = 0;
		}

		if(abs(s->speed) > s->min_speed || s->speed == 0)
		{
			return;
		}
		else
		{
			if(s->speed > 0)
			{
				s->speed = s->min_speed;
			}
			else
			{
				s->speed = -s->min_speed;
			}
		}
	}

	else
	{
		printf("invalid char value");
	}
}
