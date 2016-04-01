__author__ = 'James Boggs'

class Point(object):
    """
    A quick object to represent a location on the table. Represents
    <x, y, theta> where x is the horizontal location (the long side of the
    table), y is the vertical (short side of the table), and theta is the
    heading of the tensegrity where the black tape is 0 degrees.
    """
    def __init__(self, x, y, theta):
        """
        Create a new Point, where x, y, and theta are ints.
        :param x: The horizontal location
        :param y: The vertical location
        :param theta: The heading of the tensegrity
        """
        self.x = x
        self.y = y
        self.theta = theta

    def find_rel_dist(self, p):
        """
        Find the relative distance between this point and given point p, and
        return is as another point.
        :param p: Target point to measure
        :return: A point whose x, y, and theta represent the relative distance
        from this point to p.
        """
        assert isinstance(p, Point), "p should be a Point"
        rel_x = self.x - p.x
        rel_y = self.y - p.y
        rel_theta = (self.theta - p.theta) % 360
        return Point(rel_x, rel_y, rel_theta)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x-other.x,
                         self.y-other.y,
                         self.theta-other.theta
                         )
        else:
            msg = 'unsupported operand type(s) for -: Point and {t}'.format(t=type(other))
            raise TypeError(msg)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x+other.x,
                         self.y+other.y,
                         self.theta+other.theta
                         )
        else:
            msg = 'unsupported operand type(s) for -: Point and {t}'.format(t=type(other))
            raise TypeError(msg)