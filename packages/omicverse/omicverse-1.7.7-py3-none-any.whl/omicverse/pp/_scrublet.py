# This file is a modified version of the scrublet.py file from scanpy.
# The only difference is that it allows for the use of GPU.
# The original file can be found at:
# https://github.com/scverse/scanpy/blob/main/scanpy/preprocessing/_scrublet/core.py
from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from anndata import AnnData
from scipy import sparse

from scanpy import logging as logg
from scanpy import preprocessing as pp
from scanpy._compat import old_positionals
from scanpy.get import _get_obs_rep
from scanpy.preprocessing._scrublet import pipeline
from scanpy.preprocessing._scrublet.core import Scrublet
from .._settings import EMOJI


from importlib.util import find_spec
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from anndata import AnnData
from scipy import sparse

from scanpy import logging as logg
from scanpy import preprocessing as pp
from scanpy._compat import old_positionals
from scanpy.get import _get_obs_rep
from scanpy.preprocessing._scrublet import pipeline
from scanpy.preprocessing._scrublet.core import Scrublet

if TYPE_CHECKING:
    from scanpy._compat import _LegacyRandom
    from scanpy.neighbors import _Metric, _MetricFn


@old_positionals(
    "batch_key",
    "sim_doublet_ratio",
    "expected_doublet_rate",
    "stdev_doublet_rate",
    "synthetic_doublet_umi_subsampling",
    "knn_dist_metric",
    "normalize_variance",
    "log_transform",
    "mean_center",
    "n_prin_comps",
    "use_approx_neighbors",
    "get_doublet_neighbor_parents",
    "n_neighbors",
    "threshold",
    "verbose",
    "copy",
    "random_state",
)
def scrublet(
    adata: AnnData,
    adata_sim: AnnData | None = None,
    *,
    batch_key: str | None = None,
    sim_doublet_ratio: float = 2.0,
    expected_doublet_rate: float = 0.05,
    stdev_doublet_rate: float = 0.02,
    synthetic_doublet_umi_subsampling: float = 1.0,
    knn_dist_metric: _Metric | _MetricFn = "euclidean",
    normalize_variance: bool = True,
    log_transform: bool = False,
    mean_center: bool = True,
    n_prin_comps: int = 30,
    use_approx_neighbors: bool | None = None,
    get_doublet_neighbor_parents: bool = False,
    n_neighbors: int | None = None,
    threshold: float | None = None,
    verbose: bool = True,
    copy: bool = False,
    random_state: _LegacyRandom = 0,
    use_gpu: bool = False,
) -> AnnData | None:
    r"""Predict doublets using Scrublet with optional GPU acceleration.

    Predict cell doublets using a nearest-neighbor classifier of observed
    transcriptomes and simulated doublets. This implementation includes
    GPU acceleration options for improved performance on large datasets.

    Arguments:
        adata: Annotated data matrix of shape n_obs × n_vars
        adata_sim (AnnData): Pre-simulated doublets (default: None)
        batch_key (str): Column name for batch information (default: None)
        sim_doublet_ratio (float): Number of doublets to simulate relative to observed cells (default: 2.0)
        expected_doublet_rate (float): Estimated doublet rate for the experiment (default: 0.05)
        stdev_doublet_rate (float): Uncertainty in expected doublet rate (default: 0.02)
        synthetic_doublet_umi_subsampling (float): UMI sampling rate for synthetic doublets (default: 1.0)
        knn_dist_metric (str): Distance metric for nearest neighbors (default: 'euclidean')
        normalize_variance (bool): Whether to normalize gene variance (default: True)
        log_transform (bool): Whether to log-transform data prior to PCA (default: False)
        mean_center (bool): Whether to center data for PCA (default: True)
        n_prin_comps (int): Number of principal components for embedding (default: 30)
        use_approx_neighbors (bool): Use approximate nearest neighbor search (default: None)
        get_doublet_neighbor_parents (bool): Return parent transcriptomes for doublet neighbors (default: False)
        n_neighbors (int): Number of neighbors for KNN graph (default: None)
        threshold (float): Doublet score threshold for classification (default: None)
        verbose (bool): Whether to log progress updates (default: True)
        copy (bool): Return copy instead of modifying in place (default: False)
        random_state (int): Random seed for reproducibility (default: 0)
        use_gpu (bool): Whether to use GPU acceleration (default: False)

    Returns:
        adata with doublet predictions added if copy=False, otherwise returns modified copy
    """
    if threshold is None and not find_spec("skimage"):  # pragma: no cover
        # Scrublet.call_doublets requires `skimage` with `threshold=None` but PCA
        # is called early, which is wasteful if there is not `skimage`
        msg = "threshold is None and thus scrublet requires skimage, but skimage is not installed."
        raise ValueError(msg)

    if copy:
        adata = adata.copy()

    start = logg.info(f"Running Scrublet{EMOJI['start']}")

    adata_obs = adata.copy()

    def _run_scrublet(ad_obs: AnnData, ad_sim: AnnData | None = None):
        # With no adata_sim we assume the regular use case, starting with raw
        # counts and simulating doublets

        if ad_sim is None:
            pp.filter_genes(ad_obs, min_cells=3)
            pp.filter_cells(ad_obs, min_genes=3)

            # Doublet simulation will be based on the un-normalised counts, but on the
            # selection of genes following normalisation and variability filtering. So
            # we need to save the raw and subset at the same time.

            ad_obs.layers["raw"] = ad_obs.X.copy()
            pp.normalize_total(ad_obs)

            # HVG process needs log'd data.
            ad_obs.layers["log1p"] = ad_obs.X.copy()
            pp.log1p(ad_obs, layer="log1p")
            pp.highly_variable_genes(ad_obs, layer="log1p")
            del ad_obs.layers["log1p"]
            ad_obs = ad_obs[:, ad_obs.var["highly_variable"]].copy()

            # Simulate the doublets based on the raw expressions from the normalised
            # and filtered object.

            ad_sim = scrublet_simulate_doublets(
                ad_obs,
                layer="raw",
                sim_doublet_ratio=sim_doublet_ratio,
                synthetic_doublet_umi_subsampling=synthetic_doublet_umi_subsampling,
                random_seed=random_state,
            )
            del ad_obs.layers["raw"]
            if log_transform:
                pp.log1p(ad_obs)
                pp.log1p(ad_sim)

            # Now normalise simulated and observed in the same way

            pp.normalize_total(ad_obs, target_sum=1e6)
            pp.normalize_total(ad_sim, target_sum=1e6)

        ad_obs = _scrublet_call_doublets(
            adata_obs=ad_obs,
            adata_sim=ad_sim,
            n_neighbors=n_neighbors,
            expected_doublet_rate=expected_doublet_rate,
            stdev_doublet_rate=stdev_doublet_rate,
            mean_center=mean_center,
            normalize_variance=normalize_variance,
            n_prin_comps=n_prin_comps,
            use_approx_neighbors=use_approx_neighbors,
            knn_dist_metric=knn_dist_metric,
            get_doublet_neighbor_parents=get_doublet_neighbor_parents,
            threshold=threshold,
            random_state=random_state,
            verbose=verbose,
            use_gpu=use_gpu,
        )

        return {"obs": ad_obs.obs, "uns": ad_obs.uns["scrublet"]}

    if batch_key is not None:
        if batch_key not in adata.obs.columns:
            msg = (
                "`batch_key` must be a column of .obs in the input AnnData object,"
                f"but {batch_key!r} is not in {adata.obs.keys()!r}."
            )
            raise ValueError(msg)

        # Run Scrublet independently on batches and return just the
        # scrublet-relevant parts of the objects to add to the input object

        batches = np.unique(adata.obs[batch_key])
        scrubbed = [
            _run_scrublet(
                adata_obs[adata_obs.obs[batch_key] == batch].copy(),
                adata_sim,
            )
            for batch in batches
        ]
        scrubbed_obs = pd.concat([scrub["obs"] for scrub in scrubbed])

        # Now reset the obs to get the scrublet scores

        adata.obs = scrubbed_obs.loc[adata.obs_names.values]

        # Save the .uns from each batch separately

        adata.uns["scrublet"] = {}
        adata.uns["scrublet"]["batches"] = dict(
            zip(batches, [scrub["uns"] for scrub in scrubbed])
        )

        # Record that we've done batched analysis, so e.g. the plotting
        # function knows what to do.

        adata.uns["scrublet"]["batched_by"] = batch_key

    else:
        scrubbed = _run_scrublet(adata_obs, adata_sim)

        # Copy outcomes to input object from our processed version

        adata.obs["doublet_score"] = scrubbed["obs"]["doublet_score"]
        adata.obs["predicted_doublet"] = scrubbed["obs"]["predicted_doublet"]
        adata.uns["scrublet"] = scrubbed["uns"]

    logg.info(f"    Scrublet finished{EMOJI['done']}", time=start)

    return adata if copy else None


