import numpy as np
from scipy.spatial.transform import Rotation


def get_rotation_matrix(vec0, vec1):
    """
    Get the matrix required to rotate vec0 to vec1
    """
    vec0 = np.reshape(vec0, (1, -1))
    vec1 = np.reshape(vec1, (1, -1))
    r = Rotation.align_vectors(vec0, vec1)
    return r[0].as_matrix()


def get_three_point_normal(p0, p1, p2):
    """
    Get the normal to the plane given by three points
    """
    direction = np.cross(p1 - p0, p2 - p0)
    return direction / np.linalg.norm(direction)


def segment_contains_point(v0, v1, p, tol: float = 1.0e-4) -> bool:
    """
    True if the line segment defined by v0 and v1 contains point p
    """

    dv0v1 = np.linalg.norm(v1 - v0)
    dv0p = np.linalg.norm(v0 - p)
    dv1p = np.linalg.norm(v1 - p)
    return np.abs(dv0p + dv1p - dv0v1) < tol


def get_point_distance(p0, p1) -> float:
    """
    Return the distance between two points
    """
    return float(np.linalg.norm(p1 - p0))


def get_segment_distance(v0, v1, p) -> float:
    """
    Return the distance between the line segment v0-v1 and the point p
    """

    pv0 = p - v0
    v1v0 = v1 - v0
    side0 = np.dot(pv0, v1v0)
    if side0 < 0.0:
        return float(np.linalg.norm(pv0))
    pv1 = p - v1
    side1 = np.dot(pv1, v0 - v1)
    if side1 < 0.0:
        return float(np.linalg.norm(pv1))
    length = np.linalg.norm(v1v0)
    proj = (side1 * v0 + side0 * v1) / (length * length)
    return float(np.linalg.norm(p - proj))
