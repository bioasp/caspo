# Copyright (c) 2014-2016, Santiago Videla
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
    """
    Hypergraph representation providing the link between logical networks and 
    the corresponding expanded prior knowledge network.
    
    Parameters
    ----------
    nodes : `pandas.Series`_
        Values in the Series correspond to variables names
    
    hyper : `pandas.Series`_
        Values in the Series correspond to the index in :attr:`nodes` (target node)
    
    edges : `pandas.DataFrame`_
        Hyperedges details as a DataFrame with columns `hyper_idx` (corresponds to the index in :attr:`hyper`), 
        `name` (source node), and `sign` (1 or -1)
    
    Attributes
    ----------
    nodes : `pandas.Series`_
    hyper : `pandas.Series`_
    edges : `pandas.DataFrame`_
    clauses : dict
        Mapping from hyperedge id (`hyper_idx`) to :class:`caspo.core.clause.Clause` object instance

    clauses_idx : dict
        The reverse of :attr:`clauses`
    
    mappings : `pandas.Series`_
        Series of tuples of the form (clause, variable)
    
    
    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    .. _pandas.Series: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#series
    """
    
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
        for node_idx, variable in self.nodes.iteritems():
            for hyper_idx,_ in self.hyper[self.hyper==node_idx].iteritems():
                mappings.append((self.clauses[hyper_idx], variable))
                
        self.mappings = pd.Series(mappings)
                
    def variable(self, index):
        """
        Returns the variable name for a given variable id
        
        Parameters
        ----------
        index : int
            Variable id
            
        Returns
        -------
        str
            Variable name
        """
        return self.nodes.iloc[index]
                        
    @classmethod
    def from_graph(klass, graph, length=0):
        """
        Creates a hypergraph (expanded graph) from a :class:`caspo.core.graph.Graph` object instance
        
        Parameters
        ----------
        graph : :class:`caspo.core.graph.Graph`
            The base interaction graph to be expanded
        
        length : int
            Maximum length for hyperedges source sets. If 0, use maximum possible in each case.
        
        Returns
        -------
        caspo.core.hypergraph.HyperGraph
            Created object instance
        """
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
                
        nodes = pd.Series(nodes, name='name')
        hyper = pd.Series(hyper, name='node_idx')
        edges = pd.DataFrame(edges)

        return klass(nodes, hyper, edges)
        
    def to_funset(self):
        """
        Converts the hypergraph to a set of `gringo.Fun`_ instances
        
        Returns
        -------
        set
            Representation of the hypergraph as a set of `gringo.Fun`_ instances
        
        
        .. _gringo.Fun: http://potassco.sourceforge.net/gringo.html#Fun
        """
        fs = set()        
        for i,n in self.nodes.iteritems():
            fs.add(gringo.Fun('node', [n,i]))
        
        for j,i in self.hyper.iteritems():
            fs.add(gringo.Fun('hyper', [i,j,len(self.edges[self.edges.hyper_idx==j])]))
        
        for j,v,s in self.edges.itertuples(index=False):
            fs.add(gringo.Fun('edge', [j,v,s]))
        
        return fs
        
