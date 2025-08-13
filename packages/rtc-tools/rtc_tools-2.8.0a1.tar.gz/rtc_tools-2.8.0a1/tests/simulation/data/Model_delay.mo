model Model_delay
    parameter Real x_start;
    parameter Real t_delay = 0.22;
    output Real x(start=x_start);
    output Real z1;
    output Real z2;
    output Real z3;

equation
    der(x) = 1;
    z1 = delay(10 * x, t_delay);
    z2 = delay(100 * x, t_delay / 2);
    z3 = delay(1000 * x, 0.33);

end Model_delay;