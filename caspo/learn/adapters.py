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
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-
import os
from collections import defaultdict

from zope import component, interface

from pyzcasp import asp, potassco

from caspo import core
from interfaces import *

class Midas2Dataset(object):
    component.adapts(IMidasReader, IDiscretization, ITimePoint)
    interface.implements(IDataset, core.IClampingList)
    
    def __init__(self, midas, discretize, point):
        super(Midas2Dataset, self).__init__()
        if point.time not in midas.times:
            raise ValueError("The time-point %s does not exists in the MIDAS file. \
                              Available time-points are: %s" % (point.time, list(midas.times)))
        self.cues = []
        self.readouts = []
        
        self.setup = core.Setup(midas.stimuli, midas.inhibitors, midas.readouts)
        self.factor = discretize.factor
        
        for cond, obs in midas:
            self.cues.append(cond)
            self.readouts.append(dict([(r, discretize(v)) for r,v in obs[point.time].iteritems()]))
            
    def __iter__(self):
        for i, (cond, obs) in enumerate(zip(self.cues, self.readouts)):
            yield i, cond, obs
            
    @property
    def clampings(self):
        return self.cues

class Dataset2TermSet(asp.TermSetAdapter):
    component.adapts(IDataset)
    
    def __init__(self, dataset):
        super(Dataset2TermSet, self).__init__()
        
        self._termset = self._termset.union(asp.interfaces.ITermSet(dataset.setup))
        self._termset.add(asp.Term('dfactor', [dataset.factor]))
        
        for i, cond, obs in dataset:
            self._termset.add(asp.Term('exp', [i]))
            self._termset = self._termset.union(component.getMultiAdapter((cond, dataset), asp.ITermSet))
            
            for name, value in obs.iteritems():
                self._termset.add(asp.Term('obs', [i, name, value]))

class GraphDataset2TermSet(asp.TermSetAdapter):
    component.adapts(core.IGraph, IDataset)
    
    def __init__(self, graph, dataset):
        super(GraphDataset2TermSet, self).__init__()
        
        names = component.getUtility(core.ILogicalNames)
        names.load(graph)
        
        self._termset = asp.interfaces.ITermSet(names)
        self._termset = self._termset.union(asp.ITermSet(dataset))

class PotasscoLearner(object):
    component.adapts(asp.ITermSet, potassco.IGringoGrounder, potassco.IClaspSolver)
    interface.implements(ILearner, core.IBooleLogicNetworkSet)
    
    def __init__(self, termset, gringo, clasp):
        super(PotasscoLearner, self).__init__()
        self.termset = termset
        self.grover = component.getMultiAdapter((gringo, clasp), asp.IGrounderSolver)
        self._networks = set()
                
    @asp.cleanrun
    def learn(self, fit=0, size=0):
        self._networks = set()
        self._len_networks = 0
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.grover.grounder)
        
        guess = encodings('caspo.learn.guess')
        fixpoint = encodings('caspo.learn.fixpoint')
        rss = encodings('caspo.learn.rss')
        opt = encodings('caspo.learn.opt')
        rescale = encodings('caspo.learn.rescale')
        enum = encodings('caspo.learn.enum')
        
        programs = [self.termset.to_file(), guess, fixpoint, rss, opt]
        solutions = self.grover.run("#hide. #show formula/2. #show dnf/2. #show clause/3.", 
                            grounder_args=programs, 
                            solver_args=["--quiet=1", "--conf=jumpy", "--opt-hier=2", "--opt-heu=2"],
                            lazy=False)
        
        opt_size = solutions[0].score[1]
        
        programs = [self.termset.union(solutions[0]).to_file(), fixpoint, rss, rescale]
        solutions = self.grover.run(grounder_args=programs, solver_args=["--quiet=0,1"], lazy=False)
        
        opt_rss = solutions[0].score[0]
        
        programs = [self.termset.to_file(), guess, fixpoint, rss, enum]
        tolerance = ['-c maxrss=%s' % int(opt_rss + opt_rss*fit), '-c maxsize=%s' % (opt_size + size)]
        
        self.grover.run("#hide. #show dnf/2.", 
                grounder_args=programs + tolerance, 
                solver_args=["--opt-ignore", "0", "--conf=jumpy"])
                
        self._len_networks = self.grover.solver.__getstats__()['Models']
                
    def __len__(self):
        return self._len_networks
        
    def __iter__(self):
        if self._networks:
            for network in self._networks:
                yield network
        else:
            names = component.getUtility(core.ILogicalNames)
            for termset in self.grover:
                network = core.IBooleLogicNetwork(termset)
                names.add(network.mapping.itervalues())
                self._networks.add(network)
                yield network
            
