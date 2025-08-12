import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as ss
from sklearn.neighbors import NearestNeighbors


def get_laplacian_mtx(adata,
                      num_neighbors=6,
                      spatial_key='spatial',
                      normalization=False):
    if spatial_key in adata.obsm_keys():
        loc = adata.obsm[spatial_key]
    elif set(spatial_key) <= set(adata.obs_keys()):
        loc = adata.obs[spatial_key]
    else:
        raise KeyError("%s is not available in adata.obsm_keys" % spatial_key + " or adata.obs_keys")
    loc = pd.DataFrame(loc,
                       index=adata.obs_names)
    adj_mtx = compute_knn_adjacency_matrix(loc=loc, k=num_neighbors)
    deg_mtx = adj_mtx.sum(axis=1)
    # deg_mtx = create_degree_mtx(deg_mtx)
    deg_mtx = np.diag(deg_mtx)
    if not normalization:
        lap_mtx = deg_mtx - adj_mtx
    else:
        degrees = np.sum(adj_mtx, axis=1)
        d_inv_sqrt = np.diag(1.0 / np.sqrt(degrees))
        d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0
        lap_mtx = np.eye(deg_mtx.shape[0]) - d_inv_sqrt @ adj_mtx @ d_inv_sqrt

    return lap_mtx, adj_mtx


def compute_knn_adjacency_matrix(loc, k=5):
    # Convert the DataFrame to a numpy array (coordinates)
    X = loc.values

    # Fit the k-NN model
    nn = NearestNeighbors(n_neighbors=k + 1)  # +1 because the point itself is included as its nearest neighbor
    nn.fit(X)

    # Get the indices of the nearest neighbors
    distances, indices = nn.kneighbors(X)

    # Initialize the adjacency matrix with zeros
    adj_matrix = np.zeros((X.shape[0], X.shape[0]), dtype=int)

    # Set the nearest neighbor relationships (excluding the point itself)
    adj_matrix[np.arange(X.shape[0])[:, None], indices[:, 1:]] = 1
    adj_matrix[indices[:, 1:], np.arange(X.shape[0])[:, None]] = 1  # Ensure symmetry

    return adj_matrix


def obtain_spotnet(adata,
                   rad_cutoff=None,
                   k_cutoff=18,
                   spatial_key='spatial',
                   normalization=False,
                   knn_method='Radius',
                   data_type=None,
                   bin_size=None,
                   scale=None):
    from sklearn.neighbors import NearestNeighbors
    from scipy.sparse import csr_matrix
    if scale == None:
        if data_type == 'Visium':
            scale = 150
        elif data_type in ['Stereoseq', 'VisiumHD']:
            scale = 0.75 * bin_size
        elif data_type == 'Slideseq':
            scale = None
        elif data_type == 'ST':
            scale = 300
    coor = pd.DataFrame(adata.obsm[spatial_key])
    coor.index = adata.obs.index
    coor.columns = ['imagerow', 'imagecol']

    KNN_list = []
    if rad_cutoff == None:
        knn_method = 'KNN'

    if knn_method == 'Radius':
        nbrs = NearestNeighbors(radius=rad_cutoff).fit(coor)
        distances, indices = nbrs.radius_neighbors(coor, return_distance=True)
        KNN_list = []
        for it in range(indices.shape[0]):
            KNN_list.append(pd.DataFrame(zip([it] * indices[it].shape[0], indices[it], distances[it])))
    if knn_method == 'KNN':
        nbrs = NearestNeighbors(n_neighbors=k_cutoff + 1).fit(coor)
        distances, indices = nbrs.kneighbors(coor)
        for it in range(indices.shape[0]):
            KNN_list.append(pd.DataFrame(zip([it] * indices.shape[1], indices[it, :], distances[it, :])))

    KNN_df = pd.concat(KNN_list)
    KNN_df.columns = ['Cell1', 'Cell2', 'Distance']
    KNN_df = KNN_df.loc[KNN_df['Distance'] > 0, :]
    if scale is not None:
        KNN_df['Distance'] = KNN_df['Distance'] / KNN_df['Distance'].min() * scale
    KNN_df['InverseDistance'] = 1 / KNN_df['Distance']
    spot_net = csr_matrix((KNN_df['InverseDistance'], (KNN_df['Cell1'], KNN_df['Cell2'])))
    spot_net = (spot_net + spot_net.transpose()) / 2

    return spot_net


