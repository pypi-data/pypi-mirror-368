model ModelWithZeroStart
	Real x(start=0);
equation
	der(x) = -x;
end ModelWithZeroStart;
