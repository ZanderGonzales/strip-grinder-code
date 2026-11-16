import numpy as np
from scipy.optimize import root
import sys
from scipy.optimize import least_squares


def equations(x, r1, theta1, r3, theta5, rc, delta, thetaw,
              ra, thetaa, rb, thetab, rg_vec, rw):
    """
    Defines the four scalar equations representing two vector loop-closure
    equations for the linkage.

    The four unknowns are:
        theta2 : Angular position of link 2 (rad)
        theta3 : Angular position of link 3 (rad)
        r5     : Length of link 5 (in)
        r2     : Length of link 2 (in)

    Complex numbers are used to represent 2D vectors:
        r * exp(i * theta) = r*cos(theta) + i*r*sin(theta)

    Each complex loop equation produces two scalar equations:
        Real component -> X-direction closure
        Imaginary component -> Y-direction closure

    Returns four residuals that should all approach zero when both
    vector loop equations are satisfied.
    """

    # Unpack the optimization variables in the order expected by the solver.
    theta2, theta3, r5, r2 = x

    # Calculate the angular position of link C relative to link 3.
    # Delta represents the fixed angular offset between the two links.
    thetac = theta3 + np.deg2rad(180) - delta

    # Loop 1: Vector closure equation.
    # The sum of the vectors on one side of the loop must equal the other.
    eq1 = r2*np.exp(1j*theta2) - r3*np.exp(1j*theta3) - r1*np.exp(1j*theta1)

    # Loop 2: Vector closure equation.
    # Accounts for links 5, 2, C, W, A, and B, relative to the known
    # ground/reference vector rg_vec.
    eq2 = (
        r5*np.exp(1j*theta5)
        + r2*np.exp(1j*theta2)
        + rc*np.exp(1j*thetac)
        + rw*np.exp(1j*thetaw)
        + ra*np.exp(1j*thetaa)
        + rb*np.exp(1j*thetab)
        - rg_vec
    )

    # Separate the two complex equations into four real-valued residuals.
    # least_squares requires a real-valued residual vector.
    return [
        eq1.real,
        eq1.imag,
        eq2.real,
        eq2.imag
    ]


# ---------------------------------------------------------------------
# INPUT PARAMETERS
# ---------------------------------------------------------------------

# Known length of the W vector (in).
rw = 4.7

# Geometric measurements obtained from Brian's 3D scan (in).
grind_height = 0.056534
thickness = 0.034252


# ---------------------------------------------------------------------
# KNOWN LINKAGE GEOMETRY
# ---------------------------------------------------------------------

# Known link lengths, angular positions, and geometric offsets.
# See artifact 46 for the physical meaning and reference locations
# of the individual vectors.

r1 = 8.25
theta1 = np.deg2rad(180)

r3 = 7.0
theta5 = np.deg2rad(180)

rc = 6.0
delta = np.deg2rad(44.9)

# Calculate the angular orientation of vector W.
# atan2 accounts for the geometry defined by the grind height and thickness.
thetaw = np.deg2rad(270) - np.atan2(2*grind_height, thickness)

# Vector A: Length and angular orientation.
ra = thickness / 4
thetaa = np.deg2rad(0)

# Vector B: Length and angular orientation.
rb = 1.6 - grind_height / 2
thetab = np.deg2rad(270)

# Known ground/reference vector represented in complex form:
# Real component = X position; imaginary component = Y position.
rg_vec = -15 + 1j*2.11


# ---------------------------------------------------------------------
# INITIAL GUESSES FOR UNKNOWN VARIABLES
# ---------------------------------------------------------------------

# The nonlinear solver requires an initial estimate for each unknown.
# These values should be reasonably close to the expected physical
# configuration to help the solver converge to the desired solution.

theta2_guess = np.deg2rad(121)
theta3_guess = np.deg2rad(33)
r5_guess = 2.12
r2_guess = 4.59