def _scrublet_call_doublets(
    adata_obs: AnnData,
    adata_sim: AnnData,
    *,
    n_neighbors: int | None = None,
    expected_doublet_rate: float = 0.05,
    stdev_doublet_rate: float = 0.02,
    mean_center: bool = True,
    normalize_variance: bool = True,
    n_prin_comps: int = 30,
    use_approx_neighbors: bool | None = None,
    knn_dist_metric: _Metric | _MetricFn = "euclidean",
    get_doublet_neighbor_parents: bool = False,
    threshold: float | None = None,
    random_state: _LegacyRandom = 0,
    verbose: bool = True,
    use_gpu: bool = False,
    ) -> AnnData:
    """Core function for predicting doublets using Scrublet :cite:p:`Wolock2019`.

    Predict cell doublets using a nearest-neighbor classifier of observed
    transcriptomes and simulated doublets.

    Parameters
    ----------
    adata_obs
        The annotated data matrix of shape ``n_obs`` × ``n_vars``. Rows
        correspond to cells and columns to genes. Should be normalised with
        :func:`~scanpy.pp.normalize_total` and filtered to include only highly
        variable genes.
    adata_sim
        Anndata object generated by
        :func:`~scanpy.pp.scrublet_simulate_doublets`, with same number of vars
        as adata_obs. This should have been built from adata_obs after
        filtering genes and cells and selcting highly-variable genes.
    n_neighbors
        Number of neighbors used to construct the KNN graph of observed
        transcriptomes and simulated doublets. If ``None``, this is
        automatically set to ``np.round(0.5 * np.sqrt(n_obs))``.
    expected_doublet_rate
        The estimated doublet rate for the experiment.
    stdev_doublet_rate
        Uncertainty in the expected doublet rate.
    mean_center
        If True, center the data such that each gene has a mean of 0.
        `sklearn.decomposition.PCA` will be used for dimensionality
        reduction.
    normalize_variance
        If True, normalize the data such that each gene has a variance of 1.
        `sklearn.decomposition.TruncatedSVD` will be used for dimensionality
        reduction, unless `mean_center` is True.
    n_prin_comps
        Number of principal components used to embed the transcriptomes prior
        to k-nearest-neighbor graph construction.
    use_approx_neighbors
        Use approximate nearest neighbor method (annoy) for the KNN
        classifier.
    knn_dist_metric
        Distance metric used when finding nearest neighbors. For list of
        valid values, see the documentation for annoy (if `use_approx_neighbors`
        is True) or sklearn.neighbors.NearestNeighbors (if `use_approx_neighbors`
        is False).
    get_doublet_neighbor_parents
        If True, return the parent transcriptomes that generated the
        doublet neighbors of each observed transcriptome. This information can
        be used to infer the cell states that generated a given
        doublet state.
    threshold
        Doublet score threshold for calling a transcriptome a doublet. If
        `None`, this is set automatically by looking for the minimum between
        the two modes of the `doublet_scores_sim_` histogram. It is best
        practice to check the threshold visually using the
        `doublet_scores_sim_` histogram and/or based on co-localization of
        predicted doublets in a 2-D embedding.
    random_state
        Initial state for doublet simulation and nearest neighbors.
    verbose
        If :data:`True`, log progress updates.

    Returns
    -------
    if ``copy=True`` it returns or else adds fields to ``adata``:

    ``.obs['doublet_score']``
        Doublet scores for each observed transcriptome

    ``.obs['predicted_doublets']``
        Boolean indicating predicted doublet status

    ``.uns['scrublet']['doublet_scores_sim']``
        Doublet scores for each simulated doublet transcriptome

    ``.uns['scrublet']['doublet_parents']``
        Pairs of ``.obs_names`` used to generate each simulated doublet transcriptome

    ``.uns['scrublet']['parameters']``
        Dictionary of Scrublet parameters

    """
    # Estimate n_neighbors if not provided, and create scrublet object.

    if n_neighbors is None:
        n_neighbors = int(round(0.5 * np.sqrt(adata_obs.shape[0])))

    # Note: Scrublet() will sparse adata_obs.X if it's not already, but this
    # matrix won't get used if we pre-set the normalised slots.

    scrub = Scrublet(
        adata_obs.X,
        n_neighbors=n_neighbors,
        expected_doublet_rate=expected_doublet_rate,
        stdev_doublet_rate=stdev_doublet_rate,
        random_state=random_state,
    )

    # Ensure normalised matrix sparseness as Scrublet does
    # https://github.com/swolock/scrublet/blob/67f8ecbad14e8e1aa9c89b43dac6638cebe38640/src/scrublet/scrublet.py#L100

    scrub._counts_obs_norm = sparse.csc_matrix(adata_obs.X)
    scrub._counts_sim_norm = sparse.csc_matrix(adata_sim.X)

    scrub.doublet_parents_ = adata_sim.obsm["doublet_parents"]

    # Call scrublet-specific preprocessing where specified

    if mean_center and normalize_variance:
        pipeline.zscore(scrub)
    elif mean_center:
        pipeline.mean_center(scrub)
    elif normalize_variance:
        pipeline.normalize_variance(scrub)

    # Do PCA. Scrublet fits to the observed matrix and decomposes both observed
    # and simulated based on that fit, so we'll just let it do its thing rather
    # than trying to use Scanpy's PCA wrapper of the same functions.

    if mean_center:
        logg.info("Embedding transcriptomes using PCA...")
        pca_torch(scrub, n_prin_comps=n_prin_comps, random_state=scrub._random_state,use_gpu=use_gpu)
        #pipeline.pca(scrub, n_prin_comps=n_prin_comps, random_state=scrub._random_state)
    else:
        logg.info("Embedding transcriptomes using Truncated SVD...")
        pipeline.truncated_svd(
            scrub, n_prin_comps=n_prin_comps, random_state=scrub._random_state
        )

    # Score the doublets

    scrub.calculate_doublet_scores(
        use_approx_neighbors=use_approx_neighbors,
        distance_metric=knn_dist_metric,
        get_doublet_neighbor_parents=get_doublet_neighbor_parents,
    )

    # Actually call doublets

    scrub.call_doublets(threshold=threshold, verbose=verbose)

    # Store results in AnnData for return

    adata_obs.obs["doublet_score"] = scrub.doublet_scores_obs_

    # Store doublet Scrublet metadata

    adata_obs.uns["scrublet"] = {
        "doublet_scores_sim": scrub.doublet_scores_sim_,
        "doublet_parents": adata_sim.obsm["doublet_parents"],
        "parameters": {
            "expected_doublet_rate": expected_doublet_rate,
            "sim_doublet_ratio": (
                adata_sim.uns.get("scrublet", {})
                .get("parameters", {})
                .get("sim_doublet_ratio", None)
            ),
            "n_neighbors": n_neighbors,
            "random_state": random_state,
        },
    }

    # If threshold hasn't been located successfully then we couldn't make any
    # predictions. The user will get a warning from Scrublet, but we need to
    # set the boolean so that any downstream filtering on
    # predicted_doublet=False doesn't incorrectly filter cells. The user can
    # still use this object to generate the plot and derive a threshold
    # manually.

    if hasattr(scrub, "threshold_"):
        adata_obs.uns["scrublet"]["threshold"] = scrub.threshold_
        adata_obs.obs["predicted_doublet"] = scrub.predicted_doublets_
    else:
        adata_obs.obs["predicted_doublet"] = False

    if get_doublet_neighbor_parents:
        adata_obs.uns["scrublet"]["doublet_neighbor_parents"] = (
            scrub.doublet_neighbor_parents_
        )

    return adata_obs


