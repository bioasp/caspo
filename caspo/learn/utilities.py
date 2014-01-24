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
        self._forward = defaultdict(set)
        self._backward = defaultdict(set)
        
        designated = setup.stimuli + setup.inhibitors + setup.readouts
        marked = graph.nodes.difference(designated)
    
        for source,target,sign in graph.edges:
            self._forward[source].add((target, sign))
            self._backward[target].add((source, sign))

        compressed = self.__compress(marked)

        edges = set()
        for source, targets in self._forward.iteritems():
            for target, sign in targets:
                edges.add((source, target, sign))
        
        return core.Graph(graph.nodes.difference(compressed), edges)
        
    def __compress(self, marked, compressed=set()):
        icompressed = set()

        for node in sorted(marked):
            backward = list(self._backward[node])
            forward = list(self._forward[node])
            
            if not backward or (len(backward) == 1 and not filter(lambda e: e[0] == backward[0][0], forward)):
                self.__merge_source_targets(node)
                icompressed.add(node)
            
            elif not forward or (len(forward) == 1 and not filter(lambda e: e[0] == forward[0][0], backward)):
                self.__merge_target_sources(node)
                icompressed.add(node)
            
        if icompressed:
            return self.__compress(marked.difference(icompressed), compressed.union(icompressed))
        else:
            return compressed
            
    def __merge_source_targets(self, node):
        source = None
        if self._backward[node]:
            source, sign = self._backward[node].pop()
            self._forward[source].remove((node, sign))
                
        for target,s in self._forward[node]:
            if source:
                self._forward[source].add((target, sign*s))
                self._backward[target].add((source, sign*s))
            
            self._backward[target].remove((node, s))
                    
        del self._forward[node]

    def __merge_target_sources(self, node):
        target = None
        if self._forward[node]:
            target, sign = self._forward[node].pop()
            self._backward[target].remove((node, sign))

        for source, s in self._backward[node]:
            if target:
                self._forward[source].add((target, sign*s))
                self._backward[target].add((source, sign*s))
                
            self._forward[source].remove((node, s))

        del self._backward[node]
