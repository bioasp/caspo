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

import os

import multiprocessing as mp
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
            fs = setup_fs.union(nl.union(bl).to_funset())
            instance = ". ".join(map(str, fs)) + ". :- not diff."

            clingo = gringo.Control()
            if configure is not None:
                configure(clingo.conf)
                
            clingo.add("base", [], instance)
            clingo.load(encoding)

            clingo.ground([("base", [])])
            if clingo.solve() == gringo.SolveResult.UNSAT:
                found = True
                behaviors.known_eq[i] += (1 + network.graph['known_eq'])
                break
        
        if not found:
            behaviors.append(network)
        
    return behaviors

def io(networks, setup, processes=1, configure=None):
    n = len(networks)
    if processes > 1 and n > processes:
        pool = mp.Pool(processes)
        lp = int(np.ceil(n / float(processes)))
        
        results = [pool.apply_async(__learn_io__, args=(part,setup,configure)) for part in networks.split(np.arange(lp,n,lp))]
        output = [p.get() for p in results]
        pool.close()
        
        networks = core.LogicalNetworkList.from_hypergraph(networks.hg)
        for l in output:
            networks = networks.union(l)
    
    return __learn_io__(networks, setup, configure)
    
def core_clampings(networks, setup, configure=None):
    root = os.path.dirname(__file__)
    encoding = os.path.join(root, 'encodings/io.lp')
    
    fs = setup.to_funset().union(networks.to_funset())
    instance = ". ".join(map(str, fs)) + ". :- diff. #show clamped/2."

    clingo = gringo.Control()
    clingo.conf.solve.models = '0'
    if configure is not None:
        configure(clingo.conf)
                
    clingo.add("base", [], instance)
    clingo.load(encoding)
    
    clampings = []
    
    clingo.ground([("base", [])])
    clingo.solve(on_model=lambda m: clampings.append(core.Clamping.from_tuples((f.args() for f in m.atoms()))))
    
    return core.ClampingList(clampings)
