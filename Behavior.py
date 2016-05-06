from Exceptions import *
from ObjectConstants import *


class Behavior(object):
    """
    The Behavior class represents a single behavior which the tensegrity
    knows. Every Behavior has a method execute() which signals the tensegrity
    on how to move. Every Behavior also has an instance variable performTime
    which indicates the amount of time the Behavior will take in seconds, and
    an instance variable moveVector which represents the movement the Behavior
    will produce as a 3-vector <x, y, theta> where x and y are horizontal and
    vertical distance from the initial position of the tensegrity and theta
    is the angular distance in radians from the inital heading of the
    tensegrity. Behavior has getters and setters for each instance variable as
    well.
    """

    def __init__(self, instruction_list, num_motors):
        self.__num_motors = num_motors
        self.__instr_list = instruction_list
        for instr in self.__instr_list:
            if not self.__verify_instr(instr):
                raise InstructionMotorCountError(instr, self.__num_motors)

    def __verify_instr(self, instruction):
        """
        Check whether the instruction is a valid one. This means that it
        checks to make sure the instruction uses the appropriate number of
        motors and that the frequencies of the instruction are all in the
        appropriate range.

        :param instruction: A dict, where the keys is the motor controller ID
        and the value is that motor's frequency.
        """
        assert isinstance(instruction, dict), "instruction is not a dict!"
        motor_num_correct = len(instruction) == self.__num_motors
        for freq in instruction.values():
            if not (MOTOR_LOWER_BOUND < freq < MOTOR_UPPER_BOUND):
                raise FrequencyError(freq)
        return motor_num_correct

    def execute(self, ctrl):
        """
        Executes all of the instructions in its instruction list. Each
        instruction is a dictionary of motor numbers and the frequency to run
        them at.

        :param ctrl: The motor controller to use.
        """
        for instr in self.__instr_list:
            ctrl.run_instructions(instr)

    # TODO Implement saving and loading a behavior