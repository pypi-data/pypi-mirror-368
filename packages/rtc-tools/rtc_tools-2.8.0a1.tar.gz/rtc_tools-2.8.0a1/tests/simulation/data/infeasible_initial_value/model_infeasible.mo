model ModelInfeasible
	Real x;
    Real y;
equation
	der(x) = -x;
    y * y = -10;
end ModelInfeasible;
