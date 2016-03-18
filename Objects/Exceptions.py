from ObjectConstants import *


class FrequencyError(Exception):
    """
    Represents an error with the frequency value, i.e. when the frequency
    is over or under acceptable bounds as prescribed in ObjectConstants.py.
    """
    def __init__(self, value):
        self.freq_val = value
        fault = "lower" if value < MOTOR_LOWER_BOUND else "higher"
        self.msg = "given frequency {} than the motor's bounds".format(fault)
