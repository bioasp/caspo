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

import math, os, logging
import itertools as it
from functools import partial
from random import randint

from sklearn.metrics import mean_squared_error
import numpy as np

import gringo

from caspo import core

class Learner(object):
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
        
        root = os.path.dirname(__file__)
        self.encodings = {
            'guess':    os.path.join(root, 'encodings/gringo4/guess.lp'),
            'fixpoint': os.path.join(root, 'encodings/gringo4/fixpoint.lp'),
            'rss':      os.path.join(root, 'encodings/gringo4/residual.lp'),
            'opt':      os.path.join(root, 'encodings/gringo4/optimization.lp'),
            'enum':     os.path.join(root, 'encodings/gringo4/enumeration.lp'),
            'random':   os.path.join(root, 'encodings/gringo4/random.lp')
        }
        
        self.logger = logging.getLogger("caspo")
        
    def round(self, factor, value):
        return int(round(factor*value))
        
    def ceil(self, factor, value):
        return int(math.ceil(factor*value))

    def floor(self, factor, value):
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
        encodings = ['guess', 'fixpoint', 'rss']
        if self.optimum is None:
            clingo = self.__get_clingo__(encodings + ['opt'])
            if configure is not None:
                configure(clingo.conf)
        
            clingo.ground([("base", [])])
            clingo.solve(on_model=self.__keep_last__)

            self.logger.info("Optimum logical network learned in %.4fs" % clingo.stats['time_total'])
            
            tuples = (f.args() for f in self.last)
            self.optimum = core.LogicalNetwork.from_hypertuples(self.hypergraph, tuples)
            
        ds = self.dataset
        predictions = self.optimum.predictions(ds.clampings, ds.readouts.columns).values
        
        readouts = ds.readouts.values
        pos = ~np.isnan(readouts)

        rss = np.sum((np.vectorize(self.discrete)(readouts[pos]) - predictions[pos]*self.factor)**2)
        
        self.logger.info("Optimum logical networks has MSE %.4f and size %s" % 
                            (mean_squared_error(readouts[pos],predictions[pos]), self.optimum.size))
        
        self.networks = core.LogicalNetworkList.from_hypergraph(self.hypergraph)

        args = ['-c maxrss=%s' % int(rss + rss*fit), '-c maxsize=%s' % (self.optimum.size + size)]

        clingo = self.__get_clingo__(encodings + ['enum'], args)
        clingo.conf.solve.models = '0'
        if configure is not None:
            configure(clingo.conf)
                
        clingo.ground([("base", [])])
        clingo.solve(on_model=self.__save__)
        
        self.logger.info("%s (nearly) optimal logical networks learned in %.4fs" % (len(self.networks), clingo.stats['time_total']))
        
    def random(self, n=1, size=(28,30), nand=(2,3), maxin=2):
        args = ['-c minsize=%s' % size[0], '-c maxsize=%s' % size[1], 
                '-c minnand=%s' % nand[0], '-c maxnand=%s' % nand[1], '-c maxin=%s' % maxin]
        encodings = ['guess', 'random']
        
        clingo = self.__get_clingo__(args, encodings)
        clingo.conf.solve.models = str(n)
        clingo.conf.solver.seed = str(randint(0,32767))
        clingo.conf.solver.sign_def = '3'
        
        clingo.ground([("base", [])])
        clingo.solve(on_model=partial(self.__save__, False))
