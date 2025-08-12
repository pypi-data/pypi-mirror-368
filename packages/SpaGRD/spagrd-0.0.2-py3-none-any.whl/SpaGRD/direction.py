import anndata
import pandas as pd
import scanpy as sc
from scipy.sparse import csr_matrix
import matplotlib as mpl
import numpy as np
import plotly
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
from typing import Optional
from scipy.stats import norm


def communication_direction(
        adata: anndata.AnnData,
        spot_ccc_df: pd.DataFrame,
        database_name: str = None,
        pathway_name: str = None,
        lr_pair=None,
        k: int = 5,
        pos_idx: Optional[np.ndarray] = None,
        copy: bool = False
):
    obsp_names = []
    obsm_name = ''  ##
    if not lr_pair is None:
        obsp_names.append(database_name + '-' + lr_pair[0] + '-' + lr_pair[1])
        obsm_name = lr_pair[0] + '-' + lr_pair[1]
    elif not pathway_name is None:
        obsp_names.append(database_name + '-' + pathway_name)
        obsm_name = pathway_name
    else:
        obsp_names.append(database_name + '-total-total')
        obsm_name = 'total-total'
    adata.obsp[f'SpaGRD-{obsp_names[0]}'] = csr_matrix(spot_ccc_df.values)
    adata.obsm[f'SpaGRD-{database_name}-sum-sender'] = pd.DataFrame(spot_ccc_df.values.sum(axis=1),
                                                                    columns=[f's-{obsm_name}'],
                                                                    index=spot_ccc_df.index)
    adata.obsm[f'SpaGRD-{database_name}-sum-receiver'] = pd.DataFrame(spot_ccc_df.values.sum(axis=0),
                                                                      columns=[f'r-{obsm_name}'],
                                                                      index=spot_ccc_df.index)

    ncell = adata.shape[0]
    pts = np.array(adata.obsm['spatial'], float)
    if not pos_idx is None:
        pts = pts[:, pos_idx]
    storage = 'sparse'

    if storage == 'dense':
        for i in range(len(obsp_names)):
            # lig = name_mat[i,0]
            # rec = name_mat[i,1]
            S_np = adata.obsp['SpaGRD-' + obsp_names[i]].toarray()
            sender_vf = np.zeros_like(pts)
            receiver_vf = np.zeros_like(pts)

            tmp_idx = np.argsort(-S_np, axis=1)[:, :k]
            avg_v = np.zeros_like(pts)
            for ik in range(k):
                tmp_v = pts[tmp_idx[:, ik]] - pts[np.arange(ncell, dtype=int)]
                tmp_v = normalize(tmp_v, norm='l2')
                avg_v = avg_v + tmp_v * S_np[np.arange(ncell, dtype=int), tmp_idx[:, ik]].reshape(-1, 1)
            avg_v = normalize(avg_v)
            sender_vf = avg_v * np.sum(S_np, axis=1).reshape(-1, 1)

            S_np = S_np.T
            tmp_idx = np.argsort(-S_np, axis=1)[:, :k]
            avg_v = np.zeros_like(pts)
            for ik in range(k):
                tmp_v = -pts[tmp_idx[:, ik]] + pts[np.arange(ncell, dtype=int)]
                tmp_v = normalize(tmp_v, norm='l2')
                avg_v = avg_v + tmp_v * S_np[np.arange(ncell, dtype=int), tmp_idx[:, ik]].reshape(-1, 1)
            avg_v = normalize(avg_v)
            receiver_vf = avg_v * np.sum(S_np, axis=1).reshape(-1, 1)

            del S_np

    elif storage == 'sparse':
        for i in range(len(obsp_names)):
            # lig = name_mat[i,0]
            # rec = name_mat[i,1]
            S = adata.obsp['SpaGRD-' + obsp_names[i]]
            S_sum_sender = np.array(S.sum(axis=1)).reshape(-1)
            S_sum_receiver = np.array(S.sum(axis=0)).reshape(-1)
            sender_vf = np.zeros_like(pts)
            receiver_vf = np.zeros_like(pts)

            S_lil = S.tolil()
            for j in range(S.shape[0]):
                if len(S_lil.rows[j]) <= k:
                    tmp_idx = np.array(S_lil.rows[j], int)
                    tmp_data = np.array(S_lil.data[j], float)
                else:
                    row_np = np.array(S_lil.rows[j], int)
                    data_np = np.array(S_lil.data[j], float)
                    sorted_idx = np.argsort(-data_np)[:k]
                    tmp_idx = row_np[sorted_idx]
                    tmp_data = data_np[sorted_idx]
                if len(tmp_idx) == 0:
                    continue
                elif len(tmp_idx) == 1:
                    avg_v = pts[tmp_idx[0], :] - pts[j, :]
                else:
                    tmp_v = pts[tmp_idx, :] - pts[j, :]
                    tmp_v = normalize(tmp_v, norm='l2')
                    avg_v = tmp_v * tmp_data.reshape(-1, 1)
                    avg_v = np.sum(avg_v, axis=0)
                avg_v = normalize(avg_v.reshape(1, -1))
                sender_vf[j, :] = avg_v[0, :] * S_sum_sender[j]

            S_lil = S.T.tolil()
            for j in range(S.shape[0]):
                if len(S_lil.rows[j]) <= k:
                    tmp_idx = np.array(S_lil.rows[j], int)
                    tmp_data = np.array(S_lil.data[j], float)
                else:
                    row_np = np.array(S_lil.rows[j], int)
                    data_np = np.array(S_lil.data[j], float)
                    sorted_idx = np.argsort(-data_np)[:k]
                    tmp_idx = row_np[sorted_idx]
                    tmp_data = data_np[sorted_idx]
                if len(tmp_idx) == 0:
                    continue
                elif len(tmp_idx) == 1:
                    avg_v = -pts[tmp_idx, :] + pts[j, :]
                else:
                    tmp_v = -pts[tmp_idx, :] + pts[j, :]
                    tmp_v = normalize(tmp_v, norm='l2')
                    avg_v = tmp_v * tmp_data.reshape(-1, 1)
                    avg_v = np.sum(avg_v, axis=0)
                avg_v = normalize(avg_v.reshape(1, -1))
                receiver_vf[j, :] = avg_v[0, :] * S_sum_receiver[j]

            adata.obsm["SpaGRD_sender_vf-" + obsp_names[i]] = sender_vf
            adata.obsm["SpaGRD_receiver_vf-" + obsp_names[i]] = receiver_vf

    return adata if copy else None


