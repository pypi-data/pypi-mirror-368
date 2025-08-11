import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from ._geometry import find_farthest_point, points_on_left, sort_hull_points
from ._conehull import quickhull, conehull
from ._cone_intersection import compute_cone_hull_intersection


class FrameCollector:
    """
    Collects animation frames by listening to algorithm events.
    This eliminates the need to duplicate algorithm logic.
    """
    
    def __init__(self, points, cone):
        self.frames = []
        self.points = np.array(points)
        self.cone = cone
        self.step_counter = 0
        self.current_hull_points = []
        self.algorithm_name = "Cone-QuickHull" if cone is not None else "QuickHull"
        
    def __call__(self, event_type, event_data):
        """Callback function that receives algorithm events and generates frames."""
        
        if event_type == 'algorithm_start':
            self._handle_algorithm_start(event_data)
            
        elif event_type == 'extremes_found':
            self._handle_extremes_found(event_data)
            
        elif event_type == 'initial_split':
            self._handle_initial_split(event_data)
            
        elif event_type == 'farthest_found':
            self._handle_farthest_found(event_data)
            
        elif event_type == 'point_added':
            self._handle_point_added(event_data)
            
        elif event_type == 'standard_hull_complete':
            self._handle_standard_hull_complete(event_data)
            
        elif event_type == 'cone_processing_start':
            self._handle_cone_processing_start(event_data)
            
        elif event_type == 'cone_hull_complete':
            self._handle_cone_hull_complete(event_data)
    
    def _handle_algorithm_start(self, data):
        """Handle algorithm start event."""
        if self.cone is not None:
            # Single comprehensive initial frame for cone mode
            self.frames.append({
                'all_points': self.points.copy(),
                'active_points': self.points.copy(),
                'current_line': None,
                'farthest_point': None,
                'hull_points': [],
                'hull_edges': [],
                'cone_vectors': self.cone.copy(),
                'title': f'Step 1: Initial setup ({self.algorithm_name})',
                'description': f'Starting with {len(self.points)} points. Cone vectors shown - only halfplanes with normals in cone will be included.'
            })
        else:
            # Standard mode initial frame
            self.frames.append({
                'all_points': self.points.copy(),
                'active_points': self.points.copy(),
                'current_line': None,
                'farthest_point': None,
                'hull_points': [],
                'hull_edges': [],
                'cone_vectors': None,
                'title': f'Step 1: Initial point set ({self.algorithm_name})',
                'description': f'Starting with {len(self.points)} points'
            })
    
    def _handle_extremes_found(self, data):
        """Handle extreme points found event."""
        self.step_counter += 1
        leftmost, rightmost = data['leftmost'], data['rightmost']
        self.current_hull_points = [leftmost, rightmost]
        
        self.frames.append({
            'all_points': self.points.copy(),
            'active_points': self.points.copy(),
            'current_line': None,
            'farthest_point': None,
            'hull_points': [leftmost, rightmost],
            'hull_edges': [],
            'cone_vectors': self.cone.copy() if self.cone is not None else None,
            'title': f'Step {self.step_counter + 1}: Find extreme points',
            'description': 'Leftmost and rightmost points found'
        })
    
    def _handle_initial_split(self, data):
        """Handle initial split event."""
        self.step_counter += 1
        baseline = data['baseline']
        
        self.frames.append({
            'all_points': self.points.copy(),
            'active_points': self.points.copy(),
            'current_line': baseline,
            'farthest_point': None,
            'hull_points': self.current_hull_points.copy(),
            'hull_edges': [],
            'cone_vectors': self.cone.copy() if self.cone is not None else None,
            'title': f'Step {self.step_counter + 1}: Draw initial baseline',
            'description': 'Divide points into upper and lower sets'
        })
    
    def _handle_farthest_found(self, data):
        """Handle farthest point found event."""
        self.step_counter += 1
        points_subset = data['points_subset']
        line_segment = data['line_segment']
        farthest_point = data['farthest_point']
        
        # Determine side name based on context
        side_name = "upper" if len(points_subset) > 0 else "side"
        
        self.frames.append({
            'all_points': self.points.copy(),
            'active_points': points_subset.copy(),
            'current_line': line_segment,
            'farthest_point': farthest_point,
            'hull_points': self.current_hull_points.copy(),
            'hull_edges': self.current_hull_points.copy(),
            'cone_vectors': self.cone.copy() if self.cone is not None else None,
            'title': f'Step {self.step_counter + 1}: Process {side_name} side',
            'description': f'Find farthest point from line segment ({len(points_subset)} candidates)'
        })
    
    def _handle_point_added(self, data):
        """Handle point added to hull event."""
        self.step_counter += 1
        farthest_point = data['farthest_point']
        
        # Add to hull points if not already present
        if not any(np.allclose(farthest_point, h) for h in self.current_hull_points):
            self.current_hull_points.append(farthest_point)
        
        self.frames.append({
            'all_points': self.points.copy(),
            'active_points': np.array([]),
            'current_line': None,
            'farthest_point': farthest_point,
            'hull_points': self.current_hull_points.copy(),
            'hull_edges': self.current_hull_points.copy(),
            'cone_vectors': self.cone.copy() if self.cone is not None else None,
            'title': f'Step {self.step_counter + 1}: Add hull point',
            'description': f'Point added to hull. Split into two sub-problems.'
        })
    
    def _handle_standard_hull_complete(self, data):
        """Handle standard hull completion event."""
        self.step_counter += 1
        hull = data['hull']
        
        self.frames.append({
            'all_points': self.points.copy(),
            'active_points': np.array([]),
            'current_line': None,
            'farthest_point': None,
            'hull_points': hull,
            'hull_edges': hull,
            'cone_vectors': self.cone.copy() if self.cone is not None else None,
            'title': f'Step {self.step_counter + 1}: Standard hull complete!',
            'description': f'Standard convex hull with {len(hull)} vertices' + (' - Now applying cone constraints' if self.cone is not None else '')
        })
    
    def _handle_cone_processing_start(self, data):
        """Handle cone processing start event."""
        self.step_counter += 1
        standard_hull = data['standard_hull']
        cone_hull = data['cone_hull']
        cone_vectors = data['cone_vectors']
        
        self.frames.append({
            'all_points': self.points.copy(),
            'active_points': np.array([]),
            'current_line': None,
            'farthest_point': None,
            'hull_points': standard_hull,
            'hull_edges': standard_hull,
            'cone_vectors': cone_vectors.copy(),
            'cone_hull': cone_hull,
            'title': f'Step {self.step_counter + 1}: Apply cone constraints',
            'description': f'Standard hull (green) vs cone hull (purple) - {len(cone_hull)} vertices'
        })
    
    def _handle_cone_hull_complete(self, data):
        """Handle cone hull completion event."""
        self.step_counter += 1
        cone_hull = data['cone_hull']
        
        self.frames.append({
            'all_points': self.points.copy(),
            'active_points': np.array([]),
            'current_line': None,
            'farthest_point': None,
            'hull_points': cone_hull,
            'hull_edges': cone_hull,
            'cone_vectors': self.cone.copy(),
            'cone_hull': cone_hull,
            'title': f'Step {self.step_counter + 1}: Cone hull complete!',
            'description': f'Cone-constrained hull with {len(cone_hull)} vertices'
        })


