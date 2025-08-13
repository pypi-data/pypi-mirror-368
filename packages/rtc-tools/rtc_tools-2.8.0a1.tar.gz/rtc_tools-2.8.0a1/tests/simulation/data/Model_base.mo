model Model_base
	input Real x(fixed=true);
	Real y;
	output Real z;

equation
	x = y + 0.01;
	der(y) = z;

end Model_base;