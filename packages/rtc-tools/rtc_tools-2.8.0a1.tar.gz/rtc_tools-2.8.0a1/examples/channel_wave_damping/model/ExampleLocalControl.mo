model ExampleLocalControl
  extends Example;
  // Add PID Controllers that apply local control
  PIDController upstream_pid(
    state = dam_upstream.HQUp.H,
    target_value = 20.0,
    P = -200.0,
    I = -0.01,
    D = 0.0,
    feed_forward = 100.0,
    control_action = dam_upstream.Q
  );
  PIDController middle_pid(
    state = dam_middle.HQUp.H,
    target_value = 15.0,
    P = -200.0,
    I = -0.01,
    D = 0.0,
    feed_forward = 100.0,
    control_action = dam_middle.Q
  );
  output Modelica.Units.SI.VolumeFlowRate Q_dam_upstream = dam_upstream.Q;
  output Modelica.Units.SI.VolumeFlowRate Q_dam_middle = dam_middle.Q;
end ExampleLocalControl;