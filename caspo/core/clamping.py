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

import numpy as np
import pandas as pd

import clingo

from .literal import Literal

class ClampingList(list):
    """
    A list of :class:`caspo.core.clamping.Clamping` object instances
    """

    def to_funset(self, lname="clamping", cname="clamped"):
        """
        Converts the list of clampings to a set of `clingo.Function`_ instances

        Parameters
        ----------
        lname : str
            Predicate name for the clamping id

        cname : str
            Predicate name for the clamped variable

        Returns
        -------
        set
            Representation of all clampings as a set of `clingo.Function`_ instances


        .. _clingo.Function: https://potassco.github.io/clingo/python-api/current/clingo.html#-Function
        """
        fs = set()
        for i, clamping in enumerate(self):
            fs.add(clingo.Function(lname, [clingo.Number(i)]))
            fs = fs.union(clamping.to_funset(i, cname))

        return fs

    def to_dataframe(self, stimuli=None, inhibitors=None, prepend=""):
        """
        Converts the list of clampigns to a `pandas.DataFrame`_ object instance

        Parameters
        ----------
        stimuli : Optional[list[str]]
            List of stimuli names. If given, stimuli are converted to {0,1} instead of {-1,1}.

        inhibitors : Optional[list[str]]
            List of inhibitors names. If given, inhibitors are renamed and converted to {0,1} instead of {-1,1}.

        prepend : str
            Columns are renamed using the given string at the beginning

        Returns
        -------
        `pandas.DataFrame`_
            DataFrame representation of the list of clampings


        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        """
        stimuli, inhibitors = stimuli or [], inhibitors or []
        cues = stimuli + inhibitors
        nc = len(cues)
        ns = len(stimuli)

        variables = cues or np.array(list(set((v for (v, s) in it.chain.from_iterable(self)))))

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

        return pd.DataFrame(matrix, columns=[prepend + "%s" % c for c in (stimuli + [i+'i' for i in inhibitors] if nc > 0 else variables)])

    def to_csv(self, filename, stimuli=None, inhibitors=None, prepend=""):
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

        prepend : str
            Columns are renamed using the given string at the beginning
        """
        self.to_dataframe(stimuli, inhibitors, prepend).to_csv(filename, index=False)

    @classmethod
    def from_dataframe(cls, df, inhibitors=None):
        """
        Creates a list of clampings from a `pandas.DataFrame`_ object instance.
        Column names are expected to be of the form `TR:species_name`

        Parameters
        ----------
        df : `pandas.DataFrame`_
            Columns and rows correspond to species names and individual clampings, respectively.

        inhibitors : Optional[list[str]]
            If given, species names ending with `i` and found in the list (without the `i`)
            will be interpreted as inhibitors. That is, if they are set to 1, the corresponding species is inhibited
            and therefore its negatively clamped. Apart from that, all 1s (resp. 0s) are interpreted as positively
            (resp. negatively) clamped.

            Otherwise (if inhibitors=[]), all 1s (resp. -1s) are interpreted as positively (resp. negatively) clamped.


        Returns
        -------
        caspo.core.ClampingList
            Created object instance


        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        """
        inhibitors = inhibitors or []
        clampings = []
        ni = len(inhibitors)
        for _, row in df.iterrows():
            if ni > 0:
                literals = []
                for v, s in row.items():
                    if v.endswith('i') and v[3:-1] in inhibitors:
                        if s == 1:
                            literals.append(Literal(v[3:-1], -1))
                    else:
                        literals.append(Literal(v[3:], 1 if s == 1 else -1))
                clampings.append(Clamping(literals))
            else:

                clampings.append(Clamping([Literal(v[3:], s) for v, s in row[row != 0].items()]))

        return cls(clampings)

    @classmethod
    def from_csv(cls, filename, inhibitors=None):
        """
        Creates a list of clampings from a CSV file. Column names are expected to be of the form `TR:species_name`

        Parameters
        ----------
        filename : str
            Absolute path to a CSV file to be loaded with `pandas.read_csv`_. The resulting DataFrame is passed to :func:`from_dataframe`.

        inhibitors : Optional[list[str]]
            If given, species names ending with `i` and found in the list (without the `i`)
            will be interpreted as inhibitors. That is, if they are set to 1, the corresponding species is inhibited
            and therefore its negatively clamped. Apart from that, all 1s (resp. 0s) are interpreted as positively
            (resp. negatively) clamped.

            Otherwise (if inhibitors=[]), all 1s (resp. -1s) are interpreted as positively (resp. negatively) clamped.


        Returns
        -------
        caspo.core.clamping.ClampingList
            Created object instance


        .. _pandas.read_csv: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html#pandas.read_csv
        """
        df = pd.read_csv(filename)
        return cls.from_dataframe(df, inhibitors)

    def frequencies_iter(self):
        """
        Iterates over the frequencies of all clamped variables

        Yields
        ------
        tuple[ caspo.core.literal.Literal, float ]
            The next tuple of the form (literal, frequency)
        """
        df = self.to_dataframe()
        n = float(len(self))
        for var, sign in it.product(df.columns, [-1, 1]):
            f = len(df[df[var] == sign]) / n
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
            If the variable is not present in any of the clampings
        """
        df = self.to_dataframe()
        if literal.variable in df.columns:
            return len(df[df[literal.variable] == literal.signature]) / float(len(self))
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

        for l1, l2 in it.combinations((l for l in literals if self.frequency(l) < 1), 2):
            a1, a2 = df[l1.variable] == l1.signature, df[l2.variable] == l2.signature
            if (a1 != a2).all():
                exclusive[l1].add(l2)
                exclusive[l2].add(l1)

            if (a1 == a2).all():
                inclusive[l1].add(l2)
                inclusive[l2].add(l1)

        return exclusive, inclusive

    def differences(self, networks, readouts, prepend=""):
        """
        Returns the total number of pairwise differences over the given readouts for the given networks

        Parameters
        ----------
        networks : iterable[:class:`caspo.core.logicalnetwork.LogicalNetwork`]
            Iterable of logical networks to compute pairwise differences

        readouts : list[str]
            List of readouts species names

        prepend : str
            Columns are renamed using the given string at the beginning


        Returns
        -------
        `pandas.DataFrame`_
            Total number of pairwise differences for each clamping over each readout


        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        """
        z, p = np.zeros((len(self), len(readouts)), dtype=int), np.zeros(len(self), dtype=int)
        for n1, n2 in it.combinations(networks, 2):
            r, c = np.where(n1.predictions(self, readouts) != n2.predictions(self, readouts))
            z[r, c] += 1
            p[r] += 1

        df = pd.DataFrame(z, columns=[prepend + "%s" % c for c in readouts])
        return pd.concat([df, pd.Series(p, name='pairs')], axis=1)

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

class Clamping(frozenset):
    """
    A clamping is a frozenset of :class:`caspo.core.literal.Literal` object instances where each
    literal describes a clamped variable
    """

    @classmethod
    def from_tuples(cls, tuples):
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
        return cls(Literal(v, s) for v, s in tuples)

    def to_funset(self, index, name="clamped"):
        """
        Converts the clamping to a set of `clingo.Function`_ object instances

        Parameters
        ----------
        index : int
            An external identifier to associate several clampings together in ASP

        name : str
            A function name for the clamping

        Returns
        -------
        set
            The set of `clingo.Function`_ object instances


        .. _clingo.Function: https://potassco.github.io/clingo/python-api/current/clingo.html#-Function
        """
        fs = set()
        for var, sign in self:
            fs.add(clingo.Function(name, [clingo.Number(index), clingo.String(var), clingo.Number(sign)]))

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
        return variable in dict(self)

    def to_array(self, variables):
        """
        Converts the clamping to a 1-D array with respect to the given variables

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

        for i, var in enumerate(variables):
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
