# Strip grinder control software

The control software reads a CSV containing `[x, z]` points for the blade's top and side profiles. It uses the measured height to calculate a grinding wheel adjustment for future blades.

The pipeline lives in `src/strip_grinder.py`. Its functions are documented stubs.

1. `measure_blade_height` reads the CSV and returns the height in inches from the bottom of the strip to the top of the blade.
2. `calculate_height_correction` compares the measurement with the fixed 0.600 in target and returns the requested change in blade height in inches.
3. `calculate_motor_steps` uses the apparatus kinematics and motor calibration to convert that correction into signed step counts for the adjustment motors.
4. `package_arduino_command` turns those step counts into bytes using the command format agreed with the Arduino firmware.

`process_csv` is the intended entry point and returns the packaged command. The profiler CSV layout, controller algorithm, apparatus kinematics, motor calibration, and Arduino message format are design inputs to settle before implementation.
