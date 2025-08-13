import logging

from rtctools.simulation.csv_mixin import CSVMixin
from rtctools.simulation.simulation_problem import SimulationProblem
from rtctools.util import run_simulation_problem

logger = logging.getLogger("rtctools")


class SimpleModel(CSVMixin, SimulationProblem):
    """
    Simple model class to illustrate implementing a custom equation.

    This class illustrates how to implement a custom equation in python
    instead of Modelica.

    The model of this class is given by

    .. math::
        \frac{dx}{dt} &= y, \\
        y &= -\frac{2}{3600}x.

    The equation for :math:`x` is given in Modelica,
    while the equation for :math:`y` is implemented in this class.
    """

    def extra_equations(self):
        variables = self.get_variables()

        y = variables["y"]
        x = variables["x"]

        # A scale to improve the performance of the solver.
        # It has the average order of magnitude of the term y and 2/3600 x.
        constraint_nominal = (
            2 / 3600 * self.get_variable_nominal("x") * self.get_variable_nominal("y")
        ) ** 0.5

        return [(y - (-2 / 3600 * x)) / constraint_nominal]


# Run
run_simulation_problem(SimpleModel, log_level=logging.DEBUG)
