from Behavior import *
import numpy as np

class Repertoire(object):
    """
    A Repertoire which holds Behaviors in a manner which makes it easy to find
    the right set of Behaviors to move to a goal.
    """
    def __init__(self):
        self.__perform_times = np.array(dtype=int)
        self.__behaviors = np.array(dtype=Behavior)

    def get_performance_at(self, p):
        """
        Get the smallest amount of time it will take to reach point p, which
        is relative to the current position of the tensegrity. That is, point
        <x,y,theta> is x units away from the tensegrity horizontally, y units
        vertically, and theta degrees.
        :param p: Point to reach relative to tensegrity
        :return: an int representing seconds
        """
        return self.__perform_times[p.x, p.y, p.theta]

    def get_behavior_at(self, p):
        """
        Get the behavior which takes the shortest time to reach the given
        point relative to the tensegrity.
        :param p: Point to reach relative to tensegrity
        :return: a Behavior object which reaches the target point.
        """
        return self.__behaviors[p.x, p.y, p.theta]

    def compare_performance(self, comp_time, p):
        """
        Compare the given performance time with the existing best performance
        time to reach point p.
        :param comp_time: Time to compare with existing best
        :param p: Point to reach
        :return: True if the given performance time is less than the existing
        one
        """
        return comp_time < self.get_performance_at(p)

    def add_behavior(self, bhvr, p_time, p):
        """
        Add the given behavior and its performance time to the repertoire at
        the point it reaches, so long as the performance time of the new
        behavior is better than the best previous performance time.
        :param bhvr: The Behavior which reaches point P
        :param p: Point to reach
        """
        if self.compare_performance(p_time, p):
            self.__behaviors[p.x, p.y, p.theta] = bhvr
            self.__perform_times[p.x, p.y, p.theta] = p_time

    def __contains__(self, item):
        return item in self.__behaviors

    # TODO Implement saving and loading repertoires