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

from collections import defaultdict

import itertools as it
import networkx as nx
import pandas as pd

import gringo

from literal import Literal
from clause import Clause

class HyperGraph(object):
    
    def __init__(self, nodes, hyper, edges):
        self.nodes = nodes
        self.hyper = hyper
        self.edges = edges
        
        self.clauses = {}
        self.clauses_idx = {}
        for i,h in self.edges.groupby('hyper_idx'):
            literals = map(lambda (_,source,sign): Literal(source,sign), h.itertuples(index=False))
            clause = Clause(literals)
            
            self.clauses[i] = clause
            self.clauses_idx[clause] = i
            
        mappings = []
        for node_idx, variable in self.nodes.itertuples():
            for hyper_idx,_ in self.hyper[self.hyper['node_idx']==node_idx].itertuples():
                mappings.append((self.clauses[hyper_idx], variable))
                
        self.mappings = pd.Series(mappings)
                
    def variable(self, index):
        return self.nodes.iloc[index]['name']
                        
    @classmethod
    def from_graph(klass, graph, length=0):
        nodes = []
        hyper = []
        edges = defaultdict(list)
        j = 0
        
        for i,node in enumerate(graph.nodes_iter()):
            nodes.append(node)

            preds = graph.in_edges(node, data=True)            
            l = len(preds)
            if length > 0:
                l = min(length, l)

            for literals in it.chain.from_iterable(it.combinations(preds, r+1) for r in xrange(l)):
                valid = defaultdict(int)
                for source,target,data in literals:
                    valid[source] += 1
                                        
                if all(it.imap(lambda c: c==1, valid.values())):
                    hyper.append(i)
                    for source,target,data in literals:
                        edges['hyper_idx'].append(j)
                        edges['name'].append(source)
                        edges['sign'].append(data['sign'])
            
                    j += 1
                
        nodes = pd.DataFrame(nodes, columns=['name'])
        hyper = pd.DataFrame(hyper, columns=['node_idx'])
        edges = pd.DataFrame(edges)

        return klass(nodes, hyper, edges)
        
    def to_funset(self):
        fs = set()        
        for i,n in self.nodes.itertuples():
            fs.add(gringo.Fun('node', [n,i]))
        
        for j,i in self.hyper.itertuples():
            fs.add(gringo.Fun('hyper', [i,j,len(self.edges[self.edges.hyper_idx==j])]))
        
        for j,v,s in self.edges.itertuples(index=False):
            fs.add(gringo.Fun('edge', [j,v,s]))
        
        return fs