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

import math, os, logging
import itertools as it
from functools import partial
from random import randint

from sklearn.metrics import mean_squared_error
import numpy as np

import gringo

from caspo import core

class Learner(object):
    """
    Learner of (nearly) optimal logical networks with respect to a given
    prior knownledge network and a phospho-proteomics dataset.

    Parameters
    ----------
    graph : :class:`caspo.core.graph.Graph`
        Prior knowledge network

    dataset : :class:`caspo.core.dataset.Dataset`
        Experimental dataset

    length : int
        Maximum length for conjunction clauses

    discrete : str
        Discretization function: `round`, `ceil`, or `floor`

    factor : int
        Discretization factor, e.g. 10, 100, 1000

    Attributes
    ----------
        graph : :class:`caspo.core.graph.Graph`
        dataset : :class:`caspo.core.dataset.Dataset`
        length : int
        factor : int
        discrete : str
        hypergraph : :class:`caspo.core.hypergraph.HyperGraph`
        instance : str
        optimum : :class:`caspo.core.logicalnetwork.LogicalNetwork`
        networks : :class:`caspo.core.logicalnetwork.LogicalNetworkList`
        encodings : dict
    """
    def __init__(self, graph, dataset, length, discrete, factor):
        self.graph = graph
        self.dataset = dataset
        self.length = length
        self.factor = factor
        self.discrete = partial(self.__getattribute__(discrete), factor)

        self.hypergraph = core.HyperGraph.from_graph(self.graph, length)

        fs = self.dataset.to_funset(self.discrete).union(self.hypergraph.to_funset())
        fs.add(gringo.Fun('dfactor', [self.factor]))
        self.instance = ". ".join(map(str, fs)) + ". #show dnf/2."

        self.optimum = None
        self.networks = core.LogicalNetworkList.from_hypergraph(self.hypergraph)

        root = os.path.dirname(__file__)
        self.encodings = {
            'guess':    os.path.join(root, 'encodings/learn/guess.lp'),
            'fixpoint': os.path.join(root, 'encodings/learn/fixpoint.lp'),
            'rss':      os.path.join(root, 'encodings/learn/residual.lp'),
            'opt':      os.path.join(root, 'encodings/learn/optimization.lp'),
            'enum':     os.path.join(root, 'encodings/learn/enumeration.lp'),
            'random':   os.path.join(root, 'encodings/learn/random.lp')
        }

        self._logger = logging.getLogger("caspo")

    def round(self, factor, value):
        """
        Discretize a given value using a given factor and the closest integer function

        Parameters
        ----------
        factor : int
            The factor to be used for the discretization

        value : float
            The value to be discretized

        Returns
        -------
        int
            The discretized value
        """
        return int(round(factor*value))

    def ceil(self, factor, value):
        """
        Discretize a given value using a given factor and the ceil integer function

        Parameters
        ----------
        factor : int
            The factor to be used for the discretization

        value : float
            The value to be discretized

        Returns
        -------
        int
            The discretized value
        """
        return int(math.ceil(factor*value))

    def floor(self, factor, value):
        """
        Discretize a given value using a given factor and the floor integer function

        Parameters
        ----------
        factor : int
            The factor to be used for the discretization

        value : float
            The value to be discretized

        Returns
        -------
        int
            The discretized value
        """
        return int(math.floor(factor*value))

    def __keep_last__(self, model):
        self.last = model.atoms()

    def __save__(self, model):
        tuples = (f.args() for f in model.atoms())
        network = core.LogicalNetwork.from_hypertuples(self.hypergraph, tuples)
        self.networks.append(network)

    def __get_clingo__(self, encodings, args=[]):
        clingo = gringo.Control(args)

        clingo.add("base", [], self.instance)
        for enc in encodings:
            clingo.load(self.encodings[enc])

        return clingo

    def learn(self, fit=0, size=0, configure=None):
        """
        Learns all (nearly) optimal logical networks with give fitness and size tolerance.
        The first optimum logical network found is saved in the attribute :attr:`optimum` while
        all enumerated logical networks are saved in the attribute :attr:`networks`.

        Example::

            >>> from caspo import core, learn

            >>> graph = core.Graph.read_sif('pkn.sif')
            >>> dataset = core.Dataset('dataset.csv', 30)
            >>> zipped = graph.compress(dataset.setup)

            >>> learner = learn.Learner(zipped, dataset, 2, 'round', 100)
            >>> learner.learn(0.02, 1)

            >>> learner.networks.to_csv('networks.csv')

        Parameters
        ----------
        fit : float
            Fitness tolerance, e.g., use 0.1 for 10% tolerance with respect to the optimum

        size : int
            Size tolerance with respect to the optimum

        configure : callable
            Callable object responsible of setting a custom clingo configuration
        """
        encodings = ['guess', 'fixpoint', 'rss']
        if self.optimum is None:
            clingo = self.__get_clingo__(encodings + ['opt'])
            if configure is not None:
                configure(clingo.conf)

            clingo.ground([("base", [])])
            clingo.solve(on_model=self.__keep_last__)

            self._logger.info("Optimum logical network learned in %.4fs" % clingo.stats['time_total'])

            tuples = (f.args() for f in self.last)
            self.optimum = core.LogicalNetwork.from_hypertuples(self.hypergraph, tuples)

        ds = self.dataset
        predictions = self.optimum.predictions(ds.clampings, ds.readouts.columns).values

        readouts = ds.readouts.values
        pos = ~np.isnan(readouts)

        rss = np.sum((np.vectorize(self.discrete)(readouts[pos]) - predictions[pos]*self.factor)**2)

        self._logger.info("Optimum logical networks has MSE %.4f and size %s" %
                            (mean_squared_error(readouts[pos],predictions[pos]), self.optimum.size))

        self.networks.reset()

        args = ['-c maxrss=%s' % int(rss + rss*fit), '-c maxsize=%s' % (self.optimum.size + size)]

        clingo = self.__get_clingo__(encodings + ['enum'], args)
        clingo.conf.solve.models = '0'
        if configure is not None:
            configure(clingo.conf)

        clingo.ground([("base", [])])
        clingo.solve(on_model=self.__save__)

        self._logger.info("%s (nearly) optimal logical networks learned in %.4fs" % (len(self.networks), clingo.stats['time_total']))

    def random(self, size, n_and, max_in, n=1):
        """
        Generates `n` random logical networks with given size range, number of AND gates and maximum
        input signals for AND gates. Logical networks are saved in the attribute :attr:`networks`.

        Parameters
        ----------
        n : int
            Number of random logical networks to be generated

        size : (int,int)
            Minimum and maximum sizes

        n_and : (int,int)
            Minimum and maximum AND gates

        max_in : int
            Maximum input signals for AND gates
        """
        args = ['-c minsize=%s' % size[0], '-c maxsize=%s' % size[1],
                '-c minnand=%s' % n_and[0], '-c maxnand=%s' % n_and[1], '-c maxin=%s' % max_in]
        encodings = ['guess', 'random']

        self.networks.reset()

        clingo = self.__get_clingo__(args, encodings)
        clingo.conf.solve.models = str(n)
        clingo.conf.solver.seed = str(randint(0,32767))
        clingo.conf.solver.sign_def = '3'

        clingo.ground([("base", [])])
        clingo.solve(on_model=self.__save__)
