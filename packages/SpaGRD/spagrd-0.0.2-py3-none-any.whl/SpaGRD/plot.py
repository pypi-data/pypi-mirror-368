import time
import gseapy as gp
import scipy.sparse as ss
import seaborn as sns
from plotnine import *
from typing import Optional
import numpy as np
import pandas as pd
import scanpy as sc
import plotly
from sklearn.preprocessing import normalize
import matplotlib as mpl
import networkx as nx
from sklearn.neighbors import NearestNeighbors
from scipy.stats import norm
from networkx.drawing.nx_agraph import to_agraph
from .direction import communication_direction
from .direction import plot_cell_communication
import matplotlib.pyplot as plt


def svi_kneed_plot(interaction_df, return_fig=False):
    plot_data = interaction_df.loc[:, ['gft_score', 'svi_rank', 'cutoff_gft_score']]
    plt.figure()
    sns.scatterplot(x="svi_rank", y="gft_score",
                    hue="cutoff_gft_score",
                    data=plot_data,
                    palette='Set2')
    plt.xlabel("Rank of spatial variable L-Rs")
    plt.ylabel("GFT score")
    plt.grid(False)
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.show()
    if return_fig:
        return ax


def cell_type_heatmap(ct_ccc_df,
                      return_fig=False,
                      cmap='magma',
                      annot=False,
                      label_fontsize=None,
                      ticks_fontsize=None,
                      type='pvalue'):
    # Prepare data for plotting
    if type == 'pvalue':
        p_value = np.clip(ct_ccc_df.values, 1e-4, 1)
        p_value = -1 * np.log10(p_value)
        plot_df = pd.DataFrame(p_value,
                               index=ct_ccc_df.index,
                               columns=ct_ccc_df.columns)

    plot_df = plot_df.transpose().stack().reset_index()
    plot_df.columns = ['Receiver', 'Sender', 'Value']

    # Pivot the dataframe for heatmap compatibility
    heatmap_data = plot_df.pivot(index='Sender', columns='Receiver', values='Value')

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    cbar_ax = fig.add_axes([0.85, 0.4, 0.03, 0.3])  # Position the color bar closer to the heatmap
    sns.heatmap(heatmap_data, ax=ax, cmap=cmap, cbar=True, annot=annot, cbar_ax=cbar_ax, square=True, linewidths=0)

    # Set plot titles and labels with custom font sizes if specified
    if label_fontsize is not None:
        ax.set_title('Cell type communications', fontsize=label_fontsize)
        ax.set_xlabel('Receiver', fontsize=label_fontsize)
        ax.set_ylabel('Sender', fontsize=label_fontsize)
    else:
        ax.set_title('Cell type communications')
        ax.set_xlabel('Receiver')
        ax.set_ylabel('Sender')

    ax.set_aspect('equal')

    # Rotate x-axis labels for better readability and set tick label font size if specified
    if ticks_fontsize is not None:
        plt.xticks(rotation=90, fontsize=ticks_fontsize)
        plt.yticks(fontsize=ticks_fontsize)
    else:
        plt.xticks(rotation=90)
        plt.yticks()

    # Remove gridlines
    ax.grid(False)
    plt.grid(False)

    # Show the plot
    plt.tight_layout()
    plt.show()

    # Return the figure if specified
    if return_fig:
        return fig


def obtain_rd_single(adata, interaction, step=1):
    add_columns = [interaction + f"-{step}-ligand", interaction + f"-{step}-receptor",
                   interaction + f"-{step}-interaction", interaction + f"-{step}-new_ligand",
                   interaction + f"-{step}-new_receptor"]
    if step == 1:
        adata.obs[interaction + f"-{step}-ligand"] = adata.uns['interaction_info'][str(step - 1)][0].loc[:,
                                                     interaction].values
        adata.obs[interaction + f"-{step}-receptor"] = adata.uns['interaction_info'][str(step - 1)][1].loc[:,
                                                       interaction].values
    else:
        adata.obs[interaction + f"-{step}-ligand"] = adata.uns['interaction_info'][str(step - 1)][1].loc[:,
                                                     interaction].values
        adata.obs[interaction + f"-{step}-receptor"] = adata.uns['interaction_info'][str(step - 1)][2].loc[:,
                                                       interaction].values
    adata.obs[interaction + f"-{step}-interaction"] = adata.uns['interaction_info'][str(step)][0].loc[:,
                                                      interaction].values
    adata.obs[interaction + f"-{step}-new_ligand"] = adata.uns['interaction_info'][str(step)][1].loc[:,
                                                     interaction].values
    adata.obs[interaction + f"-{step}-new_receptor"] = adata.uns['interaction_info'][str(step)][2].loc[:,
                                                       interaction].values

    return add_columns


