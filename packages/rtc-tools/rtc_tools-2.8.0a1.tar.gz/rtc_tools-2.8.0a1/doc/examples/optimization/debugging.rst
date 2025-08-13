Debugging an Optimization Problem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Overview
--------

This example will illustrate a few tools that can help debugging an optimization problem.
For example, it will demonstrate how to test an optimization problem by only solving
for a fixed number of time steps.

A Basic Optimization Problem
----------------------------

For this example, the model is kept very basic.
We consider a single reservoir with a few target and optimization goals.
The optimization problem is given below.

.. literalinclude:: ../../../examples/single_reservoir/src/single_reservoir.py
  :language: python
  :pyobject: SingleReservoir

Optimizing for a given number of time steps
-------------------------------------------

By overwriting the method ``times``, we can control the times for which the problem is optimized.
In this case, we optimize for all times
unless the class attribute ``only_check_initial_values`` is set to ``True``.
Optimizing for only the initial time can be useful
to check for infeasibilities due to incompatible initial conditions.
