# Copyright (c) 2014-2016, Santiago Videla
#
# This file is part of caspo.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caspo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
import os, logging
import matplotlib
from matplotlib import pyplot as plt
from networkx.drawing.nx_pydot import write_dot
import numpy as np
import seaborn as sns

def coloured_network(network, setup, filename):
    """
    Plots a coloured (hyper-)graph to a dot file

    Parameters
    ----------
    network : object
        An object implementing a method `__plot__` which must return the `networkx.MultiDiGraph`_ instance to be coloured.
        Typically, it will be an instance of either :class:`caspo.core.graph.Graph`, :class:`caspo.core.logicalnetwork.LogicalNetwork`
        or :class:`caspo.core.logicalnetwork.LogicalNetworkList`

    setup : :class:`caspo.core.setup.Setup`
        Experimental setup to be coloured in the network


    .. _networkx.MultiDiGraph: https://networkx.readthedocs.io/en/stable/reference/classes.multidigraph.html#networkx.MultiDiGraph
    """
    NODES_ATTR = {
        'DEFAULT':   {'color': 'black', 'fillcolor': 'white', 'style': 'filled, bold', 'fontname': 'Helvetica', 'fontsize': 18, 'shape': 'ellipse'},
        'STIMULI':   {'color': 'olivedrab3', 'fillcolor': 'olivedrab3'},
        'INHIBITOR': {'color': 'orangered',  'fillcolor': 'orangered'},
        'READOUT':   {'color': 'lightblue',  'fillcolor': 'lightblue'},
        'INHOUT':    {'color': 'orangered',  'fillcolor': 'SkyBlue2', 'style': 'filled, bold, diagonals'},
        'GATE' :     {'fillcolor': 'black', 'fixedsize': True, 'width': 0.2, 'height': 0.2, 'label': '.'}
    }

    EDGES_ATTR = {
        'DEFAULT': {'dir': 'forward', 'penwidth': 2.5},
         1  : {'color': 'forestgreen', 'arrowhead': 'normal'},
        -1  : {'color': 'red', 'arrowhead': 'tee'}
    }

    graph = network.__plot__()

    for node in graph.nodes():
        _type = 'DEFAULT'
        for attr, value in NODES_ATTR[_type].items():
            graph.node[node][attr] = value

        if 'gate' in graph.node[node]:
            _type = 'GATE'
        elif node in setup.stimuli:
            _type = 'STIMULI'
        elif node in setup.readouts and node in setup.inhibitors:
            _type = 'INHOUT'
        elif node in setup.readouts:
            _type = 'READOUT'
        elif node in setup.inhibitors:
            _type = 'INHIBITOR'

        if _type != 'DEFAULT':
            for attr, value in NODES_ATTR[_type].items():
                graph.node[node][attr] = value

    for source, target in graph.edges():
        for k in graph.edge[source][target]:
            for attr, value in EDGES_ATTR['DEFAULT'].items():
                graph.edge[source][target][k][attr] = value

            for attr, value in EDGES_ATTR[graph.edge[source][target][k]['sign']].items():
                graph.edge[source][target][k][attr] = value

            if 'weight' in graph.edge[source][target][k]:
                graph.edge[source][target][k]['penwidth'] = 5 * graph.edge[source][target][k]['weight']

    write_dot(graph, filename)


def networks_distribution(df, filepath=None):
    """
    Generates two alternative plots describing the distribution of
    variables `mse` and `size`. It is intended to be used over a list
    of logical networks.


    Parameters
    ----------
    df: `pandas.DataFrame`_
        DataFrame with columns `mse` and `size`

    filepath: str
        Absolute path to a folder where to write the plots


    Returns
    -------
    tuple
        Generated plots


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """

    df.mse = df.mse.map(lambda f: "%.4f" % f)

    g = sns.JointGrid(x="mse", y="size", data=df)

    g.plot_joint(sns.violinplot, scale='count')
    g.ax_joint.set_yticks(range(df['size'].min(),df['size'].max() + 1))
    g.ax_joint.set_yticklabels(range(df['size'].min(),df['size'].max() + 1))

    for tick in g.ax_joint.get_xticklabels():
        tick.set_rotation(90)

    g.ax_joint.set_xlabel("MSE")
    g.ax_joint.set_ylabel("Size")

    for i,t in enumerate(g.ax_joint.get_xticklabels()):
        c = df[df['mse'] == t.get_text()].shape[0]
        g.ax_marg_x.annotate(c, xy=(i,0.5), va="center", ha="center", size=20, rotation=90)

    for i,t in enumerate(g.ax_joint.get_yticklabels()):
        s = int(t.get_text())
        c = df[df['size'] == s].shape[0]
        g.ax_marg_y.annotate(c, xy=(0.5,s), va="center", ha="center", size=20)

    if filepath:
        g.savefig(os.path.join(filepath,'networks-distribution.pdf'))

    fig = plt.figure()
    counts = df[["size","mse"]].reset_index(level=0).groupby(["size","mse"], as_index=False).count()
    cp = counts.pivot("size","mse","index").sort_index()

    ax = sns.heatmap(cp, annot=True, fmt=".0f", linewidths=.5)
    ax.set_xlabel("MSE")
    ax.set_ylabel("Size")

    if filepath:
        plt.savefig(os.path.join(filepath,'networks-heatmap.pdf'))

    return g, ax

