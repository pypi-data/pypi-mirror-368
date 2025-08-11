import numpy as np
from scipy.optimize import minimize_scalar
from skimage.measure import find_contours

def sample_parametric(
    param_fn,                   # callable t ↦ (x(t), y(t))
    t_interval,                 # (t_min, t_max)
    M,
    *,                          # kw-only below
    arclength=False,
    oversample_factor=20,
    rng=None
):
    """
    Draw M points on a 2-D curve given by a 1-parameter parametrisation.

    Parameters
    ----------
    param_fn : callable
        Maps a 1-D NumPy array of shape (k,) to an array (k, 2).
    t_interval : tuple(float, float)
        Parameter domain (inclusive).
    M : int
        Number of samples.
    arclength : bool, default False
        If True, resample so that points are approximately uniform in
        arc-length rather than uniform in parameter.
    oversample_factor : int, default 20
        Only used if `arclength=True`.  Higher ⇒ better uniformity but
        slower.
    rng : np.random.Generator, default None
        Pass your own RNG for reproducibility.
    """
    rng = np.random.default_rng(rng)
    t0, t1 = t_interval

    if not arclength:
        t = rng.uniform(t0, t1, size=M)
        return param_fn(t)

    # --- crude arc-length equalisation -------------------------------
    k = M * oversample_factor
    t_dense = np.linspace(t0, t1, k, endpoint=True)
    pts = param_fn(t_dense)
    seglen = np.linalg.norm(np.diff(pts, axis=0), axis=1)          # (k-1,)
    cumlen = np.concatenate(([0.0], np.cumsum(seglen)))
    cumlen /= cumlen[-1]                                           # normalise to [0,1]

    u = rng.uniform(0, 1, size=M)
    t = np.interp(u, cumlen, t_dense)
    return param_fn(t)


def _trace_implicit(F, xlim, ylim, grid_size=500):
    # 1) build the grid
    xs = np.linspace(xlim[0], xlim[1], grid_size)
    ys = np.linspace(ylim[0], ylim[1], grid_size)
    X, Y = np.meshgrid(xs, ys)
    Z = F(X, Y)
    
    # 2) find_contours works on (row, col) arrays, where
    #    row index ~ y and col index ~ x
    raw = find_contours(Z, level=0)
    
    # 3) convert from pixel coords back to data coords
    segments = []
    for seg in raw:
        # seg is (N,2) array of [row, col] floats
        row, col = seg[:, 0], seg[:, 1]
        x = xlim[0] + (xlim[1] - xlim[0]) * (col / (grid_size - 1))
        y = ylim[0] + (ylim[1] - ylim[0]) * (row / (grid_size - 1))
        segments.append(np.stack([x, y], axis=1))
    return segments

def _uniform_sample(paths, n_samples=1000):
    """
    Randomly sample n_samples points *approximately* uniformly along all paths.
    """
    lengths = []
    cum_dists = []
    for pts in paths:
        # length of each small segment
        d = np.hypot(np.diff(pts[:,0]), np.diff(pts[:,1]))
        lengths.append(d.sum())
        cum_dists.append(np.concatenate(([0], np.cumsum(d))))

    total_length = sum(lengths)
    samples = []
    for _ in range(n_samples):
        r = np.random.rand() * total_length
        acc = 0
        for pts, L, cd in zip(paths, lengths, cum_dists):
            if acc + L >= r:
                d_target = r - acc
                idx = np.searchsorted(cd, d_target) - 1
                idx = max(idx, 0)
                seg_len = cd[idx+1] - cd[idx]
                t = (d_target - cd[idx]) / seg_len
                p0, p1 = pts[idx], pts[idx+1]
                samples.append(p0 + t*(p1 - p0))
                break
            acc += L
    return np.array(samples)

