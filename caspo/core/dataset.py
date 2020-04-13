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

import pandas as pd
import numpy as np

import clingo # pylint: disable=import-error

from .setup import Setup
from .literal import Literal
from .clamping import Clamping, ClampingList

class Dataset(pd.DataFrame):
    """
    An experimental phospho-proteomics dataset extending `pandas.DataFrame`_

    Parameters
    ----------
    midas : Absolute PATH to a MIDAS file

    time : Data acquisition time-point for the early response

    Attributes
    ----------
        setup : :class:`caspo.core.setup.Setup`

        clampings : :class:`caspo.core.clamping.ClampingList`

        readouts : `pandas.DataFrame`_


    .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
    """

    def __init__(self, midas, time):
        df = pd.read_csv(midas)

        times = np.unique(df.filter(regex='^DA').values.flatten())
        if time not in times:
            raise ValueError("The time-point %s does not exists in the dataset. Available time-points are: %s" % (time, list(times)))

        df.drop(df.columns[0], axis=1, inplace=True)

        cond = True
        for col in df.filter(regex='^DA').columns:
            cond = cond & (df[col] == time)

        super(Dataset, self).__init__(df[cond].reset_index(drop=True))

        stimuli = [c[3:] for c in [c for c in self.columns if self.is_stimulus(c)]]
        inhibitors = [c[3:-1] for c in [c for c in self.columns if self.is_inhibitor(c)]]
        readouts = [c[3:] for c in [c for c in self.columns if self.is_readout(c)]]

        self.setup = Setup(stimuli, inhibitors, readouts)

    @property
    def clampings(self):
        clampings = []
        for _, row in self.filter(regex='^TR').iterrows():
            literals = []
            for var, sign in row.items():
                if self.is_stimulus(var):
                    literals.append(Literal(var[3:], 1 if sign == 1 else -1))
                else:
                    if sign == 1:
                        literals.append(Literal(var[3:-1], -1))

            clampings.append(Clamping(literals))

        return ClampingList(clampings)

    @property
    def readouts(self):
        return self.filter(regex='^DV').rename(columns=lambda c: c[3:]).astype(float)

    @staticmethod
    def is_stimulus(name):
        """
        Returns if the given species name is a stimulus or not

        Parameters
        ----------
        name : str

        Returns
        -------
        boolean
            True if the given name is a stimulus, False otherwise.
        """
        return name.startswith('TR') and not name.endswith('i')

    @staticmethod
    def is_inhibitor(name):
        """
        Returns if the given species name is a inhibitor or not

        Parameters
        ----------
        name : str

        Returns
        -------
        boolean
            True if the given name is a inhibitor, False otherwise.
        """
        return name.startswith('TR') and name.endswith('i')

    @staticmethod
    def is_readout(name):
        """
        Returns if the given species name is a readout or not

        Parameters
        ----------
        name : str

        Returns
        -------
        boolean
            True if the given name is a readout, False otherwise.
        """
        return name.startswith('DV')

    def to_funset(self, discrete):
        """
        Converts the dataset to a set of `clingo.Function`_ instances

        Parameters
        ----------
        discrete : callable
            A discretization function

        Returns
        -------
        set
            Representation of the dataset as a set of `clingo.Function`_ instances


        .. _clingo.Function: https://potassco.github.io/clingo/python-api/current/clingo.html#-Function
        """
        fs = self.clampings.to_funset("exp")
        fs = fs.union(self.setup.to_funset())

        for i, row in self.readouts.iterrows():
            for var, val in row.items():
                if not np.isnan(val):
                    fs.add(clingo.Function('obs', [i, var, discrete(val)]))

        return fs
