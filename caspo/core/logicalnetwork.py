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
import numpy as np

from joblib import Parallel, delayed

from sklearn.metrics import mean_squared_error

import gringo

from literal import Literal
from clause import Clause
from mapping import Mapping
from graph import Graph
from hypergraph import HyperGraph


def __parallel_predictions__(network, clampings, readouts, stimuli=[], inhibitors=[]):
    return network.predictions(clampings, readouts, stimuli, inhibitors).values

def __parallel_mse__(network, clampings, readouts, observations, pos):
    return network._mse(clampings, readouts, observations, pos)
    
class LogicalNetworkList(object):
    """
    List of :class:`caspo.core.logicalnetwork.LogicalNetwork` object instances

    Parameters
    ----------
    hg : :class:`caspo.core.hypergraph.HyperGraph`
        Underlying hypergraph of all logical networks.

    matrix : Optional[`numpy.ndarray`_]
        2-D binary array representation of all logical networks.
        If None, an empty array is initialised

    networks : Optional[`numpy.ndarray`_]
        For each network in the list, it gives the number of networks having the same behavior.
        If None, an array of ones is initialised with the same length as the number of networks in the list.

    Attributes
    ----------
    hg : :class:`caspo.core.hypergraph.HyperGraph`
    matrix : `numpy.ndarray`_
    networks : `numpy.ndarray`_
    
    
    .. _numpy.ndarray: http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html#numpy.ndarray
    """

    def __init__(self, hg, matrix=None, networks=None):
        self.hg = hg

        if matrix is None:
            self.matrix = np.array([])
        else:
            self.matrix = matrix

        if isinstance(networks, np.ndarray):
            self.networks = networks
        else:
            self.networks = np.array(networks, dtype=int) if networks else np.ones(len(self.matrix), dtype=int)


    @classmethod
    def from_csv(klass, filename):
        """
        Creates a list of logical networks from a CSV file

        Parameters
        ----------
        filename : str
           Absolute path to CSV file

        Returns
        -------
        caspo.core.logicalnetwork.LogicalNetworkList
           Created object instance
        """
        df = pd.read_csv(filename)

        edges = set()
        mappings = []
        cols = []
        for m in df.columns:
            try:
                ct = Mapping.from_str(m)
                mappings.append(ct)
                cols.append(m)                
                for source, sign in ct.clause:
                    edges.add((source,ct.target,sign))
            except:
                #current column isn't a mapping
                pass

        graph = Graph.from_tuples(edges)
        hypergraph = HyperGraph.from_graph(graph)
        hypergraph.mappings = mappings
        
        if 'networks' in df.columns:
            nnet = df['networks'].values.astype(int)
        else:
            nnet = None

        return klass(hypergraph, matrix=df[cols].values, networks=nnet)

    @classmethod
    def from_hypergraph(klass, hypergraph, networks=[]):
        """
        Creates a list of logical networks from a given hypergraph and an
        optional list of :class:`caspo.core.logicalnetwork.LogicalNetwork` object instances

        Parameters
        ----------
        hypegraph : :class:`caspo.core.hypergraph.HyperGraph`
            Underlying hypergraph for this logical network list

        networks : Optional[list]
            List of :class:`caspo.core.logicalnetwork.LogicalNetwork` object instances

        Returns
        -------
        caspo.core.logicalnetwork.LogicalNetworkList
           Created object instance
        """
        matrix = None
        nnet = None
        if networks:
            matrix = np.array([networks[0].to_array(hypergraph.mappings)])
            nnet = [networks[0].networks]
            for network in networks[1:]:
                matrix = np.append(matrix, [network.to_array(hypergraph.mappings)], axis=0)
                nnet.append(network.networks)

        return klass(hypergraph, matrix, nnet)
        
    def reset(self):
        """
        Drop all networks in the list
        """
        self.matrix = np.array([])
        self.networks = np.array([])

    def split(self, indices):
        """
        Splits logical networks according to given indices

        Parameters
        ----------
        indices : list
            1-D array of sorted integers, the entries indicate where the array is split

        Returns
        -------
        list
            List of :class:`caspo.core.logicalnetwork.LogicalNetworkList` object instances


        .. seealso:: `numpy.split <http://docs.scipy.org/doc/numpy/reference/generated/numpy.split.html#numpy-split>`_
        """
        return map(lambda part: LogicalNetworkList(self.hg, part), np.split(self.matrix, indices))

    def concat(self, other):
        """
        Returns the concatenation with another :class:`caspo.core.logicalnetwork.LogicalNetworkList` object instance.
        It is assumed that both have the same underlying hypergraph.

        Parameters
        ----------
        other : :class:`caspo.core.logicalnetwork.LogicalNetworkList`
            The list to concatenate

        Returns
        -------
        caspo.core.logicalnetwork.LogicalNetworkList
            If other is empty returns self, if self is empty returns other, otherwise a new
            :class:`caspo.core.LogicalNetworkList` is created by concatenating self and other.
        """
        if len(other) == 0:
            return self
        elif len(self) == 0:
            return other
        else:
            return LogicalNetworkList(self.hg, np.append(self.matrix, other.matrix, axis=0), np.concatenate([self.networks,other.networks]))

    def append(self, network):
        """
        Append a :class:`caspo.core.logicalnetwork.LogicalNetwork` to the list

        Parameters
        ----------
        network : :class:`caspo.core.logicalnetwork.LogicalNetwork`
            The network to append
        """
        arr = network.to_array(self.hg.mappings)
        if len(self.matrix):
            self.matrix = np.append(self.matrix, [arr], axis=0)
            self.networks = np.append(self.networks, network.networks)
        else:
            self.matrix = np.array([arr])
            self.networks = np.array([network.networks])

    def __len__(self):
        """
        Returns the number of logical networks

        Returns
        -------
        int
            Number of logical networks
        """
        return len(self.matrix)

    def __iter__(self):
        """
        Iterates over all logical networks in the list

        Yields
        ------
        caspo.core.logicalnetwork.LogicalNetwork
            The next logical network in the list
        """
        for i,arr in enumerate(self.matrix):
            yield LogicalNetwork(it.imap(lambda m: (m[0],m[1]), self.hg.mappings[np.where(arr==1)[0]]), networks=self.networks[i])
        
    def __getitem__(self, index):
        matrix, networks = self.matrix[index,:], self.networks[index]
        if hasattr(index,'__iter__'):
            return LogicalNetworkList(self.hg, matrix, networks)
        else:
            return LogicalNetwork(it.imap(lambda m: (m[0],m[1]), self.hg.mappings[np.where(matrix==1)[0]]), networks=networks)

    def to_funset(self):
        """
        Converts the list of logical networks to a set of `gringo.Fun`_ instances

        Returns
        -------
        set
            Representation of all networks as a set of `gringo.Fun`_ instances
        
        
        .. _gringo.Fun: http://potassco.sourceforge.net/gringo.html#Fun
        """
        fs = set((gringo.Fun("variable", [var]) for var in self.hg.nodes))

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

    def to_dataframe(self, networks=False, dataset=None, size=False, n_jobs=-1):
        """
        Converts the list of logical networks to a `pandas.DataFrame`_ object instance

        Parameters
        ----------
        networks : boolean
            If True, a column with number of networks having the same behavior is included in the DataFrame

        dataset: Optional[:class:`caspo.core.dataset.Dataset`]
            If not None, a column with the MSE with respect to the given dataset is included in the DataFrame

        size: boolean
            If True, a column with the size of each logical network is included in the DataFrame
        
        n_jobs : int
            Number of jobs to run in parallel. Default to -1 (all cores available)

        Returns
        -------
        `pandas.DataFrame`_
            DataFrame representation of the list of logical networks.
        
        
        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        """
        length = len(self)
        df = pd.DataFrame(self.matrix, columns=map(str, self.hg.mappings))

        if networks:
            df = pd.concat([df,pd.DataFrame({'networks': self.networks})], axis=1)

        if dataset is not None:
            clampings = dataset.clampings
            readouts = dataset.readouts.columns
            observations = dataset.readouts.values
            pos = ~np.isnan(observations)
            
            mse = Parallel(n_jobs=n_jobs)(delayed(__parallel_mse__)(n, clampings, readouts, observations[pos], pos) for n in self)
            df = pd.concat([df,pd.DataFrame({'mse': mse})], axis=1)

        if size:
            df = pd.concat([df,pd.DataFrame({'size': np.fromiter((n.size for n in self), int, length)})], axis=1)

        return df

    def to_csv(self, filename, networks=False, dataset=None, size=False, n_jobs=-1):
        """
        Writes the list of logical networks to a CSV file

        Parameters
        ----------
        filename : str
            Absolute path where to write the CSV file

        networks : boolean
            If True, a column with number of networks having the same behavior is included in the file

        dataset: Optional[:class:`caspo.core.dataset.Dataset`]
            If not None, a column with the MSE with respect to the given dataset is included

        size: boolean
            If True, a column with the size of each logical network is included
        
        n_jobs : int
            Number of jobs to run in parallel. Default to -1 (all cores available)

        """
        self.to_dataframe(networks, dataset, size).to_csv(filename, index=False)

    def frequencies_iter(self):
        """
        Iterates over all mappings' frequencies

        Yields
        ------
        tuple[tuple[caspo.core.clause.Clause, str], float]
            The next pair (mapping,frequency)
        """
        f = self.matrix.mean(axis=0)
        for i,m in self.hg.mappings.iteritems():
            if f[i] > 0:
                yield m,f[i]

    def frequency(self, mapping):
        """
        Returns frequency of a given mapping, i.e., a tuple (:class:`caspo.core.clause.Clause`, str)

        Parameters
        ----------
        mapping : tuple
            A mapping (:class:`caspo.core.clause.Clause`, str)

        Returns
        -------
        float
            Frequency of the given mapping over all logical networks

        Raises
        ------
        ValueError
            If the given mapping is not found in the mappings of :attr:`hg`
        """
        return self.matrix[:,self.hg.mappings[mapping]].mean()

    def combinatorics(self):
        """
        Returns mutually exclusive/inclusive mappings

        Returns
        -------
        (dict,dict)
            A tuple of 2 dictionaries.
            For each mapping key, the first dict has as value the set of mutually exclusive mappings while
            the second dict has as value the set of mutually inclusive mappings.
        """
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

    def predictions(self, setup, n_jobs=-1):
        """
        Returns a `pandas.DataFrame`_ with the weighted average predictions and variance of all readouts for each possible clampings.
        For each logical network the weight corresponds to the number of networks having the same behavior (:attr:`networks`).

        Parameters
        ----------
        setup : :class:`caspo.core.setup.Setup`
            Experimental setup
        
        n_jobs : int
            Number of jobs to run in parallel. Default to -1 (all cores available)

        Returns
        -------
        `pandas.DataFrame`_
            DataFrame with the weighted variance of readouts predictions for each possible clamping

        
        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        
        .. seealso:: `Wikipedia: Weighted sample variance <https://en.wikipedia.org/wiki/Weighted_arithmetic_mean#Weighted_sample_variance>`_
        """
        stimuli, inhibitors, readouts = setup.stimuli, setup.inhibitors, setup.readouts
        cues = setup.cues()
        nc = len(cues)
        nclampings = 2**nc
        predictions = np.zeros((len(self), nclampings, len(setup)))

        clampings = list(setup.clampings_iter(cues))
        predictions[:,:,:] = Parallel(n_jobs=n_jobs)(delayed(__parallel_predictions__)(n, clampings, readouts, stimuli, inhibitors) for n in self)

        avg = np.average(predictions[:,:,nc:], axis=0, weights=self.networks)
        var = np.average((predictions[:,:,nc:]-avg)**2, axis=0, weights=self.networks)

        rcues = map(lambda c: "TR:%s" % c, setup.cues(True))
        cols = np.concatenate([rcues, map(lambda r: "AVG:%s" % r, readouts), map(lambda r: "VAR:%s" % r, readouts)])
        
        #use the first network predictions to extract all clampings
        df = pd.DataFrame(np.concatenate([predictions[0,:,:nc],avg,var], axis=1), columns=cols)
        df[rcues] = df[rcues].astype(int)
        
        return df

    def weighted_mse(self, dataset, n_jobs=-1):
        """
        Returns the weighted MSE over all logical networks with respect to the given :class:`caspo.learn.dataset.Dataset` object instance.
        For each logical network the weight corresponds to the number of networks having the same behavior (:attr:`networks`).

        Parameters
        ----------
        dataset: :class:`caspo.core.dataset.Dataset`
            Dataset to compute MSE
        
        n_jobs : int
            Number of jobs to run in parallel. Default to -1 (all cores available)

        Returns
        -------
        float
            Weighted MSE
        """
        predictions = np.zeros((len(self), len(dataset.clampings), len(dataset.setup.readouts)))
        predictions[:,:,:] = Parallel(n_jobs=n_jobs)(delayed(__parallel_predictions__)(n, dataset.clampings, dataset.setup.readouts) for n in self)
        for i,network in enumerate(self):
            predictions[i,:,:] *= self.networks[i]

        readouts = dataset.readouts.values
        pos = ~np.isnan(readouts)

        return mean_squared_error(readouts[pos], (np.sum(predictions, axis=0) / np.sum(self.networks))[pos])

    def __plot__(self):
        """
        Returns a `networkx.MultiDiGraph`_ ready for plotting. Edges weights correspond to mappings frequencies.

        Returns
        -------
        `networkx.MultiDiGraph`_
            Network object instance ready for plotting
        
        
        .. _networkx.MultiDiGraph: https://networkx.readthedocs.io/en/stable/reference/classes.multidigraph.html#networkx.MultiDiGraph
        """
        graph = nx.MultiDiGraph()
        n_gates = 1

        for mapping in self.hg.mappings[np.unique(np.where(self.matrix==1)[1])]:
            graph.add_node(mapping.target)
            if len(mapping.clause) > 1:
                gate = 'gate-%s' % n_gates
                n_gates += 1
                graph.add_node(gate, gate=True)
                graph.add_edge(gate, mapping.target, sign=1, weight=self.frequency(mapping))

                for var,sign in mapping.clause:
                    graph.add_node(var)
                    graph.add_edge(var, gate, sign=sign, weight=self.frequency(mapping))
            else:
                for var,sign in mapping.clause:
                    graph.add_node(var)
                    graph.add_edge(var, mapping.target, sign=sign, weight=self.frequency(mapping))

        return graph
    