@old_positionals(
    "layer", "sim_doublet_ratio", "synthetic_doublet_umi_subsampling", "random_seed"
)
def scrublet_simulate_doublets(
    adata: AnnData,
    *,
    layer: str | None = None,
    sim_doublet_ratio: float = 2.0,
    synthetic_doublet_umi_subsampling: float = 1.0,
    random_seed: _LegacyRandom = 0,
) -> AnnData:
    r"""Simulate doublets by adding counts of random observed transcriptome pairs.

    Generate synthetic doublets by randomly selecting pairs of observed cells
    and combining their transcriptomes to create artificial doublet profiles
    for training the doublet detection classifier.

    Arguments:
        adata: Annotated data matrix of shape n_obs × n_vars
        layer (str): Layer containing raw values, or None to use .X (default: None)
        sim_doublet_ratio (float): Number of doublets to simulate relative to observed cells (default: 2.0)
        synthetic_doublet_umi_subsampling (float): UMI sampling rate for doublet creation (default: 1.0)
        random_seed (int): Random seed for reproducible doublet simulation (default: 0)

    Returns:
        adata: AnnData object containing simulated doublets with metadata
    """
    X = _get_obs_rep(adata, layer=layer)
    scrub = Scrublet(X, random_state=random_seed)

    scrub.simulate_doublets(
        sim_doublet_ratio=sim_doublet_ratio,
        synthetic_doublet_umi_subsampling=synthetic_doublet_umi_subsampling,
    )

    adata_sim = AnnData(scrub._counts_sim)
    adata_sim.obs["n_counts"] = scrub._total_counts_sim
    adata_sim.obsm["doublet_parents"] = scrub.doublet_parents_
    adata_sim.uns["scrublet"] = {"parameters": {"sim_doublet_ratio": sim_doublet_ratio}}
    return adata_sim

