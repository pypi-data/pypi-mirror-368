import warnings
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as ss
import sklearn.preprocessing
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from tqdm import tqdm

from .utils import get_laplacian_mtx, kneed_select_values, test_significant_freq

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
                       infer_param=True,
                       alpha=0.3,
                       beta=0.3,
                       step=3):
    # preprocessing
    adata.var_names_make_unique()
    sc.pp.filter_genes(adata, min_cells=1)
    lr_info = adata.uns['lr_info']
    ligand_list = lr_info.loc[:, 'ligand'].values.tolist()
    receptor_list = lr_info.loc[:, 'receptor'].values.tolist()
    interaction_list = lr_info.index.tolist()

    # get Laplacian matrix according to coordinates
    lap_mtx, adj_mtx = get_laplacian_mtx(adata,
                                         num_neighbors=n_neighbors,
                                         spatial_key=spatial_key,
                                         normalization=normalize_lap)

    # obtain current expression matrix
    if ss.issparse(adata.X):
        ligand_exp = adata[:, ligand_list].X.A
        receptor_exp = adata[:, receptor_list].X.A

    else:
        ligand_exp = adata[:, ligand_list].X
        receptor_exp = adata[:, receptor_list].X
    ligand_exp = sklearn.preprocessing.minmax_scale(ligand_exp, axis=0)
    receptor_exp = sklearn.preprocessing.minmax_scale(receptor_exp, axis=0)

    # determine parameters
    if infer_param:
        alpha_list = np.arange(0.05, 0.2, 0.05)
        beta_list = np.arange(0.05, 0.2, 0.05)
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
                                 columns=[f'{i}-ligand-init' for i in interaction_list])
    receptor_exp_df = pd.DataFrame(receptor_exp,
                                   index=adata.obs_names,
                                   columns=[f'{i}-ligand-init' for i in interaction_list])
    interaction_df = pd.DataFrame(0,
                                  index=adata.obs_names,
                                  columns=[f'{i}-interaction-init' for i in interaction_list])
    # diffusion
    diffusion_mtx_tmp = np.eye(lap_mtx.shape[0]) - alpha * lap_mtx.A
    all_interaction_mtx = np.zeros_like(ligand_exp)
    for s in range(0, step + 1):
        print("step: \t", s)
        interaction_mtx = ligand_exp * receptor_exp
        ligand_exp = diffusion_mtx_tmp @ ligand_exp - beta * interaction_mtx
        receptor_exp = receptor_exp - beta * interaction_mtx
        ligand_exp[ligand_exp < 0] = 0
        receptor_exp[receptor_exp < 0] = 0
        all_interaction_mtx += interaction_mtx

        # record
        tmp_df = pd.DataFrame(ligand_exp,
                              index=adata.obs_names,
                              columns=[f'{i}-ligand-{s}' for i in interaction_list])
        ligand_exp_df = pd.concat((ligand_exp_df, tmp_df), axis=1)
        tmp_df = pd.DataFrame(receptor_exp,
                              index=adata.obs_names,
                              columns=[f'{i}-receptor-{s}' for i in interaction_list])
        receptor_exp_df = pd.concat((receptor_exp_df, tmp_df), axis=1)
        tmp_df = pd.DataFrame(interaction_mtx,
                              index=adata.obs_names,
                              columns=[f'{i}-interaction-{s}' for i in interaction_list])
        interaction_df = pd.concat((interaction_df, tmp_df), axis=1)

    # reformat
    all_interaction_mtx = pd.DataFrame(all_interaction_mtx,
                                       index=adata.obs_names,
                                       columns=interaction_list)

    adata.obsm['ligand_process'] = ligand_exp_df
    adata.obsm['receptor_process'] = receptor_exp_df
    adata.obsm['interaction_process'] = interaction_df
    adata.obsm['interaction_score'] = all_interaction_mtx
    adata.uns['adj_mtx'] = adj_mtx


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
                              infer_param=True,
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

    # get Laplacian matrix according to coordinates
    n_neighbors = n_neighbors + 1
    lap_mtx, adj_mtx = get_laplacian_mtx(adata,
                                         num_neighbors=n_neighbors,
                                         spatial_key=spatial_key,
                                         normalization=False)

    # obtain current expression matrix
    if ss.issparse(adata.X):
        ligand_exp = adata[:, ligand_list].X.A
        receptor_exp = adata[:, receptor_list].X.A

    else:
        ligand_exp = adata[:, ligand_list].X
        receptor_exp = adata[:, receptor_list].X

    # determine parameters
    if infer_param:
        alpha_list = np.arange(0.1, 0.5, 0.1)
        beta_list = np.arange(0.1, 1.1, 0.2)
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

    # construct ligand-receptor map
    all_unique_ligands = np.unique(ligand_list).tolist()
    all_unique_receptors = np.unique(receptor_list).tolist()
    lr_mapping = pd.DataFrame(0,
                              index=all_unique_receptors,
                              columns=all_unique_ligands)
    for s, interaction in enumerate(interaction_list):
        ligand = ligand_list[s]
        receptor = receptor_list[s]
        lr_mapping.loc[receptor, ligand] = 1

    # ligand and receptor
    if ss.issparse(adata.X):
        single_ligand_exp = adata[:, all_unique_ligands].X.A
        single_receptor_exp = adata[:, all_unique_receptors].X.A

    else:
        single_ligand_exp = adata[:, all_unique_ligands].X
        single_receptor_exp = adata[:, all_unique_receptors].X
    # single molecular dynamics
    single_ligand_exp = pd.DataFrame(single_ligand_exp,
                                     index=adata.obs_names,
                                     columns=all_unique_ligands)
    single_receptor_exp = pd.DataFrame(single_receptor_exp,
                                       index=adata.obs_names,
                                       columns=all_unique_receptors)

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
                              columns=interaction_list)
    receptor_exp = pd.DataFrame(0,
                                index=adata.obs_names,
                                columns=interaction_list)
    ligand_exp.loc[:, interaction_list] = single_ligand_exp.loc[:, ligand_list].values
    receptor_exp.loc[:, interaction_list] = single_receptor_exp.loc[:, receptor_list].values

    # diffusion matrix
    diffusion_mtx = np.eye(lap_mtx.shape[0]) - alpha * lap_mtx.A

    # interaction score
    all_interaction_mtx = np.zeros_like(ligand_exp_df.values)
    interaction_sum_df = pd.DataFrame(index=interaction_list)
    step_tqdm = tqdm(range(1, step + 2))

    for s in step_tqdm:
        step_tqdm.set_description("step: ")
        interaction_mtx = ligand_exp.values * receptor_exp.values
        all_interaction_mtx += interaction_mtx

        # process ligand
        single_ligand_exp = diffusion_mtx @ single_ligand_exp.values - beta * single_ligand_exp.values * \
                            (single_receptor_exp.values @ lr_mapping.values)
        single_ligand_exp[single_ligand_exp < 0] = 0
        single_ligand_exp = pd.DataFrame(single_ligand_exp,
                                         index=adata.obs_names,
                                         columns=all_unique_ligands)

        # process receptor
        single_receptor_exp = single_receptor_exp.values - beta * single_receptor_exp * \
                              (single_ligand_exp.values @ lr_mapping.transpose().values)
        single_receptor_exp[single_receptor_exp < 0] = 0
        single_receptor_exp = pd.DataFrame(single_receptor_exp,
                                           index=adata.obs_names,
                                           columns=all_unique_receptors)
        # update new state
        ligand_exp.loc[:, interaction_list] = single_ligand_exp[ligand_list].values
        receptor_exp.loc[:, interaction_list] = single_receptor_exp[receptor_list].values

        # record
        if log_step is not None:
            if s % log_step == 0:
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

    # reformat
    all_interaction_mtx = pd.DataFrame(all_interaction_mtx,
                                       index=adata.obs_names,
                                       columns=interaction_list)
    adata.obsm['interaction_score'] = all_interaction_mtx
    adata.uns['process_record'] = {'ligand_process': ligand_exp_df,
                                   'receptor_process': receptor_exp_df,
                                   'interaction_process': interaction_df}
    adata.uns['GRD_info'] = {'lr_mapping': lr_mapping,
                             'adj_mtx': adj_mtx,
                             'lr_interaction_sum': interaction_sum_df}


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