# Initial guess vector.
# Variable order must match the unpacking in equations().
x0 = [theta2_guess, theta3_guess, r5_guess, r2_guess]


# ---------------------------------------------------------------------
# VARIABLE BOUNDS
# ---------------------------------------------------------------------

# Define allowable ranges for each optimization variable.
# Variable order: theta2, theta3, r5, r2

lower_bounds = [
    0,                  # theta2 >= 0 radians
    0,                  # theta3 >= 0 radians
    0,                  # r5 > 0
    0                   # r2 > 0
]

upper_bounds = [
    2*np.pi,            # theta2 <= 360 degrees
    2*np.pi,            # theta3 <= 360 degrees
    np.inf,             # No upper limit on r5
    np.inf              # No upper limit on r2
]


# ---------------------------------------------------------------------
# NONLINEAR LEAST-SQUARES SOLUTION
# ---------------------------------------------------------------------

# Solve the four loop-closure equations simultaneously.
#
# least_squares minimizes the sum of the squared residuals rather than
# requiring an exact zero at every iteration.
#
# x_scale='jac' scales the optimization variables based on the Jacobian,
# which can improve convergence when variables have different magnitudes
# or sensitivities.

solution = least_squares(
    equations,
    x0,
    args=(r1, theta1, r3, theta5, rc, delta, thetaw,
          ra, thetaa, rb, thetab, rg_vec, rw),
    bounds=(lower_bounds, upper_bounds),
    x_scale='jac'
)


# ---------------------------------------------------------------------
# SOLUTION VALIDATION AND OUTPUT
# ---------------------------------------------------------------------

# Check both:
# 1. Whether the solver reports successful termination.
# 2. Whether the combined residual is sufficiently small.
#
# A successful termination alone does not guarantee that the loop
# equations have been satisfied to an acceptable numerical tolerance.

if solution.success and np.linalg.norm(solution.fun) < 1e-6:

    # Extract the optimized values in the original variable order.
    theta2, theta3, r5, r2 = solution.x

    # Convert angular results from radians to degrees for readability.
    # Link lengths are reported in inches.
    print(f"theta2 = {np.rad2deg(theta2):.2f} deg")
    print(f"theta3 = {np.rad2deg(theta3):.2f} deg")
    print(f"r5 = {r5:.2f} in")
    print(f"r2 = {r2:.2f} in")

else:
    # Report the solver's termination message and the remaining
    # combined loop-closure error.
    print("Solver failed:", solution.message)
    print("Residual:", np.linalg.norm(solution.fun))


# Exit prevents the alternative root solver below from executing.
sys.exit()


# ---------------------------------------------------------------------
# ALTERNATIVE SOLVER: ROOT
# ---------------------------------------------------------------------

# This section provides an alternative approach using scipy.optimize.root.
#
# Unlike least_squares, root attempts to directly find a point where
# all four equations equal zero. It does not enforce the variable bounds
# defined above.

solution = root(
    equations,
    x0,
    args=(r1, theta1, r3, theta5, rc, delta, thetaw,
          ra, thetaa, rb, thetab, rg_vec, rw)
)


# Validate the root solution using the same convergence criteria.
if solution.success and np.linalg.norm(solution.fun) < 1e-6:

    theta2, theta3, r5, r2 = solution.x

    # Convert angles to degrees and wrap them into the 0-360 degree range.
    print(f"theta2 = {np.rad2deg(theta2)%360:.2f} deg")
    print(f"theta3 = {np.rad2deg(theta3)%360:.2f} deg")
    print(f"r5 = {r5:.2f} in")
    print(f"r2 = {r2:.2f} in")

else:
    print("Solver failed:", solution.message)


# Report the closure error for each individual vector loop.
# Each residual is the magnitude of the remaining unclosed vector (in).
print("Loop 1 residual:", np.linalg.norm(solution.fun[:2]), "in")
print("Loop 2 residual:", np.linalg.norm(solution.fun[2:]), "in")