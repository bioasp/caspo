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
from zope import component, interface

from pyzcasp import asp, potassco

from caspo import core
from interfaces import *

class Sif2Graph(core.GraphAdapter):
    component.adapts(core.IFileReader)
    
    def __init__(self, sif):
        super(Sif2Graph, self).__init__()
                
        for line in sif:
            line = line.strip()
            if line:
                try:
                    source, rel, target = line.split('\t')
                    sign = int(rel)
                except Exception, e:
                    raise IOError("Cannot read line %s in SIF file: %s" % (line, str(e)))
                    
                self.graph.nodes.add(source)
                self.graph.nodes.add(target)
                self.graph.edges.add((source,target,sign))

class Dataset2DiscreteDataset(object):
    component.adapts(core.IDataset, IDiscretization)
    interface.implements(IDiscreteDataset)
    
    def __init__(self, dataset, discretize):
        self.dataset = dataset
        self.discretize = discretize
        
    def at(self, time):
        for i, cues, obs in self.dataset.at(time):
            yield i, cues, dict(map(lambda (r,v): (r, self.discretize(v)), obs.iteritems()))
            

class TermSet2BooleLogicNetwork(object):
    component.adapts(asp.ITermSet)
    interface.implements(core.IBooleLogicNetwork)
    
    def __init__(self, termset):
        names = component.getUtility(core.ILogicalNames)
        mapping = defaultdict(set)
        for term in termset:
            if term.pred == 'dnf':
                mapping[names.variables[term.arg(0)]].add(names.clauses[term.arg(1)])
        
        self._network = core.BooleLogicNetwork(names.variables, mapping)
        names.add(self._network.mapping.itervalues())
        
    @property
    def variables(self):
        return self._network.variables
    
    @property
    def mapping(self):
        return self._network.mapping
    
    def prediction(self, var, clamping):
        return self._network.prediction(var, clamping)


class Dataset2TermSet(asp.TermSetAdapter):
    component.adapts(core.ITimePoint, IDiscreteDataset)
    
    def __init__(self, point, dd):
        super(Dataset2TermSet, self).__init__()
        
        self._termset = self._termset.union(asp.interfaces.ITermSet(dd.dataset.setup))
        self._termset.add(asp.Term('dfactor', [dd.discretize.factor]))
        
        for i, cond, obs in dd.at(point.time):
            self._termset.add(asp.Term('exp', [i]))
            self._termset = self._termset.union(component.getMultiAdapter((cond, dd.dataset), asp.ITermSet))
            
            for name, value in obs.iteritems():
                self._termset.add(asp.Term('obs', [i, name, value]))

class GraphDataset2TermSet(asp.TermSetAdapter):
    component.adapts(core.IGraph, core.ITimePoint, IDiscreteDataset)
    
    def __init__(self, graph, point, dd):
        super(GraphDataset2TermSet, self).__init__()
        
        names = component.getUtility(core.ILogicalNames)
        names.load(graph)
        
        self._termset = component.getMultiAdapter((point, dd), asp.ITermSet)
        self._termset = self._termset.union(asp.interfaces.ITermSet(names))

class PotasscoLearner(object):
    component.adapts(asp.ITermSet, potassco.IGrounderSolver)
    interface.implements(ILearner)
    
    def __init__(self, termset, solver):
        super(PotasscoLearner, self).__init__()
        self.termset = termset
        self.grover = solver
        self._networks = core.BooleLogicNetworkSet()
                
    @asp.cleanrun
    def learn(self, fit=0, size=0):
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.grover.grounder)

        grounder_args = component.getUtility(asp.IArgumentRegistry).arguments(self.grover.grounder)
        solver_args = component.getUtility(asp.IArgumentRegistry).arguments(self.grover.solver)
        
        guess = encodings('caspo.learn.guess')
        fixpoint = encodings('caspo.learn.fixpoint')
        rss = encodings('caspo.learn.rss')
        opt = encodings('caspo.learn.opt')
        rescale = encodings('caspo.learn.rescale')
        enum = encodings('caspo.learn.enum')
        
        programs = [self.termset.to_file(), guess, fixpoint, rss, opt]
        solutions = self.grover.run("#show formula/2. #show dnf/2. #show clause/3.", 
                            grounder_args=programs, 
                            solver_args=solver_args('caspo.learn.opt'))

        opt_size = solutions[0].score[1]

        programs = [self.termset.union(solutions[0]).to_file(), fixpoint, rss, rescale]
        solutions = self.grover.run(grounder_args=programs, solver_args=solver_args('caspo.learn.rescale'))

        opt_rss = solutions[0].score[0]
        
        programs = [self.termset.to_file(), guess, fixpoint, rss, enum]
        tolerance = map(lambda arg: arg.format(rss=int(opt_rss + opt_rss*fit), size=(opt_size + size)), grounder_args('caspo.learn.enum'))
        networks = self.grover.run("#show dnf/2.", 
                grounder_args=programs + tolerance, 
                solver_args=solver_args('caspo.learn.enum'), adapter=core.IBooleLogicNetwork)
        
        return core.BooleLogicNetworkSet(networks, update_names=False)
               
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

class BooleLogicNetworkSet2CsvWriter(object):
    component.adapts(core.IBooleLogicNetworkSet, core.IDataset, core.ITimePoint)
    interface.implements(core.ICsvWriter)

    def __init__(self, networks, dataset, point):
        self.networks = networks
        self.dataset = dataset
        self.point = point
        self._nheader = core.ILogicalHeaderMapping(component.getUtility(core.ILogicalNames))
            
    def mses(self):
        for network, mse in self.networks.itermses(self.dataset, self.point.time):
            row = component.getMultiAdapter((network, self._nheader), core.ILogicalMapping)
            row.mapping["MSE"] = "%.4f" % mse
            yield row.mapping
        
    def write(self, filename, path="./", quiet=False):
        self.writer = component.getUtility(core.ICsvWriter)
        header = list(self._nheader)
        header.append("MSE")
        
        self.writer.load(self.mses(), header)
        self.writer.write(filename, path, quiet)
