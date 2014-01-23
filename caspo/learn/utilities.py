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

import csv, math
from collections import defaultdict
from zope import component

from interfaces import *

class MidasReader(core.FileReader):
    interface.implements(IMidasReader)
    
    def read(self, filename):
        super(MidasReader, self).read(filename)
        self.reader = csv.DictReader(self.fd)
        
        #Header without the CellLine column
        species = self.reader.fieldnames[1:]
    
        self.stimuli = map(lambda name: name[3:], filter(lambda name: name.startswith('TR:') and not name.endswith('i'), species))
        self.inhibitors = map(lambda name: name[3:-1], filter(lambda name: name.startswith('TR:') and name.endswith('i'), species))
        self.readouts = map(lambda name: name[3:], filter(lambda name: name.startswith('DV:'), species))
        
        self.__cues = []
        self.__data = []
        cond = {}
        for row in self.reader:
            cond = {}
            for s in self.stimuli:
                cond[s] = int(row['TR:' + s] or 0)
            for i in self.inhibitors:
                cond[i] = (int(row['TR:' + i + 'i'] or 0) + 1) % 2

            obs = defaultdict(dict)
            for r in self.readouts:
                if not math.isnan(float(row['DV:' + r])):
                    obs[int(row['DA:' + r])][r] = float(row['DV:' + r])
                    
            if cond in self.__cues:
                index = self.__cues.index(cond)
                self.__data[index].update(obs)
            else:
                self.__cues.append(cond)
                self.__data.append(obs)
    
    def __iter__(self):
        return iter(zip(self.__cues, self.__data))

class Discretization(object):
    factor = 1

class Round(Discretization):
    interface.implements(IDiscretization)
    
    def __call__(self, data):
        return int(round(data * self.factor))

class Floor(Discretization):
    interface.implements(IDiscretization)
    
    def __call__(self, data):
        return int(math.floor(data * self.factor))

class Ceil(Discretization):
    interface.implements(IDiscretization)
    
    def __call__(self, data):
        return int(math.ceil(data * self.factor))
        
class DefaultCompressor(object):
    interface.implements(IGraphCompressor)
    
    def compress(self, graph, setup):
        self.pos_forward = defaultdict(set)
        self.pos_backward = defaultdict(set)
        self.neg_forward = defaultdict(set)
        self.neg_backward = defaultdict(set)

        designated = setup.stimuli + setup.inhibitors + setup.readouts
        marked = graph.nodes.difference(designated)
    
        for source,target,sign in graph.edges:
            if sign == 1:
                self.pos_forward[source].add(target)
                self.pos_backward[target].add(source)
            else:
                self.neg_forward[source].add(target)
                self.neg_backward[target].add(source)

        rnodes = self.reduce(marked)
        
        edges = set()
        for source, targets in self.pos_forward.iteritems():
            for target in targets:
                edges.add((source, target, 1))
    
        for source, targets in self.neg_forward.iteritems():
            for target in targets:
                edges.add((source, target, -1))
                
        return core.Graph(graph.nodes.difference(rnodes), edges)
        
    def reduce(self, marked, removed=set()):
        iremoved = set()

        for node in marked:
            backward = self.pos_backward[node].union(self.neg_backward[node])
            forward = self.pos_forward[node].union(self.neg_forward[node])
            if len(backward) <= 1 and len(backward.difference(forward)) > 0:
                self.remove(node)
                iremoved.add(node)
            
            elif len(forward) <= 1 and len(forward.difference(backward)) > 0:
                self.remove(node)
                iremoved.add(node)
            
        if not iremoved:
            return removed
        else:
            return self.reduce(marked.difference(iremoved), removed.union(iremoved))
            
    def remove(self, node):
        
        for source in self.pos_backward[node]:
            
            if node in self.pos_forward[source]:
                self.pos_forward[source].remove(node)
                
            if node in self.neg_forward[source]:
                self.neg_forward[source].remove(node)
        
            self.pos_forward[source] = self.pos_forward[source].union(self.pos_forward[node])
            self.neg_forward[source] = self.neg_forward[source].union(self.neg_forward[node])

        for source in self.neg_backward[node]:
            
            if node in self.pos_forward[source]:
                self.pos_forward[source].remove(node)
                
            if node in self.neg_forward[source]:
                self.neg_forward[source].remove(node)
            
            self.neg_forward[source] = self.neg_forward[source].union(self.pos_forward[node])
            self.pos_forward[source] = self.pos_forward[source].union(self.neg_forward[node])

        for target in self.pos_forward[node]:
            
            if node in self.pos_backward[target]:
                self.pos_backward[target].remove(node)
                
            if node in self.neg_backward[target]:
                self.neg_backward[target].remove(node)
            
            self.pos_backward[target] = self.pos_backward[target].union(self.pos_backward[node])
            self.neg_backward[target] = self.neg_backward[target].union(self.neg_backward[node])
    
        for target in self.neg_forward[node]:
            
            if node in self.pos_backward[target]:
                self.pos_backward[target].remove(node)
            if node in self.neg_backward[target]:
                self.neg_backward[target].remove(node)
            
            self.neg_backward[target] = self.neg_backward[target].union(self.pos_backward[node])
            self.pos_backward[target] = self.pos_backward[target].union(self.neg_backward[node])
    
        del self.pos_forward[node]
        del self.neg_forward[node]
        del self.pos_backward[node]
        del self.neg_backward[node]
        