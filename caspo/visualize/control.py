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

def intervention_strategies(df,filepath):
    if filepath:
        import matplotlib
        matplotlib.use('agg')
        
        from matplotlib import pyplot as plt
    
    import seaborn as sns

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

    