def cell_cell_score(adata,
                    interaction,
                    alpha,
                    beta,
                    step,
                    spatial_key=None,
                    num_neighbors=4):
    # construct laplacian matrix
    if 'adj_mtx' not in adata.uns.keys():
        lap_mtx, adj_mtx = get_laplacian_mtx(adata,
                                             num_neighbors=num_neighbors,
                                             sigma=1,
                                             spatial_key=spatial_key,
                                             normalization=False)
    else:
        adj_mtx = adata.uns['adj_mtx']
    deg_mtx = adj_mtx.sum(axis=1)
    deg_mtx = np.diag(deg_mtx)
    lap_mtx = deg_mtx - adj_mtx
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
        ligand_exp = ligand_exp.A
        receptor_exp = receptor_exp.A

    ccc_mtx = _calculate_ccc_mtx(ligand_exp=ligand_exp,
                                 receptor_exp=receptor_exp,
                                 diff_mtx=diff_mtx,
                                 beta=beta,
                                 step=step,
                                 )

    ccc_mtx = pd.DataFrame(ccc_mtx,
                           index=adata.obs_names,
                           columns=adata.obs_names)
    return ccc_mtx


def cell_type_score(adata, ccc_df, cell_type_key, spatial_key='spatial', k_range=50, min_cells=10):
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
    loc = sc.AnnData(loc)
    sc.pp.neighbors(loc,
                    n_neighbors=k_range)
    adj_mtx = loc.obsp['connectivities'].A
    adj_mtx[adj_mtx > 0] = 1
    adj_mtx = pd.DataFrame(adj_mtx,
                           index=adata.obs_names,
                           columns=adata.obs_names)

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
            ct_df.loc[i, j] = interaction_score
    # normalization
    ct_df = ct_df / ct_df.max().max()
    return ct_df


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
    ccc_mtx = np.zeros((ligand_exp.shape[0], receptor_exp.shape[0]))
    trace_ligand_exp_list = []
    trace_receptor_exp_list = []
    for m in range(ligand_exp.shape[1]):
        trace_ligand_exp = np.diag(ligand_exp[:, m])
        trace_receptor_exp = receptor_exp[:, m].reshape(-1, 1)
        trace_ligand_exp_list.append(trace_ligand_exp)
        trace_receptor_exp_list.append(trace_receptor_exp)
    diff_mtx_power = diff_mtx
    step_tqdm = tqdm(range(1, step + 2))
    for _ in step_tqdm:
        step_tqdm.set_description("step")
        for m in range(len(trace_receptor_exp_list)):
            trace_ligand_exp = trace_ligand_exp_list[m]
            trace_receptor_exp = trace_receptor_exp_list[m]
            trace_ligand_exp[trace_ligand_exp < 0] = 0
            trace_receptor_exp[trace_receptor_exp < 0] = 0
            tmp_ccc_mtx = trace_ligand_exp * trace_receptor_exp
            ccc_mtx = ccc_mtx + tmp_ccc_mtx
            # update trace_ligand （the above lists will be updated automatically)
            trace_ligand_exp = trace_ligand_exp - beta * tmp_ccc_mtx
            trace_receptor_exp = trace_receptor_exp - beta * tmp_ccc_mtx.sum(axis=0)
            trace_ligand_exp = diff_mtx_power @ trace_ligand_exp
            trace_ligand_exp_list[m] = trace_ligand_exp.copy()
            trace_receptor_exp_list[m] = trace_receptor_exp.copy()
    ccc_mtx = ccc_mtx.transpose()
    return ccc_mtx


