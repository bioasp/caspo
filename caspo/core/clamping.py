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
import numpy as np
import pandas as pd

import gringo

from literal import Literal

class ClampingList(pd.Series):
    """
    List of :class:`caspo.core.clamping.Clamping` object instances as a `pandas.Series`_
    
    .. _pandas.Series: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#series
    """
    
    def to_funset(self, lname="clamping", cname="clamped"):
        """
        Converts the list of clampings to a set of `gringo.Fun`_ instances
        
        Returns
        -------
        set
            Representation of all clampings as a set of `gringo.Fun`_ instances
        
        
        .. _gringo.Fun: http://potassco.sourceforge.net/gringo.html#Fun
        """
        fs = set()
        for i, clamping in self.iteritems():
            fs.add(gringo.Fun(lname, [i]))
            fs = fs.union(clamping.to_funset(i,cname))

        return fs
        
    def to_dataframe(self, stimuli=[], inhibitors=[]):
        """
        Converts the list of clampigns to a `pandas.DataFrame`_ object instance
        
        Parameters
        ----------
        stimuli : Optional[list[str]]
            List of stimuli names. If given, stimuli are converted to {0,1} instead of {-1,1}.
        
        inhibitors : Optional[list[str]]
            List of inhibitors names. If given, inhibitors are renamed and converted to {0,1} instead of {-1,1}.
        
        Returns
        -------
        `pandas.DataFrame`_
            DataFrame representation of the list of clampings
        
        
        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        """
        cues = stimuli + inhibitors
        nc = len(cues)
        ns = len(stimuli)
        
        variables = cues or np.array(list(set((v for (v,s) in it.chain.from_iterable(self)))))
            
        matrix = np.array([])
        for clamping in self:
            arr = clamping.to_array(variables)
            if nc > 0:
                arr[np.where(arr[:ns] == -1)[0]] = 0
                arr[ns + np.where(arr[ns:] == -1)[0]] = 1
            
            if len(matrix):
                matrix = np.append(matrix, [arr], axis=0)
            else:
                matrix = np.array([arr])

        return pd.DataFrame(matrix, columns=stimuli + [i+'i' for i in inhibitors] if nc > 0 else variables)
        
    def to_csv(self, filename, stimuli=[], inhibitors=[]):
        """
        Writes the list of clampings to a CSV file
        
        Parameters
        ----------
        filename : str
            Absolute path where to write the CSV file
        
        stimuli : Optional[list[str]]
            List of stimuli names. If given, stimuli are converted to {0,1} instead of {-1,1}.
        
        inhibitors : Optional[list[str]]
            List of inhibitors names. If given, inhibitors are renamed and converted to {0,1} instead of {-1,1}.
        """
        self.to_dataframe(stimuli, inhibitors).to_csv(filename, index=False)
        
    @classmethod
    def from_dataframe(klass, df, inhibitors=[]):
        """
        Creates a list of clampings from a `pandas.DataFrame`_ object instance
        
        Parameters
        ----------
        df : `pandas.DataFrame`_
            Columns and rows correspond to species names and individual clampings, respectively
            
        inhibitors : Optional[list[str]]
            If given, species names ending with `i` and found in the list will be interpreted as inhibitors


        Returns
        -------
        caspo.core.ClampingList
            Created object instance
        
        
        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        """
        clampings = []
        ni = len(inhibitors)
        for i,row in df.iterrows():
            if ni > 0:
                literals = []
                for v,s in row.iteritems():
                    if v.endswith('i') and v[:-1] in inhibitors:
                        if s == 1:
                            literals.append(Literal(v[:-1], -1))
                    else:
                        literals.append(Literal(v, 1 if s == 1 else -1))
                clampings.append(Clamping(literals))
            else:
                clampings.append(Clamping(map(lambda (v,s): Literal(v,s), row[row!=0].iteritems())))
            
        return klass(clampings)
        
    @classmethod
    def from_csv(klass, filename, inhibitors=[]):
        """
        Creates a list of clampings from a CSV file
        
        Parameters
        ----------
        filename : str
            Absolute path to a CSV file to be loaded with `pandas.read_csv`_. The resulting DataFrame is passed to :func:`from_dataframe`.
        
        inhibitors : Optional[list[str]]
            If given, species names ending with `i` and found in the list will be interpreted as inhibitors
            
            
        Returns
        -------
        caspo.core.clamping.ClampingList
            Created object instance
        
        
        .. _pandas.read_csv: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html#pandas.read_csv
        """
        df = pd.read_csv(filename)
        return klass.from_dataframe(df, inhibitors)
        
    def frequencies_iter(self):
        """
        Iterates over clamped variables' frequencies
        
        Yields
        ------
        tuple[ caspo.core.literal.Literal, float ]
            The next tuple of the form (literal, frequency)
        """
        df = self.to_dataframe()
        n = float(len(self))
        for var,sign in it.product(df.columns, [-1,1]):
            f = len(df[df[var]==sign]) / n
            if f > 0:
                yield Literal(var, sign), f
            
    def frequency(self, literal):
        """
        Returns the frequency of a clamped variable
        
        Parameters
        ----------
        literal : :class:`caspo.core.literal.Literal`
            The clamped variable
        
        Returns
        -------
        float
            The frequency of the given literal
        
        Raises
        ------
        ValueError
            If the variable is not present in any of the individual clampings
        """
        df = self.to_dataframe()
        if literal.variable in df.columns:
            return len(df[df[literal.variable]==literal.signature]) / float(len(self))
        else:
            raise ValueError("Variable not found: %s" % literal.variable)
            
    def combinatorics(self):
        """
        Returns mutually exclusive/inclusive clampings
        
        Returns
        -------
        (dict,dict)
            A tuple of 2 dictionaries.
            For each literal key, the first dict has as value the set of mutually exclusive clampings while
            the second dict has as value the set of mutually inclusive clampings.
        """
        df = self.to_dataframe()
        literals = set((l for l in it.chain.from_iterable(self)))
        exclusive, inclusive = defaultdict(set), defaultdict(set)
        
        for l1,l2 in it.combinations(it.ifilter(lambda l: self.frequency(l) < 1., literals), 2):
            a1, a2 = df[l1.variable] == l1.signature, df[l2.variable] == l2.signature
            if (a1 != a2).all():
                exclusive[l1].add(l2)
                exclusive[l2].add(l1)
                
            if (a1 == a2).all():
                inclusive[l1].add(l2)
                inclusive[l2].add(l1)
                
        return exclusive, inclusive

    def differences(self, networks, readouts):
        """
        Returns the total number of pairwise differences over the given readouts for the given networks
        
        Parameters
        ----------
        networks : iterable[:class:`caspo.core.logicalnetwork.LogicalNetwork`]
            Iterable of logical networks to compute pairwise differences
        
        readouts : list[str]
            List of readouts species names
        
        Returns
        -------
        pandas.DataFrame
            Total number of pairwise differences for each clamping over each readout
            
        """
        z,p = np.zeros((len(self), len(readouts)), dtype=int), np.zeros(len(self), dtype=int)
        for n1,n2 in it.combinations(networks,2):
            r,c = np.where(n1.predictions(self,readouts) != n2.predictions(self,readouts))
            z[r,c] += 1
            p[r] += 1
        
        return pd.concat([pd.DataFrame(z, columns=readouts), pd.Series(p, name='pairs')], axis=1)
        
    def drop_literals(self, literals):
        """
        Returns a new list of clampings without the given literals
        
        Parameters
        ----------
        literals : iterable[:class:`caspo.core.literal.Literal`]
            Iterable of literals to be removed from each clamping
        
        
        Returns
        -------
        caspo.core.clamping.ClampingList
            The new list of clampings
        """
        clampings = []
        for clamping in self:
            c = clamping.drop_literals(literals)
            if len(c) > 0:
                clampings.append(c)
        
        return ClampingList(clampings)
        
    def __plot__(self, source="", target=""):
        """
        Returns a `networkx.DiGraph`_ ready for plotting.
        
        Returns
        -------
        `networkx.DiGraph`_
            Network object instance ready for plotting
        
        
        .. _networkx.DiGraph: https://networkx.readthedocs.io/en/stable/reference/classes.digraph.html#networkx.DiGraph
        """
        graph = nx.DiGraph()
        
        if source:
            graph.add_node('source', label=source)
        if target:
            graph.add_node('target', label=target)
    
        return self.__create_graph__(graph, 'source' if source else '', self, 'target' if target else '')
    
    def __create_graph__(self, graph, parent, clampings, target):
        if not clampings.empty:
            popular, _ = sorted(clampings.frequencies_iter(), key=lambda (l,f): f)[-1]
            
            name = "%s-%s" % (parent, popular)
            graph.add_node(name, label=popular.variable, sign=popular.signature)
            if parent:
                graph.add_edge(parent, name)
            
            df = clampings.to_dataframe()
            
            popular_in = df[df[popular.variable]==popular.signature]
            self.__create_graph__(graph, name, ClampingList.from_dataframe(popular_in).drop_literals([popular]), target)

            popular_out = df[df[popular.variable]!=popular.signature]
            if not popular_out.empty:
                self.__create_graph__(graph, parent, ClampingList.from_dataframe(popular_out), target)
        
        else:
            if target:
                graph.add_edge(parent, target)
            
        return graph