def obtain_rd_system(adata, interaction, step=1):
    ligands = adata.uns['lr_info']['ligand_unit'][interaction]
    receptors = adata.uns['lr_info']['receptor_unit'][interaction]
    add_columns = [i + f"-{step}-ligand" for i in ligands] + \
                  [i + f"-{step}-receptor" for i in receptors] + \
                  [interaction + f"-{step}-interaction"] + \
                  [i + f"-{step}-new_ligand" for i in ligands] + \
                  [i + f"-{step}-new_receptor" for i in receptors]

    if step == 1:
        for ligand in ligands:
            adata.obs[ligand + f"-{step}-ligand"] = adata.uns['interaction_info'][str(step - 1)][0].loc[:,
                                                    ligand].values
        for receptor in receptors:
            adata.obs[receptor + f"-{step}-receptor"] = adata.uns['interaction_info'][str(step - 1)][1].loc[:,
                                                        receptor].values
    else:
        for ligand in ligands:
            adata.obs[ligand + f"-{step}-ligand"] = adata.uns['interaction_info'][str(step - 1)][1].loc[:,
                                                    ligand].values
        for receptor in receptors:
            adata.obs[receptor + f"-{step}-receptor"] = adata.uns['interaction_info'][str(step - 1)][2].loc[:,
                                                        receptor].values

    adata.obs[interaction + f"-{step}-interaction"] = adata.uns['interaction_info'][str(step)][0].loc[:,
                                                      interaction].values
    for ligand in ligands:
        adata.obs[ligand + f"-{step}-new_ligand"] = adata.uns['interaction_info'][str(step)][1].loc[:,
                                                    ligand].values
    for receptor in receptors:
        adata.obs[receptor + f"-{step}-new_receptor"] = adata.uns['interaction_info'][str(step)][2].loc[:,
                                                        receptor].values

    return add_columns


def plot_module_go(adata,
                   module,
                   organism='Human',
                   top_terms=20,
                   figsize=(20, 8),
                   gene_sets='GO_Biological_Process_2021',
                   return_fig=False):
    if isinstance(module, int):
        module = str(module)
    if 'module' not in module:
        module = 'module_' + module

    # add ligands and receptors
    lr_list = []
    lr_module_df = adata.uns['lr_module_info']['lr_module_df']
    lr_module_df = lr_module_df.loc[lr_module_df['module'] == module.split('module_')[-1], :]
    for lr in lr_module_df.index:
        lr_list.append(adata.uns['lr_info'].loc[lr, 'ligand'])
        lr_list.append(adata.uns['lr_info'].loc[lr, 'receptor'])
    lr_list = np.unique(lr_list).tolist()

    # enrichment analysis
    enr = gp.enrichr(gene_list=lr_list,
                     gene_sets=gene_sets,
                     organism=organism,
                     outdir=f'./tmp/GO_module-{module}',
                     no_plot=False,
                     cutoff=0.05  # test dataset, use lower value from range(0,1)
                     )

    from gseapy.plot import barplot
    ax = barplot(enr.results[enr.results.Gene_set == 'GO_Biological_Process_2021'],
                 column='P-value',
                 top_term=top_terms,
                 title=f'{gene_sets}: module {module}',
                 figsize=figsize,
                 )
    plt.yticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.show()
    if return_fig:
        return ax


