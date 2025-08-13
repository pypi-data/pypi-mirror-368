model ModelAlgebraic
	Real y;
	input Real u(fixed=false);

equation
	y + u = 1.0;

end ModelAlgebraic;