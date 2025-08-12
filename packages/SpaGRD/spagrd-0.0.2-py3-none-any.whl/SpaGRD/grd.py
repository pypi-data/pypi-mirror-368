import warnings
import scipy
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as ss
from scipy.spatial.distance import pdist, squareform
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from tqdm import tqdm
from .utils import get_laplacian_mtx, kneed_select_values, test_significant_freq, compute_knn_adjacency_matrix
from multiprocessing import Pool
from joblib import Parallel, delayed

warnings.filterwarnings("ignore")


def diffusion_and_gft(adata,
                      ratio_low_freq='infer',
                      num_low_freq=None,
                      n_neighbors=6,
                      spatial_key='spatial',
                      normalize_lap=False,
                      alpha=0.1,
                      step=2):
    # Determine the number of low frequency signals
    if not num_low_freq:
        if ratio_low_freq == 'infer':
            if adata.shape[0] <= 800:
                num_low_freq = min(20 * int(np.ceil(np.sqrt(adata.shape[0]))),
                                   adata.shape[0])
            elif adata.shape[0] <= 5000:
                num_low_freq = 15 * int(np.ceil(np.sqrt(adata.shape[0])))
            elif adata.shape[0] <= 10000:
                num_low_freq = 10 * int(np.ceil(np.sqrt(adata.shape[0])))
            else:
                num_low_freq = 5 * int(np.ceil(np.sqrt(adata.shape[0])))
        else:
            num_low_freq = int(np.ceil(np.sqrt(adata.shape[0]) * ratio_low_freq))
    num_low_freq += 1
    # Preprocessing
    adata.var_names_make_unique()
    sc.pp.filter_genes(adata, min_cells=1)

    # Get Laplacian matrix according to coordinates
    lap_mtx = get_laplacian_mtx(adata,
                                num_neighbors=n_neighbors,
                                spatial_key=spatial_key,
                                normalization=normalize_lap)
    # Fourier mode of low frequency
    num_low_freq = min(num_low_freq, adata.shape[0])
    v0 = np.ones(adata.shape[0]) * 1 / np.sqrt(adata.shape[0])
    eig_vals, eig_vecs = ss.linalg.eigsh(lap_mtx.astype(float),
                                         k=num_low_freq,
                                         which='SM',
                                         v0=v0)
    eig_vals = eig_vals[1:]
    eig_vecs = eig_vecs[:, 1:]

    adata.uns['GFT_info'] = {'eigenvalues': eig_vals,
                             'eigenvectors': eig_vecs.transpose()}

    # process multi-unites
    ligands_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)
    ligands_diffusion_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)
    receptors_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)

    if ss.issparse(adata.X):
        tmp_ligand_exp_df = pd.DataFrame(adata[:, adata.uns['lr_info']['all_ligands']].X.A,
                                         index=adata.obs_names,
                                         columns=adata.uns['lr_info']['all_ligands']).astype(np.float32)
        tmp_receptor_exp_df = pd.DataFrame(adata[:, adata.uns['lr_info']['all_receptors']].X.A,
                                           index=adata.obs_names,
                                           columns=adata.uns['lr_info']['all_receptors']).astype(np.float32)
    else:
        tmp_ligand_exp_df = pd.DataFrame(adata[:, adata.uns['lr_info']['all_ligands']].X,
                                         index=adata.obs_names,
                                         columns=adata.uns['lr_info']['all_ligands']).astype(np.float32)
        tmp_receptor_exp_df = pd.DataFrame(adata[:, adata.uns['lr_info']['all_receptors']].X,
                                           index=adata.obs_names,
                                           columns=adata.uns['lr_info']['all_receptors']).astype(np.float32)
    # Diffusion for ligands
    diffusion_mtx = np.eye(lap_mtx.shape[0]) - alpha * lap_mtx.A
    ligand_diffusion_exp_df = np.matmul(diffusion_mtx, tmp_ligand_exp_df.values)
    for i in range(step - 1):
        ligand_diffusion_exp_df = np.matmul(diffusion_mtx, ligand_diffusion_exp_df)
    ligand_diffusion_exp_df = pd.DataFrame(ligand_diffusion_exp_df,
                                           index=adata.obs_names,
                                           columns=adata.uns['lr_info']['all_ligands']).astype(np.float32)

    adata.obsm['ligand_unit_diffusion_expression'] = ligand_diffusion_exp_df

    # Process multi-units
    lr_info = adata.uns['lr_info']
    interaction_list = lr_info['interaction']

    def calculate_production_ligand_diffusion(units):
        products = ligand_diffusion_exp_df[units].values
        indications = np.prod(products, axis=1)
        indications[indications > 0] = 1
        return np.mean(products, axis=1) * indications

    def calculate_production_ligand(units):
        products = tmp_ligand_exp_df[units].values
        indications = np.prod(products, axis=1)
        indications[indications > 0] = 1
        return np.mean(products, axis=1) * indications

    def calculate_production_receptor(units):
        products = tmp_receptor_exp_df[units].values
        indications = np.prod(products, axis=1)
        indications[indications > 0] = 1
        return np.mean(products, axis=1) * indications

    # use tqdm
    tqdm_interation_list = tqdm(interaction_list)
    for interaction in tqdm_interation_list:
        tqdm_interation_list.set_description("Processing: %s" % interaction)
        ligands_exp_df[interaction] = calculate_production_ligand(lr_info['ligand_unit'][interaction])
        receptors_exp_df[interaction] = calculate_production_receptor(lr_info['receptor_unit'][interaction])
        ligands_diffusion_exp_df[interaction] = calculate_production_ligand_diffusion(
            lr_info['ligand_unit'][interaction])

    # Check validness
    valid_interactions = np.intersect1d(
        ligands_diffusion_exp_df.columns[ligands_diffusion_exp_df.sum(axis=0) > 0],
        receptors_exp_df.columns[receptors_exp_df.sum(axis=0) > 0]
    )
    ligands_diffusion_exp_df = ligands_diffusion_exp_df.loc[:, valid_interactions]
    ligands_exp_df = ligands_exp_df.loc[:, valid_interactions]
    receptors_exp_df = receptors_exp_df.loc[:, valid_interactions]

    new_ligand_list = [lr_info['ligand_unit'][interaction] for interaction in valid_interactions]
    new_receptor_list = [lr_info['receptor_unit'][interaction] for interaction in valid_interactions]
    lr_info['interaction'] = valid_interactions
    lr_info['ligand_unit'] = dict(zip(valid_interactions, new_ligand_list))
    lr_info['receptor_unit'] = dict(zip(valid_interactions, new_receptor_list))
    adata.uns['lr_info'] = lr_info

    adata.obsm['ligands_diffusion_expression'] = ligands_diffusion_exp_df.values.astype(np.float32)
    adata.obsm['ligands_expression'] = ligands_exp_df.values.astype(np.float32)
    adata.obsm['receptors_expression'] = receptors_exp_df.values.astype(np.float32)

    # GFT for ligands with diffusion
    exp_mtx = adata.obsm['ligands_diffusion_expression']
    freq_mtx = np.matmul(eig_vecs.transpose(), exp_mtx)
    freq_mtx = preprocessing.normalize(freq_mtx,
                                       norm='l1',
                                       axis=0).transpose()
    freq_mtx = pd.DataFrame(freq_mtx,
                            index=adata.uns['lr_info']['interaction'],
                            columns=[f'FC_{i}' for i in range(freq_mtx.shape[1])])
    adata.uns['GFT_info']['ligands_diffusion_freq_mtx'] = freq_mtx
    # GFT for ligands
    exp_mtx = adata.obsm['ligands_expression']
    freq_mtx = np.matmul(eig_vecs.transpose(), exp_mtx)
    freq_mtx = preprocessing.normalize(freq_mtx,
                                       norm='l1',
                                       axis=0).transpose()
    freq_mtx = pd.DataFrame(freq_mtx,
                            index=adata.uns['lr_info']['interaction'],
                            columns=[f'FC_{i}' for i in range(freq_mtx.shape[1])])
    adata.uns['GFT_info']['ligands_freq_mtx'] = freq_mtx
    # GFT for receptors
    exp_mtx = adata.obsm['receptors_expression']
    freq_mtx = np.matmul(eig_vecs.transpose(), exp_mtx)
    freq_mtx = preprocessing.normalize(freq_mtx,
                                       norm='l1',
                                       axis=0).transpose()
    freq_mtx = pd.DataFrame(freq_mtx,
                            index=adata.uns['lr_info']['interaction'],
                            columns=[f'FC_{i}' for i in range(freq_mtx.shape[1])])
    adata.uns['GFT_info']['receptors_freq_mtx'] = freq_mtx


def reaction_diffusion(adata,
                       n_neighbors=6,
                       spatial_key='spatial',
                       normalize_lap=False,
                       infer_param=False,
                       alpha=0.3,
                       beta=0.3,
                       step=3,
                       log_step=None):
    # preprocessing
    adata.var_names_make_unique()
    sc.pp.filter_genes(adata, min_cells=1)
    lr_info = adata.uns['lr_info']
    ligand_list = lr_info.loc[:, 'ligand'].values.tolist()
    receptor_list = lr_info.loc[:, 'receptor'].values.tolist()
    interaction_list = lr_info.index.tolist()
    alpha = alpha / (2 * n_neighbors)

    # get Laplacian matrix according to coordinates
    lap_mtx, adj_mtx = get_laplacian_mtx(adata,
                                         num_neighbors=n_neighbors,
                                         spatial_key=spatial_key,
                                         normalization=normalize_lap)

    # obtain current expression matrix
    if ss.issparse(adata.X):
        ligand_exp = adata[:, ligand_list].X.toarray().astype(np.float32)
        receptor_exp = adata[:, receptor_list].X.toarray().astype(np.float32)

    else:
        ligand_exp = adata[:, ligand_list].X.astype(np.float32)
        receptor_exp = adata[:, receptor_list].X.astype(np.float32)

    # determine parameters
    if infer_param:
        alpha_list = np.arange(0.2, 1, 0.2)
        beta_list = np.arange(0.2, 1, 0.2)
        best_param = [alpha_list[0], beta_list[0]]
        best_interaction = _seek_parameter_equation(ligand_exp.copy(), receptor_exp.copy(), best_param[0],
                                                    best_param[1], lap_mtx, step)
        for alpha in alpha_list:
            for beta in beta_list:
                tmp_param = [alpha, beta]
                tmp_interaction = _seek_parameter_equation(ligand_exp.copy(), receptor_exp.copy(), tmp_param[0],
                                                           tmp_param[1], lap_mtx, step)
                if tmp_interaction < best_interaction:
                    best_param = tmp_param
                    best_interaction = tmp_interaction
        print(f"parameters: \t alpha={best_param[0]},   beta={best_param[1]}")
        alpha = best_param[0]
        beta = best_param[1]

    # record
    ligand_exp_df = pd.DataFrame(ligand_exp,
                                 index=adata.obs_names,
                                 columns=[f'{i}-ligand-init' for i in interaction_list],
                                 dtype=np.float32)
    receptor_exp_df = pd.DataFrame(receptor_exp.astype(np.float32),
                                   index=adata.obs_names,
                                   columns=[f'{i}-ligand-init' for i in interaction_list],
                                   dtype=np.float32)
    interaction_df = pd.DataFrame(0,
                                  index=adata.obs_names,
                                  columns=[f'{i}-interaction-init' for i in interaction_list],
                                  dtype=np.float32)
    # diffusion
    diffusion_mtx_tmp = np.eye(lap_mtx.shape[0]) - alpha * lap_mtx
    diffusion_mtx_tmp = diffusion_mtx_tmp.astype(np.float32)
    all_interaction_mtx = np.zeros_like(ligand_exp, dtype=np.float32)
    interaction_sum_df = pd.DataFrame(index=interaction_list)
    step_tqdm = tqdm(range(1, step + 1))

    for s in step_tqdm:
        step_tqdm.set_description("step: ")
        interaction_mtx = ligand_exp * receptor_exp
        ligand_exp = diffusion_mtx_tmp @ ligand_exp - beta * interaction_mtx
        receptor_exp = receptor_exp - beta * interaction_mtx
        ligand_exp = np.clip(ligand_exp, a_min=0, a_max=None)
        receptor_exp = np.clip(receptor_exp, a_min=0, a_max=None)
        all_interaction_mtx += interaction_mtx

        # record
        if log_step is not None:
            if s % log_step == 0:
                tmp_df = pd.DataFrame(ligand_exp[ligand_list].values,
                                      index=ligand_exp.index,
                                      columns=[f'{i}-ligand-{s}' for i in interaction_list]).copy()
                ligand_exp_df = pd.concat((ligand_exp_df, tmp_df), axis=1)
                tmp_df = pd.DataFrame(receptor_exp[receptor_list].values,
                                      index=ligand_exp.index,
                                      columns=[f'{i}-receptor-{s}' for i in interaction_list]).copy()
                receptor_exp_df = pd.concat((receptor_exp_df, tmp_df), axis=1)
                tmp_df = pd.DataFrame(all_interaction_mtx,
                                      index=ligand_exp.index,
                                      columns=[f'{i}-interaction-{s}' for i in interaction_list]).copy()
                interaction_df = pd.concat((interaction_df, tmp_df), axis=1)
        # record interaction sum
        interaction_sum_list = all_interaction_mtx.sum(axis=0).copy()
        interaction_sum_df[s] = interaction_sum_list

    # reformat
    all_interaction_mtx = pd.DataFrame(all_interaction_mtx,
                                       index=adata.obs_names,
                                       columns=interaction_list)

    adata.obsm['interaction_score'] = all_interaction_mtx
    adata.uns['GRD_info'] = {'adj_mtx': adj_mtx,
                             'lr_interaction_sum': interaction_sum_df,
                             'ligand_process': ligand_exp_df,
                             'receptor_process': receptor_exp_df,
                             'interaction_process': interaction_df
                             }


