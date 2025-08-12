import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as ss
from scipy.stats import pearsonr, spearmanr
from sklearn import preprocessing


def extract_lr(adata, species, lr_database_path, min_cell=1):
    """
    :param species: only 'human' or 'mouse' is supported
    :param min_cell: for each selected pair, the spots logcountsressing ligand or receptor should be larger than the min,
    respectively.
    """
    sparse_state = False
    if ss.issparse(adata.X):
        sparse_state = True
        adata.X = adata.X.todense()
    if species == 'mouse':
        geneInter = pd.read_csv(
            f'{lr_database_path}/mouse_CellChatDB_interaction.csv', header=0,
            index_col=0)
        comp = pd.read_csv(f'{lr_database_path}/mouse_CellChatDB_complex.csv',
                           header=0,
                           index_col=0)
    elif species == 'human':
        geneInter = pd.read_csv(
            f'{lr_database_path}/human_CellChatDB_interaction.csv', header=0,
            index_col=0)
        comp = pd.read_csv(f'{lr_database_path}/human_CellChatDB_complex.csv',
                           header=0, index_col=0)
    else:
        raise ValueError("species type: {} is not supported currently. Please have a check.".format(species))

    ligand = geneInter.ligand.values.copy()
    receptor = geneInter.receptor.values.copy()
    t = []
    for i in range(len(ligand)):
        add_state = True
        for n in [ligand, receptor]:
            l = n[i]
            if l in comp.index:
                comp_original = comp.loc[l].dropna().values
                comp_existing = comp_original[pd.Series(comp_original).isin(adata.var_names)]
                n[i] = comp_existing
                if len(comp_original) != len(comp_existing):
                    add_state = False
            else:
                n[i] = pd.Series(l).values[pd.Series(l).isin(adata.var_names)]
        if not add_state:
            t.append(False)
            continue
        if (len(ligand[i]) > 0) * (len(receptor[i]) > 0):
            if (sum(adata[:, ligand[i]].X.mean(axis=1) > 0) >= min_cell) * \
                    (sum(adata[:, receptor[i]].X.mean(axis=1) > 0) >= min_cell):
                t.append(True)
            else:
                t.append(False)
        else:
            t.append(False)

    ligand_list = [tmp.tolist() for tmp in ligand[t]]
    single_ligand_list = []
    receptor_list = [tmp.tolist() for tmp in receptor[t]]
    single_receptor_list = []
    interaction_list = [geneInter[t].index.tolist()][0]
    for i in range(len(ligand_list)):
        # process ligand units
        tmp_list = ligand_list[i]
        min_molecular = tmp_list[0]
        min_value = adata[:, min_molecular].X.sum()
        for j in tmp_list[1:]:
            tmp_value = adata[:, j].X.sum()
            if tmp_value < min_value:
                min_molecular = j
                min_value = tmp_value
        single_ligand_list.append(min_molecular)
        # process receptor units
        tmp_list = receptor_list[i]
        min_molecular = tmp_list[0]
        min_value = adata[:, min_molecular].X.sum()
        for j in tmp_list[1:]:
            tmp_value = adata[:, j].X.sum()
            if tmp_value < min_value:
                min_molecular = j
                min_value = tmp_value
        single_receptor_list.append(min_molecular)

    annotation_list = geneInter.loc[interaction_list, 'annotation'].values.astype(str)
    pathway_list = geneInter.loc[interaction_list, 'pathway_name'].values.astype(str)

    lr_info = pd.DataFrame('No',
                           index=interaction_list,
                           columns=['ligand', 'receptor'])
    lr_meta_info = pd.DataFrame('No',
                                index=interaction_list,
                                columns=['annotation', 'pathway'])
    lr_info.loc[:, 'ligand'] = single_ligand_list
    lr_info.loc[:, 'receptor'] = single_receptor_list
    lr_meta_info.loc[:, 'annotation'] = annotation_list
    lr_meta_info.loc[:, 'pathway'] = pathway_list

    # filter cell-cell contact
    lr_meta_info = lr_meta_info.loc[lr_meta_info.loc[:, 'annotation'] != 'Cell-Cell Contact', :]
    lr_info = lr_info.loc[lr_meta_info.index, :]

    # add processed information to anndata object
    adata.uns['lr_info'] = lr_info
    adata.uns['lr_meta_info'] = lr_meta_info

    if sparse_state:
        adata.X = ss.csr_matrix(adata.X)

    return adata


