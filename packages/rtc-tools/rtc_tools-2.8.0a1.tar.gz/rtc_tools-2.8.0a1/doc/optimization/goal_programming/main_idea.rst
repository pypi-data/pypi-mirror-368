Main idea
=========

Goal programming is used to handle an optimization problem with multiple goals of the form

.. math::
    \text{minimise }& f_i(x), \\
    \text{subject to }& g_{ij}(x) \leq 0 \text{ for } j=1,...,m_i,

for :math:`i=1,...,N`, with :math:`N` the total number of goals.

Each goal :math:`i` has a weight :math:`\omega_i` and a priority  :math:`p_i`.
Goals with the same priority are converted into one goal.
For example, if multiple goals have priority 30,
then the resulting minimization problem for priority 30 would look like

.. math::
    \text{minimise }& \sum_{i:p_i=30} \omega_i f_i(x), \\
    \text{subject to }& g_{ij}(x) \leq0 \text{ for }j=1,...,m_i, i: p_i=30.

The reduced set of goals can be rewritten in the form

.. math::
    \text{minimise }& \sum_{i=1}^{n_p} \omega_{pi} f_{pi}(x), \\
    \text{subject to }& g_{pj}(x) \leq 0, \text{ for } j=1,...,m_p,

Problems with different priorities are solved from lowest to highest priority.
The results from previous priorities are used as constraints in the goal of the next priority
to enforce that the minimal values of the previous priorities remain minimal.
For example, suppose we have goals with priorities 10, 20, and 30.
We first solve the minimisation problem for priority 10 and find a solution :math:`x_{10}^*`.
For the next goal, we add the constraints :math:`f_{10,i}(x) \leq f_{10,i}(x_{10}^*)` or,
equivalently, :math:`f_{10,i}(x) - f_{10,i}(x_{10}^*) \leq 0`,
for :math:`i=1,2,\dots,n_{10}`.
The resulting problem for priority 20 can thus be written as

.. math::
    \text{minimise }& \sum_{i=1}^{n_{20}} f_{20,i}(x), \\
    \text{subject to }& g_{20,j}(x) \leq 0 \text{ for } j=1,...,m_{20}, \\
    \text{and }& f_{10,i}(x) \leq f_{10,i}(x_{10}^*) \text{ for } i=1,...,n_{10}.

For priority 30, we then do something similar
and add the constraints :math:`f_{10}(x) \leq f_{10,i}(x_{10}^*)`
and :math:`f_{20}(x) \leq f_{20,i}(x_{20}^*)`.
In general, the extended problem for priority :math:`p` can be written as

.. math::
    \text{minimise }& \sum_{i=1}^{n_p} f_{pi}(x), \\
    \text{subject to }& g_{qj}(x) \leq 0, \text{ for } j=1,...,m_{p}, q \leq p, \\
    \text{and }& f_{qi}(x) \leq f_{qi}(x_{q}^*), \text{ for } i=1,...,n_q, q < p.

This is the default way to convert results of a previous optimisation problem
to a constraint for the next optimisation problem.
Details on converting goals to constraints
can be found in :ref:`converting-goals-to-constraints`.

There are several options for implementing goal programming.
These options are set with
:py:meth:`rtctools.optimization.goal_programming_mixin.GoalProgrammingMixin.goal_programming_options`.

.. autoclass:: rtctools.optimization.goal_programming_mixin.GoalProgrammingMixin
    :members: goal_programming_options, goals, path_goals, priority_started, priority_completed
    :show-inheritance:

.. autoclass:: rtctools.optimization.single_pass_goal_programming_mixin.SinglePassGoalProgrammingMixin
    :members: goal_programming_options, goals, path_goals, priority_started, priority_completed
    :show-inheritance:

.. autoclass:: rtctools.optimization.single_pass_goal_programming_mixin.CachingQPSol
    :show-inheritance:
