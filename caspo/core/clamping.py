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

import itertools as it

import numpy as np
import pandas as pd

import gringo

from literal import Literal

class ClampingList(pd.Series):
    
    def to_funset(self, lname="clamping", cname="clamped"):
        fs = set()
        for i, clamping in self.iteritems():
            fs.add(gringo.Fun(lname, [i]))
            fs = fs.union(clamping.to_funset(i,cname))

        return fs
        
    def to_dataframe(self, stimuli=[], inhibitors=[]):
        cues = stimuli + inhibitors
        nc = len(cues)
        ns = len(stimuli)
        
        variables = cues or np.array(list(set((v for (v,s) in it.chain.from_iterable(c)))))
            
        matrix = np.array([])
        for clamping in self:
            arr = clamping.to_array(variables)
            if nc > 0:
                arr[np.where(arr[:ns] == -1)[0]] = 0
                arr[ns + np.where(arr[ns:] == -1)[0]] = 1
            
            if len(matrix):
                matrix = np.append(matrix, [arr], axis=0)
            else:
                matrix = np.array([arr])

        return pd.DataFrame(matrix, columns=stimuli + [i+'i' for i in inhibitors] if nc > 0 else variables)
        
    def to_csv(self, filename, stimuli=[], inhibitors=[]):
        self.to_dataframe(stimuli, inhibitors).to_csv(filename, index=False)
        
    @classmethod
    def from_csv(klass, filename):
        df = pd.read_csv(filename)
        clampings = []
        for i,row in df.iterrows():
            clampings.append(Clamping(map(lambda (v,s): Literal(v,s), row[row!=0].iteritems())))
            
        return klass(clampings)

class Clamping(frozenset):
    
    @classmethod
    def from_tuples(klass, tuples):
        return klass(it.imap(lambda (v,s): Literal(v,s), tuples))
    
    def to_funset(self, index, name="clamped"):
        fs = set()
        for var, sign in self:
            fs.add(gringo.Fun(name, [index,var,sign]))
            
        return fs
                
    def bool(self, variable):
        return dict(self)[variable] == 1
        
    def has_variable(self, variable):
        return dict(self).has_key(variable)
        
    def to_array(self, variables):
        arr = np.zeros(len(variables), np.int8)
        dc = dict(self)
        
        for i,var in enumerate(variables):
            arr[i] = dc.get(var, arr[i])
            
        return arr
                