def ligand_receptor_map(adata):
    all_ligands = adata.uns['lr_info']['all_ligands']
    all_receptors = adata.uns['lr_info']['all_receptors']
    all_interactions = adata.uns['lr_info']['interaction']
    lr_map_df = pd.DataFrame(0, index=all_ligands, columns=all_receptors)
    ligand_secrete_df = pd.DataFrame(0, index=all_ligands, columns=['secreted_signal'])
    for interaction in all_interactions:
        annotation = adata.uns['lr_info']['annotation'][interaction]
        ligands = adata.uns['lr_info']['ligand_unit'][interaction]
        receptors = adata.uns['lr_info']['receptor_unit'][interaction]
        for i in ligands:
            if annotation != "Cell-Cell Contact":
                ligand_secrete_df.loc[i, 'secreted_signal'] = 1
            for j in receptors:
                lr_map_df.loc[i, j] = 1

    return lr_map_df, ligand_secrete_df


def communicate_score(adata):
    interact_df = pd.DataFrame(0,
                               index=adata.obs_names,
                               columns=adata.uns['lr_info']['interaction'])

    def _calculate_score_d(lr_index):
        l_express = adata[:, adata.uns['lr_info']['ligand'][lr_index]].X
        l_express = l_express.sum(axis=1)
        r_express = adata[:, adata.uns['lr_info']['receptor'][lr_index]].X
        r_express = r_express.sum(axis=1)
        scores_l = np.matmul(adata.obsm['spatial_graph'], r_express)
        scores_l = np.multiply(l_express, scores_l)
        scores_r = np.matmul(adata.obsm['spatial_graph'], l_express)
        scores_r = np.multiply(r_express, scores_r)
        interact_df.iloc[:, lr_index] = scores_l + scores_r

    def _calculate_score_s(lr_index):
        l_express = adata[:, adata.uns['lr_info']['ligand'][lr_index]].X.toarray()
        l_express = l_express.sum(axis=1)
        r_express = adata[:, adata.uns['lr_info']['receptor'][lr_index]].X.toarray()
        r_express = r_express.sum(axis=1)
        scores_l = np.matmul(adata.obsm['spatial_graph'], r_express)
        scores_l = np.multiply(l_express, scores_l)
        scores_r = np.matmul(adata.obsm['spatial_graph'], l_express)
        scores_r = np.multiply(r_express, scores_r)
        interact_df.iloc[:, lr_index] = scores_l + scores_r

    if ss.issparse(adata.X):
        for lr_index in range(len(adata.uns['lr_info']['ligand'])):
            _calculate_score_s(lr_index)
    else:
        for lr_index in range(len(adata.uns['lr_info']['ligand'])):
            _calculate_score_d(lr_index)

    adata.obsm['communicate_score'] = interact_df


def lr_correlation(adata, method='pearson'):
    interaction_score_df = pd.DataFrame(index=adata.uns['lr_info']['interaction'],
                                        columns=[method])
    for interaction in adata.uns['lr_info']['interaction']:
        annotation = adata.uns['lr_info']['lr_meta'].loc[interaction, 'annotation']
        if annotation == 'Cell-Cell Contact':
            ligand_freq = adata.uns['GFT_info']['ligands_freq_mtx'].loc[interaction, :].values
        else:
            ligand_freq = adata.uns['GFT_info']['ligands_diffusion_freq_mtx'].loc[interaction, :].values
        receptor_freq = adata.uns['GFT_info']['receptors_freq_mtx'].loc[interaction, :].values
        if method == 'pearson':
            tmp = pearsonr(ligand_freq, receptor_freq)
        elif method == 'spearman':
            tmp = spearmanr(ligand_freq, receptor_freq)
        interaction_score_df.at[interaction, method] = tmp[0]
    interaction_score_df = pd.concat((interaction_score_df,
                                      adata.uns['lr_info']['lr_meta'].loc[interaction_score_df.index,
                                      ['pathway_name', 'ligand', 'receptor', 'evidence', 'annotation',
                                       'interaction_name_2']]), axis=1)
    interaction_score_df[method] = interaction_score_df[method].astype(np.float32)
    adata.uns['lr_info']['lr_score_df'] = interaction_score_df


