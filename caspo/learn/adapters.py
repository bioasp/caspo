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
from zope import component, interface

from pyzcasp import asp, potassco

from caspo import core
from interfaces import *

class Midas2Dataset(object):
    component.adapts(IMidasReader, IDiscretization, ITimePoint)
    interface.implements(IDataset, core.IClampingList)
    
    def __init__(self, midas, discretize, point):
        super(Midas2Dataset, self).__init__()
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
        names.load(component.getMultiAdapter((graph, dataset.setup), core.IGraph))
        
        self._termset = asp.interfaces.ITermSet(names)
        self._termset = self._termset.union(asp.ITermSet(dataset))

class PotasscoLearner(object):
    component.adapts(asp.ITermSet, potassco.IGringoGrounder, potassco.IClaspSolver)
    interface.implements(ILearner)
    
    def __init__(self, termset, gringo, clasp):
        super(PotasscoLearner, self).__init__()
        self.termset = termset
        self.clasp = clasp
        self.grover = component.getMultiAdapter((gringo, clasp), asp.IGrounderSolver)
                
    @asp.cleanrun
    def learn(self, fit=0, size=0):
        reg = component.getUtility(asp.IEncodingRegistry, 'caspo')

        guess = reg.get_encoding('learn.guess')
        fixpoint = reg.get_encoding('learn.fixpoint')
        rss = reg.get_encoding('learn.rss')
        
        programs = [self.termset.to_file(), guess, fixpoint, rss, reg.get_encoding('learn.opt')]
        self.grover.run("#hide. #show formula/2. #show dnf/2. #show clause/3.", grounder_args=programs, solver_args=["--quiet=1", "--conf=jumpy", "--opt-hier=2", "--opt-heu=2"])
        optimum = iter(self.grover).next()
        opt_size = optimum.score[1]
        
        programs = [self.termset.union(optimum).to_file(), fixpoint, rss, reg.get_encoding('learn.rescale')]
        self.grover.run(grounder_args=programs, solver_args=["--quiet=0,1"])
        optimum = iter(self.grover).next()
        opt_rss = optimum.score[0]
        
        programs = [self.termset.to_file(), guess, fixpoint, rss, reg.get_encoding('learn.enum')]
        tolerance = ['-c maxrss=%s' % int(opt_rss + opt_rss*fit), '-c maxsize=%s' % (opt_size + size)]
        
        self.grover.run("#hide. #show dnf/2.", grounder_args=programs + tolerance, solver_args=["--opt-ignore", "0", "--conf=jumpy"])
        
    def __iter__(self):
        for termset in self.grover:
            network = core.ILogicalNetwork(termset)
            interface.directlyProvides(network, core.IBooleLogicNetwork)
            yield network