def _seek_parameter_equation(ligand_exp_tmp,
                             receptor_exp_tmp,
                             alpha_tmp,
                             beta_tmp,
                             lap_mtx_tmp,
                             step_tmp):
    current_interaction_mtx_tmp = beta_tmp * ligand_exp_tmp * receptor_exp_tmp
    diffusion_mtx_tmp = np.eye(lap_mtx_tmp.shape[0]) - alpha_tmp * lap_mtx_tmp.A
    tmp_score = receptor_exp_tmp.mean()
    for s in range(step_tmp):
        last_tmp_score = tmp_score
        ligand_exp_tmp = diffusion_mtx_tmp @ ligand_exp_tmp - current_interaction_mtx_tmp
        receptor_exp_tmp = receptor_exp_tmp - current_interaction_mtx_tmp
        current_interaction_mtx_tmp = beta_tmp * ligand_exp_tmp * receptor_exp_tmp
        current_interaction_mtx_tmp = np.abs(current_interaction_mtx_tmp)
        tmp_score = np.abs(receptor_exp_tmp).mean()
        if np.percentile(receptor_exp_tmp, q=10) < 0 or np.percentile(ligand_exp_tmp, q=10) < 0:
            return abs(last_tmp_score)

    return abs(tmp_score)


def _permutation_test(ligand_exp,
                      receptor_exp,
                      interaction_list,
                      num_permutation,
                      beta,
                      diffusion_mtx,
                      step):
    # define a dataframe to save results
    interaction_results = pd.DataFrame(0,
                                       index=interaction_list,
                                       columns=[f'permutation_{i}' for i in range(num_permutation)])
    tqdm_permutation = tqdm(range(num_permutation))
    for p in tqdm_permutation:
        tqdm_permutation.set_description("Permutation test: %d" % p)
        ligand_exp_tmp = ligand_exp.copy()
        receptor_exp_tmp = receptor_exp.copy()
        np.random.shuffle(ligand_exp_tmp)
        np.random.shuffle(receptor_exp_tmp)
        all_interaction_mtx = np.zeros_like(ligand_exp)
        for s in range(0, step + 1):
            interaction_mtx = ligand_exp_tmp * receptor_exp_tmp
            ligand_exp_tmp = diffusion_mtx @ ligand_exp_tmp - beta * interaction_mtx
            receptor_exp_tmp = receptor_exp_tmp - beta * interaction_mtx
            ligand_exp_tmp[ligand_exp_tmp < 0] = 0
            receptor_exp_tmp[receptor_exp_tmp < 0] = 0
            all_interaction_mtx += interaction_mtx
        interaction_results.iloc[:, p] = all_interaction_mtx.sum(axis=0)

    return interaction_results


def _calculate_p_value(interaction_score,
                       permutation_results):
    num_interactions = permutation_results.shape[0]
    num_permutation = permutation_results.shape[1]
    results = pd.DataFrame(1,
                           index=permutation_results.index,
                           columns=['p-value'])
    permutation_results.loc[:, 'real'] = interaction_score.sum(axis=0).values
    # p value
    for i in range(num_interactions):
        interaction = permutation_results.index[i]
        tmp = permutation_results.iloc[i, :]
        tmp = pd.DataFrame(tmp)
        tmp = tmp.sort_values(by=interaction, ascending=False)
        tmp.loc[:, 'rank'] = range(num_permutation + 1)
        p = tmp.loc['real', 'rank']
        p = (p + 1) / num_permutation
        p = min(p, 1)
        results.iloc[i, 0] = p

    return results


def reaction_diffusion_system(adata,
                              n_neighbors=6,
                              spatial_key='spatial',
                              infer_param=False,
                              alpha=0.5,
                              beta=0.5,
                              step=10,
                              log_step=None):
    # preprocessing
    adata.var_names_make_unique()
    sc.pp.filter_genes(adata, min_cells=1)
    lr_info = adata.uns['lr_info']
    ligand_list = lr_info.loc[:, 'ligand'].values.tolist()
    receptor_list = lr_info.loc[:, 'receptor'].values.tolist()
    interaction_list = lr_info.index.tolist()
    alpha = alpha / n_neighbors

    # get Laplacian matrix according to coordinates
    lap_mtx, adj_mtx = get_laplacian_mtx(adata,
                                         num_neighbors=n_neighbors,
                                         spatial_key=spatial_key,
                                         normalization=False)

    # obtain current expression matrix
    if ss.issparse(adata.X):
        ligand_exp = adata[:, ligand_list].X.toarray()
        receptor_exp = adata[:, receptor_list].X.toarray()

    else:
        ligand_exp = adata[:, ligand_list].X
        receptor_exp = adata[:, receptor_list].X

    # determine parameters
    if infer_param:
        alpha_list = np.arange(0.1, 0.5, 0.1).astype(np.float32)
        beta_list = np.arange(0.1, 1.1, 0.2).astype(np.float32)
        best_param = [alpha_list[0], beta_list[0]]
        best_interaction = _seek_parameter_equation(ligand_exp.copy(),
                                                    receptor_exp.copy(),
                                                    best_param[0],
                                                    best_param[1],
                                                    lap_mtx,
                                                    step)
        for alpha in alpha_list:
            for beta in beta_list:
                tmp_param = [alpha, beta]
                tmp_interaction = _seek_parameter_equation(ligand_exp.copy(), receptor_exp.copy(), tmp_param[0],
                                                           tmp_param[1], lap_mtx, step)
                if tmp_interaction < best_interaction:
                    best_param = tmp_param
                    best_interaction = tmp_interaction
        print(f"parameters: \t alpha={best_param[0]},   beta={best_param[1]}")
        alpha = best_param[0]
        beta = best_param[1]

    # construct ligand-receptor map
    all_unique_ligands = np.unique(ligand_list).tolist()
    all_unique_receptors = np.unique(receptor_list).tolist()
    lr_mapping = pd.DataFrame(0,
                              index=all_unique_receptors,
                              columns=all_unique_ligands,
                              dtype=np.float32)
    for s, interaction in enumerate(interaction_list):
        ligand = ligand_list[s]
        receptor = receptor_list[s]
        lr_mapping.loc[receptor, ligand] = 1

    # ligand and receptor
    if ss.issparse(adata.X):
        single_ligand_exp = adata[:, all_unique_ligands].X.toarray()
        single_receptor_exp = adata[:, all_unique_receptors].X.toarray()

    else:
        single_ligand_exp = adata[:, all_unique_ligands].X
        single_receptor_exp = adata[:, all_unique_receptors].X

    # single molecular dynamics
    single_ligand_exp = pd.DataFrame(single_ligand_exp,
                                     index=adata.obs_names,
                                     columns=all_unique_ligands,
                                     dtype=np.float32)
    single_receptor_exp = pd.DataFrame(single_receptor_exp,
                                       index=adata.obs_names,
                                       columns=all_unique_receptors,
                                       dtype=np.float32)

    # interaction process
    ligand_exp_df = pd.DataFrame(single_ligand_exp[ligand_list].values,
                                 index=adata.obs_names,
                                 columns=[f'{i}-ligand-init' for i in interaction_list])
    receptor_exp_df = pd.DataFrame(single_receptor_exp[receptor_list].values,
                                   index=adata.obs_names,
                                   columns=[f'{i}-receptor-init' for i in interaction_list])
    interaction_df = pd.DataFrame(0,
                                  index=adata.obs_names,
                                  columns=[f'{i}-interaction-init' for i in interaction_list])

    # interaction dynamics
    ligand_exp = pd.DataFrame(0,
                              index=adata.obs_names,
                              columns=interaction_list,
                              dtype=np.float32)
    receptor_exp = pd.DataFrame(0,
                                index=adata.obs_names,
                                columns=interaction_list,
                                dtype=np.float32)
    ligand_exp.loc[:, interaction_list] = single_ligand_exp.loc[:, ligand_list].values
    receptor_exp.loc[:, interaction_list] = single_receptor_exp.loc[:, receptor_list].values

    # diffusion matrix
    diffusion_mtx = np.eye(lap_mtx.shape[0]) - alpha * lap_mtx
    diffusion_mtx = diffusion_mtx.astype(np.float32)

    # interaction score
    all_interaction_mtx = np.zeros_like(ligand_exp_df.values).astype(np.float32)
    interaction_sum_df = pd.DataFrame(index=interaction_list)
    step_tqdm = tqdm(range(1, step + 1))

    for s in step_tqdm:
        step_tqdm.set_description("step: ")
        interaction_mtx = ligand_exp.values * receptor_exp.values
        all_interaction_mtx += interaction_mtx

        # process ligand
        single_ligand_exp = diffusion_mtx @ single_ligand_exp.values - beta * single_ligand_exp.values * \
                            (single_receptor_exp.values @ lr_mapping.values)
        np.maximum(single_ligand_exp, 0, out=single_ligand_exp)
        single_ligand_exp = pd.DataFrame(single_ligand_exp,
                                         index=adata.obs_names,
                                         columns=all_unique_ligands)
        # process receptor
        single_receptor_exp = single_receptor_exp.values - beta * single_receptor_exp * \
                              (single_ligand_exp.values @ lr_mapping.transpose().values)
        np.maximum(single_receptor_exp, 0, out=single_receptor_exp)
        single_receptor_exp = pd.DataFrame(single_receptor_exp,
                                           index=adata.obs_names,
                                           columns=all_unique_receptors)
        # update the new states of ligand and receptor
        ligand_exp.loc[:, interaction_list] = single_ligand_exp[ligand_list].values
        receptor_exp.loc[:, interaction_list] = single_receptor_exp[receptor_list].values

        # record
        record_log = False
        if log_step is not None:
            if isinstance(log_step, int):
                if s % log_step == 0:
                    record_log = True
            elif isinstance(log_step, list):
                if s in log_step:
                    record_log = True
        if record_log:
            tmp_df = pd.DataFrame(single_ligand_exp[ligand_list].values,
                                  index=ligand_exp.index,
                                  columns=[f'{i}-ligand-{s}' for i in interaction_list]).copy()
            ligand_exp_df = pd.concat((ligand_exp_df, tmp_df), axis=1)
            tmp_df = pd.DataFrame(single_receptor_exp[receptor_list].values,
                                  index=ligand_exp.index,
                                  columns=[f'{i}-receptor-{s}' for i in interaction_list]).copy()
            receptor_exp_df = pd.concat((receptor_exp_df, tmp_df), axis=1)
            tmp_df = pd.DataFrame(all_interaction_mtx,
                                  index=ligand_exp.index,
                                  columns=[f'{i}-interaction-{s}' for i in interaction_list]).copy()
            interaction_df = pd.concat((interaction_df, tmp_df), axis=1)

        # record interaction sum
        interaction_sum_list = all_interaction_mtx.sum(axis=0).copy()
        interaction_sum_df[s] = interaction_sum_list

        # record overall interactions
        # overall_interaction_list.append(interaction_sum_list.sum())
    interaction_sum_df.columns = [f"step_{i}" for i in interaction_sum_df.columns]
    # reformat
    all_interaction_mtx = pd.DataFrame(all_interaction_mtx,
                                       index=adata.obs_names,
                                       columns=interaction_list)

    # add results to anndata
    adata.obsm['interaction_score'] = all_interaction_mtx
    adata.uns['GRD_info'] = {'lr_mapping': lr_mapping,
                             'adj_mtx': adj_mtx,
                             'lr_interaction_sum': interaction_sum_df,
                             'ligand_process': ligand_exp_df,
                             'receptor_process': receptor_exp_df,
                             'interaction_process': interaction_df
                             }


