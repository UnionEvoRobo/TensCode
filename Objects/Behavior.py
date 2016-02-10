from TensegrityController import TensegrityController
from Exceptions import FrequencyError
from ObjectConstants import *


class Behavior(object):
    """
    The Behavior class represents a single behavior which the tensegrity
    knows. The Behavior class is abstract, and has two subclasses:
    SimpleBehavior and ComplexBehavior. Every Behavior has a method
    execute(TensegrityController ctrl) which uses the ctrl parameter to signal
    the tensegrity on how to move. Every Behavior also has an instance variable
    performTime which indicates the amount of time the Behavior will take in
    seconds, and an instance variable moveVector which represents the movement
    the Behavior will produce as a 3-vector <x, y, theta> where x and y are
    horizontal and vertical distance from the initial position of the
    tensegrity and theta is the angular distance in radians from the inital
    heading of the tensegrity. Each Behavior has getters and setters for each
    instance variable as well.
    """

    def __init__(self):
        self.__performTime = 0
        self.__moveVector = [0,0,0]

    def set_performTime(self, time):
        """
        :param time: Time in seconds
        """
        self.__performTime = time

    @property
    def get_performTime(self):
        """
        :return: Time to perform behavior in seconds
        """
        return self.__performTime

    def set_moveVector(self, x, y, theta):
        """
        :param x: float horizontal travel distance from origin
        :param y: float vertical travel distance from origin
        :param theta: float heading change from original heading
        """
        self.__moveVector = [x, y, theta]

    def get_moveVector(self):
        """
        :return: 3-vector of floats (horz_dist, vert_dist, head_change)
        """
        return self.__moveVector

    def execute(self, ctrl): pass


class SimpleBehavior(Behavior):
    """
    A SimpleBehavior represent one of the initially discovered Behaviors which
    contain only a single list of motor frequencies.
    """
    def __init__(self, frequency_list):
        """
        Create a Behavior that represents the results of vibrating the motors
        at the given frequencies. The passed frequency list should be composed
        of integers within the motor bounds defined in ObjectConstants.py.
        :param frequency_list: list of integers
        """
        super(SimpleBehavior, self).__init__()
        assert isinstance(frequency_list, list), "frequency list isn't a list!"
        for fq in frequency_list:
            if not (MOTOR_LOWER_BOUND < fq < MOTOR_UPPER_BOUND):
                raise FrequencyError(fq)
        self.__freq_list = frequency_list

    def execute(self, ctrl):
        """
        Send the signal to the passed in TensegrityController to run the
        motors at the appropriate frequencies given in the freq_list, for
        the amount of of time given by self.__performTime.
        :param ctrl: a TensegrityController object to signal
        """
        assert isinstance(ctrl, TensegrityController), "ctrl not a Controller"
        ctrl.run_motors(self.__freq_list)


class ComplexBehavior(Behavior):
    """
    A ComplexBehavior is a calculated Behavior which combines two or more other
    Behaviors into a single new one. Thus ComplexBehaviors have a list of other
    Behavior objects, which are the iterated through and executed when a
    ComplexBehavior is executed.
    """
    def __init__(self, behavior_list):
        """
        Create a Behavior which represents chaining together many other
        Behaviors and executing them sequentially. The passed list should be
        entirely Behavior objects. Additional Behaviors can be added to the
        Behavior chain after instantiation, and the moveVector and performTime
        will be adjusted accordingly.
        :param behavior_list: list of Behavior objects ORDER MATTERS
        """
        super(ComplexBehavior, self).__init__()
        self.bhv_list = []
        assert isinstance(behavior_list, list), "frequency list isn't a list!"
        for bhv in behavior_list:
            assert isinstance(bhv, Behavior), "behavior list has non-behavior"
            self.add_behavior(bhv)

    def add_behavior(self, bhv):
        pTime = self.get_performTime + bhv.get_performTime
        self.set_performTime(pTime)
        old_mvVect = self.get_moveVector()
        bhv_mvVect = bhv.get_moveVector()
        for i in range(3):
            old_mvVect[i] += bhv_mvVect[i]
        self.set_moveVector(bhv_mvVect[0], bhv_mvVect[1], bhv_mvVect[2])
        self.bhv_list.append(bhv)

    def execute(self, ctrl):
        for bhv in self.bhv_list:
            bhv.execute(ctrl)
