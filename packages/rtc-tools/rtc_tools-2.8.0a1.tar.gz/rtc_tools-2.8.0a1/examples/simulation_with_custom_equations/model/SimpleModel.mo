model SimpleModel
    Real y;  // Depends on x through a formula that is implemented in Python.
    output Real x;
equation
    der(x) = y;
end SimpleModel;