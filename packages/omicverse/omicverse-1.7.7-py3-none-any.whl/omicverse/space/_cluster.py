"""Module providing a encapsulation of pySTAGATE."""
import torch
from torch_geometric.loader import DataLoader
from tqdm import tqdm
import torch.nn.functional as F
from ..external.STAGATE_pyG import Batch_Data,Cal_Spatial_Net,Transfer_pytorch_Data,Stats_Spatial_Net,STAGATE
import scanpy as sc
from anndata import AnnData
import numpy as np
import os
from scipy.sparse import csr_matrix
from .._settings import add_reference

class pySTAGATE:
    """
    A class representing the PyTorch implementation of STAGATE (Spatial Transcriptomics Analysis using Graph Attention autoEncoder).

    Arguments:
        adata: AnnData object
            Annotated data matrix containing spatial transcriptomics data.
        num_batch_x: int
            Number of batches in x direction for spatial partitioning.
        num_batch_y: int
            Number of batches in y direction for spatial partitioning.
        spatial_key: list, optional (default=['X','Y'])
            List of keys in adata.obs containing spatial coordinates.
        batch_size: int, optional (default=1)
            Size of batches for training.
        rad_cutoff: int, optional (default=200)
            Radius cutoff for spatial network construction.
        num_epoch: int, optional (default=1000)
            Number of epochs for training.
        lr: float, optional (default=0.001)
            Learning rate for optimization.
        weight_decay: float, optional (default=1e-4)
            Weight decay (L2 penalty) for optimization.
        hidden_dims: list, optional (default=[512, 30])
            List of hidden dimensions for the neural network layers.
        device: str, optional (default='cuda:0')
            Device to run the model on ('cuda:0' or 'cpu').

    Attributes:
        device: torch.device
            Device where the model is running.
        loader: DataLoader
            PyTorch DataLoader for batch processing.
        model: STAGATE
            The STAGATE model instance.
        optimizer: torch.optim.Adam
            Adam optimizer for model training.
        adata: AnnData
            Input annotated data matrix.
        data: torch_geometric.data.Data
            PyTorch geometric data object.

    Notes:
        The STAGATE model is designed for analyzing spatial transcriptomics data by incorporating
        spatial information through a graph attention autoencoder architecture.

    Examples:
        >>> import scanpy as sc
        >>> import omicverse as ov
        >>> adata = sc.read_h5ad('spatial_data.h5ad')
        >>> stagate = ov.space.pySTAGATE(adata, num_batch_x=3, num_batch_y=2)
        >>> stagate.train()
        >>> stagate.predicted()
    """

    def __init__(self,
                 adata: AnnData,
                 num_batch_x,
                 num_batch_y,
                 spatial_key: list = ['X','Y'],
                 batch_size: int = 1,
                rad_cutoff: int = 200,
                num_epoch: int = 1000,
                lr: float = 0.001,
                weight_decay: float = 1e-4,
                hidden_dims: list = [512, 30],
                device: str = 'cuda:0')-> None:
        # Initialize device
        device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.device=device

        # Create batches
        batch_list = Batch_Data(adata, num_batch_x=num_batch_x, num_batch_y=num_batch_y,
                                    spatial_key=spatial_key, plot_Stats=True)
        for temp_adata in batch_list:
            Cal_Spatial_Net(temp_adata, rad_cutoff=rad_cutoff)

        # Transfer to PyTorch data format
        #device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        data_list = [Transfer_pytorch_Data(adata) for adata in batch_list]
        for temp in data_list:
            temp.to(device)

        Cal_Spatial_Net(adata, rad_cutoff=rad_cutoff)
        data = Transfer_pytorch_Data(adata)
        Stats_Spatial_Net(adata)

        # batch_size=1 or 2
        self.loader = DataLoader(data_list, batch_size=batch_size, shuffle=True)

        # hyper-parameters
        self.num_epoch = num_epoch
        self.lr=lr
        self.weight_decay=weight_decay
        self.hidden_dims = hidden_dims
        self.adata=adata
        self.data=data

        # Model and optimizer
        self.model = STAGATE(hidden_dims = [data_list[0].x.shape[1]]+self.hidden_dims).to(device)
        self.optimizer = torch.optim.Adam(self.model.parameters(),
                                            lr=self.lr,
                                            weight_decay=self.weight_decay)

    def train(self):
        """
        Train the STAGATE model using the configured parameters.

        This method performs training of the STAGATE model for the specified number of epochs.
        For each epoch, it processes batches of data, computes the loss using mean squared error,
        and updates the model parameters through backpropagation.

        Arguments:
            None

        Returns:
            None

        Notes:
            - The training progress is displayed using a progress bar.
            - Gradient clipping is applied with a maximum norm of 5.
            - The model is automatically moved to the specified device (GPU/CPU).
        """       
        for epoch in tqdm(range(1, self.num_epoch+1)):
            for batch in self.loader:
                self.model.train()
                self.optimizer.zero_grad()
                z, out = self.model(batch.x, batch.edge_index)
                loss = F.mse_loss(batch.x, out) #F.nll_loss(out[data.train_mask], data.y[data.train_mask])
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 5.)
                self.optimizer.step()
        # The total network
        self.data.to(self.device)

    def predicted(self):
        """
        Generate STAGATE representations and reconstruction values for all cells.

        This method runs the trained model in evaluation mode to generate:
        1. STAGATE embeddings (stored in adata.obsm['STAGATE'])
        2. Reconstructed expression values (stored in adata.layers['STAGATE_ReX'])

        Arguments:
            None

        Returns:
            None

        Notes:
            - Negative values in reconstructed expression are set to 0
            - Results are stored directly in the AnnData object:
                - STAGATE embeddings: adata.obsm['STAGATE']
                - Reconstructed expression: adata.layers['STAGATE_ReX']
        """
        self.model.eval()
        z, out = self.model(self.data.x, self.data.edge_index)

        stagate_rep = z.to('cpu').detach().numpy()
        self.adata.obsm['STAGATE'] = stagate_rep
        rex = out.to('cpu').detach().numpy()
        rex[rex<0] = 0
        self.adata.layers['STAGATE_ReX'] = rex

        print('The STAGATE representation values are stored in adata.obsm["STAGATE"].')
        print('The rex values are stored in adata.layers["STAGATE_ReX"].')

    def cal_pSM(self, n_neighbors:int=20, resolution:int=1,
                max_cell_for_subsampling:int=5000,
                psm_key:str='pSM_STAGATE'):
        """
        Calculate the pseudo-spatial map using diffusion pseudotime (DPT) algorithm.

        This method computes a pseudo-spatial map by:
        1. Constructing a kNN graph using STAGATE embeddings
        2. Performing UMAP and Leiden clustering
        3. Computing diffusion pseudotime
        4. Storing results in the AnnData object

        Arguments:
            n_neighbors: int, optional (default=20)
                Number of neighbors for the kNN graph construction.
            resolution: float, optional (default=1)
                Resolution parameter for Leiden clustering.
            max_cell_for_subsampling: int, optional (default=5000)
                Maximum number of cells to use for distance calculation.
                If exceeded, cells will be subsampled.
            psm_key: str, optional (default='pSM_STAGATE')
                Key under which to store the pseudo-spatial map in adata.obs.

        Returns:
            numpy.ndarray
                Array containing the computed pseudo-spatial map values.

        Notes:
            - If number of cells exceeds max_cell_for_subsampling, random subsampling is performed
            - The root cell for pseudotime calculation is chosen as the cell with maximum
              total distance to all other cells
            - Results are stored in adata.obs[psm_key]
        """

        from scipy.spatial import distance_matrix
        import numpy as np

        sc.pp.neighbors(self.adata, n_neighbors=n_neighbors,
               use_rep='STAGATE')
        sc.tl.umap(self.adata)
        sc.tl.leiden(self.adata, resolution=resolution)
        sc.tl.paga(self.adata)
       # max_cell_for_subsampling = max_cell_for_subsampling
        if self.adata.shape[0] < max_cell_for_subsampling:
            sub_adata_x = self.adata.obsm['STAGATE']
        else:
            indices = np.arange(self.adata.shape[0])
            selected_ind = np.random.choice(indices, max_cell_for_subsampling, False)
            sub_adata_x = self.adata[selected_ind, :].obsm['STAGATE']

        sum_dists = distance_matrix(sub_adata_x, sub_adata_x).sum(axis=1)
        self.adata.uns['iroot'] = np.argmax(sum_dists)
        sc.tl.diffmap(self.adata)
        sc.tl.dpt(self.adata)
        self.adata.obs.rename({"dpt_pseudotime": psm_key}, axis=1, inplace=True)
        print(f'The pseudo-spatial map values are stored in adata.obs["{psm_key}"].')

        psm_values = self.adata.obs[psm_key].to_numpy()
        return psm_values
        # End-of-file (EOF)


