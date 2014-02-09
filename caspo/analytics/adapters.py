# Copyright (c) 2014, Santiago Videla
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
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

from collections import defaultdict
from itertools import combinations
from zope import component, interface

from pyzcasp import asp, potassco

from caspo import core
from interfaces import *

import numpy

class BooleLogicNetwork2LogicalBehavior(object):
    component.adapts(core.IBooleLogicNetwork)
    interface.implements(ILogicalBehavior)
    
    def __init__(self, network):
        self.representative = network
        self.networks = set()
        
    def __len__(self):
        return 1 + len(self.networks)
        
    @property
    def variables(self):
        return self.representative.variables

    @property
    def mapping(self):
        return self.representative.mapping
        
    def prediction(self, var, clamping):
        return self.representative.prediction(var, clamping)
        
class LogicalNetworkSet2LogicalBehaviorSet(object):
    component.adapts(core.IBooleLogicNetworkSet, core.ISetup, potassco.IGringoGrounder, potassco.IClaspSolver)
    interface.implements(ILogicalBehaviorSet, core.IBooleLogicNetworkSet)
    
    def __init__(self, networks, setup, grounder, solver):
        self.behaviors = set()
        self.networks = networks
        
        self.grover = component.getMultiAdapter((grounder, solver), asp.IGrounderSolver)
        self.setup = setup
        self.__io_discovery__()

    @asp.cleanrun
    def __io_discovery__(self):
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.grover.grounder)
        clamping = encodings('caspo.analytics.guess')
        fixpoint = encodings('caspo.analytics.fixpoint')
        diff = encodings('caspo.analytics.diff')
        stdin = """
        :- not diff.
        """
        setup = asp.ITermSet(self.setup)
        for network in self.networks:
            found = False
            for eb in self.behaviors:
                pair = core.BooleLogicNetworkSet([eb.representative, network])
                
                instance = setup.union(asp.ITermSet(pair))
                self.grover.run(stdin, 
                        grounder_args=[instance.to_file(), clamping, fixpoint, diff], 
                        solver_args=["--quiet"])
                    
                if self.grover.solver.unsat:
                    eb.networks.add(network)
                    found = True
                    break

            if not found:
                self.behaviors.add(ILogicalBehavior(network))
        
    def __iter__(self):
        return iter(self.behaviors)
        
    def __len__(self):
        return len(self.behaviors)

class BooleLogicNetworkSet2Analytics(object):
    component.adapts(core.IBooleLogicNetworkSet, asp.IGrounder, asp.ISolver)
    interface.implements(IAnalytics)
    
    def __init__(self, networks, grounder, solver):
        self.networks = networks
        self.grounder = grounder
        self.solver = solver
        
        self.__occu = defaultdict(lambda: defaultdict(int))
        
        for network in networks:
            for target, formula in network.mapping.iteritems():
                for clause in formula:
                    self.__occu[target][clause] += 1
        
    def frequencies(self):
        n = float(len(self.networks))
        for target, clauses in self.__occu.iteritems():
            for clause, occu in clauses.iteritems():
                yield target, clause, occu / n
        
    def frequency(self, clause, target):
        return self.__occu[target][clause] / float(len(self.networks))
        
    def __mutuals__(self, candidates, mutually):
        pairs = set()
        for (t1,c1),(t2,c2) in combinations(candidates, 2):
            valid = True
            for network in self.networks:
                has_m1 = t1 in network.mapping and c1 in network.mapping[t1]
                has_m2 = t2 in network.mapping and c2 in network.mapping[t2]
                if not mutually(has_m1,has_m2):
                    valid = False
                    break
                    
            if valid:
                pairs.add(((t1,c1),(t2,c2)))
                
        return pairs
        
    def combinatorics(self):
        n = len(self.networks)
        candidates = set()
        for target, clauses in self.__occu.iteritems():
            for clause, occu in clauses.iteritems():
                if occu < n:
                    candidates.add((target, clause))
        
        exclusive = self.__mutuals__(candidates, lambda b1,b2: b1 != b2)
        inclusive = self.__mutuals__(candidates, lambda b1,b2: b1 == b2)
        return exclusive, inclusive