class CompressedGraph(core.GraphAdapter):
    component.adapts(core.IGraph, core.ISetup)
    
    def __init__(self, graph, setup):
        super(CompressedGraph, self).__init__()
        self._forward = defaultdict(set)
        self._backward = defaultdict(set)
        
        designated = setup.stimuli + setup.inhibitors + setup.readouts
        marked = graph.nodes.difference(designated)
    
        for source,target,sign in graph.edges:
            self._forward[source].add((target, sign))
            self._backward[target].add((source, sign))

        compressed = self.__compress(marked)

        for source, targets in self._forward.iteritems():
            for target, sign in targets:
                self.graph.edges.add((source, target, sign))
        
        self.graph.nodes = graph.nodes.difference(compressed)
        
    def __compress(self, marked, compressed=set()):
        icompressed = set()

        for node in sorted(marked):
            backward = list(self._backward[node])
            forward = list(self._forward[node])
            
            if not backward or (len(backward) == 1 and not filter(lambda e: e[0] == backward[0][0], forward)):
                self.__merge_source_targets(node)
                icompressed.add(node)
            
            elif not forward or (len(forward) == 1 and not filter(lambda e: e[0] == forward[0][0], backward)):
                self.__merge_target_sources(node)
                icompressed.add(node)
            
        if icompressed:
            return self.__compress(marked.difference(icompressed), compressed.union(icompressed))
        else:
            return compressed
            
    def __merge_source_targets(self, node):
        source = None
        if self._backward[node]:
            source, sign = self._backward[node].pop()
            self._forward[source].remove((node, sign))
                
        for target,s in self._forward[node]:
            if source:
                self._forward[source].add((target, sign*s))
                self._backward[target].add((source, sign*s))
            
            self._backward[target].remove((node, s))
                    
        del self._forward[node]

    def __merge_target_sources(self, node):
        target = None
        if self._forward[node]:
            target, sign = self._forward[node].pop()
            self._backward[target].remove((node, sign))

        for source, s in self._backward[node]:
            if target:
                self._forward[source].add((target, sign*s))
                self._backward[target].add((source, sign*s))
                
            self._forward[source].remove((node, s))

        del self._backward[node]

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
        clamping = encodings('caspo.learn.guess-clamping')
        fixpoint = encodings('caspo.learn.fixpoint-models')
        diff = encodings('caspo.learn.diff')
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
        return len(self.networks)

class BooleLogicNetworkSet2Analytics(object):
    component.adapts(core.IBooleLogicNetworkSet, asp.IGrounder, asp.ISolver)
    interface.implements(IAnalytics)
    
    def __init__(self, networks, grounder, solver):
        self.networks = networks
        self.grounder = grounder
        self.solver = solver
        
        self.__occu = defaultdict(lambda: defaultdict(int))
        self.nmodels = 0
        
        for network in networks:
            self.nmodels += 1
            for target, formula in network.mapping.iteritems():
                for clause in formula:
                    self.__occu[target][clause] += 1
        
    def frequencies(self):
        for target, clauses in self.__occu.iteritems():
            for clause, occu in clauses.iteritems():
                yield target, clause, occu / float(self.nmodels)
        
    def frequency(self, clause, target):
        return self.__occu[target][clause] / float(self.nmodels)
        
    @asp.cleanrun
    def combinatorics(self):
        pass


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
        clamping = encodings('caspo.learn.guess-clamping')
        fixpoint = encodings('caspo.learn.fixpoint-models')
        diff = encodings('caspo.learn.diff')
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
        
    def mse(self, midas, time, wfn=None):
        if not wfn:
            wfn = lambda net: 1
            
        rss = 0
        norm = len(self.networks)
        for cond, obs in midas:
            for var, val in obs[time].iteritems():
                weight = 0.
                for network in self.networks:
                    weight += network.prediction(var, cond) * wfn(network)
                
                rss += pow(weight / norm - val, 2)
        
        return rss / midas.nobs[time]
