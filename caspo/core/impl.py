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
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-

from collections import defaultdict, namedtuple
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
        
class LogicalHeaderMapping(list):
    interface.implements(ILogicalHeaderMapping)

class LogicalMapping(dict):
    interface.implements(ILogicalMapping)
    
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
        self.mapping = mapping or defaultdict(set)

class Clamping(frozenset):
    interface.implements(IClamping)
    
    def __init__(self, literals=[]):
        super(Clamping, self).__init__(frozenset(literals))
