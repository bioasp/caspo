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

import os, tempfile, numpy
from collections import defaultdict
from itertools import combinations
from zope import component, interface

from pyzcasp import asp, potassco

from caspo import core, control
from interfaces import *
from impl import *

class BoolLogicNetworkSet2BooleLogicBehaviorSet(core.BooleLogicNetworkSet):
    component.adapts(core.IBooleLogicNetworkSet, core.IDataset, potassco.IGrounderSolver)
    interface.implements(IBooleLogicBehaviorSet)
    
    def __init__(self, networks, dataset, clingo):
        super(BoolLogicNetworkSet2BooleLogicBehaviorSet, self).__init__()
        
        self.networks = networks
        self.clingo = clingo
        self.dataset = dataset
        self.setup = dataset.setup
        self.__core_clampings = set()
        
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
        if self.__core_clampings:
            return self.__core_clampings
        else:
            encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.clingo.grounder)
            clamping = encodings('caspo.analyze.guess')
            fixpoint = encodings('caspo.analyze.fixpoint')
            diff = encodings('caspo.analyze.diff')
            stdin = """
            :- diff.

            #show clamped/2.
            """
            setup = asp.ITermSet(self.dataset.setup)
            instance = setup.union(asp.ITermSet(self))
            clampings = self.clingo.run(stdin, grounder_args=[instance.to_file(), clamping, fixpoint, diff], 
                                               solver_args=["0"], adapter=core.IClamping)
                                               
            self.__core_clampings = set(clampings)
            return self.__core_clampings

    def variances(self):
        n = len(self)
        weights = numpy.zeros(n, dtype=int)
        for i,network in enumerate(self):
            weights[i] = len(network)
        
        setup = self.dataset.setup
        for clamping in setup.iterclampings(self.active_cues):
            row = dict(clamping)
            for inh in setup.inhibitors:
                if inh in row:
                    row[inh + 'i'] = 1
                    del row[inh]
                    
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

    def __io_discovery__(self):
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.clingo.grounder)
        clamping = encodings('caspo.analyze.guess')
        fixpoint = encodings('caspo.analyze.fixpoint')
        diff = encodings('caspo.analyze.diff')
        stdin = """
        :- not diff.
        """
        setup = asp.ITermSet(self.setup)

        printer = component.queryUtility(core.IPrinter)
        if printer:
            printer.pprint("")

        #When the number of networks is large, using @asp.cleanrun with tmp files kills performance. 
        #because a lot of time is needed only for removing the created tmp files (clean_files function).
        TEMP_IO_LP = tempfile.NamedTemporaryFile(delete=False)
        for i, network in enumerate(self.networks):
            found = False
            for eb in self:
                pair = core.BooleLogicNetworkSet([eb, network], False)
                
                instance = setup.union(asp.ITermSet(pair))
                self.clingo.run(stdin, 
                        grounder_args=[instance.to_file(TEMP_IO_LP.name), clamping, fixpoint, diff], 
                        solver_args=["--quiet"])
                    
                if self.clingo.solver.unsat:
                    eb.networks.add(network)
                    found = True
                    break

            if not found:
                self.add(BooleLogicBehavior(network.variables, network.mapping))
            
            if printer:    
                printer.iprint("Searching input-output behaviors... %s behaviors have been found over %s logical networks." % (len(self), i+1))
        
        #explicitly unlink the single tmp file created
        TEMP_IO_LP.close() # this is needed in windows (?)
        os.unlink(TEMP_IO_LP.name)
        if printer:
            printer.pprint("\n")

class LogicalNetworkSet2Stats(object):
    component.adapts(core.ILogicalNetworkSet)
    interface.implements(IStats)
    
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
                yield (clause, target), occu / n
        
    def frequency(self, key):
        clause, target = key
        return self.__occu[target][clause] / float(len(self.networks))
        
    def __mutuals__(self, candidates, mutually):
        pairs = defaultdict(set)
        for (c1,t1),(c2,t2) in combinations(candidates, 2):
            valid = True
            for network in self.networks:
                has_m1 = t1 in network.mapping and c1 in network.mapping[t1]
                has_m2 = t2 in network.mapping and c2 in network.mapping[t2]
                if not mutually(has_m1,has_m2):
                    valid = False
                    break
                    
            if valid:
                pairs[(c1,t1)].add((c2,t2))
                pairs[(c2,t2)].add((c1,t1))
                
        return pairs
        
    def combinatorics(self):
        n = len(self.networks)
        candidates = set()
        for target, clauses in self.__occu.iteritems():
            for clause, occu in clauses.iteritems():
                if occu < n:
                    candidates.add((clause, target))
        
        exclusive = self.__mutuals__(candidates, lambda b1,b2: b1 != b2)
        inclusive = self.__mutuals__(candidates, lambda b1,b2: b1 == b2)
        return exclusive, inclusive
        