def _permutation_test_system(single_ligand_exp_orig,
                             single_receptor_exp_orig,
                             lr_mapping,
                             obs_names,
                             interaction_list,
                             ligand_list,
                             receptor_list,
                             num_permutation,
                             beta,
                             diffusion_mtx,
                             step):
    # Define a data frame to save the permutation results
    # define a dataframe to save results
    interaction_results = pd.DataFrame(0,
                                       index=interaction_list,
                                       columns=[f'permutation_{i}' for i in range(num_permutation)])
    all_unique_ligands = single_ligand_exp_orig.columns.tolist()
    all_unique_receptors = single_receptor_exp_orig.columns.tolist()

    tqdm_permutation = tqdm(range(num_permutation))
    for p in tqdm_permutation:
        tqdm_permutation.set_description("Permutation test: %d" % p)
        single_ligand_exp = single_ligand_exp_orig.copy()
        single_receptor_exp = single_receptor_exp_orig.copy()
        # shuffle them
        np.random.shuffle(single_ligand_exp.values)
        np.random.shuffle(single_receptor_exp.values)

        # interaction dynamics
        ligand_exp = pd.DataFrame(0,
                                  index=obs_names,
                                  columns=interaction_list)
        receptor_exp = pd.DataFrame(0,
                                    index=obs_names,
                                    columns=interaction_list)
        ligand_exp.loc[:, interaction_list] = single_ligand_exp.loc[:, ligand_list].values
        receptor_exp.loc[:, interaction_list] = single_receptor_exp.loc[:, receptor_list].values

        # interaction score
        all_interaction_mtx = np.zeros_like(ligand_exp.values)
        for s in range(0, step + 1):
            # interaction score
            interaction_mtx = ligand_exp.values * receptor_exp.values
            all_interaction_mtx += interaction_mtx

            # process ligand
            single_ligand_exp = diffusion_mtx @ single_ligand_exp.values - beta * single_ligand_exp.values * \
                                (single_receptor_exp.values @ lr_mapping.values)
            single_ligand_exp[single_ligand_exp < 0] = 0
            single_ligand_exp = pd.DataFrame(single_ligand_exp,
                                             index=obs_names,
                                             columns=all_unique_ligands)

            # process receptor
            single_receptor_exp = single_receptor_exp.values - beta * single_receptor_exp * \
                                  (single_ligand_exp.values @ lr_mapping.transpose().values)
            single_receptor_exp[single_receptor_exp < 0] = 0
            single_receptor_exp = pd.DataFrame(single_receptor_exp,
                                               index=obs_names,
                                               columns=all_unique_receptors)
            # update new state
            ligand_exp.loc[:, interaction_list] = single_ligand_exp.loc[:, ligand_list].values
            receptor_exp.loc[:, interaction_list] = single_receptor_exp.loc[:, receptor_list].values

        # obtain permutation results
        interaction_results.iloc[:, p] = all_interaction_mtx.sum(axis=0)

    return interaction_results


def _in_box_spots(tmp, spatial_key, x_ticks, y_ticks, i, j):
    if i == (len(x_ticks) - 2):
        tmp = tmp[np.logical_and(tmp.obsm[spatial_key][:, 0] >= x_ticks[i],
                                 tmp.obsm[spatial_key][:, 0] <= x_ticks[i + 1]), :]
    else:
        tmp = tmp[np.logical_and(tmp.obsm[spatial_key][:, 0] >= x_ticks[i],
                                 tmp.obsm[spatial_key][:, 0] < x_ticks[i + 1]), :]
    if j == (len(y_ticks) - 2):
        tmp = tmp[np.logical_and(tmp.obsm[spatial_key][:, 1] >= y_ticks[j],
                                 tmp.obsm[spatial_key][:, 1] <= y_ticks[j + 1]), :]
    else:
        tmp = tmp[np.logical_and(tmp.obsm[spatial_key][:, 1] >= y_ticks[j],
                                 tmp.obsm[spatial_key][:, 1] < y_ticks[j + 1]), :]

    return tmp.obs_names


def spot_ccc_score_single_sub(adata,
                              interaction,
                              alpha,
                              beta,
                              step,
                              spatial_key='spatial',
                              num_neighbors=4):
    # construct laplacian matrix
    lap_mtx, adj_mtx = get_laplacian_mtx(adata,
                                         num_neighbors=num_neighbors,
                                         spatial_key=spatial_key,
                                         normalization=False)
    alpha = alpha / num_neighbors
    diff_mtx = np.eye(lap_mtx.shape[0]) - alpha * lap_mtx

    # check pathway
    if interaction in adata.uns['lr_info'].index:
        all_ligands = [adata.uns['lr_info'].loc[interaction, 'ligand']]
        all_receptors = [adata.uns['lr_info'].loc[interaction, 'receptor']]
    # determine the ligand exp and receptor exp
    elif interaction in np.unique(adata.uns['lr_meta_info']['pathway']):
        all_ligands = adata.uns['lr_meta_info'].loc[adata.uns['lr_meta_info']['pathway'] == interaction, :].index
        all_ligands = adata.uns['lr_info'].loc[all_ligands, 'ligand']
        all_receptors = adata.uns['lr_meta_info'].loc[adata.uns['lr_meta_info']['pathway'] == interaction, :].index
        all_receptors = adata.uns['lr_info'].loc[all_receptors, 'receptor']
    else:
        raise KeyError(f"Can not identify {interaction} as a pathway or a L-R interaction pair")

    ligand_exp = adata[:, all_ligands].X
    receptor_exp = adata[:, all_receptors].X

    if ss.issparse(ligand_exp):
        ligand_exp = ligand_exp.toarray()
        receptor_exp = receptor_exp.toarray()

    spot_ccc_mtx = _calculate_ccc_mtx(ligand_exp=ligand_exp,
                                      receptor_exp=receptor_exp,
                                      diff_mtx=diff_mtx,
                                      beta=beta,
                                      step=step,
                                      )
    spot_ccc_mtx = pd.DataFrame(spot_ccc_mtx,
                                index=adata.obs_names,
                                columns=adata.obs_names)
    return spot_ccc_mtx


def spot_ccc_score_single(adata,
                          interaction,
                          alpha,
                          beta,
                          step,
                          spatial_key='spatial',
                          num_neighbors=4,
                          n_split=[1, 1],
                          scalar=0.1):
    # try to split data to accelerate the calculation
    if n_split[0] > 1 or n_split[1] > 1:
        min_x, min_y = adata.obsm[spatial_key].min(axis=0)
        max_x, max_y = adata.obsm[spatial_key].max(axis=0)
        x_ticks = np.linspace(min_x, max_x, n_split[0] + 1)
        y_ticks = np.linspace(min_y, max_y, n_split[1] + 1)
        x_unit = x_ticks[1] - x_ticks[0]
        y_unit = y_ticks[1] - y_ticks[0]
        spot_ccc_list = []
        for i in range(n_split[0]):
            if i == n_split[0] - 1:
                tmp_adata = adata[np.logical_and(adata.obsm[spatial_key][:, 0] >= x_ticks[i] - x_unit * scalar,
                                                 adata.obsm[spatial_key][:, 0] <= x_ticks[i + 1] + x_unit * scalar), :]
            else:
                tmp_adata = adata[np.logical_and(adata.obsm[spatial_key][:, 0] >= x_ticks[i] - x_unit * scalar,
                                                 adata.obsm[spatial_key][:, 0] < x_ticks[i + 1] + x_unit * scalar), :]
            for j in range(n_split[1]):
                if j == n_split[1] - 1:
                    tmp_adata_2 = tmp_adata[
                                  np.logical_and(tmp_adata.obsm[spatial_key][:, 1] >= y_ticks[j] - y_unit * scalar,
                                                 tmp_adata.obsm[spatial_key][:, 1] <= y_ticks[j + 1] + y_unit * scalar),
                                  :]
                else:
                    tmp_adata_2 = tmp_adata[
                                  np.logical_and(tmp_adata.obsm[spatial_key][:, 1] >= y_ticks[j] - y_unit * scalar,
                                                 tmp_adata.obsm[spatial_key][:, 1] < y_ticks[j + 1] + y_unit * scalar),
                                  :]
                if tmp_adata_2.shape[0] <= num_neighbors + 1:
                    print('Not enough spots', tmp_adata_2.shape[0])
                    continue
                tmp_ccc_mtx = spot_ccc_score_single_sub(adata=tmp_adata_2,
                                                        interaction=interaction,
                                                        alpha=alpha,
                                                        beta=beta,
                                                        step=step,
                                                        spatial_key=spatial_key,
                                                        num_neighbors=num_neighbors)
                # in box spots
                in_box_spots = _in_box_spots(tmp_adata_2, spatial_key, x_ticks, y_ticks, i, j)
                tmp_ccc_mtx = tmp_ccc_mtx.loc[in_box_spots, :]
                spot_ccc_list.append(tmp_ccc_mtx.copy())

        # merge the results
        spot_ccc_mtx = np.zeros((adata.shape[0], adata.shape[0]))
        spot_ccc_mtx = pd.DataFrame(spot_ccc_mtx, index=adata.obs_names, columns=adata.obs_names)
        for tmp in spot_ccc_list:
            spot_ccc_mtx.loc[tmp.index, tmp.columns] += tmp

    else:
        spot_ccc_mtx = spot_ccc_score_single_sub(adata,
                                                 interaction,
                                                 alpha,
                                                 beta,
                                                 step,
                                                 spatial_key,
                                                 num_neighbors)

    return spot_ccc_mtx


def spot_ccc_score_system_sub(adata,
                              interaction,
                              alpha,
                              beta,
                              step,
                              spatial_key='spatial',
                              num_neighbors=4):
    # construct laplacian matrix
    lap_mtx, adj_mtx = get_laplacian_mtx(adata,
                                         num_neighbors=num_neighbors,
                                         spatial_key=spatial_key,
                                         normalization=False)
    alpha = alpha / num_neighbors
    diff_mtx = np.eye(lap_mtx.shape[0]) - alpha * lap_mtx

    # check pathway
    if interaction in adata.uns['lr_info'].index:
        spot_ccc_mtx = spot_ccc_score_single(adata, interaction, alpha, beta, step, spatial_key, num_neighbors)
        return spot_ccc_mtx

    # determine the ligand exp and receptor exp
    elif interaction in np.unique(adata.uns['lr_meta_info']['pathway']):
        interaction_list = adata.uns['lr_meta_info'].loc[adata.uns['lr_meta_info']['pathway'] == interaction,
                           :].index.tolist()
        ligand_list = adata.uns['lr_info'].loc[interaction_list, 'ligand'].values
        receptor_list = adata.uns['lr_info'].loc[interaction_list, 'receptor'].values
    else:
        raise KeyError(f"Can not identify {interaction} as a pathway or a L-R interaction pair")

    # construct ligand-receptor map
    all_unique_ligands = np.unique(ligand_list).tolist()
    all_unique_receptors = np.unique(receptor_list).tolist()
    if not ss.issparse(adata.X):
        single_ligand_exp = pd.DataFrame(adata[:, all_unique_ligands].X,
                                         index=adata.obs_names,
                                         columns=all_unique_ligands)
        single_receptor_exp = pd.DataFrame(adata[:, all_unique_receptors].X,
                                           index=adata.obs_names,
                                           columns=all_unique_receptors)
    else:
        single_ligand_exp = pd.DataFrame(adata[:, all_unique_ligands].X.toarray(),
                                         index=adata.obs_names,
                                         columns=all_unique_ligands)
        single_receptor_exp = pd.DataFrame(adata[:, all_unique_receptors].X.toarray(),
                                           index=adata.obs_names,
                                           columns=all_unique_receptors)

    spot_ccc_mtx = _calculate_ccc_mtx_system(
        diff_mtx=diff_mtx,
        beta=beta,
        step=step,
        single_ligand_exp=single_ligand_exp,
        single_receptor_exp=single_receptor_exp,
        ligand_list=ligand_list,
        receptor_list=receptor_list,
        interaction_list=interaction_list,
    )
    spot_ccc_mtx = pd.DataFrame(spot_ccc_mtx,
                                index=adata.obs_names,
                                columns=adata.obs_names)
    return spot_ccc_mtx


