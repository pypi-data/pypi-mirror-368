r"""Module providing encapsulation of SpaceFlow for spatial flow analysis."""
import random
import numpy as np
import pandas as pd
import scanpy as sc
import torch
from tqdm import tqdm
import torch.nn as nn

import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix
from torch_geometric.nn import GCNConv, DeepGraphInfomax
from sklearn.neighbors import kneighbors_graph
from .._settings import add_reference

sf_install = False

class pySpaceFlow(object):
    r"""SpaceFlow spatial flow analysis class.
    
    SpaceFlow is a deep learning method for analyzing spatial transcriptomics data
    by learning spatially-aware cell representations. It combines graph neural networks
    with spatial regularization to capture both transcriptional and spatial relationships
    between cells.

    The method:
    1. Constructs a spatial neighborhood graph
    2. Learns embeddings using deep graph infomax
    3. Applies spatial regularization to preserve spatial structure
    4. Generates pseudo-spatial maps for trajectory analysis

    Attributes:
        adata: AnnData
            Input annotated data matrix containing:
            - Gene expression data in adata.X
            - Spatial coordinates in adata.obsm['spatial']
        sf: SpaceFlow
            Internal SpaceFlow object for computations
        embedding: array
            Learned spatial-aware embeddings after training

    Examples:
        >>> import scanpy as sc
        >>> import omicverse as ov
        >>> # Load spatial data
        >>> adata = sc.read_visium(...)
        >>> # Initialize SpaceFlow
        >>> spaceflow = ov.space.pySpaceFlow(adata)
        >>> # Train model
        >>> embedding = spaceflow.train(
        ...     spatial_regularization_strength=0.1,
        ...     z_dim=50,
        ...     epochs=1000
        ... )
        >>> # Calculate pseudo-spatial map
        >>> psm = spaceflow.cal_pSM(n_neighbors=20)
    """
    def __init__(self,adata) -> None:
        r"""Initialize SpaceFlow spatial analysis object.
        
        Arguments:
            adata: AnnData
                Annotated data matrix containing:
                - Gene expression data in adata.X
                - Spatial coordinates in adata.obsm['spatial']
                The data should be preprocessed (normalized, scaled)

        Notes:
            - Automatically checks for SpaceFlow package installation
            - Constructs initial spatial neighborhood graph
            - Uses 10 nearest neighbors for graph construction
            - Stores SpaceFlow object in self.sf
        """
        global sf_install
        try:
            from ..external.spaceflow import SpaceFlow
            sf_install=True
        except ImportError as e:
            raise ImportError(
                'Please install the SpaceFlow: `pip install SpaceFlow`.'
            ) from e
        from ..external.spaceflow import SpaceFlow
        sf = SpaceFlow(adata=adata, 
                         spatial_locs=adata.obsm['spatial'])

        spatial_locs = adata.obsm['spatial']
        spatial_graph = sf.graph_alpha(spatial_locs, n_neighbors=10)

        sf.adata_preprocessed = adata
        sf.spatial_graph = spatial_graph
        self.sf = sf
        self.adata = adata

    def train(self,spatial_regularization_strength=0.1, 
              z_dim=50, lr=1e-3, epochs=1000, max_patience=50, 
              min_stop=100, random_seed=42, gpu=0, 
              regularization_acceleration=True, edge_subset_sz=1000000):
        r"""Train SpaceFlow model for spatial embedding.
        
        This method trains a graph neural network to learn spatially-aware cell
        representations using deep graph infomax with spatial regularization.

        Arguments:
            spatial_regularization_strength: float, optional (default=0.1)
                Weight for spatial regularization term.
                Higher values enforce stronger spatial consistency.
            z_dim: int, optional (default=50)
                Dimensionality of learned embedding space.
            lr: float, optional (default=1e-3)
                Learning rate for Adam optimizer.
            epochs: int, optional (default=1000)
                Maximum number of training epochs.
            max_patience: int, optional (default=50)
                Number of epochs to wait for improvement before early stopping.
            min_stop: int, optional (default=100)
                Minimum number of epochs before allowing early stopping.
            random_seed: int, optional (default=42)
                Random seed for reproducibility.
            gpu: int, optional (default=0)
                GPU device index to use. Uses CPU if GPU unavailable.
            regularization_acceleration: bool, optional (default=True)
                Whether to use subsampling for faster regularization.
            edge_subset_sz: int, optional (default=1000000)
                Number of edges to sample for accelerated regularization.
            
        Returns:
            numpy.ndarray
                Learned embedding matrix of shape (n_cells, z_dim).

        Notes:
            - Uses deep graph infomax for self-supervised learning
            - Applies spatial regularization to preserve spatial structure
            - Employs early stopping based on loss convergence
            - Supports GPU acceleration when available
            - Results are stored in adata.obsm['spaceflow']
            - Progress is shown with a progress bar
        """
        from ..external.spaceflow import sparse_mx_to_torch_edge_list, corruption

        adata_preprocessed, spatial_graph = self.sf.adata_preprocessed, self.sf.spatial_graph
        if not adata_preprocessed:
            print("Data has not been preprocessed, please run preprocessing_data() method first!")
            return

        torch.manual_seed(random_seed)
        random.seed(random_seed)
        np.random.seed(random_seed)

        device = f"cuda:{gpu}" if torch.cuda.is_available() else 'cpu'
        model = DeepGraphInfomax(
            hidden_channels=z_dim, encoder=GraphEncoder(adata_preprocessed.shape[1], z_dim),
            summary=lambda z, *args, **kwargs: torch.sigmoid(z.mean(dim=0)),
            corruption=corruption).to(device)

        expr = adata_preprocessed.X.todense() if type(adata_preprocessed.X).__module__ != np.__name__ else adata_preprocessed.X
        expr = torch.tensor(expr).float().to(device)

        edge_list = sparse_mx_to_torch_edge_list(spatial_graph).to(device)

        model.train()
        min_loss = np.inf
        patience = 0
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        best_params = model.state_dict()

        for epoch in tqdm(range(epochs)):
            train_loss = 0.0
            torch.set_grad_enabled(True)
            optimizer.zero_grad()
            z, neg_z, summary = model(expr, edge_list)
            loss = model.loss(z, neg_z, summary)

            coords = torch.tensor(adata_preprocessed.obsm['spatial']).float().to(device)
            if regularization_acceleration or adata_preprocessed.shape[0] > 5000:
                cell_random_subset_1, cell_random_subset_2 = torch.randint(0, z.shape[0], (edge_subset_sz,)).to(
                    device), torch.randint(0, z.shape[0], (edge_subset_sz,)).to(device)
                z1, z2 = torch.index_select(z, 0, cell_random_subset_1), torch.index_select(z, 0, cell_random_subset_2)
                c1, c2 = torch.index_select(coords, 0, cell_random_subset_1), torch.index_select(coords, 0,
                                                                                                 cell_random_subset_1)
                pdist = torch.nn.PairwiseDistance(p=2)

                z_dists = pdist(z1, z2)
                z_dists = z_dists / torch.max(z_dists)

                sp_dists = pdist(c1, c2)
                sp_dists = sp_dists / torch.max(sp_dists)
                n_items = z_dists.size(dim=0)
            else:
                z_dists = torch.cdist(z, z, p=2)
                z_dists = torch.div(z_dists, torch.max(z_dists)).to(device)
                sp_dists = torch.cdist(coords, coords, p=2)
                sp_dists = torch.div(sp_dists, torch.max(sp_dists)).to(device)
                n_items = z.size(dim=0) * z.size(dim=0)

            penalty_1 = torch.div(torch.sum(torch.mul(1.0 - z_dists, sp_dists)), n_items).to(device)
            loss = loss + spatial_regularization_strength * penalty_1

            loss.backward()
            optimizer.step()
            train_loss += loss.item()

            if train_loss > min_loss:
                patience += 1
            else:
                patience = 0
                min_loss = train_loss
                best_params = model.state_dict()
            if patience > max_patience and epoch > min_stop:
                break

        model.load_state_dict(best_params)

        z, _, _ = model(expr, edge_list)
        embedding = z.cpu().detach().numpy()

        self.sf.embedding = embedding
        self.adata.obsm['spaceflow']=self.sf.embedding.copy()
        add_reference(self.adata,'SpaceFlow','embedding with SpaceFlow')

        return embedding

    def cal_pSM(self,n_neighbors:int=20,resolution:int=1,
                       max_cell_for_subsampling:int=5000,
                       psm_key='pSM_spaceflow'):
        r"""Calculate pseudo-spatial map using diffusion pseudotime.
        
        This method constructs a pseudo-spatial map by computing diffusion pseudotime
        on the learned embeddings, useful for analyzing spatial trajectories and
        organization patterns.

        Arguments:
            n_neighbors: int, optional (default=20)
                Number of neighbors for kNN graph construction.
                Higher values create denser connectivity.
            resolution: int, optional (default=1)
                Resolution parameter for Leiden clustering.
                Higher values yield more fine-grained clusters.
            max_cell_for_subsampling: int, optional (default=5000)
                Maximum number of cells to use for distance calculations.
                Enables analysis of large datasets through subsampling.
            psm_key: str, optional (default='pSM_spaceflow')
                Key in adata.obs where pseudo-spatial map values will be stored.

        Returns:
            numpy.ndarray
                Pseudo-spatial map values for each cell.

        Notes:
            - Constructs neighborhood graph from embeddings
            - Performs UMAP and Leiden clustering
            - Uses PAGA for trajectory inference
            - Computes diffusion pseudotime
            - Results are stored in adata.obs[psm_key]
            - Useful for ordering cells along spatial axes
            - Handles large datasets through subsampling
        """
        sc.pp.neighbors(self.adata, n_neighbors=n_neighbors,
               use_rep='spaceflow')
        sc.tl.umap(self.adata)
        sc.tl.leiden(self.adata, resolution=resolution)
        sc.tl.paga(self.adata)

        if self.adata.shape[0] < max_cell_for_subsampling:
            sub_adata_x = self.adata.obsm['spaceflow']
        else:
            indices = np.arange(self.adata.shape[0])
            selected_ind = np.random.choice(indices, max_cell_for_subsampling, False)
            sub_adata_x = self.adata[selected_ind, :].obsm['spaceflow']

        sum_dists = distance_matrix(sub_adata_x, sub_adata_x).sum(axis=1)
        self.adata.uns['iroot'] = np.argmax(sum_dists)
        sc.tl.diffmap(self.adata)
        sc.tl.dpt(self.adata)
        self.adata.obs.rename({"dpt_pseudotime": psm_key}, axis=1, inplace=True)
        print(f'The pseudo-spatial map values are stored in adata.obs["{psm_key}"].')
        add_reference(self.adata,'SpaceFlow','pseudo-spatial map with SpaceFlow')
        psm_values = self.adata.obs[psm_key].to_numpy()
        return psm_values


