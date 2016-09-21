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
    def from_tuples(klass, tuples):
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
        return klass(it.imap(lambda (source,target,sign): (source,target,{'sign': sign}), tuples))

    @classmethod
    def read_sif(klass, path):
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
        df = pd.read_csv(path, delim_whitespace=True, names=['source','sign','target'])
        edges = map(lambda (i,source,sign,target): (source,target,{'sign': sign}), df.itertuples())
        return klass(data=edges)

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
            return filter(lambda n: not self.node[n].get('compressed', False), preds)
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
            return filter(lambda n: not self.node[n].get('compressed', False), succs)
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
        done = False
        designated = set(setup.nodes)
        zipped = self.copy()

        marked = filter(lambda (n,d): n not in designated and not d.get('compressed',False), self.nodes(data=True))
        while marked:
            for node, data in sorted(marked):
                backward = zipped.predecessors(node)
                forward = zipped.successors(node)

                if not backward or (len(backward) == 1 and not backward[0] in forward):
                    self.__merge_source_targets(node,zipped)

                elif not forward or (len(forward) == 1 and not forward[0] in backward):
                    self.__merge_target_sources(node,zipped)

                else:
                    designated.add(node)

            marked = filter(lambda (n,d): n not in designated and not d.get('compressed',False), self.nodes(data=True))

        not_compressed = filter(lambda (n,d): not d.get('compressed', False), zipped.nodes(data=True))
        return zipped.subgraph(map(lambda (n,d): n, not_compressed))

    def __merge_source_targets(self, node, zipped):
        predecessor = zipped.predecessors(node)
        edges = []
        for target in zipped.successors(node):
            if predecessor:
                for source_edge in zipped[predecessor[0]][node].itervalues():
                    for target_edge in zipped[node][target].itervalues():
                        sign = {'sign': source_edge['sign']*target_edge['sign']}
                        if not zipped.has_edge(predecessor[0], target) or sign not in zipped[predecessor[0]][target].values():
                            edges.append((predecessor[0], target, sign))

        self.node[node]['compressed'] = zipped.node[node]['compressed'] = True
        zipped.add_edges_from(edges)

    def __merge_target_sources(self, node, zipped):
        successor = zipped.successors(node)
        edges = []
        for source in zipped.predecessors(node):
            if successor:
                for target_edge in zipped[source][node].itervalues():
                    for source_edge in zipped[node][successor[0]].itervalues():
                        sign = {'sign': target_edge['sign']*source_edge['sign']}
                        if not zipped.has_edge(source, successor[0]) or sign not in zipped[source][successor[0]].values():
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