def plot_interaction(adata,
                     interaction,
                     source='original',
                     return_figure=True,
                     **kwargs):
    # Obtain ligands
    if isinstance(interaction, pd.core.indexes.base.Index):
        interaction = interaction[0]
    ax_list = []
    ligands = adata.uns['lr_info']['ligand_unit'][interaction]
    receptors = adata.uns['lr_info']['receptor_unit'][interaction]

    # Add vectors
    if ss.issparse(adata.X):
        adata.obs.loc[:, [f'Ligand {ligand}' for ligand in ligands]] = \
            adata[:, ligands].X.A
        adata.obs.loc[:, [f'Receptor {receptor}' for receptor in receptors]] = \
            adata[:, receptors].X.A
    else:
        adata.obs.loc[:, [f'Ligand {ligand}' for ligand in ligands]] = \
            adata[:, ligands].X
        adata.obs.loc[:, [f'Receptor {receptor}' for receptor in receptors]] = \
            adata[:, receptors].X
    adata.obs.loc[:, [f'Ligand {ligand} with diffusion' for ligand in ligands]] = \
        adata.obsm['ligand_unit_diffusion_expression'].loc[:, ligands].values

    if source == 'original':
        ax_list = sc.pl.spatial(adata,
                                color=[f'Ligand {ligand}' for ligand in ligands] +
                                      [f'Receptor {receptor}' for receptor in receptors],
                                return_fig=True,
                                **kwargs)
    elif source == 'diffusion':
        ax_list = sc.pl.spatial(adata,
                                color=[f'Ligand {ligand} with diffusion' for ligand in ligands] +
                                      [f'Receptor {receptor}' for receptor in receptors],
                                return_fig=True, **kwargs)
    elif source == 'mixed':
        ax_list = sc.pl.spatial(adata,
                                color=[f'Ligand {ligand}' for ligand in ligands] +
                                      [f'Ligand {ligand} with diffusion' for ligand in ligands] +
                                      [f'Receptor {receptor}' for receptor in receptors],
                                return_fig=True, **kwargs)

    # Remove vectors
    adata.obs.drop([f'Ligand {ligand}' for ligand in ligands] +
                   [f'Ligand {ligand} with diffusion' for ligand in ligands] +
                   [f'Receptor {receptor}' for receptor in receptors],
                   axis=1)
    if return_figure:
        return ax_list


def pie_annotation(adata,
                   module,
                   fig_size=(9, 6)):
    if isinstance(module, int):
        module = str(module)
    color_map = {'ECM-Receptor': plt.cm.tab20c(9), 'Cell-Cell Contact': plt.cm.tab20c(5),
                 'Secreted Signaling': plt.cm.tab20c(13)}

    data = adata.uns['lr_info']['lr_score_df']
    data = data.loc[data['lr_module'] == module, :]
    total_counts = data.shape[0]
    unique_name, counts = np.unique(data['annotation'], return_counts=True)
    colors = [color_map[i] for i in unique_name]

    plt.figure(figsize=fig_size)
    plt.pie(counts,
            labels=unique_name,
            colors=colors,
            autopct=lambda pct: f"{pct:.1f}% ({int(pct / 100 * sum(counts))})")
    plt.title(f"interaction annotations in module {module}")
    plt.show()


def pie_pathway(adata,
                module,
                fig_size=(9, 6)):
    if isinstance(module, int):
        module = str(module)

    data = adata.uns['lr_info']['lr_score_df']
    data = data.loc[data['lr_module'] == module, :]
    unique_name, counts = np.unique(data['pathway_name'], return_counts=True)
    plt.figure(figsize=fig_size)
    plt.title(f"pathway names in module {module}")
    plt.pie(counts,
            labels=unique_name,
            autopct=lambda pct: f"{pct:.1f}% ({int(pct / 100 * sum(counts))})",
            textprops={'fontsize': 10})
    plt.show()


def lr_freq_signal(adata,
                   interaction,
                   dpi=100,
                   colors=None,
                   fontsize=10,
                   **kwargs):
    if colors is None:
        colors = ['#CA1C1C', '#345591']
    annotation = adata.uns['lr_info']['lr_meta'].at[interaction, 'annotation']
    if annotation == 'Cell-Cell Contact':
        ligands_freq_signal = adata.uns['GFT_info']['ligands_freq_mtx'].loc[interaction, :].values
    else:
        ligands_freq_signal = adata.uns['GFT_info']['ligands_diffusion_freq_mtx'].loc[interaction, :].values
    receptor_freq_signal = adata.uns['GFT_info']['receptors_freq_mtx'].loc[interaction, :].values

    # plot
    y_max = max(ligands_freq_signal.max(), receptor_freq_signal.max())
    y_min = min(ligands_freq_signal.min(), receptor_freq_signal.min())
    y_range = max(abs(y_max), abs(y_min)) * 1.05
    plt.figure(dpi=dpi, **kwargs)
    plt.subplot(211)
    plt.bar(list(range(len(ligands_freq_signal))), ligands_freq_signal, color=colors[0])
    ax = plt.gca()
    plt.xticks([])
    plt.grid(False)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    ax.spines['right'].set_color("none")
    ax.spines['top'].set_color("none")
    ax.spines['bottom'].set_color("none")
    plt.ylim(-y_range, y_range)
    plt.title(f"Ligand signals of {interaction}", fontsize=fontsize)
    plt.subplot(212)
    plt.bar(list(range(len(ligands_freq_signal))), receptor_freq_signal, color=colors[1])
    ax = plt.gca()
    plt.grid(False)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    ax.spines['right'].set_color("none")
    ax.spines['top'].set_color("none")
    plt.ylim(-y_range, y_range)
    plt.title(f"Receptor signals of {interaction}", fontsize=fontsize)
    plt.show()


