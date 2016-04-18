from ObjectConstants import *


class FrequencyError(Exception):
    """
    Represents an error with the frequency value, i.e. when the frequency
    is over or under acceptable bounds as prescribed in ObjectConstants.py.
    """
    def __init__(self, value):
        self.freq_val = value
        fault = "lower" if value < MOTOR_LOWER_BOUND else "higher"
        self.message = "given frequency {} than the motor's bounds".format(fault)


class InstructionMotorCountError(Exception):
    """
    Represents an error where the instruction passed or created somewhere is
    ill-formed or invalid because it has too many motors.
    """
    def __init__(self, instruction, tgt_motor_num):
        instr_motor_num = len(instruction)
        fault = "few" if instr_motor_num < tgt_motor_num else "many"
        self.message = "given instruction has too {} motor instructions".format(fault)
