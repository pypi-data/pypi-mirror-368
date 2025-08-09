# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sys

import numpy as np

from TerraFrame.Utilities import Earth
from TerraFrame.Utilities import Time, Conversions
from TerraFrame.Utilities.Time.JulianDate import JulianDate


def r1(phi):
    """
    This function computes the R1 rotation matrix. As per Kaplan (2005), R1 is
    defined as:

    [A] rotation matrix to transform column 3-vectors from one cartesian
    coordinate system to another. Final system is formed by rotating original
    system about its own x-axis by angle phi (counterclockwise as viewed from
    the +x direction):

    Source:
    Kaplan, G. H., 2005, U.S. Naval Observatory Circular No. 179 (Washington:
    USNO), page xi

    :param phi: Rotation angle in radians
    :return: R1 matrix
    :type phi: float
    :rtype: np.ndarray
    """

    r = np.array([[1.0, 0.0, 0.0], [0.0, np.cos(phi), np.sin(phi)],
                  [0.0, -np.sin(phi), np.cos(phi)]])

    return r


def r2(theta):
    """
    This function computes the R2 rotation matrix. As per Kaplan (2005), R2 is
    defined as:

    [A] rotation matrix to transform column 3-vectors from one cartesian
    coordinate system to another. Final system is formed by rotating original
    system about its own y-axis by angle φ (counterclockwise as viewed from
    the +y direction):

    Source:
    Kaplan, G. H., 2005, U.S. Naval Observatory Circular No. 179 (Washington:
    USNO), page xi

    :param theta: Input rotation angle in radians
    :return: R2 matrix
    :type theta: float
    :rtype: np.ndarray
    """

    r = np.array([[np.cos(theta), 0.0, -np.sin(theta)], [0.0, 1.0, 0.0],
                  [np.sin(theta), 0.0, np.cos(theta)]])

    return r


def r3(psi):
    """
    This function computes the R3 rotation matrix. As per Kaplan (2005), R3 is
    defined as:

    [A] rotation matrix to transform column 3-vectors from one cartesian
    coordinate system to another. Final system is formed by rotating original
    system about its own z-axis by angle φ (counterclockwise as viewed from
    the +z direction):

    Source:
    Kaplan, G. H., 2005, U.S. Naval Observatory Circular No. 179 (Washington:
    USNO), page xi

    :param psi: Input rotation angle in radians
    :return: R3 matrix
    :type psi: float
    :rtype: np.ndarray
    """

    r = np.array(
        [[np.cos(psi), np.sin(psi), 0.0], [-np.sin(psi), np.cos(psi), 0.0],
         [0.0, 0.0, 1.0]])

    return r


def euler_angles_from_transformation(t_m):
    """
    This function takes a transformation matrix and calculates the corresponding
    Tait–Bryan angles, following z-y′-x″ (intrinsic rotations).

    The angles are technically Tait–Bryan angles but are often called Euler
    angles. This function has been named to align with common usage.

    The Tait–Bryan angles and ordering in this function align with common
    usage in navigation and engineering.

    :param t_m: Transformation matrix
    :return: Array of Tait–Bryan angles, ordered z-y′-x″ (yaw-pitch-roll)
    :type t_m: np.ndarray
    :rtype: np.ndarray
    """

    pitch = np.asin(-t_m[0, 2])
    yaw = np.atan2(t_m[0, 1], t_m[0, 0])
    roll = np.atan2(t_m[1, 2], t_m[2, 2])

    return np.array([yaw, pitch, roll])


def transformation_from_euler(yaw, pitch, roll):
    """
    This function takes in Tait–Bryan angles, following z-y′-x″
    (intrinsic rotations), and creates the corresponding transformation matrix.

    The angles are technically Tait–Bryan angles but are often called Euler
    angles. This function has been named to align with common usage.

    The Tait–Bryan angles and ordering in this function align with common
    usage in navigation and engineering.

    :param yaw: Yaw rotation angle in radians
    :param pitch: Pitch rotation angle in radians
    :param roll: Roll rotation angle in radians
    :return: Transformation matrix
    :type yaw: float
    :type pitch: float
    :type roll: float
    :rtype: np.ndarray
    """

    t_m = r3(yaw) @ r2(pitch) @ r1(roll)

    return t_m