def _calculate_ccc_mtx_gpu(ligand_exp, receptor_exp, diff_mtx, beta, step):
    """
    GPU-accelerated version of the CCC matrix calculation function using CuPy.
    """
    import cupy as cp
    # Ensure data is on the GPU
    ligand_exp_gpu = cp.array(ligand_exp)
    receptor_exp_gpu = cp.array(receptor_exp)
    diff_mtx_gpu = cp.array(diff_mtx)

    ccc_mtx_gpu = cp.zeros((ligand_exp_gpu.shape[0], receptor_exp_gpu.shape[0]), dtype=cp.float32)
    trace_ligand_exp_list_gpu = []
    trace_receptor_exp_list_gpu = []

    for m in range(ligand_exp_gpu.shape[1]):
        trace_ligand_exp_gpu = cp.diag(ligand_exp_gpu[:, m])
        trace_receptor_exp_gpu = receptor_exp_gpu[:, m].reshape(-1, 1)
        trace_ligand_exp_list_gpu.append(trace_ligand_exp_gpu)
        trace_receptor_exp_list_gpu.append(trace_receptor_exp_gpu)

    diff_mtx_power_gpu = diff_mtx_gpu

    step_tqdm = tqdm(range(1, step + 2))
    for _ in step_tqdm:
        step_tqdm.set_description("step")
        for m in range(len(trace_receptor_exp_list_gpu)):
            trace_ligand_exp_gpu = trace_ligand_exp_list_gpu[m]
            trace_receptor_exp_gpu = trace_receptor_exp_list_gpu[m]

            # Ensuring non-negative values
            trace_ligand_exp_gpu = cp.maximum(trace_ligand_exp_gpu, 0)
            trace_receptor_exp_gpu = cp.maximum(trace_receptor_exp_gpu, 0)
            tmp_ccc_mtx_gpu = trace_ligand_exp_gpu * trace_receptor_exp_gpu
            ccc_mtx_gpu += tmp_ccc_mtx_gpu
            # Update traces
            trace_ligand_exp_gpu -= beta * tmp_ccc_mtx_gpu
            trace_receptor_exp_gpu -= beta * cp.sum(tmp_ccc_mtx_gpu, axis=0)
            trace_ligand_exp_gpu = diff_mtx_power_gpu @ trace_ligand_exp_gpu
            trace_ligand_exp_list_gpu[m] = trace_ligand_exp_gpu.copy()
            trace_receptor_exp_list_gpu[m] = trace_receptor_exp_gpu.copy()

    ccc_mtx_gpu = ccc_mtx_gpu.get()  # Transfer the result back to CPU memory if needed
    ccc_mtx_cpu = ccc_mtx_gpu.transpose()  # transpose on CPU side after retrieval
    return ccc_mtx_cpu


