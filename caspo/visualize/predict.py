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
from matplotlib import pyplot as plt

import seaborn as sns

def predictions_variance(df, filepath=None):
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
    