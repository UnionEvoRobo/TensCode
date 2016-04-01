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
        self.__curr_location = Point(0, 0, 0)

    def move_to(self, p):
        """
        Move the tensegrity to the absolute point p on the table.
        :param p: Point to move the tensegrity to
        """