class LogicalNetworkSet2LogicalPredictorSet(object):
    component.adapts(core.IBooleLogicNetworkSet, core.ISetup, potassco.IGringoGrounder, potassco.IClaspSolver)
    interface.implements(ILogicalPredictorSet)
    
    
    def __init__(self, networks, setup, grounder, solver):
        self.networks = networks
        self.setup = setup
        self.grover = component.getMultiAdapter((grounder, solver), asp.IGrounderSolver)
        
        cues = set(self.setup.stimuli + self.setup.inhibitors)
        self.active_cues = set()
        for network in self.networks:
            for formula in network.mapping.itervalues():
                for clause in formula:
                    self.active_cues = self.active_cues.union(map(lambda (l,s): l, filter(lambda (l,s): l in cues, clause)))
    
        self.inactive_cues = cues.difference(self.active_cues)
        
    @asp.cleanrun
    def core(self):
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.grover.grounder)
        clamping = encodings('caspo.analytics.guess')
        fixpoint = encodings('caspo.analytics.fixpoint')
        diff = encodings('caspo.analytics.diff')
        stdin = """
        :- diff.

        #hide.
        #show clamped/2.
        """
        setup = asp.ITermSet(self.setup)
        instance = setup.union(asp.ITermSet(self.networks))
        self.grover.run(stdin, grounder_args=[instance.to_file(), clamping, fixpoint, diff], solver_args=["0"])
                
        for termset in self.grover:                    
            yield core.IClamping(termset)
            
    def variances(self, fn=None):
        fn = fn or (lambda net: 1)
        n = len(self.networks)
        weights = numpy.zeros(n, dtype=int)
        for i,network in enumerate(self.networks):
            weights[i] = fn(network)
            
        for clamping in self.setup.iterclampings(self.active_cues):
            row = {}
            for readout in self.setup.readouts:
                predictions = numpy.zeros(n, dtype=int)
                for i,network in enumerate(self.networks):
                    predictions[i] = network.prediction(readout, clamping)
                
                average = numpy.average(predictions, weights=weights)
                variance = numpy.average((predictions-average) ** 2, weights=weights)
                row[readout] = variance
            
            yield row

    def itermse(self, midas, time):            
        predictions = numpy.empty((midas.nexps, len(midas.readouts)))
        observations = numpy.empty((midas.nexps, len(midas.readouts)))
        predictions[:] = numpy.nan
        observations[:] = numpy.nan
        for network in self.networks:
            for i, (cond, obs) in enumerate(midas):
                for j, (var, val) in enumerate(obs[time].iteritems()):
                    predictions[i][j] = network.prediction(var, cond)
                    observations[i][j] = val
        
            rss = numpy.nansum((predictions - observations) ** 2)
            yield rss / midas.nobs[time]

            
    def mse(self, midas, time, fn=None):
        fn = fn or (lambda net: 1)
        n = len(self.networks)

        norm = 0.
        for network in self.networks:
            norm += fn(network)
            
        predictions = numpy.empty((midas.nexps, len(midas.readouts)))
        observations = numpy.empty((midas.nexps, len(midas.readouts)))
        predictions[:] = numpy.nan
        observations[:] = numpy.nan
        for i, (cond, obs) in enumerate(midas):
            for j, (var, val) in enumerate(obs[time].iteritems()):
                weight = 0
                for network in self.networks:
                    weight += network.prediction(var, cond) * fn(network)
                    
                predictions[i][j] = weight / norm
                observations[i][j] = val
        
        rss = numpy.nansum((predictions - observations) ** 2)
        return rss / midas.nobs[time]
