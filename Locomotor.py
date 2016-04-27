import time
import serial
from json import loads, dumps
from ObjectConstants import RUN_TIME

class Locomotor(object):
    """
    Class which holds any number of motor controllers and controls them. The
    run_motors() function can receive a list of motor frequencies which are
    then assigned to each motor. The object can be indexed in the standard way
    and can have elements added to it or altered in a similar way to a dict.
    """
    def __init__(self, port, motor_list=None):
        """
        Give a list of motors to the Locomotor. In the future, we might test
        each one.
        :param motor_list: A list of motors to control. It is very important
        that the order of the motor list is maintained throughout runs of the
        code.
        """
        if motor_list is not None:
            self.__motor_num = len(motor_list)
            self.__motor_dict = dict(zip(range(self.__motor_num), motor_list))
            self.__ctrl = serial.Serial(port, 19200, 8, 'N', 1, timeout=0.1)

    def run_instructions(self, freq_dict):
        """
        Run a set of frequencies on the appropriate motors.
        :param freq_dict: A dict of motor ids and their frequencies
        :return: A happily vibrating tensegrity.
        """
        assert len(freq_dict) == self.__motor_num, "invalid motor amount"
        for mNum in freq_dict.keys():
            self.__motor_dict[mNum].run_motor(freq_dict[mNum], self.__ctrl)
        time.sleep(RUN_TIME)
        for mNum in freq_dict.keys():
            self.__motor_dict[mNum].stop_motor(self.__ctrl)

    def get_motor_num(self): return self.__motor_num

    def config_motors(self):
        print(
"""INSTRUCTIONS FOR CONFIGURATION:
1) Label each motor controller from 1 to N, where N= num of motor controllers
2) Each motor in the Locomotor's list will ask to be configured.
3) It will give you a motor controller to attach to the FTDI Basic.
4) Un
"""
              )
        for m_num in self.__motor_dict:
            print("Configure motor {}".format(m_num))

    def test_motors(self):
        for m_num in self.__motor_dict:
            print("Testing motor {}".format(m_num))
            self.__motor_dict[m_num].run_motor(127, self.__ctrl)
            time.sleep(RUN_TIME)
            self.__motor_dict[m_num].stop_motor(self.__ctrl)

    def __len__(self):
        return self.__motor_num

    def __getitem__(self, item):
        if item < self.__motor_num:
            return self.__motor_dict[item]
        else:
            msg = "Index {} exceeds motor number".format(item)
            raise IndexError(msg)

    def __setitem__(self, key, value):
        if key < self.__motor_num:
            self.__motor_dict[key] = value
        else:
            msg = "Index {} exceeds motor number".format(key)
            raise IndexError(msg)

    def save_locomotor(self):
        return "{mNum}, {mDict}".format(mNum=self.__motor_num,
                                          mDict=dumps(self.__motor_dict)
                                          )

    def load_locomotor(self, string):
        data_parts = string.split(',')
        self.__motor_num = int(data_parts[0])
        self.__motor_dict = loads(data_parts[1])

    # TODO Implement saving and loading a locomotor


class MotorController(object):
    """
    Class to control an individual motor. This is meant to be an abstract-like
    class, so that we can impleent a number of subclasses which each control
    different types of motors e.g. serial USB motors, bluetooth controlled
    motors, etc.
    """
    SPINUP_TIME = 0.3

    def __init__(self, motor_ID):
        self.__motor_ID = motor_ID

    def run_motor(self, freq, ctrl):
        print("Running motor {id} @ {freq}\n".format(id = self.__motor_ID,
                                                   freq=freq
                                                   )
              )