def spot_ccc_score_system(adata,
                          interaction,
                          alpha,
                          beta,
                          step,
                          spatial_key='spatial',
                          num_neighbors=4,
                          n_split=[0, 0],
                          scalar=0.1):
    # try to split data to accelerate the calculation
    if n_split[0] > 1 or n_split[1] > 1:
        min_x, min_y = adata.obsm[spatial_key].min(axis=0)
        max_x, max_y = adata.obsm[spatial_key].max(axis=0)
        x_ticks = np.linspace(min_x, max_x, n_split[0] + 1)
        y_ticks = np.linspace(min_y, max_y, n_split[1] + 1)
        x_unit = x_ticks[1] - x_ticks[0]
        y_unit = y_ticks[1] - y_ticks[0]
        spot_ccc_list = []
        for i in range(n_split[0]):
            if i == n_split[0] - 1:
                tmp_adata = adata[np.logical_and(adata.obsm[spatial_key][:, 0] >= x_ticks[i] - x_unit * scalar,
                                                 adata.obsm[spatial_key][:, 0] <= x_ticks[i + 1] + x_unit * scalar), :]
            else:
                tmp_adata = adata[np.logical_and(adata.obsm[spatial_key][:, 0] >= x_ticks[i] - x_unit * scalar,
                                                 adata.obsm[spatial_key][:, 0] < x_ticks[i + 1] + x_unit * scalar), :]
            for j in range(n_split[1]):
                if j == n_split[1] - 1:
                    tmp_adata_2 = tmp_adata[
                                  np.logical_and(tmp_adata.obsm[spatial_key][:, 1] >= y_ticks[j] - y_unit * scalar,
                                                 tmp_adata.obsm[spatial_key][:, 1] <= y_ticks[j + 1] + y_unit * scalar),
                                  :]
                else:
                    tmp_adata_2 = tmp_adata[
                                  np.logical_and(tmp_adata.obsm[spatial_key][:, 1] >= y_ticks[j] - y_unit * scalar,
                                                 tmp_adata.obsm[spatial_key][:, 1] < y_ticks[j + 1] + y_unit * scalar),
                                  :]
                if tmp_adata_2.shape[0] <= num_neighbors * 2:
                    print('Not enough spots', tmp_adata_2.shape[0])
                    continue
                tmp_ccc_mtx = spot_ccc_score_system_sub(adata=tmp_adata_2,
                                                        interaction=interaction,
                                                        alpha=alpha,
                                                        beta=beta,
                                                        step=step,
                                                        spatial_key=spatial_key,
                                                        num_neighbors=num_neighbors)
                # in box spots
                in_box_spots = _in_box_spots(tmp_adata_2, spatial_key, x_ticks, y_ticks, i, j)
                tmp_ccc_mtx = tmp_ccc_mtx.loc[in_box_spots, :]
                spot_ccc_list.append(tmp_ccc_mtx.copy())

        # merge the results
        spot_ccc_mtx = np.zeros((adata.shape[0], adata.shape[0]))
        spot_ccc_mtx = pd.DataFrame(spot_ccc_mtx, index=adata.obs_names, columns=adata.obs_names)
        for tmp in spot_ccc_list:
            spot_ccc_mtx.loc[tmp.index, tmp.columns] += tmp

    else:
        spot_ccc_mtx = spot_ccc_score_system_sub(adata,
                                                 interaction,
                                                 alpha,
                                                 beta,
                                                 step,
                                                 spatial_key,
                                                 num_neighbors)

    return spot_ccc_mtx


def spot_ccc_score(adata,
                   interaction,
                   alpha,
                   beta,
                   step,
                   spatial_key='spatial',
                   num_neighbors=4,
                   n_split=[0, 0],
                   scalar=0.1,
                   mode='single'):
    if mode == 'single':
        spot_ccc_mtx = spot_ccc_score_single(adata,
                                             interaction,
                                             alpha,
                                             beta,
                                             step,
                                             spatial_key,
                                             num_neighbors,
                                             n_split,
                                             scalar)
    elif mode == 'system':
        spot_ccc_mtx = spot_ccc_score_system(adata,
                                             interaction,
                                             alpha,
                                             beta,
                                             step,
                                             spatial_key,
                                             num_neighbors,
                                             n_split,
                                             scalar)
    else:
        raise ValueError('mode should be single or system')

    return spot_ccc_mtx


def _cell_type_score2(adata, ccc_df, cell_type_key, spatial_key='spatial', k_range=50, min_cells=10):
    # obtain adjacent matrix
    if spatial_key in adata.obsm_keys():
        loc = adata.obsm[spatial_key]
    elif set(spatial_key) <= set(adata.obs_keys()):
        loc = adata.obs[spatial_key]
    else:
        raise KeyError("%s is not available in adata.obsm_keys" % \
                       spatial_key + " or adata.obs_keys")
    loc = pd.DataFrame(loc,
                       index=adata.obs_names)
    adj_mtx = compute_knn_adjacency_matrix(loc=loc, k=k_range)
    ct_anno = adata.obs[cell_type_key]
    all_cts = np.unique(ct_anno)
    valid_cts = []
    ct_number_df = pd.DataFrame(columns=['number'])
    for ct in all_cts:
        tmp_num = adata.obs.loc[adata.obs[cell_type_key] == ct, :].shape[0]
        if tmp_num >= min_cells:
            ct_number_df.loc[ct, 'number'] = tmp_num
            valid_cts.append(ct)
    ct_df = pd.DataFrame(0, index=valid_cts, columns=valid_cts)
    for i in valid_cts:
        for j in valid_cts:
            sender_cells = ct_anno.index[ct_anno == i]
            receiver_cells = ct_anno.index[ct_anno == j]
            interaction_score = ccc_df.loc[sender_cells, receiver_cells]
            k_range_ind = adj_mtx.loc[sender_cells, receiver_cells].values
            # sum the interaction scores within k_range
            interaction_score = interaction_score.values * k_range_ind
            # normalization (average)
            interaction_score = interaction_score.sum() / k_range_ind.sum()
            print(k_range_ind.sum())
            ct_df.loc[i, j] = interaction_score
    # normalization
    ct_df = ct_df / ct_df.max().max()
    return ct_df


def determine_distance_threshold_from_ccc(spot_ccc_df, distance_df, threshold=0.01):
    # Step 1: Find the maximum CCC score in the matrix
    max_ccc_value = spot_ccc_df.max().max()  # Get the maximum CCC value
    # Step 2: Set the CCC threshold as 10% of the maximum CCC value
    ccc_threshold = threshold * max_ccc_value
    print(f"CCC threshold ({threshold} * max): {ccc_threshold}")

    # Step 3: Find the pairs with CCC score greater than the threshold
    above_threshold_indices = spot_ccc_df.to_numpy() > ccc_threshold
    above_threshold_indices = above_threshold_indices.astype(int)

    # Step 4: Get the distances corresponding to these pairs

    distance_above_threshold = distance_df * above_threshold_indices

    # Step 5: Calculate the maximum distance of these pairs
    distance_threshold = distance_above_threshold.max().max()  # Get the maximum value
    print(f"Distance threshold determined from CCC threshold: {distance_threshold}")

    return distance_threshold


def cell_type_ccc_score(adata,
                        spot_ccc_df,
                        cell_type_key,
                        method='sum',
                        spatial_key='spatial',
                        threshold=0.01,
                        min_cells=10,
                        n_permutations=200,
                        multiprocessing=True,
                        random_state=None):
    # Calculate pair wise distances
    if spatial_key in adata.obsm_keys():
        loc_df = adata.obsm[spatial_key]
    else:
        loc_df = adata.obs[spatial_key]
    distance_df = pdist(loc_df, metric='euclidean')
    distance_df = squareform(distance_df)
    distance_max = distance_df.max()
    if distance_max == 0:
        distance_max = 1e-6
    distance_df = distance_df / distance_max
    distance_df = pd.DataFrame(distance_df,
                               index=adata.obs_names,
                               columns=adata.obs_names)
    # CT label dataframe
    ct_df = pd.DataFrame(adata.obs[cell_type_key].values,
                         index=adata.obs_names,
                         columns=['label'])

    # Step 1: Determine the distance threshold based on CCC threshold
    distance_threshold = determine_distance_threshold_from_ccc(spot_ccc_df=spot_ccc_df,
                                                               distance_df=distance_df,
                                                               threshold=threshold)

    # Step 2: Create a dictionary to store the average CCC scores for each pair of labels
    label_pairs_ccc = {}
    labels = ct_df['label'].unique()
    valid_labels = []
    ct_number_df = pd.DataFrame(columns=['number'])
    for ct in labels:
        tmp_num = adata.obs.loc[adata.obs[cell_type_key] == ct, :].shape[0]
        if tmp_num >= min_cells:
            ct_number_df.loc[ct, 'number'] = tmp_num
            valid_labels.append(ct)
    labels = valid_labels

    in_distance_matrix = distance_df <= distance_threshold
    in_distance_matrix = in_distance_matrix.astype(int).values
    spot_ccc_array = spot_ccc_df.values * in_distance_matrix

    # Step 3: Iterate over pairs of labels, including same label pairings
    for label_1 in labels:
        for label_2 in labels:
            # Get the indices of the current label
            label_1_indices = ct_df[ct_df['label'] == label_1].index
            label_2_indices = ct_df[ct_df['label'] == label_2].index

            # Step 4: Create sub-dataframes for the pair of labels
            sub_ccc_df = spot_ccc_df.loc[label_1_indices, label_2_indices].values
            sub_distance_df = distance_df.loc[label_1_indices, label_2_indices].values

            # Step 5: Filter pairs within the distance threshold
            sub_distance_df = sub_distance_df <= distance_threshold
            sub_distance_df = sub_distance_df.astype(int)

            # Step 6: Calculate the mean values only for sub_distance_df == 1
            masked_ccc = sub_ccc_df * sub_distance_df
            if method == 'sum':
                average_ccc = masked_ccc.sum()
            elif method == 'mean':
                average_ccc = masked_ccc.sum() / sub_distance_df.sum()
            else:
                raise KeyError("Method should be sum or mean")

            # Store the average CCC for this pair of labels
            label_pairs_ccc[(label_1, label_2)] = average_ccc

    # Step 7: Construct a label-pair CCC score matrix
    label_pair_matrix = pd.DataFrame(0, index=labels, columns=labels, dtype=float)

    # Fill the matrix with values
    for (label_1, label_2), avg_ccc in label_pairs_ccc.items():
        label_pair_matrix.loc[label_1, label_2] = avg_ccc
    ct_ccc_df = label_pair_matrix

    # calculate p values
    permutation_count_array = np.zeros_like(ct_ccc_df)
    labels_array = ct_df['label'].values
    original_ct_ccc = calculate_ct_mtx(spot_ccc_array=spot_ccc_array,
                                       labels_array=labels_array,
                                       labels=labels)
    if random_state is not None:
        np.random.seed(random_state)

    if not multiprocessing:
        for _ in tqdm(range(n_permutations), desc="Running permutations"):
            labels_array_p = np.random.permutation(labels_array)
            tmp = calculate_ct_mtx(spot_ccc_array=spot_ccc_array,
                                   labels_array=labels_array_p,
                                   labels=labels)
            permutation_count_array[tmp >= original_ct_ccc] += 1.0
    else:
        permutation_count_array = permutation_test(spot_ccc_array=spot_ccc_array,
                                                   n_permutations=n_permutations,
                                                   labels_array=labels_array,
                                                   labels=labels,
                                                   original_ct_ccc=original_ct_ccc
                                                   )

    # p-value_matrix
    ct_pvalue_df = permutation_count_array / n_permutations
    ct_pvalue_df = pd.DataFrame(ct_pvalue_df,
                                index=labels,
                                columns=labels)

    return ct_ccc_df, ct_pvalue_df


def calculate_ct_mtx(spot_ccc_array, labels_array, labels):
    label_indices = {label: np.where(labels_array == label)[0] for label in labels}

    def compute_row(j):
        tmp_idx_j = label_indices[labels[j]]
        row = np.zeros(len(labels), dtype=float)
        for k in range(len(labels)):
            tmp_idx_k = label_indices[labels[k]]
            masked_ccc = spot_ccc_array[np.ix_(tmp_idx_j, tmp_idx_k)]
            row[k] = masked_ccc.sum()
        return row

    ct_ccc_perm = Parallel(n_jobs=1)(delayed(compute_row)(j) for j in range(len(labels)))

    return np.array(ct_ccc_perm)


def calculate_ct_mtx_optimized(spot_ccc_array, labels_array, labels):
    label_indices = {label: np.where(labels_array == label)[0] for label in labels}

    ct_ccc_perm = np.zeros((len(labels), len(labels)), dtype=float)

    for j, label_j in enumerate(labels):
        tmp_idx_j = label_indices[label_j]
        row_sum = np.zeros(len(labels), dtype=float)

        for k, label_k in enumerate(labels):
            tmp_idx_k = label_indices[label_k]
            row_sum[k] = spot_ccc_array[tmp_idx_j[:, None], tmp_idx_k].sum()

        ct_ccc_perm[j, :] = row_sum

    return ct_ccc_perm


def single_permutation_task(args):
    seed, labels_array, labels, spot_ccc_array, original_ct_ccc = args
    np.random.seed(seed)
    labels_array_p = np.random.permutation(labels_array)
    tmp = calculate_ct_mtx_optimized(
        spot_ccc_array=spot_ccc_array,
        labels_array=labels_array_p,
        labels=labels
    )
    return tmp >= original_ct_ccc


def permutation_test(n_permutations, spot_ccc_array, labels_array, labels, original_ct_ccc):
    permutation_count_array = np.zeros_like(original_ct_ccc)

    with Pool() as pool:
        # Create a list of arguments for each permutation
        args_list = [(i, labels_array, labels, spot_ccc_array, original_ct_ccc) for i in range(n_permutations)]

        # Use imap with args_list to pass the arguments
        results = list(tqdm(pool.imap(single_permutation_task, args_list, chunksize=10),
                            desc="Running permutations",
                            total=n_permutations))

    # Accumulate results
    for result in results:
        permutation_count_array += result

    return permutation_count_array