def lr_prediction(adata, method='pearson', threshold=0.3):
    # obtain current lrs and receptors
    ligand_freq_mtx = adata.uns['GFT_info']['ligand_freq_mtx']
    receptor_freq_mtx = adata.uns['GFT_info']['receptor_freq_mtx']
    all_current_ligand_term = []
    all_current_ligand_list = []
    all_current_receptor_term = []
    all_current_receptor_list = []
    all_ligand_freq_df = pd.DataFrame(
        columns=[f'FC_{i}' for i in range(adata.uns['GFT_info']['frequency_info'].size - 1)])
    all_receptor_freq_df = pd.DataFrame(
        columns=[f'FC_{i}' for i in range(adata.uns['GFT_info']['frequency_info'].size - 1)])
    for i in adata.uns['lr_info']['ligand'].keys():
        # add ligands
        tmp_list = adata.uns['lr_info']['ligand'][i]
        tmp_term = 'Ligand-' + '_'.join(tmp_list)
        if tmp_term not in all_current_ligand_term:
            all_current_ligand_term.append(tmp_term)
            all_current_ligand_list.append(tmp_list)
            tmp_freq = ligand_freq_mtx.loc[tmp_list, :].mean(axis=0)
            all_ligand_freq_df.loc[tmp_term, :] = tmp_freq

        # add receptors
        tmp_list = adata.uns['lr_info']['receptor'][i]
        tmp_term = 'Receptor-' + '_'.join(tmp_list)
        if tmp_term not in all_current_receptor_term:
            all_current_receptor_term.append(tmp_term)
            all_current_receptor_list.append(tmp_list)
            tmp_freq = receptor_freq_mtx.loc[tmp_list, :].mean(axis=0)
            all_receptor_freq_df.loc[tmp_term, :] = tmp_freq

    # De novo lr finding
    combined_freq_df = pd.concat((all_ligand_freq_df,
                                  all_receptor_freq_df),
                                 axis=0)
    combined_freq_df = combined_freq_df.transpose()
    corr_df = combined_freq_df.corr(method=method)
    corr_df = corr_df.loc[all_current_ligand_term,
    all_current_receptor_term]
    corr_df = corr_df.fillna(0)
    corr_df[corr_df < threshold] = 0

    predicted_lr = pd.DataFrame(columns=['ligand', 'receptor', f'{method} correlation'])
    for ligand in all_current_ligand_term:
        tmp_l = ligand.split('Ligand-')[1]
        tmp_values = corr_df.loc[ligand, :]
        tmp_values = tmp_values[tmp_values > 0]
        tmp_index = tmp_values.index.tolist()
        if len(tmp_index) > 0:
            for receptor in tmp_index:
                tmp_r = receptor.split('Receptor-')[1]
                tmp_corr = tmp_values[receptor]
                tmp_term = str.upper(tmp_l) + '_' + str.upper(tmp_r)
                predicted_lr.loc[tmp_term, :] = (tmp_l, tmp_r, tmp_corr)

    return predicted_lr


def lr_module(adata, threshold=0.3, resolution=1, plot=True, interaction_list=None, method='pearson'):
    # extract frequency signals of ligands and receptors
    if not interaction_list:
        valid_lrs = adata.uns['lr_info']['lr_score_df'].index[adata.uns['lr_info']['lr_score_df'][method] >
                                                              threshold].tolist()
    else:
        valid_lrs = interaction_list
    ligands_freq_df = adata.uns['GFT_info']['ligands_freq_mtx'].loc[valid_lrs, :]
    receptors_freq_df = adata.uns['GFT_info']['receptors_freq_mtx'].loc[valid_lrs, :]

    lr_adata = pd.concat((ligands_freq_df, receptors_freq_df), axis=1)
    lr_adata = sc.AnnData(lr_adata)
    sc.pp.neighbors(lr_adata, n_neighbors=3, use_rep='X')
    # plot
    sc.tl.louvain(lr_adata, resolution=resolution, key_added='lr_module')
    if plot:
        sc.tl.umap(lr_adata)
        sc.pl.umap(lr_adata, color='lr_module', size=100)

    # save
    adata.uns['lr_info']['lr_score_df']['lr_module'] = "None"
    adata.uns['lr_info']['lr_score_df'].loc[valid_lrs, 'lr_module'] = lr_adata.obs.loc[:, 'lr_module'].values


