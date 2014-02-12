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
    interface.implements(ILogicalBehaviorSet)
    
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

class BooleLogicNetworkSet2StatsMappings(object):
    component.adapts(core.IBooleLogicNetworkSet, asp.IGrounder, asp.ISolver)
    interface.implements(IStatsMappings)
    
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
        pairs = defaultdict(set)
        for (t1,c1),(t2,c2) in combinations(candidates, 2):
            valid = True
            for network in self.networks:
                has_m1 = t1 in network.mapping and c1 in network.mapping[t1]
                has_m2 = t2 in network.mapping and c2 in network.mapping[t2]
                if not mutually(has_m1,has_m2):
                    valid = False
                    break
                    
            if valid:
                pairs[(t1,c1)].add((t2,c2))
                pairs[(t2,c2)].add((t1,c1))
                
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
        
class StatsMappings2CsvWriter(object):
    component.adapts(IStatsMappings)
    interface.implements(core.ICsvWriter)
    
    def __init__(self, stats):
        self.stats =  stats
        
    def __iter__(self):
        exclusive, inclusive = self.stats.combinatorics()        
        for target, clause, freq in self.stats.frequencies():
            row = dict(link="%s=%s" % (str(clause), target), frequency="%.2f" % freq)
            if (target,clause) in exclusive:
                row["exclusive"] = ";".join(map(lambda (t,c): "%s=%s" % (str(c),t), exclusive[(target,clause)]))
                
            if (target,clause) in inclusive:
                row["inclusive"] = ";".join(map(lambda (t,c): "%s=%s" % (str(c),t), inclusive[(target,clause)]))
        
            yield row
            
    def write(self, filename, path="./"):
        self.writer = component.getUtility(core.ICsvWriter)
        header = ["link","frequency","exclusive","inclusive"]
        self.writer.load(self, header)
        self.writer.write(filename, path)

class LogicalNetworkSet2LogicalPredictorSet(object):
    component.adapts(core.IBooleLogicNetworkSet, core.IDataset, potassco.IGringoGrounder, potassco.IClaspSolver)
    interface.implements(ILogicalPredictorSet)
    
    
    def __init__(self, networks, dataset, grounder, solver):
        self.networks = networks
        self.dataset = dataset
        self.grover = component.getMultiAdapter((grounder, solver), asp.IGrounderSolver)
        
        cues = set(self.dataset.setup.stimuli + self.dataset.setup.inhibitors)
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
        setup = asp.ITermSet(self.dataset.setup)
        instance = setup.union(asp.ITermSet(self.networks))
        self.grover.run(stdin, grounder_args=[instance.to_file(), clamping, fixpoint, diff], solver_args=["0"])
                
        for termset in self.grover:                    
            yield core.IClamping(termset)
            
    def variances(self):
        n = len(self.networks)            
        for clamping in self.dataset.setup.iterclampings(self.active_cues):
            row = dict(clamping)
            for readout in self.dataset.setup.readouts:
                predictions = numpy.zeros(n, dtype=int)
                for i,network in enumerate(self.networks):
                    predictions[i] = network.prediction(readout, clamping)
                
                average = numpy.average(predictions)
                variance = numpy.average((predictions-average) ** 2)
                row[readout] = variance
            
            yield row

    def itermse(self, time):            
        predictions = numpy.empty((self.dataset.nexps, len(self.dataset.setup.readouts)))
        observations = numpy.empty((self.dataset.nexps, len(self.dataset.setup.readouts)))
        predictions[:] = numpy.nan
        observations[:] = numpy.nan
        for network in self.networks:
            for i, cond, obs in self.dataset.at(time):
                for j, (var, val) in enumerate(obs.iteritems()):
                    predictions[i][j] = network.prediction(var, cond)
                    observations[i][j] = val
        
            rss = numpy.nansum((predictions - observations) ** 2)
            yield rss / midas.nobs[time]

            
    def mse(self, time):
        n = float(len(self.networks))            
        predictions = numpy.empty((self.dataset.nexps, len(self.dataset.setup.readouts)))
        observations = numpy.empty((self.dataset.nexps, len(self.dataset.setup.readouts)))
        predictions[:] = numpy.nan
        observations[:] = numpy.nan
        for i, cond, obs in self.dataset.at(time):
            for j, (var, val) in enumerate(obs.iteritems()):
                weight = 0
                for network in self.networks:
                    weight += network.prediction(var, cond)
                    
                predictions[i][j] = weight / n
                observations[i][j] = val
        
        rss = numpy.nansum((predictions - observations) ** 2)
        return rss / self.dataset.nobs[time]
        

class LogicalBehaviorSet2LogicalPredictorSet(LogicalNetworkSet2LogicalPredictorSet):
    component.adapts(ILogicalBehaviorSet, core.IDataset, potassco.IGringoGrounder, potassco.IClaspSolver)
    
    def variances(self):
        n = len(self.networks)
        weights = numpy.zeros(n, dtype=int)
        for i,network in enumerate(self.networks):
            weights[i] = len(network)
        
        setup = self.dataset.setup
        for clamping in setup.iterclampings(self.active_cues):
            row = dict(clamping)
            for readout in setup.readouts:
                predictions = numpy.zeros(n, dtype=int)
                for i,network in enumerate(self.networks):
                    predictions[i] = network.prediction(readout, clamping)
                
                average = numpy.average(predictions, weights=weights)
                variance = numpy.average((predictions-average) ** 2, weights=weights)
                row[readout] = variance
            
            yield row
            
    def mse(self, time):
        n = sum([len(network) for network in self.networks], 0.)            
        predictions = numpy.empty((self.dataset.nexps, len(self.dataset.setup.readouts)))
        observations = numpy.empty((self.dataset.nexps, len(self.dataset.setup.readouts)))
        predictions[:] = numpy.nan
        observations[:] = numpy.nan
        for i, cond, obs in self.dataset.at(time):
            for j, (var, val) in enumerate(obs.iteritems()):
                weight = 0
                for network in self.networks:
                    weight += network.prediction(var, cond) * len(network)
                    
                predictions[i][j] = weight / n
                observations[i][j] = val
        
        rss = numpy.nansum((predictions - observations) ** 2)
        return rss / self.dataset.nobs[time]

class LogicalPredictorSet2MultiCsvWriter(object):
    component.adapts(ILogicalPredictorSet, core.ITimePoint)
    interface.implements(core.IMultiCsvWriter)

    def __init__(self, predictor, point):
        self.predictor = predictor
        self.point = point
        
    def variances(self):
        setup = self.predictor.dataset.setup
        header =  setup.stimuli + map(lambda i: i+'i', setup.inhibitors) + setup.readouts
        
        for row in self.predictor.variances():
            nrow = dict.fromkeys(header, 0)
            for inh in setup.inhibitors:
                if inh in row:
                    nrow[inh + 'i'] = 1
                    
            for sti in setup.stimuli:
                if row[sti] == 1:
                    nrow[sti] = row[sti]
            
            for read in setup.readouts:
                nrow[read] = "%.2f" % row[read]
                
            yield nrow
        
    def write(self, filenames, path="./"):
        self.writer = component.getUtility(core.ICsvWriter)
        
        setup = self.predictor.dataset.setup
        header =  setup.stimuli + map(lambda i: i+'i', setup.inhibitors) + setup.readouts

        self.writer.load(self.variances(), header)
        self.writer.write(filenames[1], path)