class SerialMotorController(MotorController):
    """
    Class to control a motor through serial comms. We use two USB outputs of a
    computer connected to two Sparkfun FTDI boards, which are then connected to
    two Pololu Qik dual-motor controllers. The class uses pySerial to
    communicate with the controllers.
    See https://pythonhosted.org/pyserial/pyserial.html#overview for more info
    on pySerial and cswiki.union.edu/index.php/Tensegrity_Robotics for more
    info on the project itself.

    :param port: The serial port which the USB is connected to,
        e.g. /dev/ttyUSB0 or COM1.
    :param sub_port: The subset of the USB port which controls this motor,
        since each USB out controls two motors. This should be either 1 or 2.
    """
    def __init__(self, motor_ID):
        super(SerialMotorController, self).__init__(motor_ID)
        self.__motor_ID = motor_ID

    def run_motor(self, freq, ctrl):
        """
        Runs the motor at a given frequency. This is fairly complicated, so for
        a full explanation look at the manual (page 8 in particular):


        In simple terms, each motor is controlled by 4 bytes. Because we are
        using pySerial, we have to send 8 bytes, so we can just ignore
        the last 4 bytes of each message. We can indicate to the controllers which
        motor to control if we know the number of the motor we are controlling.
        This is why the SerialMotorController object needs to know its motor
        number, hence the use of motor_num.

        :param freq: Frequency from -127 to 127
        """
        commandBytes = self.__get_command_bytes(freq)
        self.__spin_up(ctrl)
        ctrl.write(commandBytes)

    def stop_motor(self, ctrl):
        """
        Stop the motor immediately.
        """
        commandBytes = self.__get_command_bytes(0)
        ctrl.write(commandBytes)

    def __get_command_bytes(self, freq):
        """
        The command bytes we send to the controller are formatted as follows:
        Byte 1: Start byte - Always 128, indicates start of a signal
        Byte 2: Device type - Always 0, indicates what we're talking to
        Byte 3: Motor number & direction - Has three parts:
            Bit 0: Specifies direction of motor (0 = back, 1 = forward)
            Bits 1-6: Motor number (Multiply motor_num by 2)
            Bit 7: Always 0
        Byte 4: Motor speed - 0 to 127, where 0 is off and 127 is full

        :param freq: -127 to 127
        """
        commandBytes = bytearray(5)
        commandBytes[0] = 128   # Start byte (always 128)
        commandBytes[1] = 0     # Device type (always 0)
        direction_bit = 1 if freq < 0 else 0
        motor_num_bit = self.__motor_ID * 2
        commandBytes[2] = motor_num_bit + direction_bit
        commandBytes[3] = abs(freq)
        commandBytes[4] = 0 #last byte empty
        return commandBytes

    def __spin_up(self, ctrl):
        """
        Spin up the motor briefly, since lower voltages won't get the motor
        started.
        """
        commandBytes = self.__get_command_bytes(127)
        ctrl.write(commandBytes)
        time.sleep(self.SPINUP_TIME)

    def configure_motor(self, ctrl):
        """
        Configure the physical motor controller to accept commands only for
        this motor. This assigns the physical motor controller slot a number
        equal to self.motor_ID, which can then be referenced when command bytes
        are sent.

        Only three command bytes need to be sent to the motor controller to
        configure it:
        Byte 1: Start byte - Always 128, indicates start of a signal
        Byte 2: Change config byte - Always 2, indicates changing configuration
        Byte 3: New Settings byte - Has two parts:
            Bits 0-5: Specify motor numbers controller will respond to. If
            the number is even, controller will control the number and the
            number above it (e.g. 0x04 means M0 is number 4 and M1 is number 5)
            Bit 6: controller mode. Keep this at 0 for two motors
            Bit 7: Always 0

        This function changes the configuration of the controller board itself,
        not just one motor. Use with care, and only if you understand how this
        works.
        """
        commandBytes = bytearray(5)
        commandBytes[0] = 128
        commandBytes[1] = 2
        commandBytes[2] = self.__motor_ID + 2 # on controllers 0&1 are global
        commandBytes[3] = commandBytes[4] = 0 # last two bytes empty
        ctrl.write(commandBytes)
