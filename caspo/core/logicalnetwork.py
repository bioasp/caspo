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
import numpy as np

from sklearn.metrics import mean_squared_error

import gringo

from literal import Literal
from clause import Clause
from graph import Graph
from hypergraph import HyperGraph

class LogicalNetworkList(object):
    
    def __init__(self, hypergraph, matrix, known_eq=None):
        self.matrix = matrix
        self.hg = hypergraph
        self.known_eq = known_eq or [0]*len(matrix)
         
    @classmethod    
    def from_csv(klass, filename):
        df = pd.read_csv(filename)
        
        edges = set()
        mappings = []
        for mapping in df.columns:
            clause_str, target = mapping.split('=')
            clause = Clause.from_str(clause_str)
            mappings.append((clause, target))
            for source, sign in clause:
                edges.add((source,target,sign))
                
        graph = Graph.from_tuples(edges)
        hypergraph = HyperGraph.from_graph(graph)
        hypergraph.mappings = pd.Series(mappings)
                
        return klass(hypergraph, df.values)
        
    @classmethod    
    def from_hypergraph(klass, hypergraph, networks=[]):
        if networks:
            matrix = np.array([networks[0].to_array(hypergraph.mappings)])
            known_eq = [networks[0].graph['known_eq']]
            for network in networks[1:]:
                matrix = np.append(matrix, [network.to_array(hypergraph.mappings)], axis=0)
                known_eq.append(network.graph['known_eq'])
        else:
            matrix = np.array([])
                
        return klass(hypergraph, matrix)
        
    def split(self, indices):
        return map(lambda part: LogicalNetworkList(self.hg, part), np.split(self.matrix, indices))
        
    def union(self, other):
        if len(other) == 0:
            return self
        elif len(self) == 0:
            return other
        else:
            return LogicalNetworkList(self.hg, np.append(self.matrix, other.matrix, axis=0), self.known_eq + other.known_eq)
        
    def append(self, network):
        arr = network.to_array(self.hg.mappings)
        if len(self.matrix):
            self.matrix = np.append(self.matrix, [arr], axis=0)
            self.known_eq.append(network.graph['known_eq'])
        else:
            self.matrix = np.array([arr])
            self.known_eq = [network.graph['known_eq']]
        
    def __len__(self):
        return len(self.matrix)
        
    def __iter__(self):
        for i,arr in enumerate(self.matrix):
            yield LogicalNetwork(it.imap(lambda m: (m[0],m[1]), self.hg.mappings.values[np.where(arr==1)]), known_eq=self.known_eq[i])
        
    def to_funset(self):
        fs = set((gringo.Fun("variable", [var]) for var in self.hg.nodes['name'].values))
        
        formulas = set()
        for network in self:
            formulas = formulas.union(it.imap(lambda (_,f): f, network.formulas_iter()))
            
        formulas = pd.Series(list(formulas))
        
        for i,network in enumerate(self):
            for v,f in network.formulas_iter():
                fs.add(gringo.Fun("formula", [i, v, formulas[formulas==f].index[0]]))
        
        for formula_idx,formula in formulas.iteritems():
            for clause in formula:
                clause_idx = self.hg.clauses_idx[clause]
                fs.add(gringo.Fun("dnf",[formula_idx, clause_idx]))
                for variable, sign in clause:
                    fs.add(gringo.Fun("clause", [clause_idx, variable, sign]))

        return fs
        
    def to_dataframe(self, known_eq=False, dataset=None, size=False):
        length = len(self)
        df = pd.DataFrame(self.matrix, columns=map(lambda (c,t): "%s=%s" % (c,t), self.hg.mappings))
        
        if known_eq:
            df = pd.concat([df,pd.DataFrame({'known_eq': self.known_eq})], axis=1)
            
        if dataset:
            clampings = dataset.clampings
            columns = dataset.readouts.columns
            readouts = dataset.readouts.values
            pos = ~np.isnan(readouts)
            mse_iter = (mean_squared_error(readouts[pos], (n.predictions(clampings, columns).values)[pos]) for n in self)
            df = pd.concat([df,pd.DataFrame({'mse': np.fromiter(mse_iter, float, length)})], axis=1)
            
        if size:
            df = pd.concat([df,pd.DataFrame({'size': np.fromiter((n.size for n in self), int, length)})], axis=1) 
            
        return df
        
    def to_csv(self, filename, known_eq=False, dataset=None, size=False):
        self.to_dataframe(known_eq, dataset, size).to_csv(filename, index=False)
        
class LogicalNetwork(nx.DiGraph):
                
    @classmethod
    def from_hypertuples(klass, hg, tuples):
        return klass(map(lambda (i,j): (hg.clauses[j], hg.variable(i)), tuples), known_eq=0)

    def to_graph(self):
        edges = set()
        for clause,target in self.edges_iter():
            for source,signature in clause:
                edges.add((source,target,signature))
                
        return Graph.from_tuples(edges)
      
    @property  
    def size(self):
        return sum(map(lambda (c,t): len(c), self.edges_iter()))
        
    def step(self, state, clamping):
        ns = state.copy()
        for var in state:
            if clamping.has_variable(var):
                ns[var] = int(clamping.bool(var))
            else:
                or_value = 0
                for clause, _ in self.in_edges_iter(var):
                    or_value = or_value or clause.bool(state)
                    if or_value: break
                
                ns[var] = or_value
    
        return ns
        
    def fixpoint(self, clamping, steps=0):
        current = dict.fromkeys(self.variables(),0)
        updated = self.step(current, clamping)
        steps -= 1
        while current != updated and steps != 0:
            current = updated
            updated = self.step(current, clamping)
        
        return current
        
    def predictions(self, clampings, readouts):
        predictions = np.zeros((len(clampings), len(readouts)))
        for i, clamping in enumerate(clampings):
            fixpoint = self.fixpoint(clamping)
            for j, readout in enumerate(readouts):
                predictions[i][j] = fixpoint.get(readout,0)

        return pd.DataFrame(predictions, columns=readouts)
    
    def variables(self):
        variables = set()
        for v in self.nodes_iter():
            if isinstance(v, Clause):
                for l in v:
                    variables.add(l.variable)
            else:
                variables.add(v)
        return variables
    
    def formulas_iter(self):
        for var in it.ifilter(lambda v: self.has_node(v), self.variables()):
            yield var, frozenset(self.predecessors(var))
            
    def to_array(self, mappings):
        arr = np.zeros(len(mappings), np.int8)
        for i, (clause, target) in mappings.iteritems():
            if self.has_edge(clause, target):
                arr[i] = 1
                
        return arr