def obtain_original_ligand_freq(adata):
    eigen_t = adata.uns['GFT_info']['fourier_modes']
    eigen_t = eigen_t[1:, :]
    all_ligands = adata.uns['lr_info']['all_ligands']
    exp_mtx = adata[:, all_ligands].X
    if ss.issparse(exp_mtx):
        exp_mtx = exp_mtx.A
    # Implement GFT
    ligand_freq_mtx = np.matmul(eigen_t, exp_mtx)
    ligand_freq_mtx = preprocessing.normalize(ligand_freq_mtx,
                                              norm='l1',
                                              axis=0).transpose()
    ligand_freq_mtx = pd.DataFrame(ligand_freq_mtx,
                                   index=all_ligands,
                                   columns=[f'FC_{i}' for i in range(ligand_freq_mtx.shape[1])])
    adata.uns['GFT_info']['ligand_freq_mtx_without_diffusion'] = ligand_freq_mtx

    ligands_freq_df = pd.DataFrame(0,
                                   index=adata.uns['lr_info']['interaction'],
                                   columns=[f'freq_{i}' for i in
                                            range(adata.uns['GFT_info']['ligand_freq_mtx'].shape[1])])
    for interaction in adata.uns['lr_info']['interaction']:
        ligand = adata.uns['lr_info']['ligand'][interaction]
        ligand_freq_signal = ligand_freq_mtx.loc[ligand, :].mean(axis=0)
        ligands_freq_df.loc[interaction, :] = ligand_freq_signal.values

    adata.uns['lr_info']['ligands_freq_df_without_diffusion'] = ligands_freq_df


def lr_module_gene(adata, gene_list, threshold=0.6, alternative='two-sides'):
    # obtain_original_ligand_freq(adata)
    # calculate each gene in gene_list's correlation with lr module
    gene_lr_score_df = pd.DataFrame(columns=['related L-R module',
                                             'gene',
                                             'evidence',
                                             'correlation with ligand',
                                             'correlation with receptor'])
    tmp_adata = adata[:, gene_list]
    sc.pp.filter_genes(tmp_adata, min_cells=1)
    gene_list = tmp_adata.var_names
    if tmp_adata.shape[0] == 0:
        raise ValueError("The input gene list is not in adata.var_names")

    exp_mtx = tmp_adata.X
    if ss.issparse(exp_mtx):
        exp_mtx = exp_mtx.A

    # implement GFT
    exp_mtx = adata.uns['GFT_info']['eigenvectors'] @ exp_mtx
    exp_mtx = exp_mtx.transpose()
    exp_mtx = preprocessing.normalize(exp_mtx,
                                      norm='l1',
                                      axis=1)
    exp_mtx = pd.DataFrame(exp_mtx,
                           index=gene_list,
                           columns=[f'FC_{i}' for i in range(exp_mtx.shape[1])])

    # process lr module
    valid_module = np.unique(adata.uns['lr_info']['lr_score_df']['lr_module'])
    valid_module = np.setdiff1d(valid_module, ['None'])
    lr_module_ligand_freq_df = pd.DataFrame(0,
                                            index=valid_module,
                                            columns=[f'FC_{i}' for i in range(exp_mtx.shape[1])])
    lr_module_receptor_freq_df = pd.DataFrame(0,
                                              index=valid_module,
                                              columns=[f'FC_{i}' for i in range(exp_mtx.shape[1])])
    from tqdm import tqdm
    module_pbar = tqdm(valid_module)
    for module in module_pbar:
        module_pbar.set_description('Processing module ' + module)
        tmp_lrs = adata.uns['lr_info']['lr_score_df']['lr_module'].index[adata.uns['lr_info']['lr_score_df']
                                                                         ['lr_module'] == module]
        tmp_ligand_freq = adata.uns['GFT_info']['ligands_freq_mtx'].loc[tmp_lrs, :].mean()
        tmp_receptor_freq = adata.uns['GFT_info']['receptors_freq_mtx'].loc[tmp_lrs, :].mean()
        lr_module_ligand_freq_df.loc[module, :] = tmp_ligand_freq.values
        lr_module_receptor_freq_df.loc[module, :] = tmp_receptor_freq.values

        # search gene
        for gene in gene_list:
            tmp_ligand_corr = pearsonr(tmp_ligand_freq, exp_mtx.loc[gene, :])[0]
            tmp_receptor_corr = pearsonr(tmp_receptor_freq, exp_mtx.loc[gene, :])[0]
            if alternative == 'two-sides':
                judge = (tmp_ligand_corr >= threshold and tmp_receptor_corr >= threshold)
            else:
                judge = (tmp_ligand_corr >= threshold or tmp_receptor_corr >= threshold)
            if judge:
                if tmp_ligand_corr > tmp_receptor_corr:
                    source = 'ligand'
                else:
                    source = 'receptor'
                term = f'module_{module}-gene_{gene}'
                gene_lr_score_df.loc[term, :] = (module, gene, source, tmp_ligand_corr, tmp_receptor_corr)
    gene_lr_score_df['correlation with ligand'] = gene_lr_score_df['correlation with ligand'].astype(np.float32)
    gene_lr_score_df['correlation with receptor'] = gene_lr_score_df['correlation with receptor'].astype(np.float32)

    adata.uns['lr_gene_relation'] = gene_lr_score_df
