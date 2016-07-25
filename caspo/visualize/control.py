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
import os, warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore"); 
    import matplotlib
    from matplotlib import pyplot as plt
    
import seaborn as sns

def intervention_strategies(df,filepath):
    rwg = matplotlib.colors.ListedColormap(['red','white','green'])
    fig = plt.figure(figsize=(max((len(df.columns)-1) * .5, 4), max(len(df)*0.6,2.5)))
    
    ax = sns.heatmap(df, linewidths=.5, cbar=False, cmap=rwg, linecolor='gray')
    
    ax.set_xlabel("Species")
    ax.set_ylabel("Intervention strategy")
    
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    
    plt.tight_layout()
    
    if filepath:
        plt.savefig(os.path.join(filepath,'strategies.pdf'))
        
    return ax
    
def interventions_frequency(df, filepath):
    df = df.sort_values('frequency')
    df['conf'] = df.frequency.map(lambda f: 0 if f<0.2 else 1 if f<0.8 else 2)

    g = sns.factorplot(x="intervention", y="frequency", data=df, aspect=3, hue='conf', legend=False)
    for tick in g.ax.get_xticklabels():
        tick.set_rotation(90)
    
    g.ax.set_ylim([-.05,1.05])
    
    g.ax.set_xlabel("Intervention")
    g.ax.set_ylabel("Frequency")
    
    if filepath:
        g.savefig(os.path.join(filepath,'interventions-frequency.pdf'))

    return g
    