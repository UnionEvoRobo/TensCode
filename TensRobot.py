from time import sleep
from Behavior import Behavior
from Repertoire import Repertoire
from Locomotor import Locomotor, SerialMotorController
from Point import Point
from ImageProcessing import BoardObserver
import serial

class TensRobot(object):
    """
    The representation of the tensegrity robot, including its behavioral
    repertoire and motor controller.
    """
    def __init__(self, name, locomotor, observer):
        self.name = name
        self.__repertoire = Repertoire()
        self.__locomotor = locomotor
        self.__board_observer = observer

    def move_to_absolute(self, p):
        """
        Move the tensegrity to the absolute point p on the table.
        :param p: Point to move the tensegrity to
        """
        assert isinstance(p, Point), "can only move to Points!"
        while self.curr_location != p:
            relative_target = self.curr_location.find_rel_dist(p)
            nav_behavior = self.__repertoire.get_behavior_at(relative_target)
            nav_behavior.execute(self.__locomotor)

    def move_to_relative(self, p):
        """
        Move the tensegrity to point p where the current location of the
        tensegrity is treated as 0,0. In other words, point p can be treated
        as the relative distance the tensegirty should travel.
        :param p: Relative distance tens should travel
        """
        assert isinstance(p, Point), "can only move to Points!"
        origin_location = self.curr_location
        target_location = origin_location + p
        self.move_to_absolute(target_location)

    def run_behavior(self, bhvr):
        """
        Run a given behavior, recording the relative distance moved and
        returning it.
        :param bhvr: Behavior to test
        :return: A Point representing the relative distance moved
        """
        assert isinstance(bhvr, Behavior), "can only run Behaviors!"
        if self.__board_observer is not None:
            origin_location = self.curr_location
        bhvr.execute(self.__locomotor)
        if self.__board_observer is not None:
            rel_distance = origin_location.find_rel_dist(self.curr_location)
            return rel_distance

    def run_freqs(self, freq_list):
        """
        Run a list of frequencies on the motors, where the index of the
        frequency is the motor number to run.
        :param freq_list: List of ints with values -127 to 127
        """
        freq_dict = dict(zip(range(len(freq_list)), freq_list))
        bhvr = Behavior([freq_dict], len(freq_list))
        self.run_behavior(bhvr)

    def add_behavior(self, bhvr, p_time, rel_dist):
        """
        Add the given behavior and its information to the tensegirty's
        repertoire.
        :param bhvr: Behavior to add
        :param p_time: bhvr performance time
        :param rel_dist: relative distance bhvr travels.
        :return: True is added, false if not better than existing behavior.
        """
        return self.__repertoire.add_behavior(bhvr, p_time, rel_dist)

    def update_motor(self, motor_num, new_motor):
        self.__locomotor[motor_num] = new_motor

    def test_motors(self): self.__locomotor.test_motors()

    @property
    def curr_location(self):
        return self.__board_observer.tens_location


class TensBuilder(object):
    """
    Object which allows the user to interactive create a TensRobot by assigning
    a COM port and motors to the correct motors on the actual robot.
    """

    def build_tens(self):
        """
        An function that builds a TensRobot. Asks the user for input and allows user
        to specify which motor has which ID, to determine how many motors the Tens
        has, and to then save the TensRobot.
        """
        print("Creating a new tensegrity...")
        tens_name = raw_input("Name the tensegrity!  ")
        motor_num = input("How many motors?  ")
        COM_port = self.select_COM_port()
        motor_list = []
        for motor_ID in range(motor_num):
            new_controller = SerialMotorController(motor_ID)
            motor_list.append(new_controller)
        new_locomotor = Locomotor(COM_port, motor_list)
        new_locomotor.test_motors()

        new_observer = None  # BoardObserver()
        new_tens = TensRobot(tens_name, new_locomotor, new_observer)
        return new_tens


    def select_COM_port(self):
        user_OK = False
        while not user_OK:
            COM_port = raw_input("What COM port?  ")
            try:
                test_serial = serial.Serial(COM_port,
                                            19200, 8, 'N',
                                            timeout=0.8)
                user_OK = raw_input("So {} is correct? (Y/N)  ".format(COM_port))
                user_OK = user_OK.upper() == "Y"
            except:
                print("Bad COM port {}! Try again!".format(COM_port))
        return COM_port