def scatter_gene_distri(adata,
                        gene,
                        size=3,
                        shape='h',
                        cmap='magma',
                        spatial_info=['array_row', 'array_col'],
                        coord_ratio=1,
                        return_plot=False):
    if gene in adata.obs.columns:
        if isinstance(gene, str):
            plot_df = pd.DataFrame(adata.obs.loc[:, gene].values,
                                   index=adata.obs_names,
                                   columns=[gene])
        else:
            plot_df = pd.DataFrame(adata.obs.loc[:, gene],
                                   index=adata.obs_names,
                                   columns=gene)
        if spatial_info in adata.obsm_keys():
            plot_df['x'] = adata.obsm[spatial_info][:, 0]
            plot_df['y'] = adata.obsm[spatial_info][:, 1]
        elif set(spatial_info) <= set(adata.obs.columns):
            plot_coor = adata.obs
            plot_df['x'] = plot_coor.loc[:, spatial_info[0]].values
            plot_df['y'] = plot_coor.loc[:, spatial_info[1]].values

        if isinstance(gene, str):
            base_plot = (ggplot() + geom_point(plot_df, aes(x='x', y='y', fill=gene),
                                               shape=shape, stroke=0.1, size=size) +
                         xlim(min(plot_df.x) - 1, max(plot_df.x) + 1) +
                         ylim(min(plot_df.y) - 1, max(plot_df.y) + 1) +
                         scale_fill_cmap(cmap_name=cmap) +
                         coord_equal(ratio=coord_ratio) +
                         theme_classic() +
                         theme(legend_position=('right'),
                               legend_background=element_blank(),
                               legend_key_width=4,
                               legend_key_height=50)
                         )
            print(base_plot)
        else:
            for i in gene:
                base_plot = (ggplot() + geom_point(plot_df, aes(x='x', y='y', fill=gene),
                                                   shape=shape, stroke=0.1, size=size) +
                             xlim(min(plot_df.x) - 1, max(plot_df.x) + 1) +
                             ylim(min(plot_df.y) - 1, max(plot_df.y) + 1) +
                             scale_fill_cmap(cmap_name=cmap) +
                             coord_equal(ratio=coord_ratio) +
                             theme_classic() +
                             theme(legend_position=('right'),
                                   legend_background=element_blank(),
                                   legend_key_width=4,
                                   legend_key_height=50)
                             )
                print(base_plot)

        return
    if ss.issparse(adata.X):
        plot_df = pd.DataFrame(adata.X.todense(), index=adata.obs_names,
                               columns=adata.var_names)
    else:
        plot_df = pd.DataFrame(adata.X, index=adata.obs_names,
                               columns=adata.var_names)
    if spatial_info in adata.obsm_keys():
        plot_df['x'] = adata.obsm[spatial_info][:, 0]
        plot_df['y'] = adata.obsm[spatial_info][:, 1]
    elif set(spatial_info) <= set(adata.obs.columns):
        plot_coor = adata.obs
        plot_df = plot_df[gene]
        plot_df = pd.DataFrame(plot_df)
        plot_df['x'] = plot_coor.loc[:, spatial_info[0]].values
        plot_df['y'] = plot_coor.loc[:, spatial_info[1]].values
    plot_df['radius'] = size
    plot_df = plot_df.sort_values(by=gene, ascending=True)
    if isinstance(gene, str):
        base_plot = (ggplot() + geom_point(plot_df, aes(x='x', y='y', fill=gene),
                                           shape=shape, stroke=0.1, size=size) +
                     xlim(min(plot_df.x) - 1, max(plot_df.x) + 1) +
                     ylim(min(plot_df.y) - 1, max(plot_df.y) + 1) +
                     scale_fill_cmap(cmap_name=cmap) +
                     coord_equal(ratio=coord_ratio) +
                     theme_classic() +
                     theme(legend_position=('right'),
                           legend_background=element_blank(),
                           legend_key_width=4,
                           legend_key_height=50)
                     )
        print(base_plot)
    else:
        for i in gene:
            base_plot = (ggplot() + geom_point(plot_df, aes(x='x', y='y', fill=gene),
                                               shape=shape, stroke=0.1, size=size) +
                         xlim(min(plot_df.x) - 1, max(plot_df.x) + 1) +
                         ylim(min(plot_df.y) - 1, max(plot_df.y) + 1) +
                         scale_fill_cmap(cmap_name=cmap) +
                         coord_equal(ratio=coord_ratio) +
                         theme_classic() +
                         theme(legend_position=('right'),
                               legend_background=element_blank(),
                               legend_key_width=4,
                               legend_key_height=50)
                         )
            print(base_plot)
    if return_plot:
        return base_plot