def clusters(adata,
             methods,
             methods_kwargs,
             batch_key=None,
             lognorm=50*1e4,
             ):
    """
    Perform clustering analysis on spatial transcriptomics data using multiple methods.

    This function supports multiple clustering methods including STAGATE, GraphST, CAST, and BINARY.
    Each method processes the spatial data differently and stores its results in the AnnData object.

    Arguments:
        adata: AnnData
            Annotated data matrix containing spatial transcriptomics data.
        methods: list
            List of methods to use for clustering. Supported methods are:
            - 'STAGATE': Graph attention autoencoder-based clustering
            - 'GraphST': Graph-based spatial transcriptomics clustering
            - 'CAST': Clustering And Spatial Transcriptomics
            - 'BINARY': Binary-based spatial clustering
        methods_kwargs: dict
            Dictionary containing method-specific parameters. Each key should correspond
            to a method name and contain a dictionary of parameters for that method.
        batch_key: str, optional (default=None)
            Key in adata.obs for batch information. If None, all cells are treated as one batch.
        lognorm: float, optional (default=50*1e4)
            Normalization factor for log transformation when recovering counts.

    Returns:
        AnnData
            The input AnnData object with added clustering results in various slots:
            - STAGATE: Results in adata.obsm['STAGATE'] and adata.layers['STAGATE_ReX']
            - GraphST: Results in adata.obsm['GraphST_embedding']
            - CAST: Results in adata.obsm['X_cast']
            - BINARY: Results in adata.obsm['BINARY']

    Notes:
        - For STAGATE: If n_top_genes is specified, highly variable genes are selected
        - For GraphST: Requires counts matrix in adata.layers['counts']
        - For CAST: Requires spatial coordinates in adata.obsm['spatial']
        - For BINARY: Can handle both raw counts and normalized data

    Examples:
        >>> import scanpy as sc
        >>> import omicverse as ov
        >>> adata = sc.read_h5ad('spatial_data.h5ad')
        >>> methods = ['STAGATE', 'GraphST']
        >>> methods_kwargs = {
        ...     'STAGATE': {'num_batch_x': 3, 'num_batch_y': 2},
        ...     'GraphST': {'device': 'cuda:0', 'n_pcs': 30}
        ... }
        >>> adata = ov.space.clusters(adata, methods, methods_kwargs)
    """
    from scipy.sparse import issparse
    from ..external.GraphST import GraphST

    for method in methods:
        if method=='STAGATE':
            print('The STAGATE method is used to cluster the spatial data.')
            adata_copy=adata.copy()
            if issparse(adata_copy.obsm['spatial']):
                adata_copy.obsm['spatial']=adata_copy.obsm['spatial'].toarray()
            adata_copy.obs['X']=adata_copy.obsm['spatial'][:,0]
            adata_copy.obs['Y']=adata_copy.obsm['spatial'][:,1]
            if 'STAGATE' not in methods_kwargs:
                methods_kwargs['STAGATE']={'num_batch_x':3,'num_batch_y':2,
                                           'spatial_key':['X','Y'],'rad_cutoff':200,'num_epoch':1000,'lr':0.001,
                                           'weight_decay':1e-4,'hidden_dims':[512, 30],'device':'cuda:0',
                                           'n_top_genes':2000}
            if 'n_top_genes' in methods_kwargs['STAGATE']:
                sc.pp.highly_variable_genes(adata_copy, flavor="seurat_v3", 
                                            n_top_genes=methods_kwargs['STAGATE']['n_top_genes'])
                del methods_kwargs['STAGATE']['n_top_genes']

            STA_obj=pySTAGATE(adata_copy,**methods_kwargs['STAGATE'])
            STA_obj.train()
            STA_obj.predicted()
            adata.obsm['STAGATE']=adata_copy.obsm['STAGATE']
            adata.layers['STAGATE_ReX']=adata_copy.layers['STAGATE_ReX']
            print(f'The STAGATE embedding are stored in adata.obsm["STAGATE"].\nShape: {adata.obsm["STAGATE"].shape}')
            add_reference(adata,'STAGATE','clustering with STAGATE')

        elif method=='GraphST':
            print('The GraphST method is used to embed the spatial data.')
            adata_copy=adata.copy()
            if 'GraphST' not in methods_kwargs:
                methods_kwargs['GraphST']={'device':'cuda:0','n_pcs':30,
                                           }
            if 'counts' not in adata_copy.layers:
                from ..pp import recover_counts
                if issparse(adata_copy.X):
                    pass 
                else:
                    adata_copy.X=csr_matrix(adata_copy.X)
                print('Recover the counts matrix from log-normalized data.')
                X_counts_recovered, size_factors_sub=recover_counts(adata_copy.X, lognorm, 
                                                                    lognorm*10,  log_base=None, 
                                                          chunk_size=10000)
                adata_copy.X=X_counts_recovered
            else:
                adata_copy.X=adata_copy.layers['counts']
            
            GRT_obj=GraphST(adata_copy, **methods_kwargs['GraphST'])
            adata_copy=GRT_obj.train()
            adata.obsm['GraphST_embedding']=adata_copy.obsm['GraphST_embedding']
            adata.obsm['graphst|original|X_pca']=adata_copy.obsm['graphst|original|X_pca']

            print(f'The GraphST embedding are stored in adata.obsm["GraphST_embedding"]. \nShape: {adata.obsm["GraphST_embedding"].shape}')
            add_reference(adata,'GraphST','clustering with GraphST')

        elif method=='CAST':
            print('The CAST method is used to embed the spatial data.')
            if issparse(adata.obsm['spatial']):
                adata.obsm['spatial']=adata.obsm['spatial'].toarray()
            adata.obs['X']=adata.obsm['spatial'][:,0]
            adata.obs['Y']=adata.obsm['spatial'][:,1]

            if batch_key is None:
                adata.obs['CAST_sample']='sample1'
            else:
                adata.obs['CAST_sample']=adata.obs[batch_key]
            
            if 'CAST' not in methods_kwargs:
                methods_kwargs['CAST']={'output_path_t':'result/CAST_gas/output',
                                        'device':'cuda:0',
                                        'gpu_t':0}
            # Get the coordinates and expression data for each sample
            samples = np.unique(adata.obs['CAST_sample']) # used samples in adata
            coords_raw = {sample_t: np.array(adata.obs[['X','Y']])[adata.obs['CAST_sample'] == sample_t] for sample_t in samples}
            
            if ('norm_1e4' not in adata.layers) and ('counts' in adata.layers):
                adata.layers['norm_1e4'] = sc.pp.normalize_total(adata, target_sum=1e4, layer='counts',
                                                 inplace=False)['X'].toarray() # we use normalized counts for each cell as input gene expression
                exp_dict = {sample_t: adata[adata.obs['CAST_sample'] == sample_t].layers['norm_1e4'] for sample_t in samples}
            else:
                exp_dict = {sample_t: adata[adata.obs['CAST_sample'] == sample_t].X for sample_t in samples}
            
            output_path = methods_kwargs['CAST']['output_path_t']
            os.makedirs(output_path, exist_ok=True)

            from ..external.CAST import CAST_MARK
            embed_dict = CAST_MARK(coords_raw,exp_dict,**methods_kwargs['CAST'])

            from tqdm import tqdm
            adata.obsm['X_cast']=np.zeros((adata.shape[0],512))
            import pandas as pd
            adata.obsm['X_cast']=pd.DataFrame(adata.obsm['X_cast'],index=adata.obs.index)
            for key in tqdm(embed_dict.keys()):
                adata.obsm['X_cast'].loc[adata.obs['CAST_sample']==key]+=embed_dict[key].cpu().numpy()
            adata.obsm['X_cast']=adata.obsm['X_cast'].values
            print(f'The CAST embedding are stored in adata.obsm["X_cast"]. \nShape: {adata.obsm["X_cast"].shape}')
            add_reference(adata,'CAST','embedding with CAST')
        elif method=='BINARY':
            print('The BINARY method is used to embed the spatial data.')
            from ..external import BINARY
            if batch_key is None:
                adata.obs['BINARY_sample']='sample1'
            else:
                adata.obs['BINARY_sample']=adata.obs[batch_key]
            if 'BINARY' not in methods_kwargs:
                methods_kwargs['BINARY']={'use_method':'KNN',
                                          'cutoff':6,
                                          'obs_key':'BINARY_sample',
                                          'use_list':None,
                                          'pos_weight':10,
                                          'device':'cuda:0',
                                          'hidden_dims':[512, 30],
                                            'n_epochs': 1000,
                                            'lr':  0.001,
                                            'key_added': 'BINARY',
                                            'gradient_clipping': 5,
                                            'weight_decay': 0.0001,
                                            'verbose': True,
                                            'random_seed':0,
                                            #'lognorm':50*1e4,
                                            'n_top_genes':2000}
            adata_copy = BINARY.clean_adata(adata, save_obs=[methods_kwargs['BINARY']['obs_key']])
            if 'counts' in adata.layers:
                adata_copy.X=adata[adata_copy.obs.index].layers['counts']
            if 'counts' not in adata_copy.layers:
                from ..pp import recover_counts
                if issparse(adata_copy.X):
                    pass 
                else:
                    adata_copy.X=csr_matrix(adata_copy.X)
                print('Recover the counts matrix from log-normalized data.')
                X_counts_recovered, size_factors_sub=recover_counts(adata_copy.X, lognorm, 
                                                                    lognorm*10,  log_base=None, 
                                                          chunk_size=10000)
                adata_copy.X=X_counts_recovered
            else:
                adata_copy.X=adata_copy.layers['counts']
                #recover_counts(adata_copy.X, mult_value, max_range, log_base=None, chunk_size=1000)
            adata_copy = BINARY.Count2Binary(adata_copy)
            if 'n_top_genes' in methods_kwargs['BINARY']:
                sc.pp.highly_variable_genes(adata_copy, flavor="seurat_v3", n_top_genes=methods_kwargs['BINARY']['n_top_genes'])

            BINARY.Mutil_Construct_Spatial_Graph(adata_copy,
                                           use_method=methods_kwargs['BINARY']['use_method'],
                                           cutoff=methods_kwargs['BINARY']['cutoff'],
                                           obs_key=methods_kwargs['BINARY']['obs_key'],
                                           use_list=methods_kwargs['BINARY']['use_list'],
                                     )
            adata_copy = BINARY.train_BINARY(adata_copy,pos_weight=methods_kwargs['BINARY']['pos_weight'],
                                            device=methods_kwargs['BINARY']['device'],
                                            hidden_dims=methods_kwargs['BINARY']['hidden_dims'],
                                            n_epochs=methods_kwargs['BINARY']['n_epochs'],
                                            lr=methods_kwargs['BINARY']['lr'],
                                            key_added=methods_kwargs['BINARY']['key_added'],
                                            gradient_clipping=methods_kwargs['BINARY']['gradient_clipping'],
                                            weight_decay=methods_kwargs['BINARY']['weight_decay'],
                                            verbose=methods_kwargs['BINARY']['verbose'],
                                            random_seed=methods_kwargs['BINARY']['random_seed'])
            adata.obsm['BINARY']=adata_copy.obsm['BINARY']
            adata.uns['Spatial_Graph']=adata_copy.uns['Spatial_Graph']
            print(f'The binary embedding are stored in adata.obsm["BINARY"]. \nShape: {adata.obsm["BINARY"].shape}')
            add_reference(adata,'BINARY','clustering with BINARY')
        else:
            print(f'The method {method} is not supported.')
    return adata

