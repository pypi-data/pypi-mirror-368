model ModelWithBounds
	Real x(max=10);
equation
	der(x) = -x;
end ModelWithBounds;
