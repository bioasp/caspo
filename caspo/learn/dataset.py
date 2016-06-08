# Copyright (c) 2015, Santiago Videla
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
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

import gringo

from caspo import core

class Dataset(object):
    """
    A phospho-proteomics dataset
    """
    
    def __init__(self, midas, time):
        df = pd.read_csv(midas)

        times = np.unique(df.filter(regex='^DA').values.flatten())
        if time not in times:
            raise ValueError("The time-point %s does not exists in the dataset. Available time-points are: %s" % (time, list(times)))
        
        df.drop(df.columns[0], axis=1, inplace=True)
        self.df = df.filter(regex='^TR').drop_duplicates()
        
        clampings = []
        for i, row in self.df.iterrows():
            literals = []
            for v,s in row.iteritems():
                if self.is_stimulus(v):
                    literals.append(core.Literal(v[3:], 1 if s == 1 else -1))
                else:
                    if s == 1:
                        literals.append(core.Literal(v[3:-1], -1))
                        
            clampings.append(core.Clamping(literals))
            
        self.df = pd.concat([self.df, pd.Series(clampings, name='Clamping')], axis=1)
        
        for col in filter(lambda c: c.startswith('DA'), df.columns):
            self.df = pd.concat([self.df, df[df[col]==time][[col.replace('DA','DV')]].reset_index(drop=True)], axis=1)
        
        stimuli = map(lambda c: c[3:], filter(lambda c: self.is_stimulus(c), self.df.columns))
        inhibitors = map(lambda c: c[3:-1], filter(lambda c: self.is_inhibitor(c), self.df.columns))
        readouts = map(lambda c: c[3:], filter(lambda c: self.is_readout(c), self.df.columns))
        
        self.setup = core.Setup(stimuli, inhibitors, readouts)
        
    @property
    def clampings(self):
        return core.ClampingList(self.df['Clamping'])
                
    @property
    def readouts(self):
        return self.df.filter(regex='^DV').rename(columns=lambda c: c[3:]).astype(float)
    
    def is_stimulus(self, name):
        return name.startswith('TR') and not name.endswith('i')
        
    def is_inhibitor(self, name):
        return name.startswith('TR') and name.endswith('i')
        
    def is_readout(self, name):
        return name.startswith('DV')
        
    def to_funset(self, discrete):
        fs = self.clampings.to_funset("exp")
        fs = fs.union(self.setup.to_funset())
        
        for i,row in self.readouts.iterrows():
            for var,val in row.iteritems():
                try:
                    if not np.isnan(val):
                        fs.add(gringo.Fun('obs',[i,var,discrete(val)]))
                except Exception, e:
                    print val
                    import pdb;pdb.set_trace()
                    raise e
        
        return fs
