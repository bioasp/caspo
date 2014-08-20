# Copyright (c) 2014, Santiago Videla
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

import numpy
from collections import defaultdict, namedtuple
from itertools import chain, combinations
from zope import component
from interfaces import *

class Graph(object):
    interface.implements(IGraph)
    
    def __init__(self, nodes=[], edges=[]):
        self.nodes = set(nodes)
        self.edges = set(edges)
        
    def predecessors(self, node):
        return iter(map(lambda (source, target, sign): (source, sign), 
            filter(lambda (source, target, sign): target == node, self.edges)))

class Setup(object):
    interface.implements(ISetup)
    
    def __init__(self, stimuli, inhibitors, readouts):
        self.stimuli = stimuli
        self.inhibitors = inhibitors
        self.readouts = readouts
        
    def iterclampings(self, cues=None):
        s = cues or list(self.stimuli + self.inhibitors)
        it = chain.from_iterable(combinations(s, r) for r in xrange(len(s) + 1))

        literals_tpl = {}
        for stimulus in self.stimuli:
            literals_tpl[stimulus] = -1
        
        for c in it:
            literals = literals_tpl.copy() 
            for cues in c:
                if cues in self.stimuli:
                    literals[cues] = 1
                else:
                    literals[cues] = -1
                    
            yield Clamping(literals.iteritems())

class LogicalHeaderMapping(list):
    interface.implements(ILogicalHeaderMapping)
    
class LogicalMapping(dict):
    interface.implements(ILogicalMapping)
    
    @property
    def mapping(self):
        return self
    
class Literal(namedtuple('Literal', ['variable', 'signature'])):
    interface.implements(ILiteral)
    def __str__(self):
        if self.signature == 1:
            return self.variable
        else:
            return '!' + self.variable
    
    @classmethod     
    def from_str(cls, string):
        if string[0] == '!':
            signature = -1
            variable = string[1:]
        else:
            signature = 1
            variable = string
            
        return cls(variable, signature)
        
class Clause(frozenset):
    interface.implements(IClause)
    
    def __init__(self, literals=[]):
        super(Clause, self).__init__(frozenset(literals))
        
    def __str__(self):
        return "+".join(map(str, sorted(self)))
        
    @classmethod
    def from_str(cls, string):
        return cls(map(lambda lit: Literal.from_str(lit), string.split('+')))

class LogicalNetwork(object):
    interface.implements(ILogicalNetwork)
    
    def __init__(self, variables=[], mapping=None):
        self.variables = variables
        self.mapping = {}
        if mapping:
            for v, f in mapping.iteritems():
                self.mapping[v] = frozenset(f)
                
    def __len__(self):
        return sum(chain.from_iterable(map(lambda f: map(len, f), self.mapping.values())))
                
class BooleLogicNetwork(LogicalNetwork):
    interface.implements(IBooleLogicNetwork)
    
    def prediction(self, var, clamping):
        dc = dict(clamping)
        if var in dc:
            return (dc[var] == 1 and 1) or 0
        elif var not in self.mapping:
            return 0
        else:
            value = 0
            for clause in self.mapping[var]:
                cv = 1
                for src, sign in clause:
                    if sign == 1:
                        cv = cv and self.prediction(src, clamping)
                    else:
                        cv = cv and not self.prediction(src, clamping)
                
                    if not cv:
                        break
                    
                value = value or cv
                if value:
                    break
                
            return int(value)
            
            
    def mse(self, dataset, time):
        predictions = numpy.empty((dataset.nexps, len(dataset.setup.readouts)))
        observations = numpy.empty((dataset.nexps, len(dataset.setup.readouts)))
        predictions[:] = numpy.nan
        observations[:] = numpy.nan
        for i, cond, obs in dataset.at(time):
            for j, (var, val) in enumerate(obs.iteritems()):
                predictions[i][j] = self.prediction(var, cond)
                observations[i][j] = val
        
        rss = numpy.nansum((predictions - observations) ** 2)
        return rss / dataset.nobs[time]

class LogicalNetworkSet(set):
    interface.implements(ILogicalNetworkSet)
    
    def __init__(self, networks=[], update_names=True):
        super(LogicalNetworkSet, self).__init__(networks)
        if update_names:
            names = component.getUtility(ILogicalNames)
            for network in networks:
                names.add(network.mapping.itervalues())
    
    def add(self, network, update_names=True):
        super(LogicalNetworkSet, self).add(network)
        if update_names:
            names = component.getUtility(ILogicalNames)
            names.add(network.mapping.itervalues())

class BooleLogicNetworkSet(LogicalNetworkSet):
    interface.implements(IBooleLogicNetworkSet)
    
    def itermses(self, dataset, time):
        predictions = numpy.empty((dataset.nexps, len(dataset.setup.readouts)))
        observations = numpy.empty((dataset.nexps, len(dataset.setup.readouts)))

        observations[:] = numpy.nan
        for i, cond, obs in dataset.at(time):
            for j, (var, val) in enumerate(obs.iteritems()):
                observations[i][j] = val
                
        for network in self:
            predictions[:] = numpy.nan
            for i, cond, obs in dataset.at(time):
                for j, (var, val) in enumerate(obs.iteritems()):
                    predictions[i][j] = network.prediction(var, cond)
        
            rss = numpy.nansum((predictions - observations) ** 2)
            yield network, rss / dataset.nobs[time]

class Clamping(frozenset):
    interface.implements(IClamping)
    
    def __init__(self, literals=[]):
        super(Clamping, self).__init__(frozenset(literals))

class TimePoint(object):
    interface.implements(ITimePoint)
    
    def __init__(self, time):
        self.time = time

class Length(object):
    interface.implements(ILength)
    
    def __init__(self, length):
        self.length = length
        
