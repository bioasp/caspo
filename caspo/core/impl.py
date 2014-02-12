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

from collections import defaultdict, namedtuple
from itertools import chain, combinations
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
        return "+".join(map(str, self))
        
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
                
            return value        

class LogicalNetworkSet(set):
    interface.implements(ILogicalNetworkSet)

class BooleLogicNetworkSet(LogicalNetworkSet):
    interface.implements(IBooleLogicNetworkSet)

class Clamping(frozenset):
    interface.implements(IClamping)
    
    def __init__(self, literals=[]):
        super(Clamping, self).__init__(frozenset(literals))
        
from zope import component

from interfaces import *

class TimePoint(object):
    interface.implements(ITimePoint)
    
    def __init__(self, time):
        self.time = time

