.. _converting-goals-to-constraints:

Converting goals to constraints
===============================

The way goals are converted into constraints depends on the type of goal.
Details on the type of goals can be found in :ref:`goals`.

**Minimization goals**

Suppose we have a minimization goal of the form

    .. math::
        \text{minimize } f(x)

for the current priority, and we find a solution :math:`x^*`.
For the next priority, this goal is converted into a constraint of the form

    .. math::
        \text{subject to } f(x) \leq f(x^*).

**Target goals**

Suppose we have a target goal of the form

.. math::
    \text{minimize } & \epsilon^r, \\
    \text{subject to } & g_{low}(\epsilon) \leq g(x) \leq g_{up}(\epsilon), \\
    \text{and } & 0 \leq \epsilon \leq 1,

for the current priority, and we find a solution :math:`x^*` and :math:`\epsilon^*`.
For the next priority,
this target goal is converted into either a hard constraint or a soft constraint.

*Converting to a hard constraint (default)*

When converting a target goal into a hard constraint,
the target goal is converted into the followingng constraint.

.. math::
    \text{subject to } g_{low}(\epsilon^*) \leq g(x) \leq g_{up}(\epsilon^*).

*Converting to a soft constraint*

When converting a target goal into a soft constraint,
the target goal is replaced by the following constraints.

.. math::
    \text{subject to } & \epsilon^r \leq (\epsilon^*)^r, \\
    \text{and } & g_{low}(\epsilon) \leq g(x) \leq g_{up}(\epsilon), \\
    \text{and } & 0 \leq \epsilon \leq 1.

In other words, we keep the epsilon variables and original constraints,
but only replace the epsilon minimisation goal
by the constraint :math:`\epsilon^r \leq (\epsilon^*)^r`.
