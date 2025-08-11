import numpy as np
from ._geometry import sort_hull_points


def compute_cone_hull_intersection(hull_points, all_points, cone, cone_bounds):
    """
    Compute the intersection of halfplanes whose normals lie within the cone.
    
    Parameters:
    -----------
    hull_points : np.ndarray
        Points of the standard convex hull, sorted counterclockwise
    all_points : np.ndarray
        All input points
    cone : np.ndarray
        Two direction vectors defining the cone boundaries
    cone_bounds : None, float, or array-like, optional
        Controls the bounding box used for cone hull computation:
        - None: Use default margin of 2.0 times the data range
        - float: Use this value as margin multiplier (e.g., 3.0 for 3x data range)
        - [x_min, x_max, y_min, y_max]: Explicit bounding box coordinates
        - [[x_min, y_min], [x_max, y_max]]: Alternative explicit bounds format
        
    Returns:
    --------
    cone_hull : np.ndarray
        Vertices of the halfplane intersection (clipped to bounds)
    """
    v1, v2 = cone[0], cone[1]
    
    # Normalize the cone vectors
    v1_norm = v1 / np.linalg.norm(v1)
    v2_norm = v2 / np.linalg.norm(v2)
    
    # Ensure cone vectors are in counterclockwise order
    if np.cross(v1_norm, v2_norm) < 0:
        v1_norm, v2_norm = v2_norm, v1_norm
    
    # Sort hull points in counterclockwise order
    hull_sorted = sort_hull_points(hull_points)
    
    # Find halfplanes whose normals lie within the cone
    valid_halfplanes = []
    
    for i in range(len(hull_sorted)):
        current_point = hull_sorted[i]
        next_point = hull_sorted[(i + 1) % len(hull_sorted)]
        
        edge_vec = next_point - current_point
        outward_normal = np.array([edge_vec[1], -edge_vec[0]])
        outward_normal = outward_normal / np.linalg.norm(outward_normal)
        
        # Check if the outward normal lies within the cone
        if is_vector_in_cone(outward_normal, v1_norm, v2_norm):
            # This halfplane should be included in the intersection
            # We want the halfplane that contains the original hull interior
            # So we use the INWARD normal
            inward_normal = -outward_normal
            
            # Halfplane equation: inward_normal · (x - point) >= 0
            # We store as (a, b, c) where ax + by + c >= 0
            a, b = inward_normal
            c = -np.dot(inward_normal, current_point)
            valid_halfplanes.append((a, b, c))
    
    # If no valid halfplanes, return the full bounding box
    if not valid_halfplanes:
        return intersect_halfplanes([], all_points, cone_bounds)
    
    # Compute the intersection of the valid halfplanes
    # Since this can be unbounded, we'll clip to a reasonable bounding box
    return intersect_halfplanes(valid_halfplanes, all_points, cone_bounds)