def mappings_frequency(df, filepath=None):
    """
    Plots the frequency of logical conjunction mappings

    Parameters
    ----------
    df: `pandas.DataFrame`_
        DataFrame with columns `frequency` and `mapping`

    filepath: str
        Absolute path to a folder where to write the plot


    Returns
    -------
    plot
        Generated plot


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """

    df = df.sort_values('frequency')
    df['conf'] = df.frequency.map(lambda f: 0 if f<0.2 else 1 if f<0.8 else 2)

    g = sns.factorplot(x="mapping", y="frequency", data=df, aspect=3, hue='conf', legend=False)
    for tick in g.ax.get_xticklabels():
        tick.set_rotation(90)

    g.ax.set_ylim([-.05,1.05])

    g.ax.set_xlabel("Logical mapping")
    g.ax.set_ylabel("Frequency")

    if filepath:
        g.savefig(os.path.join(filepath,'mappings-frequency.pdf'))

    return g

def behaviors_distribution(df, filepath=None):
    """
    Plots the distribution of logical networks across input-output behaviors.
    Optionally, input-output behaviors can be grouped by MSE.

    Parameters
    ----------
    df: `pandas.DataFrame`_
        DataFrame with columns `networks` and optionally `mse`

    filepath: str
        Absolute path to a folder where to write the plot

    Returns
    -------
    plot
        Generated plot


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """

    cols = ["networks","index"]
    rcols = ["Logical networks", "Input-Output behaviors"]
    sort_cols = ["networks"]

    if "mse" in df.columns:
        cols.append("mse")
        rcols.append("MSE")
        sort_cols = ["mse"] + sort_cols

        df.mse = df.mse.map(lambda f: "%.4f" % f)

    df = df.sort_values(sort_cols).reset_index(drop=True).reset_index(level=0)[cols]
    df.columns = rcols

    if "MSE" in df.columns:
        g = sns.factorplot(x='Input-Output behaviors', y='Logical networks', hue='MSE', data=df, aspect=3, kind='bar', legend_out=False)
    else:
        g = sns.factorplot(x='Input-Output behaviors', y='Logical networks', data=df, aspect=3, kind='bar', legend_out=False)

    g.ax.set_xticks([])
    if filepath:
        g.savefig(os.path.join(filepath,'behaviors-distribution.pdf'))

    return g

def experimental_designs(df, filepath=None):
    """
    For each experimental design it plot all the corresponding
    experimental conditions in a different plot

    Parameters
    ----------
    df: `pandas.DataFrame`_
        DataFrame with columns `id` and starting with `TR:`

    filepath: str
        Absolute path to a folder where to write the plot


    Returns
    -------
    list
        Generated plots


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """

    axes = []
    bw = matplotlib.colors.ListedColormap(['white','black'])
    cols = df.columns
    for i,dd in df.groupby("id"):
        cues = dd.drop(filter(lambda c: not c.startswith("TR:"), cols) + ["id"], axis=1).reset_index(drop=True)
        cues.columns = map(lambda c: c[3:], cues.columns)

        fig = plt.figure(figsize=(max((len(cues.columns)-1) * .5, 4), max(len(cues)*0.6,2.5)))

        ax = sns.heatmap(cues, linewidths=.5, cbar=False, cmap=bw, linecolor='gray')
        [t.set_color('r') if t.get_text().endswith('i') else t.set_color('g') for t in ax.xaxis.get_ticklabels()]

        ax.set_xlabel("Stimuli (green) and Inhibitors (red)")
        ax.set_ylabel("Experimental condition")

        plt.tight_layout()
        axes.append(ax)

        if filepath:
            plt.savefig(os.path.join(filepath,'design-%s.pdf' % i))

    return axes

