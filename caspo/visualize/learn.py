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
import os
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns

def networks_distribution(df, filepath=None):
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
    