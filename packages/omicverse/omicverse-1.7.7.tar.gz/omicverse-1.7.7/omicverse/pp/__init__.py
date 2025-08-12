r"""
Preprocessing utilities for single-cell and bulk omics data.

This module provides essential preprocessing functions for quality control,
normalization, dimensionality reduction, and neighborhood analysis of omics data.
It supports both CPU and GPU computation for large-scale datasets.

Core preprocessing functions:
    preprocess: Complete preprocessing pipeline
    normalize_pearson_residuals: Pearson residuals normalization
    highly_variable_genes: Identify highly variable genes
    scale: Z-score scaling of expression data
    regress: Regress out unwanted variation
    
Dimensionality reduction:
    pca: Principal component analysis
    mde: Minimum distortion embedding
    tsne: t-SNE embedding
    umap: UMAP embedding
    
Neighborhood analysis:
    neighbors: Compute neighborhood graph
    leiden: Leiden clustering
    louvain: Louvain clustering
    
Quality control:
    quantity_control: Comprehensive QC metrics
    filter_cells: Remove low-quality cells
    filter_genes: Remove low-quality genes
    
Utility functions:
    anndata_to_GPU: Transfer data to GPU
    anndata_to_CPU: Transfer data to CPU
    recover_counts: Recover original count data
    score_genes_cell_cycle: Cell cycle scoring

Examples:
    >>> import omicverse as ov
    >>> # Basic preprocessing pipeline
    >>> ov.pp.preprocess(adata, mode='shiftlog|pearson', n_HVGs=2000)
    >>> ov.pp.scale(adata)
    >>> ov.pp.pca(adata)
    >>> 
    >>> # Quality control
    >>> ov.pp.qc(adata, tresh={'mito_perc': 20, 'nUMIs': 1000})
    >>> ov.pp.filter_cells(adata, min_genes=200)
    >>> ov.pp.filter_genes(adata, min_cells=3)
    
    >>> # Neighborhood analysis
    >>> ov.pp.neighbors(adata, n_neighbors=15, n_pcs=50)
    >>> ov.pp.leiden(adata, resolution=0.5)
    >>> ov.pp.umap(adata)
"""

from ._preprocess import (identify_robust_genes,
                          select_hvf_pegasus,
                          highly_variable_features,
                          remove_cc_genes,
                          preprocess,
                          normalize_pearson_residuals,
                          highly_variable_genes,
                          scale,
                          regress,
                          regress_and_scale,
                          neighbors,
                          pca,score_genes_cell_cycle,
                          leiden,umap,louvain,anndata_to_GPU,anndata_to_CPU,mde,tsne)

from ._qc import qc,filter_cells,filter_genes
from ._recover import recover_counts,binary_search

__all__ = [
    # Core preprocessing
    'identify_robust_genes',
    'select_hvf_pegasus',
    'highly_variable_features',
    'remove_cc_genes',
    'preprocess',
    'normalize_pearson_residuals',
    'highly_variable_genes',
    'scale',
    'regress',
    'regress_and_scale',
    
    # Dimensionality reduction
    'pca',
    'mde',
    'tsne',
    'umap',
    
    # Neighborhood and clustering
    'neighbors',
    'leiden',
    'louvain',
    
    # Quality control
    'quantity_control',
    'qc',
    'filter_cells',
    'filter_genes',
    
    # Utility functions
    'score_genes_cell_cycle',
    'anndata_to_GPU',
    'anndata_to_CPU',
    'recover_counts',
    'binary_search',
]