def _quickhull_with_frames(points, cone=None, cone_bounds=None):
    """
    Clean function that computes convex hull and generates all animation frames.
    Uses the instrumented algorithm instead of duplicating logic.
    
    Parameters:
    -----------
    points : array-like
        Input points for convex hull computation
    cone : None or array-like of shape (2, 2), optional
        If None, uses standard QuickHull algorithm with leftmost/rightmost points.
        If provided, should be two vectors [v1, v2] defining a directional cone.
    cone_bounds : None, float, or array-like, optional
        Controls the bounding box used for cone hull computation.
        
    Returns:
    --------
    hull : np.ndarray
        Convex hull points
    frames : list
        List of frame data dictionaries for visualization
    """
    if len(points) < 3:
        return points, []
    
    points = np.array(points)
    
    # Create frame collector
    frame_collector = FrameCollector(points, cone)
    
    # Run the algorithm with instrumentation
    hull = conehull(points, cone=cone, cone_bounds=cone_bounds, frame_callback=frame_collector)
    
    return hull, frame_collector.frames


# ============================================================================
# SHARED VISUALIZATION FUNCTION - Used by all display variants
# ============================================================================

def _render_frame(frame, ax, points, figsize=None):
    """
    Render a single frame to a matplotlib axis.
    Shared visualization logic used by all display variants.
    """
    ax.clear()
    
    # Plot all input points - make them more visible in final frames
    if len(frame['all_points']) > 0:
        # Check if this is a final frame (has cone_hull or is standard hull complete)
        is_final_frame = ('cone_hull' in frame and frame['cone_hull'] is not None) or \
                        ('Standard hull complete' in frame.get('title', '') or 'Cone hull complete' in frame.get('title', ''))
        
        if is_final_frame:
            # Make points more visible in final frames
            ax.scatter(frame['all_points'][:, 0], frame['all_points'][:, 1], 
                      c='black', alpha=0.8, s=60, label='All points', zorder=8, 
                      edgecolors='white', linewidth=1)
        else:
            # Standard visibility for intermediate frames
            ax.scatter(frame['all_points'][:, 0], frame['all_points'][:, 1], 
                      c='lightgray', alpha=0.6, s=40, label='All points', zorder=1)
    
    # Plot currently active points (being processed)
    if len(frame['active_points']) > 0:
        ax.scatter(frame['active_points'][:, 0], frame['active_points'][:, 1],
                  c='lightblue', s=60, label='Active points', zorder=2)
    
    # Plot current line segment being processed
    if frame['current_line'] is not None:
        line = frame['current_line']
        ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 
               'r--', linewidth=3, alpha=0.8, label='Current line', zorder=4)
        # Mark endpoints of current line
        ax.scatter([line[0][0], line[1][0]], [line[0][1], line[1][1]], 
                  c='red', s=80, marker='s', zorder=5)
    
    # Plot farthest point found
    if frame['farthest_point'] is not None:
        fp = frame['farthest_point']
        ax.scatter([fp[0]], [fp[1]], c='orange', s=150, marker='*', 
                  label='Farthest point', zorder=6, edgecolors='black', linewidth=1)
    
    # Plot current hull points
    if len(frame['hull_points']) > 0:
        hull_pts = np.array(frame['hull_points'])
        ax.scatter(hull_pts[:, 0], hull_pts[:, 1], c='blue', s=100, 
                  label='Convex hull points', zorder=7, edgecolors='darkblue', linewidth=1)
    
    # Plot completed hull edges
    if len(frame['hull_edges']) > 0:
        hull = np.array(frame['hull_edges'])
        if len(hull) > 2:
            # Sort hull points in correct order to avoid self-intersections
            hull_sorted = sort_hull_points(hull)
            # Close the polygon for hull boundary
            hull_closed = np.vstack([hull_sorted, hull_sorted[0]])
            ax.plot(hull_closed[:, 0], hull_closed[:, 1], '--', 
                   linewidth=1.5, alpha=0.8, label='Convex hull boundary', zorder=3)
            ax.fill(hull_closed[:, 0], hull_closed[:, 1], 'green', alpha=0.05, zorder=0)
    
    # Plot cone hull if different from standard hull
    if 'cone_hull' in frame and frame['cone_hull'] is not None:
        cone_hull = np.array(frame['cone_hull'])
        if len(cone_hull) > 2:
            # Sort cone hull points in correct order
            cone_hull_sorted = sort_hull_points(cone_hull)
            # Close the polygon for cone hull boundary
            cone_hull_closed = np.vstack([cone_hull_sorted, cone_hull_sorted[0]])
            ax.plot(cone_hull_closed[:, 0], cone_hull_closed[:, 1], 'purple', 
                   linewidth=4, alpha=0.9, label='Cone hull boundary', zorder=4, linestyle='solid')
            ax.fill(cone_hull_closed[:, 0], cone_hull_closed[:, 1], 'purple', alpha=0.15, zorder=0)
        
        # Plot cone hull points as scattered points
        if len(cone_hull) > 0:
            ax.scatter(cone_hull[:, 0], cone_hull[:, 1], c='purple', s=100, 
                      label='Cone hull points', zorder=8, edgecolors='darkmagenta', linewidth=1.5, marker='h')
    
    ax.set_title(frame['title'], fontsize=14, fontweight='bold')
    # ax.text(0.02, 0.98, frame['description'], transform=ax.transAxes, 
    #        fontsize=11, verticalalignment='top', 
    #        bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.8))
    
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Set consistent axis limits FIRST
    if len(points) > 0:
        margin = 0.1
        x_range = points[:, 0].max() - points[:, 0].min()
        y_range = points[:, 1].max() - points[:, 1].min()
        ax.set_xlim(points[:, 0].min() - margin * x_range, 
                   points[:, 0].max() + margin * x_range)
        ax.set_ylim(points[:, 1].min() - margin * y_range, 
                   points[:, 1].max() + margin * y_range)
    
    # Plot cone direction vectors AFTER setting axis limits
    if 'cone_vectors' in frame and frame['cone_vectors'] is not None:
        cone_vectors = frame['cone_vectors']
        if len(frame['all_points']) > 0:
            # Position vectors in top-left corner using final axis limits
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            corner_x = xlim[0] + 0.08 * (xlim[1] - xlim[0])  # 8% from left edge
            corner_y = ylim[1] - 0.18 * (ylim[1] - ylim[0])  # 18% from top edge
            
            # Scale vectors appropriately for corner display (reduced by half)
            vector_scale = 0.075 * min(xlim[1] - xlim[0], ylim[1] - ylim[0])
            
            # Use a pleasant amber/orange color
            vector_color = '#FF8C00'  # Dark orange
            arc_color = '#FFA500'     # Lighter orange for arc
            
            # Calculate angles for arc
            v1, v2 = cone_vectors[0], cone_vectors[1]
            angle1 = np.arctan2(v1[1], v1[0])
            angle2 = np.arctan2(v2[1], v2[0])
            
            # Ensure we draw the smaller arc (cone region)
            angle_diff = angle2 - angle1
            if angle_diff > np.pi:
                angle_diff -= 2 * np.pi
            elif angle_diff < -np.pi:
                angle_diff += 2 * np.pi
            
            # Draw the arc showing allowable orientations
            if abs(angle_diff) > 0.01:  # Only draw if vectors are not too similar
                arc_radius = vector_scale * 0.4
                arc_angles = np.linspace(angle1, angle1 + angle_diff, 30)
                arc_x = corner_x + arc_radius * np.cos(arc_angles)
                arc_y = corner_y + arc_radius * np.sin(arc_angles)
                ax.plot(arc_x, arc_y, color=arc_color, linewidth=3, alpha=0.7, zorder=5)
                
                # Add small arc endpoints
                ax.plot([corner_x, arc_x[0]], [corner_y, arc_y[0]], 
                       color=arc_color, linewidth=2, alpha=0.5, zorder=5)
                ax.plot([corner_x, arc_x[-1]], [corner_y, arc_y[-1]], 
                       color=arc_color, linewidth=2, alpha=0.5, zorder=5)
            
            # Draw both vectors from the same origin point
            for i, vec in enumerate(cone_vectors):
                vec_norm = vec / np.linalg.norm(vec) * vector_scale
                ax.arrow(corner_x, corner_y, 
                        vec_norm[0], vec_norm[1], 
                        head_width=vector_scale*0.12, head_length=vector_scale*0.15, 
                        fc=vector_color, ec=vector_color, alpha=0.9, linewidth=2.5, zorder=6)
                
                # Show actual coordinates - position labels to avoid overlap
                coord_str = f'[{vec[0]:.1f}, {vec[1]:.1f}]'
                label_offset_x = vec_norm[0] + vector_scale * (0.3 if i == 0 else 0.35)
                label_offset_y = vec_norm[1] + vector_scale * (0.15 if i == 0 else -0.15)
                
                ax.text(corner_x + label_offset_x, corner_y + label_offset_y, 
                       coord_str, fontsize=9, color=vector_color, 
                       weight='bold', zorder=6, 
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor=vector_color))


