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
import pandas as pd

import clingo

from .literal import Literal
from .clause import Clause
from .mapping import MappingList, Mapping

class HyperGraph(object):
    """
    Signed and directed hypergraph representation providing the link between logical networks and
    the corresponding expanded prior knowledge network.

    Parameters
    ----------
    nodes : `pandas.Series`_
        Values in the Series correspond to variables names

    hyper : `pandas.Series`_
        Values in the Series correspond to the index in attribute :attr:`nodes` (interpreted as the target node)

    edges : `pandas.DataFrame`_
        Hyperedges details as a DataFrame with columns `hyper_idx` (corresponds to the index in attribute :attr:`hyper`),
        `name` (interpreted as a source node), and `sign` (1 or -1)

    Attributes
    ----------
    nodes : `pandas.Series`_
    hyper : `pandas.Series`_
    edges : `pandas.DataFrame`_
    clauses : dict
        A mapping from an hyperedge id (`hyper_idx`) to a :class:`caspo.core.clause.Clause` object instance

    clauses_idx : dict
        The inverse mappings of those in attribute :attr:`clauses`

    mappings : :class:`caspo.core.mapping.MappingList`
        The list of all possible :class:`caspo.core.mapping.Mapping` for this hypergraph


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    .. _pandas.Series: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#series
    """

    def __init__(self, nodes, hyper, edges):
        self.nodes = nodes
        self.hyper = hyper
        self.edges = edges

        self.clauses = {}
        self.clauses_idx = {}
        for i, h in self.edges.groupby('hyper_idx'):
            literals = [Literal(source, sign) for _, source, sign in h.itertuples(index=False)]
            clause = Clause(literals)

            self.clauses[i] = clause
            self.clauses_idx[clause] = i

        mappings = []
        for node_idx, variable in self.nodes.items():
            for hyper_idx, _ in self.hyper[self.hyper == node_idx].items():
                mappings.append(Mapping(self.clauses[hyper_idx], variable))

        self._mappings = None
        self.mappings = mappings

    @property
    def mappings(self):
        return self._mappings

    @mappings.setter
    def mappings(self, mappings):
        self._mappings = MappingList(mappings)

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
    def from_graph(cls, graph, length=0):
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

        for i, node in enumerate(graph.nodes()):
            nodes.append(node)

            preds = graph.in_edges(node, data=True)
            l = len(preds)
            if length > 0:
                l = min(length, l)

            for literals in it.chain.from_iterable(it.combinations(preds, r+1) for r in range(l)):
                valid = defaultdict(int)
                for source, _, _ in literals:
                    valid[source] += 1

                if all(c == 1 for c in valid.values()):
                    hyper.append(i)
                    for source, _, data in literals:
                        edges['hyper_idx'].append(j)
                        edges['name'].append(source)
                        edges['sign'].append(data['sign'])

                    j += 1

        nodes = pd.Series(nodes, name='name')
        hyper = pd.Series(hyper, name='node_idx')
        edges = pd.DataFrame(edges)

        return cls(nodes, hyper, edges)

    def to_funset(self):
        """
        Converts the hypergraph to a set of `clingo.Function`_ instances

        Returns
        -------
        set
            Representation of the hypergraph as a set of `clingo.Function`_ instances


        .. _clingo.Function: https://potassco.github.io/clingo/python-api/current/clingo.html#-Function
        """
        fs = set()
        for i, n in self.nodes.items():
            fs.add(clingo.Function('node', [n, i]))

        for j, i in self.hyper.items():
            fs.add(clingo.Function('hyper', [i, j, len(self.edges[self.edges.hyper_idx == j])]))

        for j, v, s in self.edges.itertuples(index=False):
            fs.add(clingo.Function('edge', [j, v, s]))

        return fs
