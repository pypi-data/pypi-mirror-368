model ModelWithStart
	Real x(start=20);
equation
	der(x) = -x;
end ModelWithStart;
