import numpy as np


def sort_hull_points(hull_points):
    """
    Sort hull points in counterclockwise order around their centroid.
    This ensures proper convex polygon visualization without self-intersections.
    """
    if len(hull_points) < 3:
        return np.array(hull_points)
    
    hull_points = np.array(hull_points)
    
    centroid = np.mean(hull_points, axis=0)
    vectors = hull_points - centroid
    angles = np.arctan2(vectors[:, 1], vectors[:, 0])
    sorted_indices = np.argsort(angles)
    
    return hull_points[sorted_indices]


def find_farthest_point(points, line_start, line_end):
    """Find the point farthest from the line segment defined by line_start and line_end."""
    if len(points) == 0:
        return None, 0

    line_vec = line_end - line_start
    max_dist = 0
    farthest_point = None

    for point in points:
        point_vec = point - line_start

        # determinant of the 2x2 matrix [line_vec, point_vec]
        det = np.linalg.det(np.column_stack((line_vec, point_vec)))
        dist = abs(det) / np.linalg.norm(line_vec)

        if dist > max_dist:
            max_dist = dist
            farthest_point = point

    return farthest_point, max_dist


def points_on_left(points, a, b):
    """Returns points strictly to the left of ab"""
    ab = b - a
    left = []
    for p in points:
        det = np.linalg.det(np.column_stack((ab, p - a)))
        if det > 1e-12:  # Use a small epsilon for numerical stability
            left.append(p)
    return np.array(left) 
