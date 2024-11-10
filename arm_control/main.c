#include "Servo.h"
int main()
{

	stdio_init_all();

	Joy j;
	JoyInit(&j, 0.49, 0.49, 0.015, 26, 27, 0, 1);
	adc_init();

	adc_gpio_init(26);
	adc_gpio_init(27);

	Servo s_1, s_2;

	ServoInit(&s_1, 0, false);
	ServoInit(&s_2, 1, false);

	ServoOn(&s_1);
	ServoOn(&s_2);
	int i = 10;
	float a = 1;

	while(1)
	{

		JoyValue(&j);
		adcSetVelocity(&s_1, &j, 0);
		adcSetVelocity(&s_2, &j, 1);
		controlServo(&s_1);
		controlServo(&s_2);
		ServoPosition(&s_1, s_1.angle);
		ServoPosition(&s_2, s_2.angle);



		//printf("sp: %f ::", s_1.speed);

		//printf("%d\n", s_1.angle);
		//printf("%f\n",j.y);
		//printf("%f : %d ::", s_1.speed, s_1.angle);
		//printf("%f\n", j.y);

		//JoyRealValue(&j);
	}

}
