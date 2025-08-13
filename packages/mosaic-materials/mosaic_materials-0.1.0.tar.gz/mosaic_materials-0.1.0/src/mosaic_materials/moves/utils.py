from ctypes import Array, c_int

import numpy as np
import numpy.typing as npt
from numba import njit


def ids2cids(ids: list[int]) -> Array[c_int]:
    """Convert a list of integers to a ctypes array of c_int."""

    lenids = len(ids)
    cids = (lenids * c_int)()
    for i in range(lenids):
        cids[i] = ids[i]

    return cids


@njit(fastmath=True)
def unit_vector(vector: np.ndarray) -> np.ndarray:
    """
    Normalise a 1x3 vector to a unit vector.

    Parameters:
    ----------
    v : np.ndarray
        Input vector of shape (3,).

    Returns:
    -------
    np.ndarray
        Normalized unit vector of shape (3,).
    """
    return vector / np.sqrt(np.sum(np.square(vector)))


@njit(fastmath=True)
def random_vector(rand1: float, rand2: float) -> npt.NDArray[np.floating]:
    """Generate a random unit vector using two random numbers."""

    phi = rand1 * 2 * np.pi
    z = rand2 * 2 - 1

    z2 = z * z
    x = np.sqrt(1 - z2) * np.cos(phi)
    y = np.sqrt(1 - z2) * np.sin(phi)

    return np.array([x, y, z])


@njit
def rodrigues(
    a: npt.NDArray[np.floating], b: npt.NDArray[np.floating], theta: float
) -> npt.NDArray[np.floating]:
    """
    Apply Rodrigues' rotation formula to rotate a vector about another vector.

    Parameters:
    ----------
    a
        The vector to rotate of shape (3,).
    b
        The rotation axis vector of shape (3,). Must be a unit vector.
    theta
        The rotation angle in radians.

    Returns:
    -------
    The rotated vector of shape (3,).
    """

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    term1 = a * cos_theta
    term2 = np.cross(b, a) * sin_theta
    term3 = b * np.dot(b, a) * (1 - cos_theta)

    return term1 + term2 + term3


@njit(fastmath=True)
def _rotate_cluster_inplace(
    pos_old: np.ndarray,  # float64[:,3]
    img_old: np.ndarray,  # int32[:,3]
    L: np.ndarray,  # float64[3]
    axis: np.ndarray,  # float64[3], must be unit‐length
    theta: float,  # radians
    pos_new: np.ndarray,  # float64[:,3], same shape as pos_old
    img_new: np.ndarray,  # int32[:,3], same shape as img_old
) -> None:
    n = pos_old.shape[0]

    # --- 1) compute center‐of‐mass in absolute coords ---
    com0 = 0.0
    com1 = 0.0
    com2 = 0.0
    for i in range(n):
        com0 += pos_old[i, 0] + img_old[i, 0] * L[0]
        com1 += pos_old[i, 1] + img_old[i, 1] * L[1]
        com2 += pos_old[i, 2] + img_old[i, 2] * L[2]

    com0 /= n
    com1 /= n
    com2 /= n

    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    one_minus_cos = 1.0 - cos_t

    b0 = axis[0]
    b1 = axis[1]
    b2 = axis[2]

    # --- 2) for each atom, rotate and re‐wrap ---
    for i in range(n):
        # absolute old
        a0 = pos_old[i, 0] + img_old[i, 0] * L[0]
        a1 = pos_old[i, 1] + img_old[i, 1] * L[1]
        a2 = pos_old[i, 2] + img_old[i, 2] * L[2]

        # relative to COM
        v0_0 = a0 - com0
        v0_1 = a1 - com1
        v0_2 = a2 - com2

        # cross b × v0
        cx = b1 * v0_2 - b2 * v0_1
        cy = b2 * v0_0 - b0 * v0_2
        cz = b0 * v0_1 - b1 * v0_0

        # dot b · v0
        dot = b0 * v0_0 + b1 * v0_1 + b2 * v0_2

        # Rodrigues: r = v0*cosθ + (b×v0)*sinθ + b*(b·v0)*(1−cosθ)
        r0_0 = v0_0 * cos_t
        r0_1 = v0_1 * cos_t
        r0_2 = v0_2 * cos_t

        r1_0 = cx * sin_t
        r1_1 = cy * sin_t
        r1_2 = cz * sin_t

        tmp = dot * one_minus_cos
        r2_0 = b0 * tmp
        r2_1 = b1 * tmp
        r2_2 = b2 * tmp

        rot0 = r0_0 + r1_0 + r2_0
        rot1 = r0_1 + r1_1 + r2_1
        rot2 = r0_2 + r1_2 + r2_2

        # back to absolute & wrap
        abs0 = rot0 + com0
        abs1 = rot1 + com1
        abs2 = rot2 + com2

        # new image tag & fractional position
        img_i0 = np.floor(abs0 / L[0])
        pos_i0 = abs0 - img_i0 * L[0]
        img_i1 = np.floor(abs1 / L[1])
        pos_i1 = abs1 - img_i1 * L[1]
        img_i2 = np.floor(abs2 / L[2])
        pos_i2 = abs2 - img_i2 * L[2]

        pos_new[i, 0] = pos_i0
        pos_new[i, 1] = pos_i1
        pos_new[i, 2] = pos_i2
        img_new[i, 0] = img_i0
        img_new[i, 1] = img_i1
        img_new[i, 2] = img_i2
