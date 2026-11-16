"""Control pipeline from blade profile measurements to Arduino commands."""

from pathlib import Path


def measure_blade_height(csv_path: Path) -> float:
    """Read the blade profile CSV and return the overall blade height in inches.

    Measure from the bottom of the strip to the top of the blade using the
    profiler's coordinate conventions.
    """
    pass


def calculate_height_correction(
    measured_height_in: float, target_height_in: float = 0.600
) -> float:
    """Return the signed change in blade height to request for future blades.

    A positive value requests a taller blade. A negative value requests a
    shorter blade. Zero means hold the wheel position. The chosen controller
    will determine how to use earlier readings and when to issue corrections.
    """
    pass


def calculate_motor_steps(height_correction_in: float) -> dict[str, int]:
    """Convert a requested height change into signed step counts by motor.

    Use the apparatus kinematics and motor calibration to map the desired
    change in blade height to wheel motion and then to whole motor steps.
    """
    pass


def package_arduino_command(motor_steps: dict[str, int]) -> bytes:
    """Encode the motor IDs and signed step counts for the Arduino firmware.

    Return the complete command as bytes for the caller to send.
    """
    pass


def process_csv(csv_path: Path, target_height_in: float = 0.600) -> bytes:
    """Run the pipeline for one blade profile CSV.

    Measure height, calculate the requested correction, convert it to motor
    steps, and return the packaged Arduino command.
    """
    pass