def find_hvgs(adata, norm_method=None, num_genes=2000):
    # Normalization
    if norm_method == "CPM":
        sc.pp.normalize_total(adata, target_sum=1e5)
        # log-transform
        sc.pp.log1p(adata)
    else:
        pass
    # Find high variable genes using sc.pp.highly_variable_genes() with default 
    # parameters
    sc.pp.highly_variable_genes(adata, n_top_genes=num_genes)
    HVG_list = adata.var.index[adata.var.highly_variable]
    HVG_list = list(HVG_list)

    return HVG_list


def create_adjacent_mtx(coor_df,
                        spatial_names=['array_row', 'array_col'],
                        num_neighbors=4):
    # Transform coordinate dataframe to coordinate array
    coor_array = coor_df.loc[:, spatial_names].values
    coor_array.astype(np.float32)
    edge_list = []
    num_neighbors += 1
    for i in range(coor_array.shape[0]):
        point = coor_array[i, :]
        distances = np.sum(np.asarray((point - coor_array) ** 2), axis=1)
        distances = pd.DataFrame(distances,
                                 index=range(coor_array.shape[0]),
                                 columns=["distance"])
        distances = distances.sort_values(by='distance', ascending=True)
        neighbors = distances[1:num_neighbors].index.tolist()
        edge_list.extend((i, j) for j in neighbors)
        edge_list.extend((j, i) for j in neighbors)
    # Remove duplicates
    edge_list = set(edge_list)
    edge_list = list(edge_list)
    row_index = []
    col_index = []
    row_index.extend(j[0] for j in edge_list)
    col_index.extend(j[1] for j in edge_list)

    sparse_mtx = ss.coo_matrix((np.ones_like(row_index), (row_index, col_index)),
                               shape=(coor_array.shape[0], coor_array.shape[0]))

    return sparse_mtx


def create_degree_mtx(diag):
    diag = np.array(diag)
    diag = diag.flatten()
    row_index = list(range(diag.size))
    col_index = row_index
    sparse_mtx = ss.coo_matrix((diag, (row_index, col_index)),
                               shape=(diag.size, diag.size))

    return sparse_mtx


def cal_mean_expression(adata, gene_list):
    tmp_adata = adata[:, gene_list].copy()
    if 'log1p' not in adata.uns_keys():
        tmp_adata = sc.pp.log1p(tmp_adata)
    mean_vector = tmp_adata.X.mean(axis=1)
    mean_vector = np.array(mean_vector).ravel()

    return mean_vector


def kneed_select_values(value_list, S=3, increasing=True):
    from kneed import KneeLocator
    x_list = list(range(1, 1 + len(value_list)))
    y_list = value_list.copy()
    if increasing:
        magic = KneeLocator(x=x_list,
                            y=y_list,
                            S=S,
                            curve='convex')
    else:
        y_list = y_list[::-1].copy()
        magic = KneeLocator(x=x_list,
                            y=y_list,
                            direction='decreasing',
                            S=S,
                            curve='convex')
    return magic.elbow


def test_significant_freq(freq_array,
                          cutoff,
                          num_pool=64):
    """
    Significance test by comparing the intensities in low frequency FMs and
    in high frequency FMs.

    Parameters
    ----------
    freq_array : array
        The graph signals of genes in frequency domain.
    cutoff : int
        Watershed between low frequency signals and high frequency signals.
    num_pool : int, optional
        The cores used for multiprocess calculation to accelerate speed. The
        default is 64.

    Returns
    -------
    array
        The calculated p values.

    """
    from scipy.stats import ranksums
    from multiprocessing.dummy import Pool as ThreadPool

    def _test_by_feq(gene_index):
        freq_signal = freq_array[gene_index, :]
        freq_1 = freq_signal[:cutoff]
        freq_1 = freq_1[freq_1 > 0]
        freq_2 = freq_signal[cutoff:]
        freq_2 = freq_2[freq_2 > 0]
        if freq_1.size <= 80 or freq_2.size <= 80:
            freq_1 = np.concatenate((freq_1, freq_1, freq_1, freq_1))
            freq_2 = np.concatenate((freq_2, freq_2, freq_2, freq_2))
        if freq_1.size <= 120 or freq_2.size <= 120:
            freq_1 = np.concatenate((freq_1, freq_1, freq_1))
            freq_2 = np.concatenate((freq_2, freq_2, freq_2))
        if freq_1.size <= 160 or freq_2.size <= 160:
            freq_1 = np.concatenate((freq_1, freq_1))
            freq_2 = np.concatenate((freq_2, freq_2))
        pval = ranksums(freq_1, freq_2, alternative='greater').pvalue
        return pval

    gene_index_list = list(range(freq_array.shape[0]))
    # pool = ThreadPool(num_pool)
    pool = ThreadPool()
    res = pool.map(_test_by_feq, gene_index_list)

    return res
