import numpy as np
import pandas as pd
import scipy.sparse as ss


def extract_lr(adata, species, min_cell=0):
    """
    :param species: only 'human' or 'mouse' is supported
    :param min_cell: for each selected pair, the spots logcountsressing ligand or receptor should be larger than the min,
    respectively.
    """
    if species == 'mouse':
        geneInter = pd.read_csv('https://figshare.com/ndownloader/files/36638919', index_col=0)
        comp = pd.read_csv('https://figshare.com/ndownloader/files/36638916', header=0, index_col=0)

    elif species == 'human':
        geneInter = pd.read_csv('https://figshare.com/ndownloader/files/36638943', header=0, index_col=0)
        comp = pd.read_csv('https://figshare.com/ndownloader/files/36638940', header=0, index_col=0)
    else:
        raise ValueError("species type: {} is not supported currently. Please have a check.".format(species))
    ligand = geneInter.ligand.values
    receptor = geneInter.receptor.values
    t = []
    for i in range(len(ligand)):
        for n in [ligand, receptor]:
            l = n[i]
            if l in comp.index:
                n[i] = comp.loc[l].dropna().values[pd.Series \
                    (comp.loc[l].dropna().values).isin(adata.var_names)]
            else:
                n[i] = pd.Series(l).values[pd.Series(l).isin(adata.var_names)]
        if (len(ligand[i]) > 0) * (len(receptor[i]) > 0):
            if (sum(adata[:, ligand[i]].X.mean(axis=1) > 0) >= min_cell) * \
                    (sum(adata[:, ligand[i]].X.mean(axis=1) > 0) >= min_cell):
                t.append(True)
            else:
                t.append(False)
        else:
            t.append(False)
    lr_info = {}
    lr_info['ligand'] = [tmp.tolist() for tmp in ligand[t]]
    lr_info['receptor'] = [tmp.tolist() for tmp in receptor[t]]
    lr_info['interaction'] = geneInter[t].index.tolist()

    adata.uns['lr_info'] = lr_info
    pass


def communicate_score(adata):
    interact_df = pd.DataFrame(0, index=adata.obs_names,
                               columns=adata.uns['lr_info']['interaction'])

    def _calculate_score_d(lr_index):
        l_express = adata[:, adata.uns['lr_info']['ligand'][lr_index]].X
        l_express = l_express.sum(axis=1)
        r_express = adata[:, adata.uns['lr_info']['receptor'][lr_index]].X
        r_express = r_express.sum(axis=1)
        scores_l = np.matmul(adata.uns['spatial_graph'], r_express)
        scores_l = np.multiply(l_express, scores_l)
        scores_r = np.matmul(adata.uns['spatial_graph'], l_express)
        scores_r = np.multiply(l_express, scores_r)
        interact_df.iloc[:, lr_index] = scores_l + scores_r

    def _calculate_score_s(lr_index):
        l_express = adata[:, adata.uns['lr_info']['ligand'][lr_index]].X.toarray()
        l_express = l_express.sum(axis=1)
        r_express = adata[:, adata.uns['lr_info']['receptor'][lr_index]].X.toarray()
        r_express = r_express.sum(axis=1)
        scores_l = np.matmul(adata.uns['spatial_graph'], r_express)
        scores_l = np.multiply(l_express, scores_l)
        scores_r = np.matmul(adata.uns['spatial_graph'], l_express)
        scores_r = np.multiply(l_express, scores_r)
        interact_df.iloc[:, lr_index] = scores_l + scores_r

    if ss.issparse(adata.X):
        for lr_index in range(len(adata.obsm['lr_info']['ligand'])):
            _calculate_score_s(lr_index)
    else:
        for lr_index in range(len(adata.obsm['lr_info']['ligand'])):
            _calculate_score_d(lr_index)

    adata.obsm['commu_score'] = interact_df