def plot_cell_communication(
        adata: anndata.AnnData,
        database_name: str = None,
        pathway_name: str = None,
        lr_pair=None,
        keys=None,
        plot_method: str = "cell",
        background: str = "summary",
        background_legend: bool = False,
        clustering: str = None,
        summary: str = "sender",
        cmap: str = "coolwarm",
        cluster_cmap: dict = None,
        pos_idx: np.ndarray = np.array([0, 1], int),
        ndsize: float = 1,
        scale: float = 1.0,
        normalize_v: bool = False,
        normalize_v_quantile: float = 0.95,
        arrow_color: str = "#333333",
        grid_density: float = 1.0,
        grid_knn: int = None,
        grid_scale: float = 1.0,
        grid_thresh: float = 1.0,
        grid_width: float = 0.005,
        stream_density: float = 1.0,
        stream_linewidth: float = 1,
        stream_cutoff_perc: float = 5,
        filename: str = None,
        alpha_img: float = 1.0,
        ax: Optional[mpl.axes.Axes] = None
):
    if not keys is None:
        ncell = adata.shape[0]
        V = np.zeros([ncell, 2], float)
        signal_sum = np.zeros([ncell], float)
        for key in keys:
            if summary == 'sender':
                V = V + adata.obsm['SpaGRD_sender_vf-' + database_name + '-' + key][:, pos_idx]
                signal_sum = signal_sum + adata.obsm['SpaGRD-' + database_name + "-sum-sender"]['s-' + key]
            elif summary == 'receiver':
                V = V + adata.obsm['SpaGRD_receiver_vf-' + database_name + '-' + key][:, pos_idx]
                signal_sum = signal_sum + adata.obsm['SpaGRD-' + database_name + "-sum-receiver"]['r-' + key]
        V = V / float(len(keys))
        signal_sum = signal_sum / float(len(keys))
    elif keys is None:
        if not lr_pair is None:
            vf_name = database_name + '-' + lr_pair[0] + '-' + lr_pair[1]
            sum_name = lr_pair[0] + '-' + lr_pair[1]
        elif not pathway_name is None:
            vf_name = database_name + '-' + pathway_name
            sum_name = pathway_name
        else:
            vf_name = database_name + '-total-total'
            sum_name = 'total-total'
        if summary == 'sender':
            V = adata.obsm['SpaGRD_sender_vf-' + vf_name][:, pos_idx]
            signal_sum = adata.obsm['SpaGRD-' + database_name + "-sum-sender"]['s-' + sum_name]
        elif summary == 'receiver':
            V = adata.obsm['SpaGRD_receiver_vf-' + vf_name][:, pos_idx]
            signal_sum = adata.obsm['SpaGRD-' + database_name + "-sum-receiver"]['r-' + sum_name]

    if ax is None:
        fig, ax = plt.subplots()
    if normalize_v:
        V = V / np.quantile(np.linalg.norm(V, axis=1), normalize_v_quantile)
    plot_cell_signaling(
        adata.obsm["spatial"][:, pos_idx],
        V,
        signal_sum,
        cmap=cmap,
        cluster_cmap=cluster_cmap,
        plot_method=plot_method,
        background=background,
        clustering=clustering,
        background_legend=background_legend,
        adata=adata,
        summary=summary,
        scale=scale,
        ndsize=ndsize,
        filename=filename,
        arrow_color=arrow_color,
        grid_density=grid_density,
        grid_knn=grid_knn,
        grid_scale=grid_scale,
        grid_thresh=grid_thresh,
        grid_width=grid_width,
        stream_density=stream_density,
        stream_linewidth=stream_linewidth,
        stream_cutoff_perc=stream_cutoff_perc,
        ax=ax,
        fig=fig,
        alpha_img=alpha_img
    )

    return ax