def _cell_type_score(adata, ccc_df, cell_type_key, min_cells=10):
    ct_anno = adata.obs[cell_type_key]
    all_cts = np.unique(ct_anno)
    valid_cts = []
    ct_number_df = pd.DataFrame(columns=['number'])
    for ct in all_cts:
        tmp_num = adata.obs.loc[adata.obs[cell_type_key] == ct, :].shape[0]
        if tmp_num >= min_cells:
            ct_number_df.loc[ct, 'number'] = tmp_num
            valid_cts.append(ct)
    ct_df = pd.DataFrame(0, index=valid_cts, columns=valid_cts)
    for i in valid_cts:
        for j in valid_cts:
            sender_cells = ct_anno.index[ct_anno == i]
            receiver_cells = ct_anno.index[ct_anno == j]
            interaction_score = ccc_df.loc[sender_cells, receiver_cells]
            # normalization (average)
            interaction_score = interaction_score.values.mean()
            ct_df.loc[i, j] = interaction_score
    # normalization
    ct_df = ct_df / ct_df.max().max()
    return ct_df


def _calculate_ccc_mtx(ligand_exp,
                       receptor_exp,
                       diff_mtx,
                       beta,
                       step,
                       ):
    ligand_exp = ligand_exp.astype(np.float32)
    receptor_exp = receptor_exp.astype(np.float32)
    diff_mtx = diff_mtx.astype(np.float32)
    ccc_mtx = np.zeros((ligand_exp.shape[0], receptor_exp.shape[0]), dtype=np.float32)
    trace_ligand_exp_list = []
    trace_receptor_exp_list = []
    for m in range(ligand_exp.shape[1]):
        trace_ligand_exp = np.diag(ligand_exp[:, m])
        trace_receptor_exp = receptor_exp[:, m].reshape(-1, 1)
        trace_ligand_exp_list.append(trace_ligand_exp)
        trace_receptor_exp_list.append(trace_receptor_exp)

    diff_mtx_power = diff_mtx.copy()
    step_tqdm = tqdm(range(1, step + 1))
    for _ in step_tqdm:
        step_tqdm.set_description("step")
        for m in range(len(trace_receptor_exp_list)):
            trace_ligand_exp = trace_ligand_exp_list[m]
            trace_receptor_exp = trace_receptor_exp_list[m]
            tmp_ccc_mtx = trace_ligand_exp * trace_receptor_exp
            ccc_mtx = ccc_mtx + tmp_ccc_mtx

            # Update trace_ligand （the above lists will be updated automatically)
            trace_ligand_exp = diff_mtx_power @ trace_ligand_exp - beta * tmp_ccc_mtx
            trace_receptor_exp = trace_receptor_exp - beta * tmp_ccc_mtx.sum(axis=1).reshape(-1, 1)
            trace_ligand_exp = np.clip(trace_ligand_exp, 0, None)
            trace_receptor_exp = np.clip(trace_receptor_exp, 0, None)
            trace_ligand_exp_list[m] = trace_ligand_exp
            trace_receptor_exp_list[m] = trace_receptor_exp
    ccc_mtx = ccc_mtx.transpose()

    return ccc_mtx


def _calculate_ccc_mtx_system(
        single_ligand_exp,
        single_receptor_exp,
        ligand_list,
        receptor_list,
        interaction_list,
        diff_mtx,
        beta,
        step,
):
    single_ligand_exp = single_ligand_exp.astype(np.float32)
    single_receptor_exp = single_receptor_exp.astype(np.float32)
    diff_mtx = diff_mtx.astype(np.float32)
    ccc_mtx = np.zeros_like(diff_mtx, dtype=np.float32)
    trace_single_ligand_exp_dict = dict()
    trace_single_receptor_exp_dict = dict()

    # obtain the initial distribution
    for single_ligand in single_ligand_exp.columns:
        trace_single_ligand_exp = np.diag(single_ligand_exp[single_ligand].values)
        trace_single_ligand_exp_dict[single_ligand] = trace_single_ligand_exp
    for single_receptor in single_receptor_exp.columns:
        trace_single_receptor_exp = single_receptor_exp[single_receptor].values.reshape(-1, 1)
        trace_single_receptor_exp_dict[single_receptor] = trace_single_receptor_exp

    diff_mtx_power = diff_mtx
    step_tqdm = tqdm(range(1, step + 1))

    for _ in step_tqdm:
        step_tqdm.set_description("step")

        # initialize interaction values for recoding
        trace_ccc_ligand_dict = dict()
        trace_ccc_receptor_dict = dict()
        for single_ligand in single_ligand_exp.columns:
            trace_ccc_ligand = np.zeros_like(ccc_mtx, dtype=np.float32)
            trace_ccc_ligand_dict[single_ligand] = trace_ccc_ligand
        for single_receptor in single_receptor_exp.columns:
            trace_ccc_receptor = np.zeros(ccc_mtx.shape[1], dtype=np.float32).reshape(-1, 1)
            trace_ccc_receptor_dict[single_receptor] = trace_ccc_receptor

        # calculate interaction
        for k, lr in enumerate(interaction_list):
            # obtain the ligand and receptor of current interaction
            ligand = ligand_list[k]
            receptor = receptor_list[k]
            # obtain spatial distributions for these molecules
            tmp_single_ligand = trace_single_ligand_exp_dict[ligand]
            tmp_single_receptor = trace_single_receptor_exp_dict[receptor]
            # calculate interaction ccc matrix
            tmp_ccc_mtx = tmp_single_ligand * tmp_single_receptor
            ccc_mtx = ccc_mtx + tmp_ccc_mtx

            # Record interactions
            trace_ccc_ligand_dict[ligand] = trace_ccc_ligand_dict[ligand] + tmp_ccc_mtx
            trace_ccc_receptor_dict[receptor] = trace_ccc_receptor_dict[receptor] + tmp_ccc_mtx.sum(axis=1).reshape(-1,
                                                                                                                    1)

        # update ligand states
        for single_ligand in single_ligand_exp.columns:
            tmp = (diff_mtx_power @ trace_single_ligand_exp_dict[single_ligand])
            tmp = tmp - beta * trace_ccc_ligand_dict[single_ligand]  # according to grd equations
            # clip to ensure non-negative values
            trace_single_ligand_exp_dict[single_ligand] = np.clip(tmp, 0, None)

        # update receptor states
        for single_receptor in single_receptor_exp.columns:
            tmp = trace_single_receptor_exp_dict[single_receptor] - beta * trace_ccc_receptor_dict[single_receptor]
            # clip to ensure non-negative values
            trace_single_receptor_exp_dict[single_receptor] = np.clip(tmp, 0, None)

    ccc_mtx = ccc_mtx.transpose()
    return ccc_mtx


def pathway_ccc(adata,
                pathway,
                alpha,
                beta,
                step,
                mode='single',
                ):
    # obtain meta_info
    lr_mata_info = adata.uns['lr_meta_info']
    interaction_list = lr_mata_info.index[lr_mata_info['pathway_name'] == pathway]

    # find ligands corresponding to this pathway
    ligand_list = adata.uns['lr_info'].loc[interaction_list, 'ligand'].values.tolist()
    receptor_list = adata.uns['lr_info'].loc[interaction_list, 'receptor'].values.tolist()
    adjacent_mtx = adata.uns['adj_mtx']

    # obtain lr mapping
    if mode == 'system':
        all_unique_ligands = np.unique(ligand_list)
        all_unique_receptors = np.unique(receptor_list)
        if ss.issparse(adata.X):
            ligand_exp = adata[:, all_unique_ligands].X.A
            receptor_exp = adata[:, all_unique_receptors].X.A

        else:
            ligand_exp = adata[:, all_unique_ligands].X
            receptor_exp = adata[:, all_unique_receptors].X
        lr_mapping = adata.uns['lr_mapping'].loc[all_unique_receptors, all_unique_ligands]
        ccc_score = spot_ccc_score_system(ligand_exp=ligand_exp,
                                          receptor_exp=receptor_exp,
                                          lr_mapping=lr_mapping,
                                          adjacent_mtx=adjacent_mtx,
                                          alpha=alpha,
                                          beta=beta,
                                          step=step)
    elif mode == 'single':
        # obtain ligand exp and receptor exp
        if ss.issparse(adata.X):
            ligand_exp = adata[:, ligand_list].X.A
            receptor_exp = adata[:, receptor_list].X.A

        else:
            ligand_exp = adata[:, ligand_list].X
            receptor_exp = adata[:, receptor_list].X

        ccc_score = spot_ccc_score_single(ligand_exp=ligand_exp,
                                          receptor_exp=receptor_exp,
                                          adj_mtx=adjacent_mtx,
                                          alpha=alpha,
                                          beta=beta,
                                          step=step)
    return ccc_score


def pathway_direction(adata,
                      ccc_mtx,
                      pathway_name,
                      spatial_key='spatial',
                      k=5,
                      ):
    # prepare
    n_cell = adata.shape[0]
    pts = np.array(adata.obsm[spatial_key], float)

    # initialize
    S_np = ccc_mtx
    sender_vf = np.zeros_like(pts)
    receiver_vf = np.zeros_like(pts)

    tmp_idx = np.argsort(-S_np, axis=1)[:, :k]
    avg_v = np.zeros_like(pts)
    for ik in range(k):
        tmp_v = pts[tmp_idx[:, ik]] - pts[np.arange(n_cell, dtype=int)]
        tmp_v = normalize(tmp_v, norm='l2')
        avg_v = avg_v + tmp_v * S_np[np.arange(n_cell, dtype=int), tmp_idx[:, ik]].reshape(-1, 1)
    avg_v = normalize(avg_v)
    sender_vf = avg_v * np.sum(S_np, axis=1).reshape(-1, 1)

    S_np = S_np.T
    tmp_idx = np.argsort(-S_np, axis=1)[:, :k]
    avg_v = np.zeros_like(pts)
    for ik in range(k):
        tmp_v = -pts[tmp_idx[:, ik]] + pts[np.arange(n_cell, dtype=int)]
        tmp_v = normalize(tmp_v, norm='l2')
        avg_v = avg_v + tmp_v * S_np[np.arange(n_cell, dtype=int), tmp_idx[:, ik]].reshape(-1, 1)
    avg_v = normalize(avg_v)
    receiver_vf = avg_v * np.sum(S_np, axis=1).reshape(-1, 1)

    adata.obsm["commot_sender_vf-" + pathway_name] = sender_vf
    adata.obsm["commot_receiver_vf-" + pathway_name] = receiver_vf
    s_sum_df = pd.DataFrame(ccc_mtx.sum(axis=1).reshape(-1, 1),
                            index=adata.obs_names,
                            columns=["s-" + pathway_name])
    r_sum_df = pd.DataFrame(ccc_mtx.sum(axis=0).reshape(-1, 1),
                            index=adata.obs_names,
                            columns=["r-" + pathway_name])
    adata.obsm['commot' + "-sum-sender"] = s_sum_df
    adata.obsm['commot' + "-sum-receiver"] = r_sum_df


