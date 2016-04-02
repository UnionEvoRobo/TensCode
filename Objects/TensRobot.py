from Behavior import Behavior
from Repertoire import Repertoire
from Locomotor import Locomotor
from Point import Point

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
