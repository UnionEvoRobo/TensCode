# TODO Implement TensegrityController and TestTensController
class Locomotor(object):
    """
    Class which holds any number of motor controllers and controls them. The
    run_motors() function can receive a list of motor frequencies which are
    then assigned to each motor.
    """
    def __init__(self, motor_list):
        """
        Give a list of motors to the Locomotor. In the future, we might test
        each one.
        :param motor_list: A list of motors to control. It is very important
        that the order of the motor list is maintained throughout runs of the
        code.
        """
        self.__motor_num = len(motor_list)
        self.__motor_dict = dict(zip(range(self.__motor_num), motor_list))

    def run_instructions(self, freq_dict):
        """
        Run a set of frequencies on the appropriate motors.
        :param freq_dict: A dict of motor ids and their frequencies
        :return: A happily vibrating tensegrity.
        """
        assert len(freq_dict) == self.__motor_num, "invalid motor amount"
        for mNum in freq_dict.keys():
            print "Running motor {mNum} at {mFreq}".format(mNum=mNum,
                                                           mFreq=freq_dict[mNum])

    def get_motor_num(self): return self.__motor_num

    def save_locomotr(self): return "|{mNum}, {mDict}|".format(mNum=self.__motor_num,
                                                               mDict=self.__motor_dict
                                                               )