def reaction_diffusion_system_source(adata,
                                     n_neighbors=6,
                                     spatial_key='spatial',
                                     normalize_lap=False,
                                     alpha=0.3,
                                     beta=0.3,
                                     gamma=0.3,
                                     step=2):
    # Preprocessing
    adata.var_names_make_unique()
    sc.pp.filter_genes(adata, min_cells=1)

    # Get Laplacian matrix according to coordinates
    lap_mtx = get_laplacian_mtx(adata,
                                num_neighbors=n_neighbors,
                                spatial_key=spatial_key,
                                normalization=normalize_lap)
    diffusion_mtx = np.eye(lap_mtx.shape[0]) - alpha * lap_mtx.A

    # Define several dataframe to save the process of reaction-diffusion
    interaction_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)
    next_ligand_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)
    next_receptor_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)

    # Extract initial ligand expression matrix and receptor expression matrix
    if ss.issparse(adata.X):
        ligand_exp_df = pd.DataFrame(adata[:, adata.uns['lr_info']['all_ligands']].X.A,
                                     index=adata.obs_names,
                                     columns=adata.uns['lr_info']['all_ligands']).astype(np.float32)
        receptor_exp_df = pd.DataFrame(adata[:, adata.uns['lr_info']['all_receptors']].X.A,
                                       index=adata.obs_names,
                                       columns=adata.uns['lr_info']['all_receptors']).astype(np.float32)
    else:
        ligand_exp_df = pd.DataFrame(adata[:, adata.uns['lr_info']['all_ligands']].X,
                                     index=adata.obs_names,
                                     columns=adata.uns['lr_info']['all_ligands']).astype(np.float32)
        receptor_exp_df = pd.DataFrame(adata[:, adata.uns['lr_info']['all_receptors']].X,
                                       index=adata.obs_names,
                                       columns=adata.uns['lr_info']['all_receptors']).astype(np.float32)
    # init state
    init_ligand_exp_df = ligand_exp_df.copy()
    init_receptor_exp_df = receptor_exp_df.copy()

    # Process ligands
    # obtain the characters of ligands
    lr_map_df = adata.uns['lr_info']['lr_map']
    l_secreted_df = adata.uns['lr_info']['l_secreted']
    for ligand in ligand_exp_df.columns:
        # current (current time point) gene expression of the signal ligand
        current_ligand_values = ligand_exp_df.loc[:, ligand].values
        # search the related receptors which can interact with above ligand
        related_receptors = lr_map_df.loc[ligand, :][lr_map_df.loc[ligand, :] == 1].index.tolist()
        # obtain next time point status of the ligand
        interaction_values = np.zeros_like(current_ligand_values)
        for receptor in related_receptors:
            # current (current time point) gene expression of a related receptor
            current_receptor_values = receptor_exp_df.loc[:, receptor].values
            # reaction term and sum
            interaction_values += beta * current_ligand_values * current_receptor_values
        # obtain the class of the ligand
        annotation = l_secreted_df.loc[ligand, 'secreted_signal']
        if annotation == 1:
            next_ligand_values = np.matmul(diffusion_mtx, current_ligand_values) - interaction_values + \
                                 gamma * init_ligand_exp_df.loc[:, ligand].values
        else:
            next_ligand_values = current_ligand_values - interaction_values + \
                                 gamma * init_ligand_exp_df.loc[:, ligand].values
        next_ligand_values[next_ligand_values < 0] = 0  # remove negative values
        next_ligand_exp_df.loc[:, ligand] = next_ligand_values

    # Process receptors
    for receptor in receptor_exp_df.columns:
        # current (current time point) gene expression of the signal receptor
        current_receptor_values = receptor_exp_df.loc[:, receptor].values
        # search the related ligands which can interact with above receptor
        related_ligands = lr_map_df.loc[:, receptor][lr_map_df.loc[:, receptor] == 1].index.tolist()
        # obtain next time point status of the receptor
        interaction_values = np.zeros_like(current_receptor_values)
        for ligand in related_ligands:
            # current (current time point) gene expression of a related ligand
            current_ligand_values = ligand_exp_df.loc[:, ligand].values
            # reaction term and sum
            interaction_values += beta * current_ligand_values * current_receptor_values
        next_receptor_values = current_receptor_values - interaction_values + \
                               gamma * init_receptor_exp_df.loc[:, receptor].values
        next_receptor_values[next_receptor_values < 0] = 0  # remove negative values
        next_receptor_exp_df.loc[:, receptor] = next_receptor_values

    # Measure the interaction intensity of interactions
    lr_info = adata.uns['lr_info']
    interaction_list = lr_info['interaction']

    def calculate_production_ligand(units):
        products = ligand_exp_df[units].values
        indications = np.prod(products, axis=1)
        return indications

    def calculate_production_receptor(units):
        products = receptor_exp_df[units].values
        indications = np.prod(products, axis=1)
        return indications

    # use tqdm
    tqdm_interation_list = tqdm(interaction_list)
    for interaction in tqdm_interation_list:
        tqdm_interation_list.set_description("Processing: %s" % interaction)
        # extract current status
        tmp_ligand_values = calculate_production_ligand(lr_info['ligand_unit'][interaction])
        tmp_receptor_values = calculate_production_receptor(lr_info['receptor_unit'][interaction])
        # compute next time point
        interaction_values = beta * tmp_ligand_values * tmp_receptor_values
        # save
        interaction_exp_df.loc[:, interaction] = interaction_values

    adata.uns['interaction_info'] = {'0': [ligand_exp_df.copy(), receptor_exp_df.copy()],
                                     '1': [interaction_exp_df.copy(),
                                           next_ligand_exp_df.copy(),
                                           next_receptor_exp_df.copy()]}

    # The future interaction across multiple time point
    for i in range(step - 1):
        ligand_exp_df = next_ligand_exp_df
        receptor_exp_df = next_receptor_exp_df
        next_ligand_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)
        next_receptor_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)
        interaction_exp_df = pd.DataFrame(index=adata.obs_names).astype(np.float32)

        for ligand in ligand_exp_df.columns:
            # current (current time point) gene expression of the signal ligand
            current_ligand_values = ligand_exp_df.loc[:, ligand].values
            # search the related receptors which can interact with above ligand
            related_receptors = lr_map_df.loc[ligand, :][lr_map_df.loc[ligand, :] == 1].index.tolist()
            # obtain next time point status of the ligand
            interaction_values = np.zeros_like(current_ligand_values)
            for receptor in related_receptors:
                # current (current time point) gene expression of a related receptor
                current_receptor_values = receptor_exp_df.loc[:, receptor].values
                # reaction term and sum
                interaction_values += beta * current_ligand_values * current_receptor_values
            # obtain the class of the ligand
            annotation = l_secreted_df.loc[ligand, 'secreted_signal']
            if annotation == 1:
                next_ligand_values = np.matmul(diffusion_mtx, current_ligand_values) - interaction_values + \
                                     gamma * init_ligand_exp_df.loc[:, ligand].values
            else:
                next_ligand_values = current_ligand_values - interaction_values + \
                                     gamma * init_ligand_exp_df.loc[:, ligand].values
            next_ligand_values[next_ligand_values < 0] = 0  # remove negative values
            next_ligand_exp_df.loc[:, ligand] = next_ligand_values

        # Process receptors
        for receptor in receptor_exp_df.columns:
            # current (current time point) gene expression of the signal receptor
            current_receptor_values = receptor_exp_df.loc[:, receptor].values
            # search the related ligands which can interact with above receptor
            related_ligands = lr_map_df.loc[:, receptor][lr_map_df.loc[:, receptor] == 1].index.tolist()
            # obtain next time point status of the receptor
            interaction_values = np.zeros_like(current_receptor_values)
            for ligand in related_ligands:
                # current (current time point) gene expression of a related ligand
                current_ligand_values = ligand_exp_df.loc[:, ligand].values
                # reaction term and sum
                interaction_values += beta * current_ligand_values * current_receptor_values
            next_receptor_values = current_receptor_values - interaction_values + \
                                   gamma * init_receptor_exp_df.loc[:, receptor].values
            next_receptor_values[next_receptor_values < 0] = 0  # remove negative values
            next_receptor_exp_df.loc[:, receptor] = next_receptor_values

        tqdm_interation_list = tqdm(interaction_list)
        for interaction in tqdm_interation_list:
            annotation = adata.uns['lr_info']['annotation'][interaction]
            tqdm_interation_list.set_description("Processing: %s" % interaction)
            # extract current status
            tmp_ligand_values = calculate_production_ligand(lr_info['ligand_unit'][interaction])
            tmp_receptor_values = calculate_production_receptor(lr_info['receptor_unit'][interaction])
            # compute next time point
            interaction_values = beta * tmp_ligand_values * tmp_receptor_values
            # save
            interaction_exp_df.loc[:, interaction] = interaction_values

        adata.uns['interaction_info'][str(i + 2)] = [interaction_exp_df.copy(),
                                                     next_ligand_exp_df.copy(),
                                                     next_receptor_exp_df.copy()]


def obtain_lr_freq(adata):
    # Extract fourier modes and L-R information
    eigen_t = adata.uns['GFT_info']['fourier_modes']
    eigen_t = eigen_t[1:, :]
    all_ligands = adata.uns['lr_info']['all_ligands']
    all_receptors = adata.uns['lr_info']['all_receptors']

    # Implement GFT for ligands
    exp_mtx = adata.uns['diffusion_ligands'].values
    ligand_freq_mtx = np.matmul(eigen_t, exp_mtx)
    ligand_freq_mtx = preprocessing.normalize(ligand_freq_mtx,
                                              norm='l1',
                                              axis=0).transpose()
    ligand_freq_mtx = pd.DataFrame(ligand_freq_mtx,
                                   index=all_ligands,
                                   columns=[f'FC_{i}' for i in range(ligand_freq_mtx.shape[1])])

    # Implement GFT for receptors
    if ss.issparse(adata.X):
        exp_mtx = adata[:, all_receptors].X.A
    else:
        exp_mtx = adata[:, all_receptors].X
    receptor_freq_mtx = np.matmul(eigen_t, exp_mtx)
    receptor_freq_mtx = preprocessing.normalize(receptor_freq_mtx,
                                                norm='l1',
                                                axis=0).transpose()
    receptor_freq_mtx = pd.DataFrame(receptor_freq_mtx,
                                     index=all_receptors,
                                     columns=[f'FC_{i}' for i in range(receptor_freq_mtx.shape[1])])

    # save results to adata
    adata.uns['GFT_info']['ligand_freq_mtx'] = ligand_freq_mtx
    adata.uns['GFT_info']['receptor_freq_mtx'] = receptor_freq_mtx


def low_pass_enhancement(adata,
                         ratio_low_freq='infer',
                         ratio_neighbors='infer',
                         c=0.001,
                         spatial_info=['array_row', 'array_col'],
                         normalize_lap=False,
                         inplace=False):
    """
    Implement gene expression with low-pass filter. After this step, the 
    spatially variables genes will be more smooth than the previous. The 
    function can also be treated as denoising. Note that the denoising results
    is related to spatial graph topology so that only the results of spatially 
    variable genes could be convincing.

    Parameters
    ----------
    adata : AnnData
        adata.X is the normalized count matrix. Besides, the spatial coordinates of all spots should be found
        in adata.obs or adata.obsm.
    ratio_low_freq : float | "infer", optional
        The ratio_low_freq will be used to determine the number of the FMs with
        low frequencies. Indeed, the ratio_low_freq * sqrt(number of spots) low
        frequency FMs will be calculated. The default is 'infer'.
        A high can achieve better smoothness. c should be set to [0, 0.1].
    ratio_neighbors: float | 'infer', optional
        The ratio_neighbors will be used to determine the number of neighbors
        when construct the KNN graph by spatial coordinates. Indeed, ratio_neighbors * sqrt(number of spots) / 2
        indicates the K. If 'infer', the para will be set to 1.0. The default is 'infer'.
    c: float, optional
        c balances the smoothness and difference with previous expression. The
        default is 0.001
    spatial_info : list | tuple | string, optional
        The column names of spatial coordinates in adata.obs_names or key
        in adata.obsm_keys() to obtain spatial information. The default
        is ['array_row', 'array_col'].
    normalize_lap : bool. optional
        Whether you need to normalize the Laplacian matrix. The default is False.
    inplace: bool, optional
        Whether you need to replace adata.X with the enhanced expression matrix.
        

    Returns
    -------
    count_matrix: DataFrame

    """
    import scipy.sparse as ss
    if ratio_low_freq == 'infer':
        if adata.shape[0] <= 800:
            num_low_frequency = min(20 * int(np.ceil(np.sqrt(adata.shape[0]))),
                                    adata.shape[0])
        elif adata.shape[0] <= 5000:
            num_low_frequency = 15 * int(np.ceil(np.sqrt(adata.shape[0])))
        elif adata.shape[0] <= 10000:
            num_low_frequency = 10 * int(np.ceil(np.sqrt(adata.shape[0])))
        else:
            num_low_frequency = 5 * int(np.ceil(np.sqrt(adata.shape[0])))
    else:
        num_low_frequency = int(np.ceil(np.sqrt(adata.shape[0]) * \
                                        ratio_low_freq))

    if ratio_neighbors == 'infer':
        if adata.shape[0] <= 500:
            num_neighbors = 4
        else:
            num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2))
    else:
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2 \
                                    * ratio_neighbors))

    adata.var_names_make_unique()
    sc.pp.filter_genes(adata, min_cells=1)

    # Get Laplacian matrix according to coordinates 
    lap_mtx = get_laplacian_mtx(adata,
                                num_neighbors=num_neighbors,
                                spatial_key=spatial_info,
                                normalization=normalize_lap)

    # Fourier modes of low frequency
    num_low_frequency = min(num_low_frequency, adata.shape[0])
    eigvals, eigvecs = ss.linalg.eigsh(lap_mtx.astype(float),
                                       k=num_low_frequency,
                                       which='SM')

    # *********************** Graph Fourier Tranform **************************
    # Calculate GFT
    eigvecs_T = eigvecs.transpose()
    if not ss.issparse(adata.X):
        exp_mtx = adata.X
    else:
        exp_mtx = adata.X.toarray()
    frequency_array = np.matmul(eigvecs_T, exp_mtx)
    # low-pass filter
    filter_list = [1 / (1 + c * eigv) for eigv in eigvals]
    filter_array = np.matmul(np.diag(filter_list), frequency_array)
    filter_array = np.matmul(eigvecs, filter_array)
    filter_array[filter_array < 0] = 0

    # whether need to replace original count matrix
    if inplace and not ss.issparse(adata.X):
        adata.X = filter_array
    elif inplace:
        import scipy.sparse as ss
        adata.X = ss.csr.csr_matrix(filter_array)

    filter_array = pd.DataFrame(filter_array,
                                index=adata.obs_names,
                                columns=adata.var_names)
    return filter_array


