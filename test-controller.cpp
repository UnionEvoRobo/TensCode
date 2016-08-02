
#include <iostream>
#include <unistd.h>
#include <time.h>

#include "tensegrity-controller.hpp"



int main(int argc, char** argv)
{

	srand(time(NULL));


	int opt;


	float inspd0 = 0.5;
	float inspd1 = 0.5;
	float inspd2 = 0.5;

	int spd0 = 0;
	int spd1 = 0;
	int spd2 = 0;

	int duration = 3; //seconds

	bool randomspeeds = 0;
	bool testmotors = 0;
	bool useTracking = 0;

	//std::cout << argv << std::endl;


	std::string portName("/dev/ttyUSB0");

  while ((opt = getopt(argc, argv, "p:1:2:3:d:rtT")) != -1) {
        switch (opt) {
					case 'p':
					      portName = std::string(optarg);
								break;
        case '1':
            inspd0= atof(optarg);
            break;
        case '2':
            inspd1 = atof(optarg);
            break;
        case '3':
            inspd2 = atof(optarg);
            break;
				case 'd':
						duration = atoi(optarg);
						break;
				case 'r':
						randomspeeds = 1;
						break;
				case 't':
						testmotors = 1;
						break;
				case 'T':
					useTracking = 1;
					//std::cout << "tracking" << std::endl;
					break;
        default: /* '?' */
            fprintf(stderr, "Usage: %s [-p serialPort] [-1 motor1speed] [-2 motor2speed] [-3 motor3speed] [-d duration] [-r]andom [-t]estmotors\n",
                    argv[0]);
            exit(EXIT_FAILURE);
        }
    }

	tensegrity::Tensegrity_Controller tens(portName);

	if (useTracking)
	{
		//spinner.start();
	}
	if (testmotors)
	{

		tens.set_all_motor_speeds(40,0,0);
		sleep(2);
		std::cout << "-------------------------------------" << std::endl;
		tens.stop_all_motors();
		std::cout << "=====================================" << std::endl;

		tens.set_all_motor_speeds(0,40,0);
		sleep(2);
		std::cout << "-------------------------------------" << std::endl;
		tens.stop_all_motors();
		std::cout << "=====================================" << std::endl;

		tens.set_all_motor_speeds(0,0,40);
		sleep(2);
		std::cout << "-------------------------------------" << std::endl;
		tens.stop_all_motors();
		std::cout << "=====================================" << std::endl;

	}
	else
	{
		if (!randomspeeds)
		{
			spd0 = 2*MAXSPEED*inspd0 - MAXSPEED;
			spd1 = 2*MAXSPEED*inspd1 - MAXSPEED;
			spd2 = 2*MAXSPEED*inspd2 - MAXSPEED;

			// spd0 = 254*inspd0 - 127;
			// spd1 = 254*inspd1 - 127;
			// spd2 = 254*inspd2 - 127;

			//std::cout << "***" << std::endl<< a << "," << spd0 <<","<<b<<","<<spd1<<","<<c<<","<<spd2<<std::endl;
		}
		else
		{
			spd0 = ((double)rand()/RAND_MAX)*2*MAXSPEED - MAXSPEED;
			spd1 = ((double)rand()/RAND_MAX)*2*MAXSPEED - MAXSPEED;
			spd2 = ((double)rand()/RAND_MAX)*2*MAXSPEED - MAXSPEED;
		}

		std::cout << spd0 << " " << spd1 << " "	 << spd2 << std::endl;

		tens.set_all_motor_speeds(spd0,spd1,spd2);
		// tens.set_motor_speed(0, spd0);
		// tens.set_motor_speed(1, spd1);
		// tens.set_motor_speed(2, spd2);
		sleep(duration);

}
/*
	for (int i = 0; i < 10; i++)
	{

		cout << spd0 << " " << spd1 << " " << spd2 ;
		tens.set_motor_speed(0, spd0);
		tens.set_motor_speed(1, spd0);
		tens.set_motor_speed(2, spd0);
		usleep(1000000);
	}
*/
		tens.stop_all_motors();


	/*
	std::cout << "hello world``!\n";
  serial::Serial sp("/dev/ttyUSB1",B19200);
  std::string str(5,0);
  str[0] = 0xAA;
  str[1] = 0x00;
  str[2] = 0x09;
  str[3] = 0x00;
  sp.send(str);
	return 0;
*/

}
