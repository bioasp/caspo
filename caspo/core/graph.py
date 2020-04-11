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

import itertools as it
import pandas as pd
import networkx as nx

class Graph(nx.MultiDiGraph):
    """
    Prior knowledge network (aka interaction graph) extending `networkx.MultiDiGraph`_

    .. _networkx.MultiDiGraph: https://networkx.readthedocs.io/en/stable/reference/classes.multidigraph.html#networkx.MultiDiGraph
    """

    @classmethod
    def from_tuples(cls, tuples):
        """
        Creates a graph from an iterable of tuples describing edges like (source, target, sign)

        Parameters
        ----------
        tuples : iterable[(str,str,int))]
            Tuples describing signed and directed edges

        Returns
        -------
        caspo.core.graph.Graph
            Created object instance
        """
        return cls(it.imap(lambda source_target_sign: (source_target_sign[0], source_target_sign[1], {'sign': source_target_sign[2]}), tuples))

    @classmethod
    def read_sif(cls, path):
        """
        Creates a graph from a `simple interaction format (SIF)`_ file

        Parameters
        ----------
        path : str
            Absolute path to a SIF file

        Returns
        -------
        caspo.core.graph.Graph
            Created object instance


        .. _simple interaction format (SIF): http://wiki.cytoscape.org/Cytoscape_User_Manual/Network_Formats
        """
        df = pd.read_csv(path, delim_whitespace=True, names=['source', 'sign', 'target']).drop_duplicates()
        edges = [(source, target, {'sign': sign}) for _, source, sign, target in df.itertuples()]
        return cls(data=edges)

    def predecessors(self, node, exclude_compressed=True):
        """
        Returns the list of predecessors of a given node

        Parameters
        ----------
        node : str
            The target node

        exclude_compressed : boolean
            If true, compressed nodes are excluded from the predecessors list

        Returns
        -------
        list
            List of predecessors nodes
        """
        preds = super(Graph, self).predecessors(node)
        if exclude_compressed:
            return [n for n in preds if not self.node[n].get('compressed', False)]
        else:
            return preds

    def successors(self, node, exclude_compressed=True):
        """
        Returns the list of successors of a given node

        Parameters
        ----------
        node : str
            The target node

        exclude_compressed : boolean
            If true, compressed nodes are excluded from the successors list

        Returns
        -------
        list
            List of successors nodes
        """
        succs = super(Graph, self).successors(node)
        if exclude_compressed:
            return [n for n in succs if not self.node[n].get('compressed', False)]
        else:
            return succs

    def compress(self, setup):
        """
        Returns the compressed graph according to the given experimental setup

        Parameters
        ----------
        setup : :class:`caspo.core.setup.Setup`
            Experimental setup used to compress the graph

        Returns
        -------
        caspo.core.graph.Graph
            Compressed graph
        """
        designated = set(setup.nodes)
        zipped = self.copy()

        marked = [(n, d) for n, d in self.nodes(data=True) if n not in designated and not d.get('compressed', False)]
        while marked:
            for node, _ in sorted(marked):
                backward = zipped.predecessors(node)
                forward = zipped.successors(node)

                if not backward or (len(backward) == 1 and not backward[0] in forward):
                    self.__merge_source_targets(node, zipped)

                elif not forward or (len(forward) == 1 and not forward[0] in backward):
                    self.__merge_target_sources(node, zipped)

                else:
                    designated.add(node)

            marked = [(n, d) for n, d in self.nodes(data=True) if n not in designated and not d.get('compressed', False)]

        not_compressed = [(n, d) for n, d in zipped.nodes(data=True) if not d.get('compressed', False)]
        return zipped.subgraph([n for n, _ in not_compressed])

    def __merge_source_targets(self, node, zipped):
        predecessor = zipped.predecessors(node)
        edges = []
        for target in zipped.successors(node):
            if predecessor:
                for source_edge in zipped[predecessor[0]][node].values():
                    for target_edge in zipped[node][target].values():
                        sign = {'sign': source_edge['sign']*target_edge['sign']}
                        if not zipped.has_edge(predecessor[0], target) or sign not in list(zipped[predecessor[0]][target].values()):
                            edges.append((predecessor[0], target, sign))

        self.node[node]['compressed'] = zipped.node[node]['compressed'] = True
        zipped.add_edges_from(edges)

    def __merge_target_sources(self, node, zipped):
        successor = zipped.successors(node)
        edges = []
        for source in zipped.predecessors(node):
            if successor:
                for target_edge in zipped[source][node].values():
                    for source_edge in zipped[node][successor[0]].values():
                        sign = {'sign': target_edge['sign']*source_edge['sign']}
                        if not zipped.has_edge(source, successor[0]) or sign not in list(zipped[source][successor[0]].values()):
                            edges.append((source, successor[0], {'sign': target_edge['sign']*source_edge['sign']}))

        self.node[node]['compressed'] = zipped.node[node]['compressed'] = True
        zipped.add_edges_from(edges)

    def __plot__(self):
        """
        Returns a copy of this graph ready for plotting

        Returns
        -------
        caspo.core.graph.Graph
            A copy of the object instance
        """
        return self.copy()
