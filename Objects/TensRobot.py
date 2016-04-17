from time import sleep
from Behavior import Behavior
from Repertoire import Repertoire
from Locomotor import Locomotor, SerialMotorController
from Point import Point
import serial

class TensRobot(object):
    """
    The representation of the tensegrity robot, including its behavioral
    repertoire and motor controller.
    """
    def __init__(self, locomotor):
        self.__repertoire = Repertoire()
        self.__locomotor = locomotor
        # TODO Implement a BoardObserver object and make it an instance var

    def move_to_absolute(self, p):
        """
        Move the tensegrity to the absolute point p on the table.
        :param p: Point to move the tensegrity to
        """
        assert isinstance(p, Point), "can only move to Points!"
        while self.__curr_location != p:
            relative_target = self.__curr_location.find_rel_dist(p)
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
        origin_location = self.__curr_location
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
        origin_location = self.__curr_location
        bhvr.execute(self.__locomotor)
        rel_distance = origin_location.find_rel_dist(self.__curr_location)
        return rel_distance

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


    @property
    def __curr_location(self):
        # TODO Implement ability for tens to find its location
        return Point(0,0,0) # FIXME Remove this crap


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
        motor_num = input("How many motors?")
        COM_port = self.select_COM_port()
        test_serial = serial.Serial(COM_port, 19200, 5, 'N', timeout=0.3)
        motor_list = []
        for motor_ID in range(motor_num):
            motor_list.append(self.define_motor(COM_port, motor_ID))

    def select_COM_port(self):
        COM_port = raw_input("What COM port?")
        user_OK = False
        while not user_OK:
            try:
                test_serial = serial.Serial(COM_port,
                                            19200, 5, 'N',
                                            timeout=0.3)
                user_OK = raw_input("So {} is correct? (Y/N)".format(COM_port)
                user_OK = user_OK == "Y"
            except:
                print("Bad COM port! Try again!")
        return COM_port

    def define_motor(self,COM_port, m_ID):
        """
        Allow the user to choose which real motor this motor will be
        controlling. This is used in conjunction with hardware configurations.
        :param m_ID: ID of the motor.
        :return: A SerialMotorController object which controls the approriate
        hardware motor.
        """
        cfgdo = raw_input("Configure and test Motor {} now? (Y/N)".format(m_ID))
        while cfgdo == 'Y':
            new_motor = SerialMotorController(COM_port, m_ID)
            new_motor.configure_motor()
            new_motor.run_motor(127)
            sleep(5)