def determine_frequency_ratio(adata,
                              low_end=5,
                              high_end=5,
                              ratio_neighbors='infer',
                              spatial_info='spatial',
                              normalize_lap=False):
    """
     This function automatically chooses the number of FMs based on the kneedle algorithm.

     Parameters
     ----------
     adata : AnnData
         adata.X is the normalized count matrix. Additionally, the spatial coordinates of all spots should be found in
         adata.obs or adata.obsm.
     low_end : float, optional
         The range of low-frequency FMs. The default is 3.
     high_end : float, optional
         The range of high-frequency FMs. The default is 3.
     ratio_neighbors : float | str, optional
         The ratio_neighbors will be used to determine the number of neighbors
         when constructing the KNN graph by spatial coordinates. Specifically,
         ratio_neighbors * sqrt(number of spots) / 2 indicates the K. If 'infer', the parameter will be set to 1.0.
         The default is 'infer'.
     spatial_info : list | tuple | string, optional
         The column names of spatial coordinates in adata.obs_names or key
         in adata.obsm_keys() to obtain spatial information. The default is "spatial".
     normalize_lap : bool, optional
         Whether to normalize the Laplacian matrix. The default is False.

     Returns
     -------
     low_cutoff : float
         The low_cutoff * sqrt(the number of spots) low-frequency FMs are
         recommended in detecting SVG.
     high_cutoff : float
         The high_cutoff * sqrt(the number of spots) high-frequency FMs are
         recommended in detecting SVG.
     """
    # Determine the number of neighbors
    if ratio_neighbors == 'infer':
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2))
    else:
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2 * ratio_neighbors))
    if adata.shape[0] > 20000 and low_end >= 3:
        low_end = 3
    if adata.shape[0] > 20000 and high_end >= 3:
        high_end = 3

    # *************** Construct graph and corresponding matrix ***************
    lap_mtx, _ = get_laplacian_mtx(adata,
                                   num_neighbors=num_neighbors,
                                   spatial_key=spatial_info,
                                   normalization=normalize_lap)
    if adata.shape[0] <= 20000:
        eig_vals, eig_vecs = scipy.linalg.eigh(lap_mtx)
        eig_vals_s = eig_vals[:int(np.ceil(low_end * np.sqrt(adata.shape[0])))]
        eig_vecs_s = eig_vecs[:, :int(np.ceil(low_end * np.sqrt(adata.shape[0])))]
        eig_vals_l = eig_vals[-int(np.ceil(high_end * np.sqrt(adata.shape[0]))):]
        eig_vecs_l = eig_vecs[:, -int(np.ceil(high_end * np.sqrt(adata.shape[0]))):]
    else:
        lap_mtx = ss.csr_matrix(lap_mtx)
        # Next, calculate the eigenvalues and eigenvectors of the Laplace matrix
        eig_vals_s, eig_vecs_s = ss.linalg.eigsh(lap_mtx.astype(float),
                                                 k=int(np.ceil(low_end * np.sqrt(adata.shape[0]))),
                                                 which='SM')

        eig_vals_l, eig_vecs_l = ss.linalg.eigsh(lap_mtx.astype(float),
                                                 k=int(np.ceil(high_end * np.sqrt(adata.shape[0]))),
                                                 which='LM')

    low_cutoff = np.ceil(kneed_select_values(eig_vals_s) / np.sqrt(adata.shape[0]) * 1000) / 1000
    if low_cutoff >= low_end:
        low_cutoff = low_end
    if low_cutoff < 1:
        low_cutoff = 1
    num_low = int(np.ceil(np.sqrt(adata.shape[0]) * low_cutoff))
    high_cutoff = np.ceil(kneed_select_values(eig_vals_l,
                                              increasing=False) / np.sqrt(adata.shape[0]) * 1000) / 1000
    if high_cutoff < 1:
        high_cutoff = 1
    if high_cutoff >= high_end:
        high_cutoff = high_end
    num_high = int(np.ceil(np.sqrt(adata.shape[0]) * high_cutoff))

    adata.uns['FMs_after_select'] = {'low_FMs_frequency': eig_vals_s[:num_low],
                                     'low_FMs': eig_vecs_s[:, :num_low],
                                     'high_FMs_frequency': eig_vals_l[(len(eig_vals_l) - num_high):],
                                     'high_FMs': eig_vecs_l[:, (len(eig_vals_l) - num_high):]}

    return low_cutoff, high_cutoff


def svi_detection(adata,
                  ratio_low_freq=1,
                  ratio_high_freq=1,
                  ratio_neighbors=1,
                  spatial_info='spatial',
                  normalize_lap=False,
                  filter_peaks=False,
                  S=5,
                  cal_pval=True):
    """
    Rank genes accoding to GFT score to find spatially variable genes based on
    graph Fourier transform.

    Parameters
    ----------
    adata : AnnData
        adata.X is the normalized count matrix. Besides, the spatial coordinates could be found
        in adata.obs or adata.obsm.
    ratio_low_freq : float | "infer", optional
        The ratio_low_freq will be used to determine the number of the FMs with
        low frequencies. Indeed, the ratio_low_freq * sqrt(number of spots) low
        frequency FMs will be calculated. If 'infer', the ratio_low_freq will be
        set to 1.0. The default is 'infer'.
    ratio_high_freq: float | 'infer', optional
        The ratio_high_freq will be used to determine the number of the FMs of
        high frequencies. Indeed, the ratio_high_freq * sqrt(number of spots) 
        high frequency FMs will be calculated. If 'infer', the ratio_high_freq
        will be set to 1.0. The default is 'infer'.
    ratio_neighbors: float | 'infer', optional
        The ratio_neighbors will be used to determine the number of neighbors
        when construct the KNN graph by spatial coordinates. Indeed, ratio_neighbors * sqrt(number of spots) / 2
        indicates the K. If 'infer', the para will be set to 1.0. The default is 'infer'.
    spatial_info : list | tuple | string, optional
        The column names of spatial coordinates in adata.obs_names or key
        in adata.varm_keys() to obtain spatial information. The default
        is ['array_row', 'array_col'].
    normalize_lap : bool, optional
        Whether you need to normalize laplacian matrix. The default is false.
    filter_peaks: bool, optional
        For calculated vectors/signals in frequency/spectral domian, whether
        filter low peaks to stress the important peaks. The default is True.
    S: int, optional
        The sensitivity parameter in Kneedle algorithm. A large S will enable
        more genes identified as SVGs according to gft_score. The default is
        5.
    cal_pval : bool, optional
        Whether you need to calculate p val by mannwhitneyu. The default is False.
    Returns
    -------
    score_df : dataframe
        Return gene information.

    """
    # Ensure parameters
    if ratio_low_freq == 'infer':
        num_low_frequency = int(np.ceil(np.sqrt(adata.shape[0])))
    else:
        num_low_frequency = int(np.ceil(np.sqrt(adata.shape[0]) * ratio_low_freq))
    if ratio_high_freq == 'infer':
        num_high_frequency = int(np.ceil(np.sqrt(adata.shape[0])))
    else:
        num_high_frequency = int(np.ceil(np.sqrt(adata.shape[0]) * ratio_high_freq))

    if ratio_neighbors == 'infer':
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2))
    else:
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2 * ratio_neighbors))
    if adata.shape[0] <= 500:
        num_neighbors = 4

    # Check dimensions
    if 'FMs_after_select' in adata.uns_keys():
        low_condition = (num_low_frequency == adata.uns['FMs_after_select']['low_FMs_frequency'].size)
        high_condition = (num_high_frequency == adata.uns['FMs_after_select']['high_FMs_frequency'].size)
    else:
        low_condition = False
        high_condition = False
    # ************ Construct graph and corresponding matrixs *************
    lap_mtx, _ = get_laplacian_mtx(adata,
                                   num_neighbors=num_neighbors,
                                   spatial_key=spatial_info,
                                   normalization=normalize_lap)

    # Next, calculate the eigenvalues and eigenvectors of the Laplacian
    # matrix as the Fourier modes with certain frequencies
    if not low_condition:
        eigvals_s, eigvecs_s = ss.linalg.eigsh(lap_mtx.astype(float),
                                               k=num_low_frequency,
                                               which='SM')
    else:
        eigvals_s, eigvecs_s = adata.uns['FMs_after_select'] \
            ['low_FMs_frequency'], \
            adata.uns['FMs_after_select']['low_FMs']
        print('The precalculated low-frequency FMs are USED')
    if not high_condition:
        if num_high_frequency > 0:
            # Fourier bases of high frequency
            eigvals_l, eigvecs_l = ss.linalg.eigsh(lap_mtx.astype(float),
                                                   k=num_high_frequency,
                                                   which='LM')
    else:
        eigvals_l, eigvecs_l = adata.uns['FMs_after_select'] \
            ['high_FMs_frequency'], \
            adata.uns['FMs_after_select']['high_FMs']
        print('The precalculated high-frequency FMs are USED')
    if num_high_frequency > 0:
        # eigenvalues
        eig_vals = np.concatenate((eigvals_s, eigvals_l))
        # eigenvectors
        eig_vecs = np.concatenate((eigvecs_s, eigvecs_l), axis=1)
    else:
        eig_vals = eigvals_s
        eig_vecs = eigvecs_s

    # ************************ Graph Fourier Transform *************************
    # Calculate GFT
    eig_vecs = eig_vecs.transpose()
    exp_mtx = adata.obsm['interaction_score'].values
    exp_mtx = preprocessing.minmax_scale(exp_mtx, axis=0)
    frequency_array = np.matmul(eig_vecs, exp_mtx)
    frequency_array = np.abs(frequency_array)

    # Filter noise peaks
    if filter_peaks:
        frequency_array_thres_low = np.quantile(frequency_array[:num_low_frequency, :], q=0.5, axis=0)
        frequency_array_thres_high = np.quantile(frequency_array[num_low_frequency:, :], q=0.5, axis=0)
        for j in range(frequency_array.shape[1]):
            frequency_array[:num_low_frequency, :] \
                [frequency_array[:num_low_frequency, j] <= \
                 frequency_array_thres_low[j], j] = 0
            frequency_array[num_low_frequency:, :] \
                [frequency_array[num_low_frequency:, j] <= \
                 frequency_array_thres_high[j], j] = 0

    frequency_array = preprocessing.normalize(frequency_array,
                                              norm='l1',
                                              axis=0)

    eig_vals = np.abs(eig_vals)
    eigvals_weight = np.exp(-1 * eig_vals)
    score_list = np.matmul(eigvals_weight, frequency_array)
    score_ave = np.matmul(eigvals_weight, (1 / len(eig_vals)) * \
                          np.ones(len(eig_vals)))
    score_list = score_list / score_ave
    print("Graph Fourier Transform finished!")

    # Rank genes according to smooth score
    score_df = score_list
    score_df = pd.DataFrame(score_df)
    score_df.index = adata.obsm['interaction_score'].columns
    score_df.columns = ['gft_score']
    score_df = score_df.sort_values(by="gft_score", ascending=False)
    score_df.loc[:, "svi_rank"] = range(1, score_df.shape[0] + 1)

    # Determine cutoff of gft_score
    from kneed import KneeLocator
    magic = KneeLocator(score_df.svi_rank.values,
                        score_df.gft_score.values,
                        direction='decreasing',
                        curve='convex',
                        S=S)
    score_df['cutoff_gft_score'] = False
    score_df['cutoff_gft_score'][:(magic.elbow + 1)] = True

    if cal_pval:
        if num_high_frequency == 0:
            raise ValueError("ratio_high_freq should be greater than 0")
        p_val_list = test_significant_freq(
            freq_array=frequency_array.transpose(),
            cutoff=num_low_frequency)
        from statsmodels.stats.multitest import multipletests
        qval_list = multipletests(np.array(p_val_list), method='fdr_by')[1]
        score_df.loc[:, 'pvalue'] = p_val_list
        score_df.loc[:, 'qvalue'] = qval_list

    return score_df