def angle_and_axis_from_transformation(t_m):
    """
    This function takes in a transformation matrix and computes the
    corresponding angle and axis of rotation.

    :param t_m: Transformation matrix
    :return: angle and axis of rotation
    :type t_m: np.ndarray
    :rtype: tuple(float, np.ndarray)
    """

    angle = np.arccos((np.trace(t_m) - 1.0) / 2.0)

    # Avoid dividing by zero if rotation is effectively none.
    if abs(angle) < sys.float_info.epsilon:
        angle = 0.0
        axis = np.array([1.0, 0, 0])

        return angle, axis

    axis = np.array(
        (t_m[2, 1] - t_m[1, 2], t_m[0, 2] - t_m[2, 0], t_m[1, 0] - t_m[0, 1]))

    axis /= (2.0 * np.sin(angle))

    return angle, axis


def calculate_s_prime(time):
    """
    This function computes the Terrestrial Intermediate Origin (TIO) locator
    called s' (or s prime) per IERS Conventions (2010).

    Note that technically, per IERS Conventions (2010), the input time should
    be Barycentric Dynamical Time (TDB) but the difference between TDB and TT is
    already small. Additionally, we do not consider effects outside the
    Geocentric Celestial Reference System (GCRS) and the primary driver of the
    TDB vs TT difference is earth's mean anomaly in its orbit. The error from
    this simplication is less than a microarcsecond in nutation.

    :type time: JulianDate
    :param time: Terrestrial time measured in Julian centuries.
    :return: s prime
    :rtype: float
    """

    assert (time.time_scale == Time.TimeScales.TT)

    # This is an approximation good for the next century. See section 5.5.2 of
    # IERS Conventions (2010) for more context.
    s_prime = -47e-6 * float(time)

    s_prime = Conversions.arcsec_to_rad(s_prime)

    return s_prime


def cirs_to_gcrs(x, y, s):
    """
    This function computes the transformation matrix from the Celestial
    Intermediate Reference System (CIRS) to the Geocentric Celestial
    Reference System (GCRS) per IERS Conventions (2010).

    x and y are coordinates of the Celestial Intermediate Pole (CIP) and s is
    the Celestial Intermediate Origin (CIO) locator parameter which provides
    the position of the CIO on the equator of the CIP.

    :type x: float
    :type y: float
    :type s: float
    :param x: X coordinate of the CIP
    :param y: Y coordinate of the CIP
    :param s: CIO location parameter
    :return: CGRS to CIRS transformation matrix
    :rtype: np.ndarray
    """

    # This should never be true in reality
    assert (1.0 - x ** 2 - y ** 2 > 0.0)

    # e and d formulas from Capitaine (2003)
    e = np.atan2(y, x)
    d = np.atan2(np.sqrt(x ** 2 + y ** 2), np.sqrt(1 - x ** 2 - y ** 2))

    t_gc = r3(-e) @ r2(-d) @ r3(e) @ r3(s)

    return t_gc


def earth_rotation_matrix(time):
    """
    This function computes the earth rotation matrix at a given datetime in UT1.

    :param time: JulianDate in UT1
    :return: TIRS to ITRS transformation matrix
    :type time: JulianDate
    :rtype: np.ndarray
    """

    assert (time.time_scale == Time.TimeScales.UT1)

    era = Earth.earth_rotation_angle(time)

    r_era = r3(-era)

    return r_era


def itrs_to_tirs(pm_x, pm_y, sp):
    """
    This function computes the transformation matrix from the International
    Terrestrial Reference System (ITRS) to the Terrestrial Intermediate
    Reference System (TIRS) per IERS Conventions (2010).

    pm_x and pm_y are coordinates of polar motion and sp (s') is the
    the Terrestrial Intermediate Origin (TIO) locator parameter which provides
    the position of the TIO on the equator of the CIP.

    :type pm_x: float
    :type pm_y: float
    :type sp: float
    :param pm_x: Polar motion x coordinate
    :param pm_y: Polar motion y coordinate
    :param sp: TIO location parameter
    :return: TIRS to ITRS transformation matrix
    :rtype: np.ndarray
    """

    t_ti = (r3(-sp) @ r2(pm_x) @ r1(pm_y))

    return t_ti
