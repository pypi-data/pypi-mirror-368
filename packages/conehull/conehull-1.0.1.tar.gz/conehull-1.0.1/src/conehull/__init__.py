"""
ConeHull: A 2D convex hull algorithm with directional cone constraints.

This package implements the conehull function. 
It takes in a set of 2D points and two vectors specifying a convex cone.
It returns the hull of the points obtained by intersecting 
over all halfplanes with normals lying in the cone.

Main Functions:
--------------
conehull : Compute convex hull or cone hull

Visualization Functions (import from conehull.view):
---------------------------------------------------
conehull_animated : Auto-playing animation
conehull_step_by_step : Manual step-by-step viewer  
conehull_jupyter : Interactive Jupyter widget
plot_hull : Simple hull visualization
plot_cone_comparison : Compare standard vs cone hull
"""

from ._conehull import conehull

__all__ = [
    'conehull',
]

# Package metadata
__version__ = "1.0.1"
__author__ = "Tryggvi Kalman Jónsson"
__description__ = "2D convex hull algorithm with directional cone constraints and visualization tools" 
