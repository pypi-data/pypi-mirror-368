from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import numpy as np
from sklearn.utils import check_array, check_random_state

from scanpy import logging as logg
from scanpy._compat import old_positionals
from scanpy._settings import settings
from scanpy._utils import NeighborsView
from scanpy.tools._utils import _choose_representation, get_init_pos_from_paga
#from .._settings import EMOJI

EMOJI = {
    "start": "🚀",
    "done": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
}

if TYPE_CHECKING:
    from typing import Literal

    from anndata import AnnData

    from scanpy._utils.random import _LegacyRandom

    _InitPos = Literal["paga", "spectral", "random"]


@old_positionals(
    "min_dist",
    "spread",
    "n_components",
    "maxiter",
    "alpha",
    "gamma",
    "negative_sample_rate",
    "init_pos",
    "random_state",
    "a",
    "b",
    "copy",
    "method",
    "neighbors_key",
)
def umap(  # noqa: PLR0913, PLR0915
    adata: AnnData,
    *,
    min_dist: float = 0.5,
    spread: float = 1.0,
    n_components: int = 2,
    maxiter: int | None = None,
    alpha: float = 1.0,
    gamma: float = 1.0,
    negative_sample_rate: int = 5,
    init_pos: _InitPos | np.ndarray | None = "spectral",
    random_state: _LegacyRandom = 0,
    a: float | None = None,
    b: float | None = None,
    method: Literal["umap", "rapids","torchdr","mde"] = "umap",
    key_added: str | None = None,
    neighbors_key: str = "neighbors",
    copy: bool = False,
) -> AnnData | None:
    r"""Embed the neighborhood graph using UMAP with multiple backend options.

    UMAP (Uniform Manifold Approximation and Projection) implementation with support
    for multiple computational backends including GPU-accelerated variants using
    TorchDR and MDE for improved performance on large datasets.

    Arguments:
        adata: Annotated data matrix of shape n_obs × n_vars
        min_dist (float): Minimum distance between embedded points (default: 0.5)
        spread (float): Scale at which embedded points are spread out (default: 1.0)
        n_components (int): Number of dimensions for the embedding (default: 2)
        maxiter (int): Number of optimization iterations (default: None)
        alpha (float): Initial learning rate for optimization (default: 1.0)
        gamma (float): Weighting for negative samples (default: 1.0)
        negative_sample_rate (int): Number of negative samples per positive sample (default: 5)
        init_pos: Initialization method for embedding positions (default: 'spectral')
        random_state (int): Random seed for reproducible results (default: 0)
        a (float): UMAP curve parameter (default: None)
        b (float): UMAP curve parameter (default: None)
        method (str): Implementation method: 'umap', 'torchdr', 'mde', 'rapids' (default: 'umap')
        key_added (str): Key for storing results in AnnData (default: None)
        neighbors_key (str): Key for accessing neighbor information (default: 'neighbors')
        copy (bool): Return copy instead of modifying in place (default: False)

    Returns:
        adata with UMAP embedding if copy=False, otherwise returns modified copy

    """
    adata = adata.copy() if copy else adata

    key_obsm, key_uns = ("X_umap", "umap") if key_added is None else [key_added] * 2

    if neighbors_key is None:  # backwards compat
        neighbors_key = "neighbors"
    if neighbors_key not in adata.uns:
        msg = f"Did not find .uns[{neighbors_key!r}]. Run `sc.pp.neighbors` first."
        raise ValueError(msg)

    start = logg.info(f"computing UMAP{EMOJI['start']}")

    neighbors = NeighborsView(adata, neighbors_key)

    if "params" not in neighbors or neighbors["params"]["method"] != "umap":
        logg.warning(
            f'.obsp["{neighbors["connectivities_key"]}"] have not been computed using umap'
        )

    with warnings.catch_warnings():
        # umap 0.5.0
        warnings.filterwarnings("ignore", message=r"Tensorflow not installed")
        import umap

    from umap.umap_ import find_ab_params, simplicial_set_embedding

    if a is None or b is None:
        a, b = find_ab_params(spread, min_dist)
    adata.uns[key_uns] = dict(params=dict(a=a, b=b))
    if isinstance(init_pos, str) and init_pos in adata.obsm:
        init_coords = adata.obsm[init_pos]
    elif isinstance(init_pos, str) and init_pos == "paga":
        init_coords = get_init_pos_from_paga(
            adata, random_state=random_state, neighbors_key=neighbors_key
        )
    else:
        init_coords = init_pos  # Let umap handle it
    if hasattr(init_coords, "dtype"):
        init_coords = check_array(init_coords, dtype=np.float32, accept_sparse=False)

    if random_state != 0:
        adata.uns[key_uns]["params"]["random_state"] = random_state
    #random_state = check_random_state(random_state)

    neigh_params = neighbors["params"]
    X = _choose_representation(
        adata,
        use_rep=neigh_params.get("use_rep", None),
        n_pcs=neigh_params.get("n_pcs", None),
        silent=True,
    )
    if method == "umap":
        # the data matrix X is really only used for determining the number of connected components
        # for the init condition in the UMAP embedding
        default_epochs = 500 if neighbors["connectivities"].shape[0] <= 10000 else 200
        n_epochs = default_epochs if maxiter is None else maxiter
        X_umap, _ = simplicial_set_embedding(
            data=X,
            graph=neighbors["connectivities"].tocoo(),
            n_components=n_components,
            initial_alpha=alpha,
            a=a,
            b=b,
            gamma=gamma,
            negative_sample_rate=negative_sample_rate,
            n_epochs=n_epochs,
            init=init_coords,
            random_state=random_state,
            metric=neigh_params.get("metric", "euclidean"),
            metric_kwds=neigh_params.get("metric_kwds", {}),
            densmap=False,
            densmap_kwds={},
            output_dens=False,
            verbose=settings.verbosity > 3,
        )
    elif method == "torchdr":
        from torchdr import UMAP
        import torch
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        n_neighbors = neighbors["params"]["n_neighbors"]
        n_epochs = (
            500 if maxiter is None else maxiter
        )  # 0 is not a valid value for rapids, unlike original umap
        X_contiguous = np.ascontiguousarray(X, dtype=np.float32)
        
        umap = UMAP(
            n_neighbors=n_neighbors,
            n_components=n_components,
            max_iter=n_epochs,
            min_dist=min_dist,
            spread=spread,
            a=a,
            b=b,
            lr = alpha,
            device=device,
            random_state=random_state,
        )
        X_umap = umap.fit(X_contiguous).embedding_.detach().cpu().numpy()

        
        del umap
        import gc
        torch.cuda.empty_cache()
        gc.collect()

    elif method == "mde":
        try:
            from pymde import MDE, constraints, penalties, preprocess
            import torch
        except ImportError as err:
            raise ImportError("Please install pymde package via `pip install pymde`") from err
            
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Convert random_state to torch seed
        import pymde
        pymde.seed(random_state)
        
        # Get neighbor graph from connectivities
        connectivities = neighbors["connectivities"]
        
        # Convert to PyTorch sparse tensor
        rows, cols = connectivities.nonzero()
        edges = torch.tensor(np.vstack([rows, cols]).T, dtype=torch.int64)
        
        # Filter out self-loops and ensure each edge appears only once
        mask = edges[:, 0] != edges[:, 1]
        edges = edges[mask]
        
        # Sort edges to ensure i < j
        sorted_edges = torch.zeros_like(edges)
        sorted_edges[:, 0] = torch.min(edges[:, 0], edges[:, 1])
        sorted_edges[:, 1] = torch.max(edges[:, 0], edges[:, 1])
        edges = torch.unique(sorted_edges, dim=0)
        
        # Create weights for edges based on connectivities
        weights = torch.ones(edges.shape[0], device=device)
        
        # Add dissimilar edges for better embedding
        n_similar = edges.shape[0]
        n_dissimilar = int(n_similar * min_dist)  # Use min_dist to scale number of dissimilar edges
        
        try:
            # Try to generate dissimilar edges
            dissimilar_edges = preprocess.dissimilar_edges(
                X.shape[0], 
                num_edges=int(n_dissimilar), 
                similar_edges=edges,
            )
            
            # Combine similar and dissimilar edges
            all_edges = torch.cat([edges, dissimilar_edges.to(edges.device)])
            
            # Create weights: positive for similar edges, negative for dissimilar
            all_weights = torch.cat([
                weights,  # Positive weights for similar edges
                -0.5 * torch.ones(dissimilar_edges.shape[0], device=device)  # Negative weights for dissimilar
            ])
            
            # Create PushAndPull distortion function
            distortion_function = penalties.PushAndPull(
                weights=all_weights,
                attractive_penalty=penalties.Log1p,
                repulsive_penalty=penalties.Log,
            )
            
            # Use the combined edges
            edges_to_use = all_edges
            
        except Exception as e:
            # Fallback to simple quadratic penalty if dissimilar edges fail
            logg.warning(f"Failed to generate dissimilar edges: {str(e)}. Using quadratic penalty instead.")
            distortion_function = penalties.Quadratic(weights)
            edges_to_use = edges
        
        n_epochs = 500 if maxiter is None else maxiter
        
        # Create MDE problem with appropriate penalty
        mde = MDE(
            n_items=X.shape[0],
            embedding_dim=n_components,
            edges=edges_to_use.to(device),
            distortion_function=distortion_function,
            constraint=constraints.Standardized(),
            device=device
        )
        
        # Compute embedding with initial random state
        if isinstance(init_coords, np.ndarray):
            embedding = mde.embed(
                verbose=settings.verbosity > 3,
                max_iter=n_epochs,
                # Set random initial state if not using existing embedding
                X=None if init_coords is None else init_coords
            )
        else:
            embedding = mde.embed(
                verbose=settings.verbosity > 3,
                max_iter=n_epochs,
            )
        
        X_umap = embedding.cpu().numpy()
        
        # Clean up
        del mde, embedding, edges, weights
        if 'all_edges' in locals():
            del all_edges
        if 'all_weights' in locals():
            del all_weights
        if 'distortion_function' in locals():
            del distortion_function
    
        
        torch.cuda.empty_cache()
        import gc
        gc.collect()
        
    elif method == "rapids":
        msg = (
            "`method='rapids'` is deprecated. "
            "Use `rapids_singlecell.tl.louvain` instead."
        )
        warnings.warn(msg, FutureWarning, stacklevel=2)
        metric = neigh_params.get("metric", "euclidean")
        if metric != "euclidean":
            msg = (
                f"`sc.pp.neighbors` was called with `metric` {metric!r}, "
                "but umap `method` 'rapids' only supports the 'euclidean' metric."
            )
            raise ValueError(msg)
        from cuml import UMAP

        n_neighbors = neighbors["params"]["n_neighbors"]
        n_epochs = (
            500 if maxiter is None else maxiter
        )  # 0 is not a valid value for rapids, unlike original umap
        X_contiguous = np.ascontiguousarray(X, dtype=np.float32)
        umap = UMAP(
            n_neighbors=n_neighbors,
            n_components=n_components,
            n_epochs=n_epochs,
            learning_rate=alpha,
            init=init_pos,
            min_dist=min_dist,
            spread=spread,
            negative_sample_rate=negative_sample_rate,
            a=a,
            b=b,
            verbose=settings.verbosity > 3,
            random_state=random_state,
        )
        X_umap = umap.fit_transform(X_contiguous)
    adata.obsm[key_obsm] = X_umap  # annotate samples with UMAP coordinates
    logg.info(
        f"    finished {EMOJI['done']}",
        time=start,
        deep=(
            "added\n"
            f"    {key_obsm!r}, UMAP coordinates (adata.obsm)\n"
            f"    {key_uns!r}, UMAP parameters (adata.uns)"
        ),
    )
    return adata if copy else None