class Clamping(frozenset):
    """
    A clamping is a frozenset of :class:`caspo.core.literal.Literal` object instances where each 
    literal describes a clamped variable
    """
    
    @classmethod
    def from_tuples(klass, tuples):
        """
        Creates a clamping from tuples of the form (variable, sign)
        
        Parameters
        ----------
        tuples : iterable[(str,int)]
            An iterable of tuples describing clamped variables
        
        Returns
        -------
        caspo.core.clamping.Clamping
            Created object instance
        """
        return klass(it.imap(lambda (v,s): Literal(v,s), tuples))
    
    def to_funset(self, index, name="clamped"):
        """
        Converts the clamping to a set of `gringo.Fun`_ object instances
        
        Returns
        -------
        set
            The set of `gringo.Fun`_ object instances
        
        
        .. _gringo.Fun: http://potassco.sourceforge.net/gringo.html#Fun
        """
        fs = set()
        for var, sign in self:
            fs.add(gringo.Fun(name, [index,var,sign]))
            
        return fs

    def bool(self, variable):
        """
        Returns whether the given variable is positively clamped
        
        Parameters
        ----------
        variable : str
            The variable name
        

        Returns
        -------
        boolean
            True if the given variable is positively clamped, False otherwise
        """
        return dict(self)[variable] == 1
        
    def has_variable(self, variable):
        """
        Returns whether the given variable is present in the clamping
        
        Parameters
        ----------
        variable : str
            The variable name
        

        Returns
        -------
        boolean
            True if the given variable is present in the clamping, False otherwise
        """
        return dict(self).has_key(variable)
        
    def to_array(self, variables):
        """
        Converts the clamping to an 1-D array with respect to the given variables
        
        Parameters
        ----------
        variables : list[str]
            List of variables names
            
    
        Returns
        -------
        `numpy.ndarray`_
            1-D array where position `i` correspond to the sign of the clamped variable at 
            position `i` in the given list of variables
        
        
        .. _numpy.ndarray: http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html#numpy.ndarray
        """
        arr = np.zeros(len(variables), np.int8)
        dc = dict(self)
        
        for i,var in enumerate(variables):
            arr[i] = dc.get(var, arr[i])
            
        return arr
        
    def drop_literals(self, literals):
        """
        Returns a new clamping without the given literals
        
        Parameters
        ----------
        literals : iterable[:class:`caspo.core.literal.Literal`]
            Iterable of literals to be removed
            
        Returns
        -------
        caspo.core.clamping.Clamping
            A new clamping without the given literals
        """
        return self.difference(literals)
