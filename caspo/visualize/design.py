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

def experimental_designs(df,filepath):
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

def differences_distribution(df, filepath):    
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
    