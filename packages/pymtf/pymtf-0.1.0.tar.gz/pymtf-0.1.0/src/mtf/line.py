import numpy as np
from collections.abc import Collection


class Line:
    """
    Representation of a line using slope intercept.
    
    This does not account for a perfectly vertical (infinite slope) line.
    """

    def __init__(self, slope, intercept):
        self._slope = slope
        self._intercept = intercept

    def abc(self):
        """
        Returns a, b, c from the representation of a line expressed as:
        
        a * x + b * y + c = 0
        """
        return (-self._slope, 1, -self._intercept)
    
    def dist(self, pt: Collection[2]):
        """
        Return the absolute value of the perpendicular distance from the line.

        Using equation from:
        https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
        """
        a, b, c = self.abc()
        return np.abs(a * pt[0] + b * pt[1] + c) / np.sqrt(a**2 + b**2)
    
    def signed_dist(self, pt: Collection[2]):
        """
        Same as dist but signed based on which side of the line.
        """
        a, b, c = self.abc()
        return (a * pt[0] + b * pt[1] + c) / np.sqrt(a**2 + b**2)
    
    @property
    def slope(self):
        return self._slope
    
    @property
    def intercept(self):
        return self._intercept
    
    @staticmethod
    def from_points(pt1: Collection[2], pt2: Collection[2]):
        slope = (pt2[1] - pt1[1]) / (pt2[0] - pt1[0])
        intercept = (pt1[1] - slope * pt1[0])
        return Line(slope, intercept)
    
    def __repr__(self):
        return f"<Line slope: {self.slope:.1f} intercept: {self.intercept:.1f}>"