def plot_molecule_scatter(adata,
                          molecule_name,
                          figsize=(3, 3),
                          size=None,
                          vmin=0,
                          vmax=1,
                          dpi=300,
                          cmap='viridis',
                          add_title=True,
                          show=True):
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    time.sleep(2)
    coords = adata.obsm['spatial']
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    expression = adata[:, molecule_name].X.flatten()
    if size is not None:
        scatter = ax.scatter(coords[:, 0],
                             coords[:, 1],
                             c=expression,
                             s=size,
                             cmap=cmap,
                             vmin=vmin,
                             marker='o',
                             vmax=vmax)
    else:
        scatter = ax.scatter(coords[:, 0],
                             coords[:, 1],
                             c=expression,
                             marker='o',
                             cmap=cmap,
                             vmin=vmin,
                             vmax=vmax
                             )
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.05)
    cbar = plt.colorbar(scatter, cax=cax)
    if add_title:
        ax.set_title(molecule_name)
    ax.axis('on')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    plt.tight_layout()
    if show:
        plt.show()
    return fig


def dynamic_plot(adata,
                 lr_pair,
                 cmap='Oranges',
                 color='interaction',
                 save_path=None,
                 fps=5,
                 spot_size=None,
                 **kwargs):
    import imageio
    import os

    data = adata.uns['GRD_info']

    if color == 'ligand':
        plot_df = data['ligand_process']
    elif color == 'receptor':
        plot_df = data['receptor_process']
    else:
        plot_df = data['interaction_process']
    selected_logs = []
    for i in plot_df.columns:
        if lr_pair in i:
            selected_logs.append(i)
    img_list = []
    plot_adata = sc.AnnData(plot_df)
    plot_adata.obsm['spatial'] = adata.obsm['spatial'].copy()
    plot_adata.uns['spatial'] = adata.uns['spatial'].copy()
    vmax = plot_df[selected_logs].max().max()
    for i in selected_logs:
        fig = sc.pl.spatial(plot_adata, color=i, vmax=vmax, spot_size=spot_size, cmap=cmap,
                            return_fig=True, show=False, **kwargs)
        fig = fig[0]
        fig.figure.tight_layout()
        fig.figure.tight_layout()
        fig.figure.tight_layout()
        fig.figure.canvas.draw()
        img = np.frombuffer(fig.figure.canvas.tostring_argb(), dtype='uint8')
        width, height = fig.figure.canvas.get_width_height()
        img = img.reshape((height, width, 4))
        img_rgb = img[:, :, 1:4]
        img_list.append(img_rgb)
    # save gif
    save_name = lr_pair + '_' + color + "_dynamic.gif"
    if save_path is not None:
        save_name = os.path.join(save_path, save_name)
    imageio.mimsave(save_name, img_list, fps=fps)