class GraphEncoder(nn.Module):
    r"""Graph convolutional encoder for SpaceFlow.
    
    This class implements a two-layer graph convolutional network (GCN) that serves
    as the encoder component in the SpaceFlow model. It learns to transform gene
    expression data into a spatially-aware latent representation.

    Architecture:
    1. Input layer: Gene expression features
    2. First GCN layer with PReLU activation
    3. Second GCN layer with PReLU activation
    4. Output layer: Learned embeddings

    Attributes:
        conv1: GCNConv
            First graph convolutional layer
        conv2: GCNConv
            Second graph convolutional layer
        prelu: PReLU
            Parametric ReLU activation function

    Notes:
        - Uses PyTorch Geometric's GCNConv implementation
        - Learns spatially-aware representations
        - Preserves both local and global structure
        - Part of the deep graph infomax framework
    """
    def __init__(self, in_channels, hidden_channels):
        super(GraphEncoder, self).__init__()
        self.conv = GCNConv(in_channels, hidden_channels, cached=False)
        self.prelu = nn.PReLU(hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels, cached=False)
        self.prelu2 = nn.PReLU(hidden_channels)

    def forward(self, x, edge_index):
        r"""Forward propagation through graph encoder.
        
        Arguments:
            x: Input node features.
            edge_index: Graph edge indices.
            
        Returns:
            Encoded node representations.
        """
        x = self.conv(x, edge_index)
        x = self.prelu(x)
        x = self.conv2(x, edge_index)
        x = self.prelu2(x)
        return x
    # End-of-file (EOF)
