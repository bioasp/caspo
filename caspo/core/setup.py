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

import json
import itertools as it
import numpy as np

import gringo

from clamping import Clamping

class Setup(object):
    """
    Experimental setup describing stimuli, inhibitors and readouts species names
    """
    def __init__(self, stimuli, inhibitors, readouts):
        self.stimuli = list(stimuli)
        self.inhibitors = list(inhibitors)
        self.readouts = list(readouts)
        
    @property
    def nodes(self):
        """
        Returns unique species names in the experimental setup
        
        :return: species names
        :rtype: :class:`frozenset`
        """
        return frozenset(self.stimuli + self.inhibitors + self.readouts)
        
    def clampings_iter(self, cues=None):
        """
        Iterator over clampings
        
        :param cues: optionally restrict clampings over a given iterable of species names
        :return: iterator over all possible clampings
        :rtype: iterator
        """
        s = cues or list(self.stimuli + self.inhibitors)
        clampings = it.chain.from_iterable(it.combinations(s,r) for r in xrange(len(s) + 1))

        literals_tpl = {}
        for stimulus in self.stimuli:
            literals_tpl[stimulus] = -1
        
        for c in clampings:
            literals = literals_tpl.copy() 
            for cues in c:
                if cues in self.stimuli:
                    literals[cues] = 1
                else:
                    literals[cues] = -1
                    
            yield Clamping(literals.iteritems())

    def to_funset(self):
        """
        Converts the experimental setup to a set of :class:`gringo.Fun` instances
        
        :return: the set of gringo.Fun instances
        :rtype: :class:`set`
        """
        fs = set((gringo.Fun('stimulus',[str(var)]) for var in self.stimuli))
        fs = fs.union((gringo.Fun('inhibitor',[str(var)]) for var in self.inhibitors))
        fs = fs.union((gringo.Fun('readout',[str(var)]) for var in self.readouts))
        
        return fs
        
    @classmethod
    def from_json(klass, filename):
        """
        Creates a Setup instance from a JSON file like:
    
        >>> {"stimuli": ["egf", "tnfa", ...], 
        ...  "inhibitors": ["pi3k", "raf1", ...], 
        ...  "readouts": ["raf1", "erk", "ap1", ...]}
        
        :param klass: :class:`caspo.core.Setup`
        :param filename: absolute path to JSON file
        :return: created object instance
        :rtype: :class:`caspo.core.Setup`
        """
        with open(filename) as fp:
            raw = json.load(fp)
        
        return klass(raw['stimuli'],raw['inhibitors'],raw['readouts'])
        
    def to_json(self, filename):
        """
        Writes the experimental setup to a JSON file
        
        :param filename: absolute path where to write the JSON file
        """
        with open(filename, 'w') as fp:
            json.dump(dict(stimuli=self.stimuli, inhibitors=self.inhibitors, readouts=self.readouts), fp)
            
    def filter(self, networks):
        """
        Returns a new experimental setup restricted to species active in the given networks
        
        :param networks: list of networks :class:`caspo.core.LogicalNetworkList`
        :return: restricted setup
        :rtype: :class:`caspo.core.Setup`
        """
        cues = self.stimuli + self.inhibitors
        active_cues = set()
        active_readouts = set()
        mappings = np.unique(networks.hg.mappings.values[np.where(networks.matrix==1)[1]])
        for clause,var in mappings:
            active_cues = active_cues.union((l for (l,s) in clause if l in cues))
            if var in self.readouts:
                active_readouts.add(var)
            
        return Setup(active_cues.intersection(self.stimuli), active_cues.intersection(self.inhibitors), active_readouts)
        
    def cues(self, rename_inhibitors=False):
        """
        Returns stimuli and inhibitors species
        
        :param rename_inhibitors: whether to end inhibitors with 'i' or not. Default to False
        :return: list of species names in order. Stimuli followed by inhibitors
        :rtype: list
        """
        if rename_inhibitors:
            return self.stimuli + [i+'i' for i in self.inhibitors]
        else:
            return self.stimuli + self.inhibitors
            
    def __len__(self):
        return len(self.stimuli + self.inhibitors + self.readouts)
        