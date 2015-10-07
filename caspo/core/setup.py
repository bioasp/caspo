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

import gringo

from clamping import Clamping

class Setup(object):
    def __init__(self, stimuli, inhibitors, readouts):
        self.stimuli = stimuli
        self.inhibitors = inhibitors
        self.readouts = readouts
        
    @property
    def nodes(self):
        return frozenset(self.stimuli + self.inhibitors + self.readouts)
        
    def clampings_iter(self, cues=None):
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
        fs = set((gringo.Fun('stimulus',[str(var)]) for var in self.stimuli))
        fs = fs.union((gringo.Fun('inhibitor',[str(var)]) for var in self.inhibitors))
        fs = fs.union((gringo.Fun('readout',[str(var)]) for var in self.readouts))
        
        return fs
        
    @classmethod
    def from_json(klass, filename):
        with open(filename) as fp:
            raw = json.load(fp)
        
        return klass(raw['stimuli'],raw['inhibitors'],raw['readouts'])
        
    def to_json(self, filename):
        with open(filename, 'w') as fp:
            json.dump(dict(stimuli=self.stimuli, inhibitors=self.inhibitors, readouts=self.readouts), fp)
            
    def __len__(self):
        return len(self.stimuli + self.inhibitors + self.readouts)
        