def intersect_halfplanes(halfplanes, all_points, cone_bounds):
    """
    Compute the intersection of halfplanes and return the vertices.
    
    Parameters:
    -----------
    halfplanes : list of tuples
        Each tuple is (a, b, c) representing the halfplane ax + by + c >= 0
    all_points : np.ndarray
        All input points (used to determine reasonable bounding box)
    cone_bounds : None, float, or array-like, optional
        Controls the bounding box used for cone hull computation:
        - None: Use default margin of 2.0 times the data range
        - float: Use this value as margin multiplier (e.g., 3.0 for 3x data range)
        - [x_min, x_max, y_min, y_max]: Explicit bounding box coordinates
        - [[x_min, y_min], [x_max, y_max]]: Alternative explicit bounds format
        
    Returns:
    --------
    vertices : np.ndarray
        Vertices of the intersection polygon
    """
    # Determine bounding box for clipping
    if cone_bounds is None:
        margin = 2.0
        x_min, x_max = all_points[:, 0].min(), all_points[:, 0].max()
        y_min, y_max = all_points[:, 1].min(), all_points[:, 1].max()
        
        x_range = x_max - x_min
        y_range = y_max - y_min
        
        x_min -= margin * x_range
        x_max += margin * x_range
        y_min -= margin * y_range
        y_max += margin * y_range
    elif isinstance(cone_bounds, (int, float)):
        margin = cone_bounds
        x_min, x_max = all_points[:, 0].min(), all_points[:, 0].max()
        y_min, y_max = all_points[:, 1].min(), all_points[:, 1].max()
        
        x_range = x_max - x_min
        y_range = y_max - y_min
        
        x_min -= margin * x_range
        x_max += margin * x_range
        y_min -= margin * y_range
        y_max += margin * y_range
    elif isinstance(cone_bounds, (list, np.ndarray)) and len(cone_bounds) == 4:
        x_min, x_max, y_min, y_max = cone_bounds
    elif isinstance(cone_bounds, (list, np.ndarray)) and len(cone_bounds) == 2 and len(cone_bounds[0]) == 2:
        x_min, y_min = cone_bounds[0]
        x_max, y_max = cone_bounds[1]
    else:
        raise ValueError("Invalid cone_bounds format. Expected None, float, [x_min, x_max, y_min, y_max], or [[x_min, y_min], [x_max, y_max]]")
    
    # Start with the bounding box as initial polygon
    # Box vertices in counterclockwise order
    current_polygon = np.array([
        [x_min, y_min],
        [x_max, y_min],
        [x_max, y_max],
        [x_min, y_max]
    ])
    
    # If no halfplanes, return the full bounding box
    if len(halfplanes) == 0:
        return current_polygon
    
    # Apply each halfplane constraint using Sutherland-Hodgman clipping
    for a, b, c in halfplanes:
        current_polygon = clip_polygon_by_halfplane(current_polygon, a, b, c)
        
        # If polygon becomes empty, return original points
        if len(current_polygon) == 0:
            return all_points
    
    return current_polygon


def clip_polygon_by_halfplane(polygon, a, b, c):
    """
    Clip a polygon by a halfplane using Sutherland-Hodgman algorithm.
    
    Parameters:
    -----------
    polygon : np.ndarray
        Vertices of the polygon
    a, b, c : float
        Halfplane equation: ax + by + c >= 0
        
    Returns:
    --------
    clipped_polygon : np.ndarray
        Vertices of the clipped polygon
    """
    if len(polygon) == 0:
        return polygon
    
    def is_inside(point):
        return a * point[0] + b * point[1] + c >= -1e-10
    
    def compute_intersection(p1, p2):
        # Find intersection of line p1-p2 with halfplane boundary ax + by + c = 0
        # Line: p1 + t*(p2-p1)
        # Substitute into ax + by + c = 0 and solve for t
        
        dx, dy = p2 - p1
        denominator = a * dx + b * dy
        
        if abs(denominator) < 1e-10:
            return p1  # Lines are parallel
        
        t = -(a * p1[0] + b * p1[1] + c) / denominator
        return p1 + t * (p2 - p1)
    
    if len(polygon) == 0:
        return np.array([])
    
    output_list = []
    
    for i in range(len(polygon)):
        current_vertex = polygon[i]
        previous_vertex = polygon[i - 1]
        
        if is_inside(current_vertex):
            if not is_inside(previous_vertex):
                # Entering the halfplane
                intersection = compute_intersection(previous_vertex, current_vertex)
                output_list.append(intersection)
            output_list.append(current_vertex)
        elif is_inside(previous_vertex):
            # Exiting the halfplane
            intersection = compute_intersection(previous_vertex, current_vertex)
            output_list.append(intersection)
    
    return np.array(output_list) if output_list else np.array([])


def is_vector_in_cone(vector, cone_v1, cone_v2):
    """
    Check if a vector lies within the cone defined by two boundary vectors.
    
    Parameters:
    -----------
    vector : np.ndarray
        Vector to test (should be normalized)
    cone_v1, cone_v2 : np.ndarray
        Normalized cone boundary vectors (assumed to be in counterclockwise order)
        
    Returns:
    --------
    bool
        True if vector is within the cone, False otherwise
    """
    # Use cross products to check if vector is between cone_v1 and cone_v2
    # Vector is inside cone if:
    # 1. cross(cone_v1, vector) >= 0 (vector is counterclockwise from cone_v1)
    # 2. cross(vector, cone_v2) >= 0 (vector is clockwise from cone_v2)
    
    cross1 = np.cross(cone_v1, vector)
    cross2 = np.cross(vector, cone_v2)
    
    # Allow small numerical tolerance
    tolerance = 1e-10
    return cross1 >= -tolerance and cross2 >= -tolerance 