def pca_torch(
    self: Scrublet,
    n_prin_comps: int = 50,
    *,
    random_state: _LegacyRandom = 0,
    svd_solver: Literal["auto", "full", "arpack", "randomized","gesvd", "gesvdj", "gesvda"] = "auto",
    use_gpu: bool = False,
) -> None:
    if self._counts_sim_norm is None:
        msg = "_counts_sim_norm is not set"
        raise RuntimeError(msg)
    

    X_obs = self._counts_obs_norm.toarray()
    X_sim = self._counts_sim_norm.toarray()

    if use_gpu:
        if svd_solver == "auto":
            svd_solver = "gesvd"
        try:
            from torchdr import PCA
        except ImportError:
            raise ImportError("torchdr is not installed. Please install it using `pip install torchdr`.")
        import torch
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        pca = PCA(
            n_components=n_prin_comps, random_state=None, svd_driver=svd_solver,
            device=device,
        ).fit(X_obs)
    else:
        from sklearn.decomposition import PCA
        if svd_solver == "auto":
            svd_solver = "arpack"
        pca = PCA(
            n_components=n_prin_comps, random_state=random_state, svd_solver=svd_solver,
        ).fit(X_obs)
    self.set_manifold(pca.transform(X_obs), pca.transform(X_sim))

