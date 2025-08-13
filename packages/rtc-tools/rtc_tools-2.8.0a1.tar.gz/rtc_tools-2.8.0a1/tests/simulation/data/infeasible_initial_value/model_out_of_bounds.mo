model ModelOutOfBounds
	Real x(max=10, start=20);
equation
	der(x) = -x;
end ModelOutOfBounds;