def merge_cluster(adata,
                  groupby='mclust',
                  use_rep='STAGATE',
                  threshold=0.05,
                  plot=True,
                  start_idx=0,
                  **kwargs):
    """
    Merge clusters based on hierarchical clustering of their representation.

    This function performs hierarchical clustering on existing clusters and merges them
    based on a distance threshold. It can optionally visualize the dendrogram showing
    the merging process.

    Arguments:
        adata: AnnData
            Annotated data matrix containing cluster information.
        groupby: str, optional (default='mclust')
            Key in adata.obs containing the cluster labels to be merged.
        use_rep: str, optional (default='STAGATE')
            Key in adata.obsm to use for calculating distances between clusters.
        threshold: float, optional (default=0.05)
            Distance threshold for merging clusters. Lower values result in more merging.
        plot: bool, optional (default=True)
            Whether to plot the dendrogram with the merging threshold line.
        start_idx: int, optional (default=0)
            Starting index for cluster numbering in the output.
        **kwargs:
            Additional arguments passed to scanpy.pl.dendrogram().

    Returns:
        dict
            Dictionary mapping original cluster labels to merged cluster labels.

    Notes:
        - The function uses scipy's hierarchical clustering implementation
        - Merged clusters are stored in adata.obs[f'{groupby}_tree']
        - The dendrogram is stored in adata.uns[f'dendrogram_{groupby}']
        - Cluster labels in the output are prefixed with 'c'

    Examples:
        >>> import scanpy as sc
        >>> import omicverse as ov
        >>> adata = sc.read_h5ad('clustered_data.h5ad')
        >>> # Merge clusters using STAGATE representation
        >>> cluster_map = ov.space.merge_cluster(adata, 
        ...                                      groupby='leiden',
        ...                                      use_rep='STAGATE',
        ...                                      threshold=0.1)
        >>> # Access merged clusters
        >>> print(adata.obs['leiden_tree'])
    """
    sc.tl.dendrogram(adata,groupby=groupby,use_rep=use_rep)
    import numpy as np
    from scipy.cluster.hierarchy import fcluster

    # 你的链接矩阵
    linkage_matrix = adata.uns[f'dendrogram_{groupby}']['linkage']

    # 选择一个阈值来确定簇
    #threshold = 0.05  # 这个值需要根据具体情况调整

    # 使用fcluster来合并类别
    clusters = fcluster(linkage_matrix, threshold, criterion='distance')
    
    # 创建字典
    cluster_dict = {}
    for idx, cluster_id in enumerate(clusters):
        key = f'c{cluster_id}'
        if key not in cluster_dict:
            cluster_dict[key] = []
        cluster_dict[key].append(idx+start_idx)
    
    reversed_dict = {}
    for key, values in cluster_dict.items():
        for value in values:
            reversed_dict[str(value)] = key
    
    #adata.obs['mclust_tree']=adata.obs['mclust'].map(reversed_dict)
    adata.obs[groupby]=adata.obs[groupby].astype(str)
    adata.obs[f'{groupby}_tree']=adata.obs[groupby].map(reversed_dict)
    print(f'The merged cluster information is stored in adata.obs["{groupby}_tree"].')
    if plot:
        ax=sc.pl.dendrogram(adata,groupby=groupby,show=False,**kwargs)
        ax.plot((ax.get_xticks().min(),ax.get_xticks().max()),(threshold,threshold))
    return reversed_dict