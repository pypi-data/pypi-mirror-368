model PIDController
  input Real state;
  parameter Real target_value;
  parameter Real P = 1.0;
  parameter Real I = 0.0;
  parameter Real D = 0.0;
  parameter Real feed_forward = 0.0;
  output Real control_action;
  Real _error;
  Real error_integral(nominal = 3600);
equation
  _error = target_value - state;
  der(error_integral) = _error;
  control_action = feed_forward + P * _error + I * error_integral + D * der(_error);
initial equation
  error_integral = 0.0;
end PIDController;