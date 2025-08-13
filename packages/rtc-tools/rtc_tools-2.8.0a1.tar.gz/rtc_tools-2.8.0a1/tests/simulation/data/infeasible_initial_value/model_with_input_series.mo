model ModelWithInputSeries
	Real x;
	input Real f_in;
equation
	der(x) = -x + f_in;
end ModelWithInputSeries;