def differences_distribution(df, filepath=None):
    """
    For each experimental design it plot all the corresponding
    generated differences in different plots

    Parameters
    ----------
    df: `pandas.DataFrame`_
        DataFrame with columns `id`, `pairs`, and starting with `DIF:`

    filepath: str
        Absolute path to a folder where to write the plots


    Returns
    -------
    list
        Generated plots


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """

    axes = []
    cols = df.columns
    for i,dd in df.groupby("id"):
        palette = sns.color_palette("Set1", len(dd))
        fig = plt.figure()

        readouts = dd.drop(filter(lambda c: not c.startswith("DIF:"), cols) + ["id"], axis=1).reset_index(drop=True)
        readouts.columns = map(lambda c: c[4:], readouts.columns)

        ax1 = readouts.T.plot(kind='bar', stacked=True, color=palette)

        ax1.set_xlabel("Readout")
        ax1.set_ylabel("Pairwise differences")
        plt.tight_layout()

        if filepath:
            plt.savefig(os.path.join(filepath,'design-%s-readouts.pdf' % i))

        fig = plt.figure()
        behaviors = dd[["pairs"]].reset_index(drop=True)
        ax2 = behaviors.plot.bar(color=palette, legend=False)

        ax2.set_xlabel("Experimental condition")
        ax2.set_ylabel("Pairs of input-output behaviors")
        plt.tight_layout()

        if filepath:
            plt.savefig(os.path.join(filepath,'design-%s-behaviors.pdf' % i))

        axes.append((ax1,ax2))

    return axes

def predictions_variance(df, filepath=None):
    """
    Plots the mean variance prediction for each readout

    Parameters
    ----------
    df: `pandas.DataFrame`_
        DataFrame with columns starting with `VAR:`

    filepath: str
        Absolute path to a folder where to write the plots


    Returns
    -------
    plot
        Generated plot


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """

    df = df.filter(regex="^VAR:")

    by_readout = df.mean(axis=0).reset_index(level=0)
    by_readout.columns=['Readout','Prediction variance (mean)']

    by_readout['Readout'] = by_readout.Readout.map(lambda n: n[4:])

    g1 = sns.factorplot(x='Readout', y='Prediction variance (mean)', data=by_readout, kind='bar', aspect=2)

    for tick in g1.ax.get_xticklabels():
        tick.set_rotation(90)

    if filepath:
        g1.savefig(os.path.join(filepath,'predictions-variance.pdf'))

    return g1


def intervention_strategies(df, filepath=None):
    """
    Plots all intervention strategies

    Parameters
    ----------
    df: `pandas.DataFrame`_
        DataFrame with columns starting with `TR:`

    filepath: str
        Absolute path to a folder where to write the plot


    Returns
    -------
    plot
        Generated plot


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """
    logger = logging.getLogger("caspo")

    LIMIT = 50
    if len(df) > LIMIT:
        logger.warning("Too many intervention strategies to visualize. A sample of %s strategies will be considered." % LIMIT)
        df = df.sample(LIMIT)

    values = np.unique(df.values.flatten())
    if len(values) == 3:
        rwg = matplotlib.colors.ListedColormap(['red','white','green'])
    elif 1 in values:
        rwg = matplotlib.colors.ListedColormap(['white','green'])
    else:
        rwg = matplotlib.colors.ListedColormap(['red','white'])

    fig = plt.figure(figsize=(max((len(df.columns)-1) * .5, 4), max(len(df)*0.6,2.5)))

    df.columns = map(lambda c: c[3:], df.columns)
    ax = sns.heatmap(df, linewidths=.5, cbar=False, cmap=rwg, linecolor='gray')

    ax.set_xlabel("Species")
    ax.set_ylabel("Intervention strategy")

    for tick in ax.get_xticklabels():
        tick.set_rotation(90)

    plt.tight_layout()

    if filepath:
        plt.savefig(os.path.join(filepath,'strategies.pdf'))

    return ax

def interventions_frequency(df, filepath=None):
    """
    Plots the frequency of occurrence for each intervention

    Parameters
    ----------
    df: `pandas.DataFrame`_
        DataFrame with columns `frequency` and `intervention`

    filepath: str
        Absolute path to a folder where to write the plot


    Returns
    -------
    plot
        Generated plot


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """

    df = df.sort_values('frequency')
    df['conf'] = df.frequency.map(lambda f: 0 if f<0.2 else 1 if f<0.8 else 2)

    g = sns.factorplot(x="intervention", y="frequency", data=df, aspect=3, hue='conf', legend=False)
    for tick in g.ax.get_xticklabels():
        tick.set_rotation(90)

    [t.set_color('r') if t.get_text().endswith('-1') else t.set_color('g') for t in g.ax.xaxis.get_ticklabels()]

    g.ax.set_ylim([-.05,1.05])

    g.ax.set_xlabel("Intervention")
    g.ax.set_ylabel("Frequency")

    if filepath:
        g.savefig(os.path.join(filepath,'interventions-frequency.pdf'))

    return g