class StatsMappings2CsvWriter(object):
    component.adapts(IStats)
    interface.implements(core.ICsvWriter)
    
    def __init__(self, stats):
        self.stats =  stats
        
    def __iter__(self):
        exclusive, inclusive = self.stats.combinatorics()        
        for key, freq in self.stats.frequencies():
            row = dict(key="%s=%s" % key, frequency="%.2f" % freq)
            if key in exclusive:
                row["exclusive"] = ";".join(map(lambda (c,t): "%s=%s" % (c,t), exclusive[key]))
                
            if key in inclusive:
                row["inclusive"] = ";".join(map(lambda (c,t): "%s=%s" % (c,t), inclusive[key]))
        
            yield row
            
    def write(self, filename, path="./"):
        self.writer = component.getUtility(core.ICsvWriter)
        header = ["key","frequency","exclusive","inclusive"]
        self.writer.load(self, header)
        self.writer.write(filename, path)
        
class BooleLogicBehaviorSet2MultiCsvWriter(object):
    component.adapts(IBooleLogicBehaviorSet, core.ITimePoint)
    interface.implements(core.IMultiFileWriter)

    def __init__(self, behaviors, point):
        self.behaviors = behaviors
        self.point = point
        
    def mses(self):
        header = core.ILogicalHeaderMapping(component.getUtility(core.ILogicalNames))
        for behavior, mse in self.behaviors.itermses(self.behaviors.dataset, self.point.time):
            row = component.getMultiAdapter((behavior, header), core.ILogicalMapping)
            row.mapping["MSE"] = "%.4f" % mse
            row.mapping["Networks"] = len(behavior)
            yield row.mapping
        
    def variances(self, header):
        setup = self.behaviors.dataset.setup
        for row in self.behaviors.variances():
            nrow = dict.fromkeys(header, 0)
            for inh in setup.inhibitors:
                if inh + 'i' in row:
                    nrow[inh + 'i'] = row[inh + 'i']
                    
            for sti in setup.stimuli:
                if row[sti] == 1:
                    nrow[sti] = row[sti]
            
            for read in setup.readouts:
                nrow[read] = "%.2f" % row[read]
                
            yield nrow
            
    def core(self, header):
        setup = self.behaviors.dataset.setup        
        for clamping in self.behaviors.core():
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
        writer = core.ICsvWriter(self.behaviors)
        writer.write(filenames[0], path)
        
        writer = component.getUtility(core.ICsvWriter)
        
        header = list(core.ILogicalHeaderMapping(component.getUtility(core.ILogicalNames)))
        header.append("MSE")
        header.append("Networks")
        writer.load(self.mses(), header)
        writer.write(filenames[1], path)
        
        setup = self.behaviors.dataset.setup
        
        header = setup.stimuli + map(lambda i: i+'i', setup.inhibitors) + setup.readouts
        writer.load(self.variances(header), header)
        writer.write(filenames[2], path)
        
        stimuli = self.behaviors.active_cues.intersection(setup.stimuli)
        inhibitors = self.behaviors.active_cues.intersection(setup.inhibitors)
        header =  list(stimuli) + map(lambda i: i+'i', inhibitors)
        writer.load(self.core(header), header)
        writer.write(filenames[3], path)
        
class StrategySet2Stats(object):
    component.adapts(control.IStrategySet)
    interface.implements(IStats)
    
    def __init__(self, strategies):
        self.strategies = strategies
        self.__occu = defaultdict(int)
        for strategy in strategies:
            for lit in strategy:
                self.__occu[lit] += 1
                
    def frequencies(self):
        n = float(len(self.strategies))
        for lit, occu in self.__occu.iteritems():
            yield lit, occu / n
        
    def frequency(self, key):
        return self.__occu[key] / float(len(self.strategies))
        
    def __mutuals__(self, candidates, mutually):
        pairs = defaultdict(set)
        for l1,l2 in combinations(candidates, 2):
            valid = True
            for strategy in self.strategies:
                if not mutually(l1 in strategy, l2 in strategy):
                    valid = False
                    break
                    
            if valid:
                pairs[l1].add(l2)
                pairs[l2].add(l1)
                
        return pairs
        
    def combinatorics(self):
        n = len(self.strategies)
        candidates = set()
        for lit, occu in self.__occu.iteritems():
            if occu < n:
                candidates.add(lit)
        
        exclusive = self.__mutuals__(candidates, lambda b1,b2: b1 != b2)
        inclusive = self.__mutuals__(candidates, lambda b1,b2: b1 == b2)
        return exclusive, inclusive
        