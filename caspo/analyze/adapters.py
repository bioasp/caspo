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
from impl import *

import numpy

class BoolLogicNetworkSet2BooleLogicBehaviorSet(core.BooleLogicNetworkSet):
    component.adapts(core.IBooleLogicNetworkSet, core.IDataset, potassco.IGringoGrounder, potassco.IClaspSolver)
    interface.implements(IBooleLogicBehaviorSet)
    
    def __init__(self, networks, dataset, grounder, solver):
        super(BoolLogicNetworkSet2BooleLogicBehaviorSet, self).__init__()
        
        self.networks = networks
        self.grover = component.getMultiAdapter((grounder, solver), asp.IGrounderSolver)
        self.dataset = dataset
        self.setup = dataset.setup
        
        cues = set(self.dataset.setup.stimuli + self.dataset.setup.inhibitors)
        self.active_cues = set()
        for network in self.networks:
            for formula in network.mapping.itervalues():
                for clause in formula:
                    self.active_cues = self.active_cues.union(map(lambda (l,s): l, filter(lambda (l,s): l in cues, clause)))
    
        self.inactive_cues = cues.difference(self.active_cues)
        self.__io_discovery__()
        
    @asp.cleanrun
    def core(self):
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.grover.grounder)
        clamping = encodings('caspo.analyze.guess')
        fixpoint = encodings('caspo.analyze.fixpoint')
        diff = encodings('caspo.analyze.diff')
        stdin = """
        :- diff.

        #hide.
        #show clamped/2.
        """
        setup = asp.ITermSet(self.dataset.setup)
        instance = setup.union(asp.ITermSet(self))
        self.grover.run(stdin, grounder_args=[instance.to_file(), clamping, fixpoint, diff], solver_args=["0"])
                
        for termset in self.grover:                    
            yield core.IClamping(termset)

    def variances(self):
        n = len(self)
        weights = numpy.zeros(n, dtype=int)
        for i,network in enumerate(self):
            weights[i] = len(network)
        
        setup = self.dataset.setup
        for clamping in setup.iterclampings(self.active_cues):
            row = dict(clamping)
            for readout in setup.readouts:
                predictions = numpy.zeros(n, dtype=int)
                for i,network in enumerate(self):
                    predictions[i] = network.prediction(readout, clamping)
                
                average = numpy.average(predictions, weights=weights)
                variance = numpy.average((predictions-average) ** 2, weights=weights)
                row[readout] = variance
            
            yield row
            
    def mse(self, time):
        n = sum([len(network) for network in self], 0.)            
        predictions = numpy.empty((self.dataset.nexps, len(self.dataset.setup.readouts)))
        observations = numpy.empty((self.dataset.nexps, len(self.dataset.setup.readouts)))
        predictions[:] = numpy.nan
        observations[:] = numpy.nan
        for i, cond, obs in self.dataset.at(time):
            for j, (var, val) in enumerate(obs.iteritems()):
                weight = 0
                for network in self:
                    weight += network.prediction(var, cond) * len(network)
                    
                predictions[i][j] = weight / n
                observations[i][j] = val
        
        rss = numpy.nansum((predictions - observations) ** 2)
        return rss / self.dataset.nobs[time]

    @asp.cleanrun
    def __io_discovery__(self):
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.grover.grounder)
        clamping = encodings('caspo.analyze.guess')
        fixpoint = encodings('caspo.analyze.fixpoint')
        diff = encodings('caspo.analyze.diff')
        stdin = """
        :- not diff.
        """
        setup = asp.ITermSet(self.setup)
        for network in self.networks:
            found = False
            for eb in self:
                pair = core.BooleLogicNetworkSet([eb, network])
                
                instance = setup.union(asp.ITermSet(pair))
                self.grover.run(stdin, 
                        grounder_args=[instance.to_file(), clamping, fixpoint, diff], 
                        solver_args=["--quiet"])
                    
                if self.grover.solver.unsat:
                    eb.networks.add(network)
                    found = True
                    break

            if not found:
                self.add(BooleLogicBehavior(network.variables, network.mapping))

class BooleLogicNetworkSet2StatsMappings(object):
    component.adapts(core.IBooleLogicNetworkSet)
    interface.implements(IStatsMappings)
    
    def __init__(self, networks):
        self.networks = networks    
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
        
class BooleLogicBehaviorSet2MultiCsvWriter(object):
    component.adapts(IBooleLogicBehaviorSet, core.ITimePoint)
    interface.implements(core.IMultiFileWriter)

    def __init__(self, behaviors, point):
        self.behaviors = behaviors
        self.point = point
        self._core_clampings = 0
        
    def variances(self, header):
        setup = self.behaviors.dataset.setup
        for row in self.behaviors.variances():
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
            
    def core(self, header):
        setup = self.behaviors.dataset.setup        
        for clamping in self.behaviors.core():
            self._core_clampings += 1
            dc = dict(clamping)
            nrow = dict.fromkeys(header, 0)
            for inh in self.behaviors.active_cues.intersection(setup.inhibitors):
                if inh in dc:
                    nrow[inh + 'i'] = 1

            for sti in self.behaviors.active_cues.intersection(setup.stimuli):
                if dc[sti] == 1:
                    nrow[sti] = dc[sti]
                    
            yield nrow
        
    def write(self, filenames, path="./"):
        writer = component.getMultiAdapter((self.behaviors, self.behaviors.dataset, self.point), core.ICsvWriter)
        writer.write(filenames[0], path)
        setup = self.behaviors.dataset.setup
        
        writer = component.getUtility(core.ICsvWriter)
        
        header = setup.stimuli + map(lambda i: i+'i', setup.inhibitors) + setup.readouts
        writer.load(self.variances(header), header)
        writer.write(filenames[1], path)
        
        stimuli = self.behaviors.active_cues.intersection(setup.stimuli)
        inhibitors = self.behaviors.active_cues.intersection(setup.inhibitors)
        header =  list(stimuli) + map(lambda i: i+'i', inhibitors)
        writer.load(self.core(header), header)
        writer.write(filenames[2], path)
        
        writer = component.getUtility(core.IFileWriter)
        lines = []
        lines.append("Total Boolean logic networks: %s" % len(self.behaviors.networks))
        lines.append("Total I/O Boolean logic behaviors: %s" % len(self.behaviors))
        lines.append("Weighted MSE: %.4f" % self.behaviors.mse(self.point.time))
        lines.append("Core predictions: %.2f%%" % ((100. * self._core_clampings) / 2**(len(self.behaviors.active_cues))))
        writer.load(lines, "caspo analytics summary")
        writer.write(filenames[3], path)
