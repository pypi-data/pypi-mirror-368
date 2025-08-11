import numpy as np
from scipy.spatial import ConvexHull
from ._geometry import find_farthest_point, points_on_left
from ._cone_intersection import compute_cone_hull_intersection


def quickhull_rec(points, a, b, frame_callback=None):
    """Recursive step of the quickhull algorithm."""
    if len(points) == 0:
        return [a, b]
    
    farthest, _ = find_farthest_point(points, a, b)
    
    if frame_callback:
        frame_callback('farthest_found', {
            'points_subset': points, 
            'line_segment': [a, b], 
            'farthest_point': farthest
        })
    
    left1 = points_on_left(points, a, farthest)
    left2 = points_on_left(points, farthest, b)
    
    if frame_callback:
        frame_callback('point_added', {
            'farthest_point': farthest,
            'left1': left1,
            'left2': left2
        })
    
    hull1 = quickhull_rec(left1, a, farthest, frame_callback)
    hull2 = quickhull_rec(left2, farthest, b, frame_callback)
    # Remove duplicate farthest point
    return hull1[:-1] + hull2


def quickhull(points, frame_callback=None):
    """
    Compute the standard convex hull of a set of points using the QuickHull algorithm.
    
    Parameters:
    -----------
    points : array-like
        Input points for convex hull computation
    frame_callback : callable, optional
        Callback function for instrumentation/animation. Called as:
        frame_callback(event_type, event_data)
        
    Returns:
    --------
    hull : np.ndarray
        Convex hull points
    """
    if len(points) < 3:
        return points
    
    points = np.array(points)
    
    # Use fast SciPy implementation when no animation callback is needed
    if frame_callback is None:
        hull = ConvexHull(points)
        # Return hull vertices in order
        return points[hull.vertices]
    
    # Use custom implementation for animation support
    if frame_callback:
        frame_callback('algorithm_start', {
            'points': points, 
            'cone': None, 
            'algorithm': 'QuickHull'
        })
    
    leftmost = points[np.argmin(points[:, 0])]
    rightmost = points[np.argmax(points[:, 0])]
    extreme_a, extreme_b = leftmost, rightmost
    
    if frame_callback:
        frame_callback('extremes_found', {
            'leftmost': leftmost, 
            'rightmost': rightmost
        })
    
    above = points_on_left(points, extreme_a, extreme_b)
    below = points_on_left(points, extreme_b, extreme_a)

    if frame_callback:
        frame_callback('initial_split', {
            'baseline': [extreme_a, extreme_b],
            'above': above,
            'below': below
        })

    upper = quickhull_rec(above, extreme_a, extreme_b, frame_callback)
    lower = quickhull_rec(below, extreme_b, extreme_a, frame_callback)

    # Remove duplicate endpoints
    hull = upper[:-1] + lower[:-1]
    # Remove duplicates (in case of collinear points)
    unique_hull = []
    for p in hull:
        if not any(np.allclose(p, q) for q in unique_hull):
            unique_hull.append(p)

    result_hull = np.array(unique_hull)
    
    if frame_callback:
        frame_callback('standard_hull_complete', {'hull': result_hull})
    
    return result_hull


def conehull(points, cone=None, cone_bounds=None, frame_callback=None):
    """
    Compute the convex hull or cone hull of a set of points.
    
    Parameters:
    -----------
    points : array-like
        Input points for convex hull computation
    cone : None or array-like of shape (2, 2), optional
        If None, uses standard QuickHull algorithm with leftmost/rightmost points.
        If provided, should be two vectors [v1, v2] defining a directional cone.
        The algorithm will compute the intersection of all halfplanes whose 
        outward normals lie between the cone vectors. This creates a larger
        (unbounded) region that contains the original convex hull.
    cone_bounds : None, float, or array-like, optional
        Controls the bounding box used for cone hull computation:
        - None: Use default margin of 2 times the data range
        - float: Use this value as margin multiplier (e.g., 3.0 for 3x data range)
        - [x_min, x_max, y_min, y_max]: Explicit bounding box coordinates
        - [[x_min, y_min], [x_max, y_max]]: Alternative explicit bounds format
    frame_callback : callable, optional
        Callback function for instrumentation/animation. Called as:
        frame_callback(event_type, event_data)
        
    Returns:
    --------
    hull : np.ndarray
        For standard hull: convex hull points
        For cone hull: vertices of the halfplane intersection (clipped to bounds)
    """
    if cone is None:
        # Standard convex hull - delegate to quickhull
        return quickhull(points, frame_callback=frame_callback)
    
    if len(points) < 3:
        return points
    
    points = np.array(points)
    cone = np.array(cone)
    if cone.shape != (2, 2):
        raise ValueError("Cone must be two 2D vectors: shape (2, 2)")
    
    if frame_callback:
        frame_callback('algorithm_start', {
            'points': points, 
            'cone': cone, 
            'algorithm': 'Cone-QuickHull'
        })
    
    standard_hull = quickhull(points, frame_callback=frame_callback)
    if len(standard_hull) < 3:
        return standard_hull
    
    # Apply cone constraints: find intersection of halfplanes with normals in cone
    cone_hull = compute_cone_hull_intersection(standard_hull, points, cone, cone_bounds)
    
    if frame_callback:
        frame_callback('cone_processing_start', {
            'standard_hull': standard_hull,
            'cone_hull': cone_hull,
            'cone_vectors': cone
        })
    
    if frame_callback:
        frame_callback('cone_hull_complete', {'cone_hull': cone_hull})
    
    return cone_hull

 