def cell_cell_score_system(ligand_exp,
                           receptor_exp,
                           lr_mapping,
                           adjacent_mtx,
                           alpha,
                           beta,
                           step):
    # degree vector, spot (cell) degree
    deg_vec = adjacent_mtx.sum(axis=0)
    ccc_mtx = np.zeros_like(adjacent_mtx).astype(np.float32)
    lr_mapping = lr_mapping.values

    for t in range(0, step + 1):
        print(t)
        if t == 0:
            int_mtx = ligand_exp * (receptor_exp @ lr_mapping)
            v = receptor_exp
            previous_u_list = [ligand_exp]
            previous_int_list = [beta * int_mtx]

            # find ccc
            tmp_ccc = int_mtx.sum(axis=1) * np.eye(ccc_mtx.shape[0])
            ccc_mtx += tmp_ccc

            # update receptor
            int_receptor_mtx = receptor_exp * (ligand_exp @ lr_mapping.transpose())
            v = v - beta * int_receptor_mtx
            v[v < 0] = 0

        if t > 0:
            current_u_list = []  # save u corresponding to diverse neighbors
            current_int_list = []  # save interaction corresponding to diverse neighbors
            int_receptor_mtx_sum = np.zeros_like(int_receptor_mtx).astype(np.float32)

            for n in range(t + 1):
                if n == 0:
                    # neighbor 0 (only remaining)
                    int_mtx = previous_int_list[0]
                    u = previous_u_list[0] - alpha * previous_u_list[0] * deg_vec[:, np.newaxis] - int_mtx
                    u[u < 0] = 0

                    # new int mtx and sum
                    int_mtx = u * (v @ lr_mapping)
                    int_mtx[int_mtx < 0] = 0

                    int_receptor_mtx = v * (u @ lr_mapping.transpose())
                    int_receptor_mtx_sum += int_receptor_mtx

                    # calculate ccc
                    tmp_ccc = int_mtx.sum(axis=1) * np.linalg.matrix_power(adjacent_mtx, n)
                    ccc_mtx += tmp_ccc

                    # save the process
                    current_u_list.append(u)
                    current_int_list.append(beta * int_mtx)

                if n == t:
                    # neighbor t (only diffusion)
                    u = alpha * previous_u_list[-1]
                    u[u < 0] = 0
                    int_mtx = u * (v @ lr_mapping)
                    int_mtx[int_mtx < 0] = 0

                    int_receptor_mtx = v * (u @ lr_mapping.transpose())
                    int_receptor_mtx_sum += int_receptor_mtx

                    # calculate ccc
                    tmp_ccc = int_mtx.sum(axis=1) * np.linalg.matrix_power(adjacent_mtx, n)
                    ccc_mtx += tmp_ccc
                else:
                    int_mtx = previous_int_list[n]
                    u = previous_u_list[n] - alpha * previous_u_list[n] * deg_vec[:, np.newaxis] - int_mtx + \
                        alpha * previous_u_list[n - 1]
                    u[u < 0] = 0

                    # new int mtx and sum
                    int_mtx = u * (v @ lr_mapping)
                    int_mtx[int_mtx < 0] = 0

                    int_receptor_mtx = v * (u @ lr_mapping.transpose())
                    int_receptor_mtx_sum += int_receptor_mtx

                    # calculate ccc
                    tmp_ccc = int_mtx.sum(axis=1) * np.linalg.matrix_power(adjacent_mtx, n)
                    ccc_mtx += tmp_ccc

                    # save the process
                    current_u_list.append(u)
                    current_int_list.append(beta * int_mtx)

            # update v
            v = v - beta * int_receptor_mtx_sum
            v[v < 0] = 0

            # update state
            previous_int_list = current_int_list
            previous_u_list = current_u_list
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
        ccc_score = cell_cell_score_system(ligand_exp=ligand_exp,
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

        ccc_score = cell_cell_score(ligand_exp=ligand_exp,
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
    function can also be treated as denoising. Note that the denosing results 
    is related to spatial graph topology so that only the results of spatially 
    variable genes could be convincing.

    Parameters
    ----------
    adata : AnnData
        adata.X is the normalized count matrix. Besides, the spatial coordinat-
        es of all spots should be found in adata.obs or adata.obsm.
    ratio_low_freq : float | "infer", optional
        The ratio_low_freq will be used to determine the number of the FMs with
        low frequencies. Indeed, the ratio_low_freq * sqrt(number of spots) low
        frequency FMs will be calculated. The default is 'infer'.
        A high can achieve better smoothness. c should be setted to [0, 0.1].
    ratio_neighbors: float | 'infer', optional
        The ratio_neighbors will be used to determine the number of neighbors
        when contruct the KNN graph by spatial coordinates. Indeed, ratio_neighobrs * sqrt(number of spots) / 2
        indicates the K. If 'infer', the para will be set to 1.0. The default is 'infer'.
    c: float, optional
        c balances the smoothness and difference with previous expression. The
        default is 0.001
    spatial_info : list | tuple | string, optional
        The column names of spatial coordinates in adata.obs_names or key
        in adata.obsm_keys() to obtain spatial information. The default
        is ['array_row', 'array_col'].
    normalize_lap : bool. optional
        Whether you need to normalize the Laplcian matrix. The default is False.
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
                              spatial_info=['array_row', 'array_col'],
                              normalize_lap=False):
    """
    This function could choosed the number of FMs automatically based on
    kneedle algorithm.

    Parameters
    ----------
    adata : AnnData
        adata.X is the normalized count matrix. Besides, the spatial coordinates of all spots should be found in
        adata.obs or adata.obsm.
    low_end : float, optional
        The the range of low-frequency FMs. The default is 5.
    high_end : TYPE, optional
        The the range of high-frequency FMs. The default is 5.
    ratio_neighbors : float, optional
        The ratio_neighbors will be used to determine the number of neighbors
        when construct the KNN graph by spatial coordinates. Indeed, ratio_neighbors * sqrt(number of spots) / 2
        indicates the K. If 'infer', the para
        will be set to 1.0. The default is 'infer'.
    spatial_info : list | tupple | string, optional
        The column names of spatial coordinates in adata.obs_names or key
        in adata.obsm_keys() to obtain spatial information. The default
        is ['array_row', 'array_col'].
    normalize_lap : TYPE, optional
        Whether you need to normalize the Laplacian matrix. The default is False.
        The default is False.

    Returns
    -------
    low_cutoff : float
        The low_cutoff * sqrt(the number of spots) low-frequency FMs are
        recommended in detecting SVG.
    high_cutoff : float
        The high_cutoff * sqrt(the number of spots) low-frequency FMs are
        recommended in detecting SVG.

    """
    # Determine the number of neighbors
    if ratio_neighbors == 'infer':
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2))
    else:
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2 \
                                    * ratio_neighbors))
    if adata.shape[0] <= 500:
        num_neighbors = 4
    if adata.shape[0] > 15000 and low_end >= 3:
        low_end = 3
    if adata.shape[0] > 15000 and high_end >= 3:
        high_end = 3
    # Ensure gene index uniquely and all gene had expression  
    adata.var_names_make_unique()
    sc.pp.filter_genes(adata, min_cells=1)

    # *************** Construct graph and corresponding matrixs ***************
    lap_mtx, _ = get_laplacian_mtx(adata,
                                   num_neighbors=num_neighbors,
                                   spatial_key=spatial_info,
                                   normalization=normalize_lap)

    # Next, calculate the eigenvalues and eigenvectors of the Laplace matrix
    # Fourier bases of low frequency
    eig_vals_s, eig_vecs_s = ss.linalg.eigsh(lap_mtx.astype(float),
                                             k=int(np.ceil(low_end * np.sqrt(adata.shape[0]))),
                                             which='SM')
    low_cutoff = np.ceil(kneed_select_values(eig_vals_s) / np.sqrt(adata.shape[0]) * 1000) / 1000
    if low_cutoff >= low_end:
        low_cutoff = low_end
    if low_cutoff < 1:
        low_cutoff = 1
    num_low = int(np.ceil(np.sqrt(adata.shape[0]) * low_cutoff))
    eig_vals_l, eig_vecs_l = ss.linalg.eigsh(lap_mtx.astype(float),
                                             k=int(np.ceil(high_end * np.sqrt(adata.shape[0]))),
                                             which='LM')
    high_cutoff = np.ceil(kneed_select_values(eig_vals_l, increasing=False) / np.sqrt(adata.shape[0]) * 1000) / 1000
    if high_cutoff < 1:
        high_cutoff = 1
    if high_cutoff >= high_end:
        high_cutoff = high_end
    num_high = int(np.ceil(np.sqrt(adata.shape[0]) * \
                           high_cutoff))

    adata.uns['FMs_after_select'] = {'low_FMs_frequency': eig_vals_s[:num_low],
                                     'low_FMs': eig_vecs_s[:, :num_low],
                                     'high_FMs_frequency': eig_vals_l[(len(eig_vals_l) - num_high):],
                                     'high_FMs': eig_vecs_l[:, (len(eig_vals_l) - num_high):]}

    return low_cutoff, high_cutoff