def interaction_sum_over_time(adata, save_fig=None, figsize=(10, 5), return_fig=False):
    """
    Plot the sum of ligand-receptor interaction values over time.

    Parameters:
        adata: AnnData object containing the interaction data in `adata.uns['GRD_info']['lr_interaction_sum']`.
        save_fig: str or None, path to save the figure. If None, the figure is not saved.
        figsize: tuple, size of the figure.
        return_fig: bool, whether to return the matplotlib Axes object.

    Returns:
        ax: matplotlib Axes object if `return_fig` is True, otherwise None.
    """
    # Extract interaction data
    plot_df = adata.uns['GRD_info']['lr_interaction_sum']
    interaction_sums = plot_df.sum(axis=0).values

    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(range(len(interaction_sums)), interaction_sums, label='Interaction Sum', color='blue', linewidth=2)
    ax.set_xlabel('Time', fontsize=14)
    ax.set_ylabel('Interaction Sum', fontsize=14)
    ax.set_title("Total LR Interactions Over Time", fontsize=14)

    # Customize plot appearance
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    # Save the plot if a path is provided
    if save_fig:
        plt.savefig(save_fig, dpi=300, bbox_inches='tight')
        print(f"Figure saved at {save_fig}")

    # Show the plot
    plt.show()

    # Return the Axes object if needed
    return ax if return_fig else None


def interaction_lr_over_time(adata, lr, save_fig=None, return_fig=False, figsize=(10, 5)):
    """
    Plot ligand-receptor interaction dynamics over time for specified LR pairs.

    Parameters:
        adata: AnnData object containing interaction data in `adata.uns['GRD_info']['lr_interaction_sum']`.
        lr: str or list of str, the ligand-receptor pair(s) to plot.
        save_fig: str or None, base path to save figures. If None, figures are not saved.
        return_fig: bool, whether to return the matplotlib Axes object(s).
        figsize: tuple, size of the figure.

    Returns:
        Axes object(s) if `return_fig` is True, otherwise None.
    """
    # Extract interaction data
    plot_df = adata.uns['GRD_info']['lr_interaction_sum']
    lr_list = [lr] if isinstance(lr, str) else lr

    # Initialize storage for Axes objects
    axes_list = []
    if lr == 'all':
        interaction_sums = plot_df.sum(axis=0).values
        lr_molecular = 'Interaction Sum'
        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(range(len(interaction_sums)), interaction_sums, label=lr_molecular, color='blue', linewidth=2)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Interaction Sum', fontsize=12)
        ax.set_title(f"{lr_molecular} Interaction Over Time", fontsize=14)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

        # Save figure if save path is provided
        if save_fig:
            save_path = f"{save_fig}_{lr_molecular}_interaction_over_time.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved at {save_path}")

        plt.show()
        if return_fig:
            axes_list.append(ax)

    for lr_molecular in lr_list:
        if lr_molecular not in plot_df.index:
            print(f"Warning: {lr_molecular} not found in interaction data.")
            continue

        # Extract interaction data for the current LR pair
        interaction_sums = plot_df.loc[lr_molecular, :].values

        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(range(len(interaction_sums)), interaction_sums, label=lr_molecular, color='blue', linewidth=2)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Interaction Sum', fontsize=12)
        ax.set_title(f"{lr_molecular} Interaction Over Time", fontsize=14)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

        # Save figure if save path is provided
        if save_fig:
            save_path = f"{save_fig}_{lr_molecular}_interaction_over_time.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved at {save_path}")

        plt.show()

        # Store Axes if needed
        if return_fig:
            axes_list.append(ax)

    # Return Axes object(s) if specified
    if return_fig:
        return axes_list if len(axes_list) > 1 else axes_list[0]