class LogicalNetwork(nx.DiGraph):
    """
    Logical network class extends `networkx.DiGraph`_ with nodes being,
    either :class:`caspo.core.clause.Clause` object instances or species names (str).

    Attributes
    ----------
    networks : int
        Number of networks having the same behavior (including this representative network itself)
    
    
    .. _networkx.DiGraph: https://networkx.readthedocs.io/en/stable/reference/classes.digraph.html#networkx.DiGraph
    """
    
    @classmethod
    def from_hypertuples(klass, hg, tuples):
        """
        Creates a logical network from an iterable of integer tuples matching mappings in the given 
        :class:`caspo.core.hypergraph.HyperGraph`

        Parameters
        ----------
        hg : :class:`caspo.core.hypergraph.HyperGraph`
            Underlying hypergraph

        tuples : (int,int)
            tuples matching mappings in the given hypergraph

        Returns
        -------
        caspo.core.logicalnetwork.LogicalNetwork
            Created object instance
        """
        return klass(map(lambda (i,j): (hg.clauses[j], hg.variable(i)), tuples), networks=1)
        
    @property
    def networks(self):
        return self.graph.get('networks',1)

    def to_graph(self):
        """
        Converts the logical network to its underlying interaction graph

        Returns
        -------
        caspo.core.graph.Graph
            The underlying interaction graph
        """
        edges = set()
        for clause,target in self.edges_iter():
            for source,signature in clause:
                edges.add((source,target,signature))

        return Graph.from_tuples(edges)

    @property
    def size(self):
        """
        int: The size of this logical network
        """
        return sum(map(lambda (c,t): len(c), self.edges_iter()))

    def step(self, state, clamping):
        """
        Performs a simulation step from the given state and with respect to the given clamping

        Parameters
        ----------
        state : dict
            The key-value mapping describing the current state of the logical network

        clamping : caspo.core.clamping.Clamping
            A clamping over variables in the logical network

        Returns
        -------
        dict
            The key-value mapping describing the next state of the logical network
        """
        ns = state.copy()
        for var in state:
            if clamping.has_variable(var):
                ns[var] = int(clamping.bool(var))
            else:
                or_value = 0
                for clause, _ in self.in_edges_iter(var):
                    or_value = or_value or clause.bool(state)
                    if or_value: break

                ns[var] = int(or_value)

        return ns

    def fixpoint(self, clamping, steps=0):
        """
        Computes the fixpoint with respect to a given :class:`caspo.core.clamping.Clamping`

        Parameters
        ----------
        clamping : :class:`caspo.core.clamping.Clamping`
            The clamping with respect to the fixpoint is computed
        steps : int
            If greater than zero, a maximum of steps is performed

        Returns
        -------
        dict
            The key-value mapping describing the state of the logical network
        """
        current = dict.fromkeys(self.variables(),0)
        updated = self.step(current, clamping)
        steps -= 1
        while current != updated and steps != 0:
            current = updated
            updated = self.step(current, clamping)

        return current

    def predictions(self, clampings, readouts, stimuli=[], inhibitors=[], nclampings=-1):
        """
        Computes network predictions for the given iterable of clampings

        Parameters
        ----------
        clampings : iterable
            Iterable over clampings

        readouts : list[str]
            List of readouts names

        stimuli : Optional[list[str]]
            List of stimuli names

        inhibitors : Optional[list[str]]
            List of inhibitors names

        nclampings : Optional[int]
            If greater than zero, it must be the number of clampings in the iterable. Otherwise,
            clampings must implement the special method :func:`__len__`


        Returns
        -------
        `pandas.DataFrame`_
            DataFrame with network predictions for each clamping. If stimuli and inhibitors are given,
            columns are included describing each clamping. Otherwise, columns correspond to readouts only.
        
        
        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        """
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
    
    def mse(self, dataset):
        clampings = dataset.clampings
        readouts = dataset.readouts.columns
        observations = dataset.readouts.values
        pos = ~np.isnan(observations)
        
        return self._mse(clampings, readouts, observations[pos], pos)
    
    def _mse(self, clampings, readouts, observations, pos):
        return mean_squared_error(observations, (self.predictions(clampings, readouts).values)[pos])

    def variables(self):
        """
        Returns variables in the logical network

        Returns
        -------
        set[str]
            Unique variables names
        """
        variables = set()
        for v in self.nodes_iter():
            if isinstance(v, Clause):
                for l in v:
                    variables.add(l.variable)
            else:
                variables.add(v)
        return variables

    def formulas_iter(self):
        """
        Iterates over all variable-clauses in the logical network

        Yields
        ------
        tuple[str,frozenset[caspo.core.clause.Clause]]
            The next tuple of the form (variable, set of clauses) in the logical network.
        """
        for var in it.ifilter(lambda v: self.has_node(v), self.variables()):
            yield var, frozenset(self.predecessors(var))

    def to_array(self, mappings):
        """
        Converts the logical network to a binary array with respect to the given mappings from a
        :class:`caspo.core.hypergraph.HyperGraph` object instance.

        Parameters
        ----------
        mappings : :class:`caspo.core.mapping.MappingList`
            Mappings to create the binary array

        Returns
        -------
        `numpy.ndarray`_
            Binary array with respect to the given mappings describing the logical network


        .. _numpy.ndarray: http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html#numpy.ndarray
        """
        arr = np.zeros(len(mappings), np.int8)
        for i, (clause, target) in mappings.iteritems():
            if self.has_edge(clause, target):
                arr[i] = 1

        return arr

    def __plot__(self):
        """
        Returns a `networkx.MultiDiGraph`_ ready for plotting.

        Returns
        -------
        `networkx.MultiDiGraph`_
            Network object instance ready for plotting
        
        
        .. _networkx.MultiDiGraph: https://networkx.readthedocs.io/en/stable/reference/classes.multidigraph.html#networkx.MultiDiGraph
        """
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
