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

def behaviors_distribution(df,filepath):
    if filepath:
        import matplotlib
        matplotlib.use('agg')
        
        from matplotlib import pyplot as plt
    
    import seaborn as sns
    
    cols = ["known_eq","index"]
    rcols = ["Logical networks", "Input-Output behaviors"]
    sort_cols = ["known_eq"]
    
    if "mse" in df.columns:
        cols.append("mse")
        rcols.append("MSE")
        sort_cols = ["mse"] + sort_cols
        
        df.mse = df.mse.map(lambda f: "%.4f" % f)
    
    df = df.sort_values(sort_cols).reset_index(drop=True).reset_index(level=0)[cols]
    df.known_eq = df.known_eq + 1
    df.index = df.index + 1
    
    df.columns = rcols
    
    if "MSE" in df.columns:
        g = sns.factorplot(x='Input-Output behaviors', y='Logical networks', hue='MSE', data=df, aspect=3, kind='bar', legend_out=False)
    else:
        g = sns.factorplot(x='Input-Output behaviors', y='Logical networks', data=df, aspect=3, kind='bar', legend_out=False)
    
    g.ax.set_xticks([])
    if filepath:    
        g.savefig(os.path.join(filepath,'behaviors-distribution.pdf'))
    
    return g
    