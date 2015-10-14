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
        if isinstance(known_eq, np.ndarray):
            self.known_eq = known_eq
        else:
            self.known_eq = np.array(known_eq or [0]*len(matrix))
            
         
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
        known_eq=None
        if networks:
            matrix = np.array([networks[0].to_array(hypergraph.mappings)])
            known_eq = [networks[0].graph['known_eq']]
            for network in networks[1:]:
                matrix = np.append(matrix, [network.to_array(hypergraph.mappings)], axis=0)
                known_eq.append(network.graph['known_eq'])
        else:
            matrix = np.array([])
                
        return klass(hypergraph, matrix, known_eq)
        
    def split(self, indices):
        return map(lambda part: LogicalNetworkList(self.hg, part), np.split(self.matrix, indices))
        
    def union(self, other):
        if len(other) == 0:
            return self
        elif len(self) == 0:
            return other
        else:
            return LogicalNetworkList(self.hg, np.append(self.matrix, other.matrix, axis=0), np.concatenate([self.known_eq,other.known_eq]))
        
    def append(self, network):
        arr = network.to_array(self.hg.mappings)
        if len(self.matrix):
            self.matrix = np.append(self.matrix, [arr], axis=0)
            self.known_eq = np.append(self.known_eq, network.graph['known_eq'])
        else:
            self.matrix = np.array([arr])
            self.known_eq = np.array([network.graph['known_eq']])
        
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
        
    def frequencies_iter(self):
        f = self.matrix.mean(axis=0)
        for i,m in self.hg.mappings.iteritems():
            if f[i] > 0:
                yield m,f[i]
            
    def frequency(self, mapping):
        m = self.hg.mappings[self.hg.mappings==mapping]
        if not m.empty:
            return self.matrix[:,m.index[0]].mean()
        else:
            raise ValueError("Mapping not found: %s" % mapping)
            
    def combinatorics(self):
        f = self.matrix.mean(axis=0)
        candidates = np.where((f < 1) & (f > 0))[0]
        exclusive, inclusive = defaultdict(set), defaultdict(set)
        for i,j in it.combinations(candidates, 2):
            xor = np.logical_xor(self.matrix[:,i],self.matrix[:,j])
            if xor.all():
                exclusive[self.hg.mappings[i]].add(self.hg.mappings[j])
                exclusive[self.hg.mappings[j]].add(self.hg.mappings[i])
                
            if (~xor).all():
                inclusive[self.hg.mappings[i]].add(self.hg.mappings[j])
                inclusive[self.hg.mappings[j]].add(self.hg.mappings[i])
                
        return exclusive, inclusive

    def variances(self, setup):
        stimuli, inhibitors, readouts = setup.stimuli, setup.inhibitors, setup.readouts
        cues = setup.cues()
        nc = len(cues)
        nclampings = 2**nc
        predictions = np.zeros((len(self), nclampings, len(setup)))
        
        clampings = list(setup.clampings_iter(cues))
        for i,network in enumerate(self):
            predictions[i,:,:] = network.predictions(clampings, readouts, stimuli, inhibitors).values

        weights = self.known_eq + 1
        avg = np.average(predictions[:,:,nc:], axis=0, weights=weights)
        var = np.average((predictions[:,:,nc:]-avg)**2, axis=0, weights=weights)
        
        cols = np.concatenate([setup.cues(True), readouts])
        return pd.DataFrame(np.concatenate([predictions[0,:,:nc],var], axis=1), columns=cols)
        
    def weighted_mse(self, dataset):
        eq = self.known_eq + 1
        predictions = np.zeros((len(self), len(dataset.clampings), len(dataset.setup.readouts)))
        for i,network in enumerate(self):
            predictions[i,:,:] = network.predictions(dataset.clampings, dataset.setup.readouts).values * eq[i]
        
        readouts = dataset.readouts.values
        pos = ~np.isnan(readouts)

        return mean_squared_error(readouts[pos], (np.sum(predictions, axis=0) / np.sum(eq))[pos])
        
    def __plot__(self):
        graph = nx.MultiDiGraph()
        n_gates = 1
        
        for clause,target in self.hg.mappings[np.unique(np.where(self.matrix==1)[1])]:
            graph.add_node(target)
            if len(clause) > 1:
                gate = 'gate-%s' % n_gates
                n_gates += 1
                graph.add_node(gate, gate=True)
                graph.add_edge(gate, target, sign=1, weight=self.frequency((clause, target)))
                
                for var,sign in clause:
                    graph.add_node(var)
                    graph.add_edge(var, gate, sign=sign, weight=self.frequency((clause, target)))
                    
            else:
                for var,sign in clause:
                    graph.add_node(var)
                    graph.add_edge(var, target, sign=sign, weight=self.frequency((clause, target)))
                    
        return graph
    
        
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
        
    def predictions(self, clampings, readouts, stimuli=[], inhibitors=[], nclampings=-1):
        cues = stimuli + inhibitors
        nc = len(cues)
        ns = len(stimuli)
        predictions = np.zeros((nclampings if nclampings > 0 else len(clampings), nc+len(readouts)), dtype=np.int8)
        for i, clamping in enumerate(clampings):
            if nc > 0:
                arr = clamping.to_array(cues)
                arr[np.where(arr[:ns] == -1)[0]] = 0
                arr[ns + np.where(arr[ns:] == -1)[0]] = 1
                predictions[i,:nc] = arr
            
            fixpoint = self.fixpoint(clamping)
            for j, readout in enumerate(readouts):
                predictions[i,nc+j] = fixpoint.get(readout,0)

        return pd.DataFrame(predictions, columns=np.concatenate([stimuli, [i+'i' for i in inhibitors], readouts]))
    
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
        
    def __plot__(self):
        graph = nx.MultiDiGraph()
        n_gates = 1
        for target, formula in self.formulas_iter():
            graph.add_node(target)
            for clause in formula:
                if len(clause) > 1:
                    gate = 'gate-%s' % n_gates
                    n_gates += 1
                    graph.add_node(gate, gate=True)
                    graph.add_edge(gate, target, sign=1)
                    
                    for var,sign in clause:
                        graph.add_node(var)
                        graph.add_edge(var, gate, sign=sign)
                else:
                    for var,sign in clause:
                        graph.add_node(var)
                        graph.add_edge(var, target, sign=sign)
                    
        return graph
        
