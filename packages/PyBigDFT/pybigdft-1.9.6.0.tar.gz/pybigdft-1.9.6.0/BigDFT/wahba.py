"""
This module provides helper subroutines for performing rototranslations.

In particular, this module can solve Wahba's problem, which seeks to compute
the optimal rotation matrix between two sets of points.

https://en.wikipedia.org/wiki/Kabsch_algorithm
"""
import numpy as np


def apply_R(R: np.matrix, A: np.matrix) -> np.matrix:
    """
    Apply the rotation on the set of vectors A.

    Args:
      R (numpy.matrix): a rotation matrix.
      A (numpy.matrix): the set of vectors to rotate.

    Returns:
      (numpy.matrix): the set of vectors, rotated by the matrix.
    """
    A2 = R*A.T
    A2 = A2.T
    return A2


# ideally returns np.matrix, but np.tile returns np.ndarray
def apply_t(t: np.matrix, A: np.matrix) -> np.ndarray:
    """
    Apply a translation on the set of vectors A.

    Args:
      t (numpy.matrix): a translation matrix.
      A (numpy.matrix): the set of vectors to translate.

    Returns:
      (numpy.ndarray): the set of vectors, translated by the matrix.
    """
    n = A.shape[0]

    return A + np.tile(t, (1, n)).T


def apply_Rt(R: np.matrix, t: np.matrix, A: np.matrix) -> np.ndarray:
    """
    Rotate the element and apply the translation on the rotated vector.

    Args:
      R (numpy.matrix): a rotation matrix.
      t (numpy.matrix): a translation matrix.
      A (numpy.matrix): the set of vectors to translate.

    Returns:
      (numpy.matrix): the set of vectors, rototranslated.
    """
    RA = apply_R(R, A)
    return apply_t(t, RA)


def rigid_transform_3D(A: np.matrix, B: np.matrix, verbose: bool = False) -> tuple[np.matrix, np.matrix, float]:
    """
    Find the transformation R and t such that R*A + t ~= B, with an error
    quantified by J.

    Args:
      A (numpy.matrix): an NX3 matrix of points.
      B (numpy.matrix): a second NX3 matrix of points.
      verbose (bool): whether to be verbose during the calculation.

    Returns:
      (numpy.matrix): 3x3 rotation matrix/
      (numpy.matrix): 3X1 column vector representing the translation.
      (float): a quantification of the error.
    """
    from futile.Utils import write as safe_print

    assert len(A) == len(B)

    N = A.shape[0]  # total points

    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)

    # print 'centre',centroid_A,centroid_B
    # centre the points
    AA = A - np.tile(centroid_A, (N, 1))
    BB = B - np.tile(centroid_B, (N, 1))

    # dot is matrix multiplication for array
    H = np.transpose(AA) * BB

    # print 'H',H

    U, S, Vt = np.linalg.svd(H)

    R = Vt.T * U.T

    # special reflection case
    if np.linalg.det(R) < 0:
        if verbose:
            safe_print("#Reflection detected")
        Vt[2, :] *= -1
        R = Vt.T * U.T

    t = -R*centroid_A.T + centroid_B.T

    # print t

    # identify also the accuracy of wahba
    A2 = R*A.T + np.tile(t, (1, N))
    A2 = A2.T

    # Find the error
    err = A2 - B

    err = np.multiply(err, err)
    err = sum(err)
    rmse = np.sqrt(err/N)

    return R, t, rmse


def interpolate_points(A: np.matrix, B: np.matrix, steps: int, extrapolation_steps: int = 0) -> list:
    """
    Given a set of points A and B, this generates a list of point sets
    that interpolate between A and B in a specified number of steps.

    Args:
      A (numpy.matrix): an NX3 matrix of points.
      B (numpy.matrix): a second NX3 matrix of points.
      steps (int): the number of steps to take between A and B.
      extrapolation_steps (int): optionally, we can extrapolate a number of
        steps beyond B on the same trajectory.

    Returns:
      (list): a list of points interpolating between A and B including
      A and B.
    """
    from scipy.linalg import funm
    from copy import deepcopy
    R, t, rmse = rigid_transform_3D(A, B)

    if steps < 0:
        raise ValueError("Steps must be greater than or equal to zero.")

    # Scale the rotation
    R = funm(R, lambda x: x**(1.0/(steps+1)))

    # Apply each rotation.
    point_list = [deepcopy(A)]
    for i in range(1, steps+extrapolation_steps+2):
        new_point = deepcopy(point_list[-1])

        centroid = np.mean(new_point, axis=0)
        centroid = centroid.T

        new_point = apply_t(-1.0*centroid, new_point)
        new_point = apply_R(R, new_point)
        new_point = apply_t(centroid, new_point)

        point_list.append(new_point)

    # Compute a new translation matrix between the last two points.
    R, t, rmse = rigid_transform_3D(point_list[steps+1], B)
    t = 1.0/(steps+1) * t

    # Apply each translation.
    for i in range(1, steps+extrapolation_steps+2):
        point_list[i] = apply_t(i*t, point_list[i])

    # In order to remove any noise from the extrapolation, we copy
    # the points B at the end of the interpolation.
    point_list[steps+1] = deepcopy(B)

    return point_list


# Test with random data
if __name__ == '__main__':
    from futile.Utils import write as safe_print

    # Random rotation and translation
    R = np.matrix(np.random.rand(3, 3), copy=False)
    t = np.matrix(np.random.rand(3, 1), copy=False)

    # make R a proper rotation matrix, force orthonormal
    U, S, Vt = np.linalg.svd(R)
    R = U*Vt

    # remove reflection
    if np.linalg.det(R) < 0:
        Vt[2, :] *= -1
        R = U*Vt

    # number of points
    n = 6

    A = np.matrix(np.random.rand(n, 3), copy=False)
    B = R*A.T + np.tile(t, (1, n))
    B = B.T

    # recover the transformation
    ret_R, ret_t, ret_rmse = rigid_transform_3D(A, B)

    A2 = (ret_R*A.T) + np.tile(ret_t, (1, n))
    A2 = A2.T

    # Find the error
    err = A2 - B

    err = np.multiply(err, err)
    err = sum(err)
    rmse = np.sqrt(err/n)

    safe_print("Points A")
    safe_print(A)
    safe_print("")

    safe_print("Points B")
    safe_print(B)
    safe_print("")

    safe_print("Rotation")
    safe_print(R)
    safe_print("")

    safe_print("Translation")
    safe_print(t)
    safe_print("")

    safe_print("RMSE:", rmse)
    safe_print("If RMSE is near zero, the function is correct!")
