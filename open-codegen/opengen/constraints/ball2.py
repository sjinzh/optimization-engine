import casadi.casadi as cs
import numpy as np
from opengen.constraints.constraint import Constraint


class Ball2(Constraint):
    """A Euclidean ball constraint

    A constraint of the form ||u-u0|| <= r, where u0 is the center
    of the ball and r is its radius

    """

    def __init__(self, center, radius: float):
        """Constructor for a Euclidean ball constraint

        Args:
            center: center of the ball; if this is equal to Null, the
            ball is centered at the origin

            radius: radius of the ball

        Returns:
            New instance of Ball2 with given center and radius
        """
        if radius <= 0:
            raise Exception("The radius must be a positive number")

        if center is not None and not (isinstance(center, list)
                                       or isinstance(center, np.ndarray)):
            raise Exception("center is neither None nor a list nor np.ndarray")

        self.__center = None if center is None else np.array([float(i) for i in center])
        self.__radius = float(radius)

    @property
    def center(self):
        """Returns the center of the ball"""
        return self.__center

    @property
    def radius(self):
        """Returns the radius of the ball"""
        return self.__radius

    def distance_squared(self, u):
        """Computes the squared distance between a given point `u` and this ball

            :param u: given point; can be a list of float, a numpy
                n-dim array (`ndarray`) or a CasADi SX symbol

            :return: distance from set as a float or a CasADi symbol
        """
        # Function `distance` can be applied to CasADi symbols and
        # lists of numbers. However, if `u` is a symbol, we need to
        # use appropriate CasADi functions like cs.sign and cs.norm_2
        if isinstance(u, cs.SX):
            # Case I: `u` is a CasADi SX symbol
            sign_fun = cs.sign
            max_fun = cs.fmax
            norm_fun = cs.norm_2
            v = u if self.__center is None else u - self.__center
        elif (isinstance(u, list) and all(isinstance(x, (int, float)) for x in u))\
                or isinstance(u, np.ndarray):
            # Case II: `u` is an array of numbers or an np.ndarray
            sign_fun = np.sign
            norm_fun = np.linalg.norm
            max_fun = np.fmax
            if self.__center is None:
                v = u
            else:
                # Note: self.__center is np.ndarray (`u` might be a list)
                z = self.__center.reshape((len(u), 1))
                u = np.array(u).reshape((len(u), 1))
                v = np.subtract(u, z)
        else:
            raise Exception("u is of invalid type")

        # Compute squared distance
        # Let B = B(xc, r) be a Euclidean ball centered at xc with radius r
        #
        # dist_B^2(u) = max(0, sign(t(u))*t(u)^2), where
        # t(u) = ||u - x_c|| - r
        #
        # Note: there is another way to take squared distances:
        # d_B^2(u) = ||u||^2 * (1 - 1 / max{r, ||u||})^2,
        # but this leads to slightly lengthier CasADi symbols for
        # the Jacobian of the squared distance, so this approach was
        # abandoned
        t = norm_fun(v) - self.radius
        return max_fun(0.0, sign_fun(t) * t ** 2)

    def project(self, u):
        # Idea: Computes projection on Ball as follows
        #   Proj_B(u) = u / max{1, ||u||},
        # which avoids dividing by zero or defining the projections
        raise NotImplementedError()