def _auto_bounds(F,
                 initial_lim=(-1, 1),
                 grid_size=200,
                 pad_frac=0.1,
                 expand_factor=2,
                 max_iters=4):
    """
    Heuristically find xlim, ylim so that F(x,y)=0 appears inside.
    
    Uses skimage.measure.find_contours on a coarse grid:
      1. Start with box [−R,R]×[−R,R].
      2. Evaluate F on a grid_size×grid_size grid.
      3. Run find_contours at level=0.
      4. If contours found, map their pixel coords back to data coords,
         compute min/max, pad by pad_frac, and return.
      5. Otherwise, expand R and retry (up to max_iters).
    """
    R = initial_lim[1]
    for _ in range(max_iters):
        # build the grid
        xs = np.linspace(-R, R, grid_size)
        ys = np.linspace(-R, R, grid_size)
        X, Y = np.meshgrid(xs, ys)
        Z = F(X, Y)

        # find all zero‐level contours (list of (n,2) arrays of [row, col])
        raw_contours = find_contours(Z, level=0)
        if raw_contours:
            # convert each contour from pixel → data coords
            segs = []
            for seg in raw_contours:
                rows, cols = seg[:, 0], seg[:, 1]
                x = xs[0] + (xs[-1] - xs[0]) * (cols / (grid_size - 1))
                y = ys[0] + (ys[-1] - ys[0]) * (rows / (grid_size - 1))
                segs.append(np.vstack([x, y]).T)

            # merge all points and find bounds
            all_pts = np.vstack(segs)
            xmin, xmax = all_pts[:,0].min(), all_pts[:,0].max()
            ymin, ymax = all_pts[:,1].min(), all_pts[:,1].max()
            
            # pad by a fraction of the span
            dx = (xmax - xmin) * pad_frac
            dy = (ymax - ymin) * pad_frac
            return (xmin - dx, xmax + dx), (ymin - dy, ymax + dy)

        # no contour found → expand search box
        R *= expand_factor

    # fallback if nothing ever appeared
    return (-R, R), (-R, R)

def sample_implicit_curve(
    F,                             # callable (x,y) ↦ scalar
    n_samples,
    xlim=None, ylim=None,
):
    auto_xlim, auto_ylim = _auto_bounds(F)
    if xlim is None:
        xlim = auto_xlim
    if ylim is None:
        ylim = auto_ylim

    paths = _trace_implicit(F, xlim=xlim, ylim=ylim)
    pts = _uniform_sample(paths, n_samples=n_samples)
    return pts

def sample_implicit_region(
    F,
    n_samples,
    xlim=None, ylim=None,
    rng=None,
    batch_size=10_000
):
    """
    Uniformly sample points inside the region F(x,y) <= 0
    over the rectangle [xlim]×[ylim], by rejection.

    Parameters
    ----------
    F : callable
        Vectorized function (X,Y) -> array of values.
    xlim, ylim : 2‐tuples
        (min, max) for x and y.
    n_samples : int
        Number of points you want.
    rng : None, int, or np.random.Generator
        Seed or Generator for reproducibility.
    batch_size : int
        How many candidates to draw at once.

    Returns
    -------
    points : (n_samples, 2) array
        Uniform points in the set {F(x,y) <= 0}.
    """
    auto_xlim, auto_ylim = _auto_bounds(F)
    if xlim is None:
        xlim = auto_xlim
    if ylim is None:
        ylim = auto_ylim

    if rng is None or isinstance(rng, (int, np.integer)):
        rng = np.random.default_rng(rng)

    pts = []
    while len(pts) < n_samples:
        # grab a batch of random candidates
        xs = rng.uniform(xlim[0], xlim[1], size=batch_size)
        ys = rng.uniform(ylim[0], ylim[1], size=batch_size)
        vals = F(xs, ys)
        mask = vals <= 0
        # collect the ones that lie inside
        new_pts = np.column_stack((xs[mask], ys[mask]))
        pts.append(new_pts)
    pts = np.vstack(pts)
    return pts[:n_samples]