def plot_cell_signaling(X,
                        V,
                        signal_sum,
                        cmap="coolwarm",
                        cluster_cmap=None,
                        arrow_color="tab:blue",
                        plot_method="cell",
                        background='summary',
                        clustering=None,
                        background_legend=False,
                        adata=None,
                        summary='sender',
                        ndsize=1,
                        scale=1.0,
                        grid_density=1,
                        grid_knn=None,
                        grid_scale=1.0,
                        grid_thresh=1.0,
                        grid_width=0.005,
                        stream_density=1.0,
                        stream_linewidth=1,
                        stream_cutoff_perc=5,
                        filename=None,
                        ax=None,
                        alpha_img=1,
                        fig=None
                        ):
    ndcolor = signal_sum
    ncell = X.shape[0]

    V_cell = V.copy()
    V_cell_sum = np.sum(V_cell, axis=1)
    V_cell[np.where(V_cell_sum == 0)[0], :] = np.nan
    if summary == "sender":
        X_vec = X
    elif summary == "receiver":
        X_vec = X - V / scale

    if plot_method == "grid" or plot_method == "stream":
        # Get a rectangular grid
        xl, xr = np.min(X[:, 0]), np.max(X[:, 0])
        epsilon = 0.02 * (xr - xl);
        xl -= epsilon;
        xr += epsilon
        yl, yr = np.min(X[:, 1]), np.max(X[:, 1])
        epsilon = 0.02 * (yr - yl);
        yl -= epsilon;
        yr += epsilon
        ngrid_x = int(50 * grid_density)
        gridsize = (xr - xl) / float(ngrid_x)
        ngrid_y = int((yr - yl) / gridsize)
        meshgrid = np.meshgrid(np.linspace(xl, xr, ngrid_x), np.linspace(yl, yr, ngrid_y))
        grid_pts = np.concatenate((meshgrid[0].reshape(-1, 1),
                                   meshgrid[1].reshape(-1, 1)), axis=1)

        if grid_knn is None:
            grid_knn = int(X.shape[0] / 50)
        nn_mdl = NearestNeighbors()
        nn_mdl.fit(X)
        dis, nbs = nn_mdl.kneighbors(grid_pts, n_neighbors=grid_knn)
        w = norm.pdf(x=dis, scale=gridsize * grid_scale)
        w_sum = w.sum(axis=1)

        V_grid = (V[nbs] * w[:, :, None]).sum(axis=1)
        V_grid /= np.maximum(1, w_sum)[:, None]

        if plot_method == "grid":
            grid_thresh *= np.percentile(w_sum, 99) / 100
            grid_pts, V_grid = grid_pts[w_sum > grid_thresh], V_grid[w_sum > grid_thresh]
        elif plot_method == "stream":
            x_grid = np.linspace(xl, xr, ngrid_x)
            y_grid = np.linspace(yl, yr, ngrid_y)
            V_grid = V_grid.T.reshape(2, ngrid_y, ngrid_x)
            vlen = np.sqrt((V_grid ** 2).sum(0))
            grid_thresh = 10 ** (grid_thresh - 6)
            grid_thresh = np.clip(grid_thresh, None, np.max(vlen) * 0.9)
            cutoff = vlen.reshape(V_grid[0].shape) < grid_thresh
            length = np.sum(np.mean(np.abs(V[nbs]), axis=1), axis=1).T
            length = length.reshape(ngrid_y, ngrid_x)
            cutoff |= length < np.percentile(length, stream_cutoff_perc)

            V_grid[0][cutoff] = np.nan

    if isinstance(cmap, str):
        if cmap == 'Plotly':
            cmap = plotly.colors.qualitative.Plotly
        elif cmap == 'Light24':
            cmap = plotly.colors.qualitative.Light24
        elif cmap == 'Dark24':
            cmap = plotly.colors.qualitative.Dark24
        elif cmap == 'Alphabet':
            cmap = plotly.colors.qualitative.Alphabet

    idx = np.argsort(ndcolor)
    if background == 'summary' or background == 'cluster':
        if not ndsize == 0:
            if background == 'summary':
                ax.scatter(X[idx, 0], X[idx, 1], s=ndsize, c=ndcolor[idx], cmap=cmap, linewidth=0)
            elif background == 'cluster':
                labels = np.array(adata.obs[clustering], str)
                unique_labels = np.sort(list(set(list(labels))))
                for i_label in range(len(unique_labels)):
                    idx = np.where(labels == unique_labels[i_label])[0]
                    if cluster_cmap is None:
                        ax.scatter(X[idx, 0],
                                   X[idx, 1],
                                   s=ndsize,
                                   c=cmap[i_label],
                                   linewidth=0,
                                   label=unique_labels[i_label])
                    elif not cluster_cmap is None:
                        ax.scatter(X[idx, 0],
                                   X[idx, 1],
                                   s=ndsize,
                                   c=cluster_cmap[unique_labels[i_label]],
                                   linewidth=0,
                                   label=unique_labels[i_label])
                if background_legend:
                    ax.legend(markerscale=2.0, loc=[1.0, 0.0])
        if plot_method == "cell":
            ax.quiver(X_vec[:, 0],
                      X_vec[:, 1],
                      V_cell[:, 0],
                      V_cell[:, 1],
                      scale=scale,
                      scale_units='x',
                      color=arrow_color)
        elif plot_method == "grid":
            ax.quiver(grid_pts[:, 0],
                      grid_pts[:, 1],
                      V_grid[:, 0],
                      V_grid[:, 1],
                      scale=scale,
                      scale_units='x',
                      width=grid_width,
                      color=arrow_color)
        elif plot_method == "stream":
            lengths = np.sqrt((V_grid ** 2).sum(0))
            stream_linewidth *= 2 * lengths / lengths[~np.isnan(lengths)].max()
            ax.streamplot(x_grid,
                          y_grid,
                          V_grid[0],
                          V_grid[1],
                          color=arrow_color,
                          density=stream_density,
                          linewidth=stream_linewidth)
    elif background == 'image':
        spatial_mapping = adata.uns.get("spatial", {})
        library_id = list(spatial_mapping.keys())[0]
        spatial_data = spatial_mapping[library_id]
        img = spatial_data['images']['hires']
        sf = spatial_data['scalefactors']['tissue_hires_scalef']
        ax.imshow(img, alpha=alpha_img)
        if plot_method == "cell":
            ax.quiver(X_vec[:, 0] * sf,
                      X_vec[:, 1] * sf,
                      V_cell[:, 0] * sf,
                      V_cell[:, 1] * sf,
                      scale=scale,
                      scale_units='x',
                      color=arrow_color)
        elif plot_method == "grid":
            ax.quiver(grid_pts[:, 0] * sf,
                      grid_pts[:, 1] * sf,
                      V_grid[:, 0] * sf,
                      V_grid[:, 1] * sf,
                      scale=scale,
                      scale_units='x',
                      width=grid_width,
                      color=arrow_color)
        elif plot_method == "stream":
            lengths = np.sqrt((V_grid ** 2).sum(0))
            stream_linewidth *= 2 * lengths / lengths[~np.isnan(lengths)].max()
            ax.streamplot(x_grid * sf,
                          y_grid * sf,
                          V_grid[0] * sf,
                          V_grid[1] * sf,
                          color=arrow_color,
                          density=stream_density,
                          linewidth=stream_linewidth)

    ax.axis("equal")
    ax.axis("off")
    if not filename is None:
        plt.savefig(filename, dpi=500, bbox_inches='tight', transparent=True)