def svi_detection(adata,
                  ratio_low_freq='infer',
                  ratio_high_freq='infer',
                  ratio_neighbors='infer',
                  spatial_info=['array_row', 'array_col'],
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
        adata.X is the normalized count matrix. Besides, the spatial coordinat-
        es could be found in adata.obs or adata.obsm.
    ratio_low_freq : float | "infer", optional
        The ratio_low_freq will be used to determine the number of the FMs with
        low frequencies. Indeed, the ratio_low_freq * sqrt(number of spots) low
        frequecy FMs will be calculated. If 'infer', the ratio_low_freq will be
        set to 1.0. The default is 'infer'.
    ratio_high_freq: float | 'infer', optional
        The ratio_high_freq will be used to determine the number of the FMs of
        high frequencies. Indeed, the ratio_high_freq * sqrt(number of spots) 
        high frequency FMs will be calculated. If 'infer', the ratio_high_freq
        will be set to 1.0. The default is 'infer'.
    ratio_neighbors: float | 'infer', optional
        The ratio_neighbors will be used to determine the number of neighbors
        when contruct the KNN graph by spatial coordinates. Indeed, ratio_neighbors * sqrt(number of spots) / 2
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
        num_neighbors = int(np.ceil(np.sqrt(adata.shape[0]) / 2 \
                                    * ratio_neighbors))
    if adata.shape[0] <= 500:
        num_neighbors = 4

    # Check dimensions
    if 'FMs_after_select' in adata.uns_keys():
        low_condition = (num_low_frequency == adata.uns['FMs_after_select'] \
            ['low_FMs_frequency'].size)
        high_condition = (num_high_frequency == adata.uns['FMs_after_select'] \
            ['high_FMs_frequency'].size)
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
        pval_list = test_significant_freq(
            freq_array=frequency_array.transpose(),
            cutoff=num_low_frequency)
        from statsmodels.stats.multitest import multipletests
        qval_list = multipletests(np.array(pval_list), method='fdr_by')[1]
        score_df.loc[:, 'pvalue'] = pval_list
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
        adata.X is the normalized count matrix. Besides, the spatial coordinat-
        es could be found in adata.obs or adata.obsm.
    ratio_low_freq : float | "infer", optional
        The ratio_low_freq will be used to determine the number of the FMs with
        low frequencies. Indeed, the ratio_low_freq * sqrt(number of spots) low
        frequency FMs will be calculated. If 'infer', the ratio_low_freq will be
        set to 1.0. The default is 'infer'.
    ratio_high_freq: float | 'infer', optional
        The ratio_high_freq will be used to determine the number of the FMs with
        high frequencies. Indeed, the ratio_high_freq * sqrt(number of spots) 
        high frequency FMs will be calculated. If 'infer', the ratio_high_freq
        will be set to 0. The default is 'infer'.
    ratio_neighbors: float | 'infer', optional
        The ratio_neighbors will be used to determine the number of neighbors
        when contruct the KNN graph by spatial coordinates. Indeed, ratio_neig-
        hobrs * sqrt(number of spots) / 2 indicates the K. If 'infer', the para
        will be set to 1.0. The default is 'infer'.
    spatial_info : list | tupple | str, optional
        The column names of spaital coordinates in adata.obs_keys() or 
        key in adata.obsm_keys. The default is ['array_row','array_col'].
    return_freq_domain : bool, optional
        Whether you need to return gene signals in frequency domain. The default is
        True.
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
    lap_mtx, _ = get_laplacian_mtx(adata, num_neighbors=num_neighbors,
                                   spatial_key=spatial_info,
                                   normalization=normalize_lap)

    # Calculate the eigenvalues and eigenvectors of the Laplace matrix
    np.random.seed(123)
    if num_high_frequency > 0:
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
        eig_val_s, eig_vec_s = ss.linalg.eigsh(lap_mtx.astype(float),
                                               k=num_low_frequency,
                                               which='SM')
        eig_vec = eig_vec_s
        eig_val = eig_val_s

    # ************************Graph Fourier Transform***************************
    # Calculate GFT
    eig_vec = eig_vec.transpose()
    exp_mtx = adata.obsm['interaction_score'].values
    exp_mtx = preprocessing.minmax_scale(exp_mtx, axis=0)
    frequency_array = np.matmul(eig_vec, exp_mtx)
    # Spectral domian normalization
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
                       ratio_neighbors=2,
                       n_neighbors=8,
                       normalize_lap=False,
                       random_state=None,
                       algorithm='louvain',
                       **kwargs
                       ):
    if ratio_fms == 'infer':
        if adata.shape[0] <= 500:
            ratio_fms = 4
        elif adata.shape[0] <= 10000:
            ratio_fms = 2
        else:
            ratio_fms = 1
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
    if gft_adata.shape[1] >= 400:
        sc.pp.pca(adata)
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
    lr_umap_df = pd.DataFrame(gft_adata.obsm['X_umap'], index=gft_adata.obs.index, columns=['UMAP_1', 'UMAP_2'])
    lr_module_df = [str(eval(i_tm) + 1) for i_tm in gft_adata.obs.clustering.tolist()]
    cate_order = [str(i) for i in range(1, 1 + gft_adata.obs.clustering.cat.categories.size)]
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