def calculate_frequency_domain(adata,
                               ratio_low_freq='infer',
                               ratio_high_freq='infer',
                               ratio_neighbors='infer',
                               spatial_info=['array_row', 'array_col'],
                               return_freq_domain=True,
                               normalize_lap=False):
    """
    Obtain gene signals in frequency/spectral domain for all genes in 
    adata.var_names.

    Parameters
    ----------
    adata : AnnData
        adata.X is the normalized count matrix. Besides, the spatial coordinates could be found in adata.obs or
        adata.obsm.
    ratio_low_freq : float | "infer", optional
        The ratio_low_freq will be used to determine the number of the FMs with low frequencies. Indeed,
        the ratio_low_freq * sqrt(number of spots) low frequency FMs will be calculated.
        If 'infer', the ratio_low_freq will be set to 1.0. The default is 'infer'.
    ratio_high_freq: float | 'infer', optional
        The ratio_high_freq will be used to determine the number of the FMs with high frequencies. Indeed,
        the ratio_high_freq * sqrt(number of spots) high frequency FMs will be calculated.
        If 'infer', the ratio_high_freq will be set to 0. The default is 'infer'.
    ratio_neighbors: float | 'infer', optional
        The ratio_neighbors will be used to determine the number of neighbors
        when construct the KNN graph by spatial coordinates. Indeed, ratio_neighobrs * sqrt(number of spots) / 2
        indicates the K. If 'infer', the para will be set to 1.0. The default is 'infer'.
    spatial_info : list | tuple | str, optional
        The column names of spatial coordinates in adata.obs_keys() or key in adata.obsm_keys.
        The default is ['array_row','array_col'].
    return_freq_domain : bool, optional
        Whether you need to return gene signals in frequency domain. The default is True.
    normalize_lap : bool, optional
        Whether you need to normalize laplacian matrix. The default is false.

    Returns
    -------
    If return_freq_domain, return DataFrame, the index indicates the gene and 
    the columns indicates corresponding frequencies/smoothness.

    """
    # Critical parameters
    # Ensure parameters
    if ratio_low_freq == 'infer':
        num_low_frequency = int(np.ceil(np.sqrt(adata.shape[0])))
    else:
        num_low_frequency = int(np.ceil(np.sqrt(adata.shape[0]) * \
                                        ratio_low_freq))
    if ratio_high_freq == 'infer':
        num_high_frequency = int(np.ceil(np.sqrt(adata.shape[0])))
    else:
        num_high_frequency = int(np.ceil(np.sqrt(adata.shape[0]) * \
                                         ratio_high_freq))
    if adata.shape[0] >= 10000:
        num_high_frequency = int(np.ceil(np.sqrt(adata.shape[0])))

    if ratio_neighbors == 'infer':
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2))
    else:
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2 * ratio_neighbors))
    if adata.shape[0] <= 500:
        num_neighbors = 4

    # ************** Construct graph and corresponding matrix ****************
    lap_mtx, _ = get_laplacian_mtx(adata,
                                   num_neighbors=num_neighbors,
                                   spatial_key=spatial_info,
                                   normalization=normalize_lap)

    # Calculate the eigenvalues and eigenvectors of the Laplace matrix
    np.random.seed(123)
    if adata.shape[0] <= 20000:
        eig_val, eig_vec = scipy.linalg.eigh(lap_mtx)
        if num_high_frequency > 0:
            eig_val_s = eig_val[:num_low_frequency]
            eig_vec_s = eig_vec[:, :num_low_frequency]
            eig_val_l = eig_val[-num_high_frequency:]
            eig_vec_l = eig_vec[:, -num_high_frequency:]
            eig_val = np.concatenate((eig_val_s, eig_val_l))
            eig_vec = np.concatenate((eig_vec_s, eig_vec_l), axis=1)
        else:
            eig_val = eig_val[:num_low_frequency]
            eig_vec = eig_vec[:, :num_low_frequency]
    else:
        if num_high_frequency > 0:
            lap_mtx = ss.csr_matrix(lap_mtx)
            # Fourier modes of low frequency
            eig_val_s, eig_vec_s = ss.linalg.eigsh(lap_mtx.astype(float),
                                                   k=num_low_frequency,
                                                   which='SM')
            # Fourier modes of high frequency
            eig_val_l, eig_vec_l = ss.linalg.eigsh(lap_mtx.astype(float),
                                                   k=num_high_frequency,
                                                   which='LM')
            eig_val = np.concatenate((eig_val_s, eig_val_l))  # eigenvalues
            eig_vec = np.concatenate((eig_vec_s, eig_vec_l), axis=1)  # eigenvectors
        else:
            eig_val, eig_vec = ss.linalg.eigsh(lap_mtx.astype(float),
                                               k=num_low_frequency,
                                               which='SM')

    # ************************Graph Fourier Transform***************************
    # Calculate GFT
    eig_vec = eig_vec.transpose()
    exp_mtx = adata.obsm['interaction_score'].values
    frequency_array = np.matmul(eig_vec, exp_mtx)
    # Spectral domain normalization
    frequency_array = preprocessing.normalize(frequency_array, norm='l1', axis=0)

    # ********************** Results of GFT ***********************************
    frequency_df = pd.DataFrame(frequency_array,
                                columns=adata.var_names,
                                index=['low_spec_' + str(low) for low in range(1, num_low_frequency + 1)] \
                                      + ['high_spec_' + str(high) for high in range(1, num_high_frequency + 1)])
    adata.varm['freq_domain'] = frequency_df.transpose()
    adata.uns['FM_info'] = {'eig_vec': eig_vec, 'eig_val': eig_val}

    if return_freq_domain:
        return frequency_df


def identify_lr_module(adata,
                       svi_list,
                       ratio_fms='infer',
                       metric='euclidean',
                       resolution=1,
                       spatial_info='spatial',
                       ratio_neighbors=5,
                       n_neighbors=8,
                       normalize_lap=False,
                       algorithm='louvain',
                       n_pcs=50,
                       random_state=3,
                       **kwargs
                       ):
    if ratio_fms == 'infer':
        if adata.shape[0] <= 500:
            ratio_fms = 5
        elif adata.shape[0] <= 10000:
            ratio_fms = 5
        else:
            ratio_fms = 2

    if isinstance(svi_list, str):
        if svi_list == 'infer':
            gene_score = adata.var.sort_values(by='svg_rank')
            adata = adata[:, gene_score.index]
            svi_list = adata.var[adata.var.cutoff_gft_score][adata.var.qvalue < 0.05].index.tolist()

    # extract lr information
    tmp_adata = sc.AnnData(adata.obsm['interaction_score'])
    # extract location information
    if isinstance(spatial_info, str):
        location_df = adata.obsm[spatial_info]
        spatial_key = ['x', 'y'] if location_df.shape[1] == 2 else ['x', 'y', 'z']
        location_df = pd.DataFrame(location_df, index=adata.obs_names, columns=spatial_key)
    else:
        location_df = adata.obs.loc[:, spatial_info].copy()
        spatial_key = spatial_info
    tmp_adata.obs.loc[:, location_df.columns] = location_df.values

    tmp_adata = tmp_adata[:, svi_list].copy()
    tmp_adata.obsm['interaction_score'] = adata.obsm['interaction_score'].loc[:, svi_list]

    calculate_frequency_domain(tmp_adata,
                               ratio_low_freq=ratio_fms,
                               ratio_high_freq=0,
                               ratio_neighbors=ratio_neighbors,
                               spatial_info=spatial_key,
                               return_freq_domain=False,
                               normalize_lap=normalize_lap)
    # Create new anndata to store freq domain information
    gft_adata = sc.AnnData(tmp_adata.varm['freq_domain'])
    eig_vec = tmp_adata.uns['FM_info']['eig_vec']
    if n_pcs:
        sc.pp.pca(gft_adata, n_comps=n_pcs)
        sc.pp.neighbors(gft_adata, n_neighbors=n_neighbors, metric=metric)
    else:
        sc.pp.neighbors(gft_adata, n_neighbors=n_neighbors, metric=metric, use_rep='X')

    # Determine the used clustering algorithm
    if algorithm == 'louvain':
        clustering_alg = sc.tl.louvain
    elif algorithm == 'leiden':
        clustering_alg = sc.tl.leiden
    else:
        raise ValueError("""unknown clustering algorithm chosen""")

    # Next, clustering genes for given resolution
    clustering_alg(gft_adata,
                   resolution=resolution,
                   random_state=random_state,
                   **kwargs,
                   key_added='clustering')
    sc.tl.umap(gft_adata)
    lr_umap_df = pd.DataFrame(gft_adata.obsm['X_umap'],
                              index=gft_adata.obs.index,
                              columns=['UMAP_1', 'UMAP_2'])
    lr_module_df = [str(eval(i_tm) + 1) for i_tm in gft_adata.obs.clustering.tolist()]
    cate_order = [str(i) for i in range(1,
                                        1 + gft_adata.obs.clustering.cat.categories.size)]
    lr_module_df = pd.DataFrame(lr_module_df, index=gft_adata.obs_names, columns=['module'])
    lr_module_df['module'] = lr_module_df['module'].astype(pd.CategoricalDtype(
        categories=cate_order, ordered=True))
    gft_adata.obs['module'] = lr_module_df['module']

    # lr module pseudo expression
    all_lr_ms = lr_module_df['module'].cat.categories
    module_df = pd.DataFrame(0, index=adata.obs_names, columns='module_' + all_lr_ms)
    pseudo_df = pd.DataFrame(0, index=adata.obs_names, columns='module_' + all_lr_ms)

    for lr_m in all_lr_ms:
        pseudo_exp = tmp_adata[:, gft_adata.obs.module[gft_adata.obs.module == lr_m].index].X.mean(axis=1)
        pseudo_exp = np.ravel(pseudo_exp)
        pseudo_df['module_' + str(lr_m)] = pseudo_exp.copy()
        predict_module = KMeans(n_clusters=2, random_state=random_state).fit_predict(pseudo_exp.reshape(-1, 1))
        pseudo_exp_median = np.median(pseudo_exp)
        pseudo_exp_cluster = np.where(pseudo_exp > pseudo_exp_median, 1, 0)

        cluster_middle_param = sum(abs(predict_module - pseudo_exp_cluster))
        cluster_middle_param_reverse = sum(abs(predict_module - abs(pseudo_exp_cluster - 1)))
        if cluster_middle_param > cluster_middle_param_reverse:
            predict_module = abs(predict_module - 1)

        module_df['module_' + str(lr_m)] = predict_module
    module_df = module_df.astype(str)

    # obtain freq signal
    freq_signal_module_df = pd.DataFrame(0,
                                         columns=module_df.columns,
                                         index=tmp_adata.varm['freq_domain'].columns)

    for lr_m in all_lr_ms:
        tm_gene_list = gft_adata.obs.module[gft_adata.obs.module == lr_m].index
        freq_signal = tmp_adata.varm['freq_domain'].loc[tm_gene_list, :].mean(axis=0)
        freq_signal_module_df.loc[:, 'module_' + lr_m] = freq_signal

    lr_module_info = {'lr_module_df': lr_module_df, 'module_binary_df': module_df, 'module_pseudo_df': pseudo_df,
                      'lr_umap_df': lr_umap_df, 'module_freq_signal_df': freq_signal_module_df,
                      'eig_vec': eig_vec}
    adata.uns['lr_module_info'] = lr_module_info

    return adata


def lr_module_genes(adata,
                    gene_list,
                    cutoff=0.3,
                    ):
    from scipy.spatial.distance import cosine
    # GFT for svg list
    exp_mtx = adata[:, gene_list].X
    if ss.issparse(exp_mtx):
        exp_mtx = exp_mtx.A

    # obtain eigenvectors
    eig_vec = adata.uns['lr_module_info']['eig_vec']
    exp_mtx = preprocessing.minmax_scale(exp_mtx, axis=0)
    frequency_df = np.matmul(eig_vec, exp_mtx)
    frequency_df = preprocessing.normalize(frequency_df, norm='l1', axis=0)
    frequency_df = pd.DataFrame(frequency_df,
                                index=[f'freq_{i}' for i in range(1, 1 + frequency_df.shape[0])],
                                columns=gene_list)

    # obtain module frequency signals
    freq_signal_module_df = adata.uns['lr_module_info']['module_freq_signal_df']

    # seek the matched module for each gene
    gene_module_df = pd.DataFrame('No', index=gene_list, columns=['module'])
    gene_module_df.loc[:, 'value'] = 0
    for gene in gene_list:
        freq_gene = frequency_df.loc[:, gene].values
        best_module = freq_signal_module_df.columns[0]
        freq_module = freq_signal_module_df.loc[:, best_module].values
        # best_metric = pearsonr(freq_gene, freq_module)[0]
        best_metric = 1 - cosine(freq_gene, freq_module)
        for module in freq_signal_module_df.columns[1:]:
            freq_module = freq_signal_module_df.loc[:, module].values
            # tmp_metric = pearsonr(freq_gene, freq_module)[0]
            tmp_metric = 1 - cosine(freq_gene, freq_module)
            if tmp_metric > best_metric:
                best_module = module
                best_metric = tmp_metric
        if best_metric >= cutoff:
            gene_module_df.loc[gene, 'module'] = best_module
            gene_module_df.loc[gene, 'value'] = best_metric
    gene_module_df = gene_module_df.loc[gene_module_df['module'] != 'No', :]
    # add gene_module_df to adata
    adata.uns['lr_module_info']['gene_module_df'] = gene_module_df

    return gene_module_df
