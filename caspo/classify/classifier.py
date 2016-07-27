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

import os

import multiprocessing as mp
from joblib import Parallel, delayed

import numpy as np

import gringo

from caspo import core

def __learn_io__(networks, setup, configure):
    root = os.path.dirname(__file__)
    encoding = os.path.join(root, 'encodings/io.lp')
    setup_fs = setup.to_funset()
    
    behaviors = core.LogicalNetworkList.from_hypergraph(networks.hg)
    for network in networks:
        found = False
        nl = core.LogicalNetworkList.from_hypergraph(networks.hg, [network])
        for i,behavior in enumerate(behaviors):
            bl = core.LogicalNetworkList.from_hypergraph(networks.hg, [behavior])
            fs = setup_fs.union(nl.concat(bl).to_funset())
            instance = ". ".join(map(str, fs)) + "."

            clingo = gringo.Control()
            if configure is not None:
                configure(clingo.conf)
                
            clingo.add("base", [], instance)
            clingo.load(encoding)

            clingo.ground([("base", [])])
            if clingo.solve() == gringo.SolveResult.UNSAT:
                found = True
                behaviors.known_eq[i] += (1 + network.known_eq)
                break
        
        if not found:
            behaviors.append(network)
        
    return behaviors

class Classifier(object):
    """
    Classifier of given list of logical networks with respect to a given experimental setup
    
    Parameters
    ----------
    networks : :class:`caspo.core.logicalnetwork.LogicalNetworkList`
        The list of networks

    setup : :class:`caspo.core.setup.Setup`
        The experimental setup with respect to the input-output behaviors must be computed
    
    
    Attributes
    ----------
    networks : :class:`caspo.core.logicalnetwork.LogicalNetworkList`
    setup : :class:`caspo.core.setup.Setup`
    """
    
    def __init__(self, networks, setup):
        self.networks = networks
        self.setup = setup
    
    def classify(self, n_jobs=-1, configure=None):
        """
        Returns input-output behaviors for the list of logical networks :attr:`networks`

        n_jobs : int
            Number of jobs to run in parallel. Default to -1 (all cores available)
    
        configure : callable
            Callable object responsible of setting clingo configuration
    
    
        Returns
        -------
        caspo.core.logicalnetwork.LogicalNetworkList
            The list of networks with one representative for each behavior
        """
        networks = self.networks
        
        n = len(networks)
        cpu = n_jobs if n_jobs > -1 else mp.cpu_count()
    
        if cpu > 1:
            lp = int(np.ceil(n / float(cpu))) if n > cpu else 1
            parts = networks.split(np.arange(lp, n, lp))
        
            behaviors_parts = Parallel(n_jobs=n_jobs)(delayed(__learn_io__)(part, self.setup, configure) for part in parts)
            networks = core.LogicalNetworkList.from_hypergraph(networks.hg)
            for b in behaviors_parts:
                networks = networks.concat(b)

        return __learn_io__(networks, self.setup, configure)