def cell_type_chord_diagram(ct_ccc_df,
                            ct_pvalue_df,
                            cmap="tab20",
                            pvalue_cutoff=0.05,
                            ccc_cutoff=0.05,
                            return_fig=False):
    pvalue_mtx = ct_pvalue_df.values.copy()
    pvalue_mtx = np.clip(pvalue_mtx, 1e-4, 1)
    pvalue_mtx = -1 * np.log10(pvalue_mtx)
    cutoff = -1 * np.log10(pvalue_cutoff)
    pvalue_mtx[pvalue_mtx < cutoff] = 0
    ct_mtx = ct_ccc_df.values.copy()
    cutoff = ct_mtx.max() * ccc_cutoff
    ct_mtx[ct_mtx < cutoff] = 0
    ct_mtx[ct_mtx > 0] = 1
    plot_df = ct_mtx * pvalue_mtx
    plot_df = pd.DataFrame(plot_df,
                           index=ct_ccc_df.index,
                           columns=ct_ccc_df.columns)
    from pycirclize import Circos
    # remove useless cell types
    row_sums = plot_df.sum(axis=1)
    col_sums = plot_df.sum(axis=0)
    valid_cts = plot_df.index[(row_sums > 0) | (col_sums > 0)]
    plot_df = plot_df.loc[valid_cts, valid_cts]
    circos = Circos.chord_diagram(
        plot_df,
        start=-255,
        end=105,
        space=4.5,
        r_lim=(93, 100),
        cmap=cmap,
        label_kws=dict(r=94, size=14, color="black"),
        link_kws=dict(ec="black", lw=0.5),
    )
    fig = circos.plotfig()
    fig.show()

    if return_fig:
        return fig


def plot_circular_network(ct_ccc_df,
                          ct_pvalue_df,
                          node_colors=None,
                          pvalue_cutoff=0.05,
                          ccc_cutoff=0.05,
                          return_fig=False,
                          figsize=(6, 6)):
    pvalue_mtx = ct_pvalue_df.values.copy()
    pvalue_mtx = np.clip(pvalue_mtx, 1e-4, 1)
    pvalue_mtx = -1 * np.log10(pvalue_mtx)
    cutoff = -1 * np.log10(pvalue_cutoff)
    pvalue_mtx[pvalue_mtx < cutoff] = 0
    ct_mtx = ct_ccc_df.values.copy()
    cutoff = ct_mtx.max() * ccc_cutoff
    ct_mtx[ct_mtx < cutoff] = 0
    ct_mtx[ct_mtx > 0] = 1
    plot_df = ct_mtx * pvalue_mtx
    plot_df = pd.DataFrame(plot_df,
                           index=ct_ccc_df.index,
                           columns=ct_ccc_df.columns)
    # Create a directed graph
    G = nx.DiGraph()

    # Ensure the index and columns of the DataFrame are identical
    if not plot_df.index.equals(ct_ccc_df.columns):
        raise ValueError("DataFrame's index and columns must be identical.")

    # Get node names
    nodes = plot_df.index
    num_nodes = len(nodes)

    # Add nodes and edges
    G.add_nodes_from(nodes)
    for source in nodes:
        for target in nodes:
            weight = plot_df.loc[source, target]
            if weight != 0:  # Only draw edges with non-zero weight
                G.add_edge(source, target, weight=weight * 2)

    # If node_colors is not specified, use the default color map
    if node_colors is None:
        node_colors = plt.cm.tab20(np.linspace(0, 1, num_nodes))

    # Create a node color map
    if not isinstance(node_colors, dict):
        node_color_map = dict(zip(nodes, node_colors))
    else:
        node_color_map = dict(zip(nodes, [node_colors[node] for node in nodes]))
    # Use circular_layout
    pos = nx.circular_layout(G)

    # Draw the figure
    plt.figure(figsize=figsize)

    # Draw nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=200,
        node_color=[node_color_map[node] for node in nodes],
        edgecolors='black'
    )

    # Draw node labels (avoid overlapping with nodes)
    for node, (x, y) in pos.items():
        label_x = x * 1.1
        label_y = y * 1.1
        horizontal_alignment = 'center'
        vertical_alignment = 'center'
        if x > 0:  # Node is on the right
            horizontal_alignment = 'left'
        elif x < 0:  # Node is on the left
            horizontal_alignment = 'right'
        if y > 0:  # Node is above
            vertical_alignment = 'bottom'
        elif y < 0:  # Node is below
            vertical_alignment = 'top'

        plt.text(
            label_x, label_y, node, fontsize=14, color='black',
            ha=horizontal_alignment, va=vertical_alignment
        )

    # Draw edges
    for source, target, data in G.edges(data=True):
        weight = data['weight']
        color = node_color_map[source]
        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(source, target)],
            width=weight,
            edge_color=[color],
            connectionstyle='arc3, rad=0.2' if source != target else 'arc3, rad=0.5',  # Larger arc for self-loops
            arrows=True,
            arrowsize=10
        )

    # plt.title("Cell-Cell Communications", fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    ax = plt.gca()

    plt.show()
    if return_fig:
        return ax