# ============================================================================
# SPECIALIZED FUNCTIONS - Different output formats using shared base
# ============================================================================

def conehull_animated(points, interval=800, save_path=None, show_plot=True, cone=None, cone_bounds=None):
    """
    Create auto-playing animation of QuickHull or Cone-QuickHull algorithm.
    
    Parameters:
    -----------
    points : array-like
        Input points for convex hull computation
    interval : int, optional
        Animation frame interval in milliseconds (default: 800)
    save_path : str, optional
        Path to save animation. Supports .gif, .mp4, .webm formats
    show_plot : bool, optional
        Whether to display the animation (default: True)
    cone : None or array-like of shape (2, 2), optional
        If None, uses standard QuickHull algorithm with leftmost/rightmost points.
        If provided, should be two vectors [v1, v2] defining a directional cone.
    cone_bounds : None, float, or array-like, optional
        Controls the bounding box used for cone hull computation.
        
    Returns:
    --------
    hull : np.ndarray
        Convex hull points
    anim : matplotlib.animation.FuncAnimation
        Animation object for further manipulation
    """
    
    # Use shared base function
    hull, frames = _quickhull_with_frames(points, cone=cone, cone_bounds=cone_bounds)
    
    if len(frames) == 0:
        return hull, None
    
    # Create animation using shared visualization
    fig, ax = plt.subplots(figsize=(12, 10))
    
    def animate_frame(frame_idx):
        _render_frame(frames[frame_idx], ax, points)
        plt.tight_layout()
    
    # Create animation object
    anim = FuncAnimation(fig, animate_frame, frames=len(frames), 
                        interval=interval, repeat=True, blit=False)
    
    # Save animation if path provided
    if save_path:
        if save_path.endswith('.gif'):
            anim.save(save_path, writer='pillow', fps=1000//interval)
            print(f"Animation saved as: {save_path}")
        elif save_path.endswith('.mp4'):
            anim.save(save_path, writer='ffmpeg', fps=1000//interval)
            print(f"Animation saved as: {save_path}")
        elif save_path.endswith('.webm'):
            anim.save(save_path, writer='ffmpeg', fps=1000//interval, codec='libvpx-vp9')
            print(f"Animation saved as: {save_path}")
        else:
            print("Warning: save_path should end with .gif, .mp4, or .webm")
    
    # Show plot if requested
    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    
    return hull, anim


def conehull_step_by_step(points, figsize=(12, 10), cone=None, cone_bounds=None):
    """
    Create manual step-by-step viewer for QuickHull or Cone-QuickHull algorithm.
    
    Parameters:
    -----------
    points : array-like
        Input points for convex hull computation
    figsize : tuple, optional
        Figure size (width, height)
    cone : None or array-like of shape (2, 2), optional
        If None, uses standard QuickHull algorithm with leftmost/rightmost points.
        If provided, should be two vectors [v1, v2] defining a directional cone.
    cone_bounds : None, float, or array-like, optional
        Controls the bounding box used for cone hull computation.
        
    Returns:
    --------
    hull : np.ndarray
        Convex hull points
    frames : list
        List of frame data for external use
    show_frame : function
        Function to display a specific frame: show_frame(frame_number)
    """
    
    # Use shared base function
    hull, frames = _quickhull_with_frames(points, cone=cone, cone_bounds=cone_bounds)
    
    if len(frames) == 0:
        return hull, frames, None
    
    def show_frame(frame_number):
        """Display a specific frame of the algorithm."""
        if frame_number < 0 or frame_number >= len(frames):
            print(f"Frame {frame_number} not available. Valid range: 0-{len(frames)-1}")
            return
            
        frame = frames[frame_number]
        
        # Create figure and render using shared visualization
        fig, ax = plt.subplots(figsize=figsize)
        _render_frame(frame, ax, points)
        
        # Add frame counter to title
        ax.set_title(f"{frame['title']} (Frame {frame_number}/{len(frames)-1})", 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
        # Print navigation info
        print(f"\n📍 Frame {frame_number}/{len(frames)-1}")
        if frame_number > 0:
            print(f"   ⬅️  Previous: show_frame({frame_number-1})")
        if frame_number < len(frames)-1:
            print(f"   ➡️  Next: show_frame({frame_number+1})")
        print(f"   🏠 First: show_frame(0)")
        print(f"   🏁 Last: show_frame({len(frames)-1})")
    
    return hull, frames, show_frame


def conehull_jupyter(points, figsize=(12, 8), cone=None, cone_bounds=None):
    """
    Create interactive Jupyter widget for QuickHull or Cone-QuickHull algorithm.
    
    Parameters:
    -----------
    points : array-like
        Input points for convex hull computation
    figsize : tuple, optional
        Figure size (width, height)
    cone : None or array-like of shape (2, 2), optional
        If None, uses standard QuickHull algorithm with leftmost/rightmost points.
        If provided, should be two vectors [v1, v2] defining a directional cone.
    cone_bounds : None, float, or array-like, optional
        Controls the bounding box used for cone hull computation.
        
    Returns:
    --------
    QuickHullStepViewer
        Interactive widget object with navigation controls
    """
    
    # Use shared base function
    hull, frames = _quickhull_with_frames(points, cone=cone, cone_bounds=cone_bounds)
    
    if len(frames) == 0:
        return None
    
    # Import here to avoid dependency issues when not using Jupyter
    try:
        import ipywidgets as widgets
        from IPython.display import display, clear_output
    except ImportError:
        print("Error: ipywidgets and IPython required for Jupyter interface")
        print("Install with: pip install ipywidgets")
        return None
    
    class QuickHullStepViewer:
        def __init__(self, hull, frames, figsize):
            self.hull = hull
            self.frames = frames
            self.figsize = figsize
            self.current_frame = 0
            self.points = frames[0]['all_points']  # Get original points from first frame
            
            # Create widgets
            self.frame_slider = widgets.IntSlider(
                value=0, min=0, max=len(frames) - 1, step=1,
                description='Frame:', continuous_update=False,
                style={'description_width': 'initial'},
                layout=widgets.Layout(width='500px')
            )
            
            self.prev_button = widgets.Button(
                description='◀ Previous', button_style='info',
                layout=widgets.Layout(width='100px')
            )
            
            self.next_button = widgets.Button(
                description='Next ▶', button_style='success',
                layout=widgets.Layout(width='100px')
            )
            
            self.reset_button = widgets.Button(
                description='⟲ Reset', button_style='warning',
                layout=widgets.Layout(width='100px')
            )
            
            self.play_button = widgets.Button(
                description='▶ Auto Play', button_style='primary',
                layout=widgets.Layout(width='120px')
            )
            
            # Frame info display
            self.frame_info = widgets.HTML(
                value=self._get_frame_info_html(0),
                layout=widgets.Layout(width='100%', height='80px')
            )
            
            # Connect button events
            self.prev_button.on_click(self._prev_frame)
            self.next_button.on_click(self._next_frame)
            self.reset_button.on_click(self._reset_frame)
            self.play_button.on_click(self._auto_play)
            self.frame_slider.observe(self._slider_changed, names='value')
            
            # Output widget for plots
            self.output = widgets.Output()
            
            # Create layout
            button_box = widgets.HBox([
                self.prev_button, self.next_button, 
                self.reset_button, self.play_button
            ], layout=widgets.Layout(justify_content='center'))
            
            controls = widgets.VBox([
                self.frame_slider, button_box, self.frame_info
            ], layout=widgets.Layout(padding='10px'))
            
            self.widget = widgets.VBox([controls, self.output])
            
            # Show initial frame
            self._update_display()
        
        def _get_frame_info_html(self, frame_idx):
            """Generate HTML info for the current frame."""
            if frame_idx >= len(self.frames):
                return "<b>Invalid frame</b>"
                
            frame = self.frames[frame_idx]
            html = f"""
            <div style='background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%); 
                        padding: 15px; border-radius: 8px; border: 2px solid #4a90e2;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <h3 style='margin: 0 0 8px 0; color: #2c3e50;'>{frame['title']}</h3>
                <p style='margin: 0 0 8px 0; color: #555; font-size: 14px;'>{frame['description']}</p>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <small style='color: #7f8c8d; font-weight: bold;'>Frame {frame_idx + 1} of {len(self.frames)}</small>
                    <small style='color: #27ae60; font-weight: bold;'>Hull Points: {len(frame.get('hull_points', []))}</small>
                </div>
            </div>
            """
            return html
        
        def _update_display(self):
            """Update the plot display."""
            with self.output:
                clear_output(wait=True)
                
                # Create figure and render using shared visualization
                fig, ax = plt.subplots(figsize=self.figsize)
                _render_frame(self.frames[self.current_frame], ax, self.points)
                plt.tight_layout()
                plt.show()
            
            # Update frame info
            self.frame_info.value = self._get_frame_info_html(self.current_frame)
            
            # Update slider without triggering callback
            self.frame_slider.unobserve(self._slider_changed, names='value')
            self.frame_slider.value = self.current_frame
            self.frame_slider.observe(self._slider_changed, names='value')
            
            # Update button states
            self.prev_button.disabled = (self.current_frame == 0)
            self.next_button.disabled = (self.current_frame == len(self.frames) - 1)
        
        def _prev_frame(self, button):
            if self.current_frame > 0:
                self.current_frame -= 1
                self._update_display()
        
        def _next_frame(self, button):
            if self.current_frame < len(self.frames) - 1:
                self.current_frame += 1
                self._update_display()
        
        def _reset_frame(self, button):
            self.current_frame = 0
            self._update_display()
        
        def _slider_changed(self, change):
            self.current_frame = change['new']
            self._update_display()
        
        def _auto_play(self, button):
            """Auto-play through all frames."""
            import time
            
            # Disable buttons during auto-play
            self.play_button.description = '⏸ Playing...'
            for btn in [self.prev_button, self.next_button, self.reset_button, self.play_button]:
                btn.disabled = True
            
            try:
                for i in range(self.current_frame, len(self.frames)):
                    self.current_frame = i
                    self._update_display()
                    time.sleep(2.0)  # 2 second delay between frames
            except KeyboardInterrupt:
                pass
            finally:
                # Re-enable buttons
                self.play_button.description = '▶ Auto Play'
                for btn in [self.prev_button, self.next_button, self.reset_button, self.play_button]:
                    btn.disabled = False
                self._update_display()
        
        def show(self):
            """Display the interactive viewer."""
            display(self.widget)
            
        def get_summary(self):
            """Get a summary of the algorithm execution."""
            return {
                'total_points': len(self.points),
                'hull_points': len(self.hull),
                'total_steps': len(self.frames),
                'hull_efficiency': f"{len(self.hull)/len(self.points):.1%}"
            }
    
    return QuickHullStepViewer(hull, frames, figsize)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def plot_hull(hull=None, points=None, cone=None, show_convex_hull=False, figsize=(12, 10), title=None, show=True, save_path=None):
    """
    Plot the hull result using the same styling as the animation's final frame.
    This is a standalone visualization function that accepts pre-computed hull.
    
    Parameters:
    -----------
    hull : array-like, optional
        Pre-computed hull points. If None, will be computed from points.
        If both hull and points are None, will generate sample data.
    points : array-like, optional
        Original input points that were used for hull computation.
        If None but hull is provided, will use hull points as the point set.
        If both hull and points are None, will generate sample data.
    cone : None or array-like of shape (2, 2), optional
        If provided, cone vectors will be displayed and hull will be styled as cone hull.
        If None, hull will be styled as standard convex hull.
    show_convex_hull : bool, optional
        If True and cone is provided, also compute and display the standard convex hull
        for comparison (similar to the "Apply cone constraints" animation frame).
    figsize : tuple, optional
        Figure size (width, height)
    title : str, optional
        Custom title for the plot. If None, auto-generates based on algorithm type.
    show : bool, optional
        Whether to display the plot (default: True)
    save_path : str, optional
        Path to save the plot image. Supports common formats like .png, .jpg, .pdf, .svg
        
    Returns:
    --------
    fig : matplotlib.figure.Figure or None
        Figure object (returned only if show=False)
    """
    
    # Handle optional parameters
    if hull is None and points is None:
        # Generate sample data for demonstration
        np.random.seed(42)  # For reproducible results
        points = np.random.rand(20, 2) * 10
        # Compute hull from generated points
        from ._conehull import conehull
        hull = conehull(points, cone=cone)
    elif hull is None and points is not None:
        # Compute hull from provided points
        points = np.array(points)
        from ._conehull import conehull
        hull = conehull(points, cone=cone)
    elif hull is not None and points is None:
        # Use hull points as the point set (hull is subset of original points)
        hull = np.array(hull)
        points = hull.copy()
    else:
        # Both provided - convert to arrays (original behavior)
        points = np.array(points)
        hull = np.array(hull)
    
    # Create frame data structure like the final animation frame
    if cone is not None:
        # Cone hull case
        cone = np.array(cone)
        
        if show_convex_hull:
            # Show both standard and cone hulls (like "Apply cone constraints" frame)
            from ._conehull import conehull
            standard_hull = conehull(points)  # Compute standard hull for comparison
            
            frame_data = {
                'all_points': points.copy(),
                'active_points': np.array([]),
                'current_line': None,
                'farthest_point': None,
                'hull_points': standard_hull,
                'hull_edges': standard_hull,
                'cone_vectors': cone,
                'cone_hull': hull,
                'title': title or f'Cone Hull vs Standard Hull Comparison',
                'description': f'Standard hull vs cone hull - {len(hull)} cone vertices, {len(standard_hull)} standard vertices'
            }
        else:
            # Show cone hull (but still compute standard hull for comparison)
            from ._conehull import conehull
            standard_hull = conehull(points)  # Compute standard hull for point display
            
            frame_data = {
                'all_points': points.copy(),
                'active_points': np.array([]),
                'current_line': None,
                'farthest_point': None,
                'hull_points': standard_hull,  # Show standard hull points
                'hull_edges': standard_hull,  # Use standard hull for boundary
                'cone_vectors': cone,
                'cone_hull': hull,
                'title': title or f'Cone Hull Complete! ({len(hull)} vertices)',
                'description': f'Cone-constrained hull with {len(hull)} vertices'
            }
    else:
        # Standard hull case
        frame_data = {
            'all_points': points.copy(),
            'active_points': np.array([]),
            'current_line': None,
            'farthest_point': None,
            'hull_points': hull,
            'hull_edges': hull,
            'cone_vectors': None,
            'title': title or f'Standard Hull Complete! ({len(hull)} vertices)',
            'description': f'Standard convex hull with {len(hull)} vertices'
        }
    
    # Create figure and render using shared visualization
    fig, ax = plt.subplots(figsize=figsize)
    _render_frame(frame_data, ax, points)
    plt.tight_layout()
    
    # Save figure if path provided
    if save_path:
        # Use reasonable settings for different formats
        save_kwargs = {
            'dpi': 300,  # High resolution
            'bbox_inches': 'tight',  # Remove extra whitespace
            'facecolor': 'white',  # White background
            'edgecolor': 'none'  # No border
        }
        
        # Add format-specific optimizations
        if save_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            save_kwargs['format'] = save_path.split('.')[-1].lower()
            if save_path.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['format'] = 'jpeg'
        elif save_path.lower().endswith('.pdf'):
            save_kwargs['format'] = 'pdf'
        elif save_path.lower().endswith('.svg'):
            save_kwargs['format'] = 'svg'
        
        fig.savefig(save_path, **save_kwargs)
        print(f"Plot saved as: {save_path}")
    
    if show:
        plt.show()
        return None
    else:
        return fig
