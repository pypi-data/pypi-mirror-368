model ModelOutOfSymbolicBounds
	parameter Real ymax = 25;
	Real x(max=ymax - 15, start=20);
equation
	der(x) = -x;
end ModelOutOfSymbolicBounds;