def plot_signaling_direction(adata,
                             spot_ccc_df,
                             k=5,
                             plot_method: str = "grid",
                             alpha_img: float = 1.0,
                             background: str = "summary",
                             background_legend: bool = False,
                             clustering: str = None,
                             summary: str = "sender",
                             cmap: str = "coolwarm",
                             cluster_cmap: dict = None,
                             pos_idx: np.ndarray = np.array([0, 1], int),
                             ndsize: float = 8,
                             scale: float = 0.00001,
                             normalize_v: bool = True,
                             normalize_v_quantile: float = 0.995,
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
                             return_fig=False,
                             **kwargs):
    communication_direction(adata, spot_ccc_df=spot_ccc_df, database_name='tmp', pathway_name='tmp', k=k)
    ax = plot_cell_communication(adata,
                                 database_name='tmp',
                                 pathway_name='tmp',
                                 lr_pair=None,
                                 plot_method=plot_method,
                                 background=background,
                                 background_legend=background_legend,
                                 clustering=clustering,
                                 summary=summary,
                                 cmap=cmap,
                                 cluster_cmap=cluster_cmap,
                                 pos_idx=pos_idx,
                                 ndsize=ndsize,
                                 scale=scale,
                                 normalize_v=normalize_v,
                                 normalize_v_quantile=normalize_v_quantile,
                                 arrow_color=arrow_color,
                                 grid_density=grid_density,
                                 grid_knn=grid_knn,
                                 grid_scale=grid_scale,
                                 grid_thresh=grid_thresh,
                                 grid_width=grid_width,
                                 stream_density=stream_density,
                                 stream_linewidth=stream_linewidth,
                                 stream_cutoff_perc=stream_cutoff_perc,
                                 filename=filename,
                                 alpha_img=alpha_img,
                                 **kwargs
                                 )
    tmp_list = ['SpaGRD-tmp-sum-sender', 'SpaGRD-tmp-sum-receiver',
                'SpaGRD_sender_vf-tmp-tmp', 'SpaGRD_receiver_vf-tmp-tmp']
    for tmp in tmp_list:
        adata.obsm.pop(tmp)
    adata.obsp.pop('SpaGRD-tmp-tmp')

    ax.figure.show()
    if return_fig:
        return ax


def umap_lr_module(adata,
                   palette=None,
                   return_fig=False):
    plt.style.use("default")
    plot_df = pd.concat((adata.uns['lr_module_info']['lr_module_df'],
                         adata.uns['lr_module_info']['lr_umap_df']),
                        axis=1)
    if palette:
        palette = sns.color_palette("palette")
    elif plot_df['module'].cat.categories.size <= 20:
        palette = sns.color_palette("tab20")
    else:
        palette = sns.color_palette("husl")
    plt.figure(figsize=(5.5, 4.8))
    sns.scatterplot(data=plot_df,
                    x="UMAP_1",
                    y="UMAP_2",
                    hue="module",
                    palette=palette,
                    s=40, edgecolor="black", linewidth=0.1, alpha=0.85)

    sns.despine()
    plt.xlabel("UMAP_1", fontsize=12)
    plt.ylabel("UMAP_2", fontsize=12)
    plt.legend(title="LR Module", fontsize=12, title_fontsize=12,
               loc="center left", bbox_to_anchor=(0.98, 0.5), frameon=False)
    plt.grid(False)
    plt.tight_layout()
    ax = plt.gca()
    plt.show()
    if return_fig:
        return ax


def binary_lr_module(adata,
                     lr_module,
                     spot_size=None,
                     img_key=None,
                     return_fig=False,
                     **kwargs):
    plot_df = adata.uns['lr_module_info']['module_binary_df']
    adata.obs['lr_module_plot'] = plot_df[f'module_{lr_module}']
    adata.uns['lr_module_plot_colors'] = ["#D3D8D6", "#FF6879"]
    if return_fig:
        ax = sc.pl.spatial(adata, color='lr_module_plot', img_key=img_key, return_fig=return_fig,
                           spot_size=spot_size, title=f'LR Module {lr_module}', **kwargs)
        return ax
    else:
        sc.pl.spatial(adata, color='lr_module_plot', img_key=img_key, spot_size=spot_size,
                      title=f'LR Module {lr_module}', **kwargs)
