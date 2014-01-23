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
from zope import component

from pyzcasp import asp, potassco

from interfaces import *

class Midas2Dataset(object):
    component.adapts(IMidasReader, IDiscretization, ITimePoint)
    interface.implements(IDataset)
    
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

class Dataset2TermSet(asp.TermSetAdapter):
    component.adapts(IDataset)
    
    def __init__(self, dataset):
        super(Dataset2TermSet, self).__init__()
        
        self._termset = self._termset.union(asp.interfaces.ITermSet(dataset.setup))
        self._termset.add(asp.Term('dfactor', [dataset.factor]))
        
        for i, cond, obs in dataset:
            for name, value in cond.iteritems():
                self._termset.add(asp.Term('exp', [i, name, value]))
                
            for name, value in obs.iteritems():
                self._termset.add(asp.Term('obs', [i, name, value]))


class GraphDataset2TermSet(asp.TermSetAdapter):
    component.adapts(core.IGraph, IDataset)
    
    def __init__(self, graph, dataset):
        super(GraphDataset2TermSet, self).__init__()
        
        compressor = component.getUtility(IGraphCompressor)
        names = component.getUtility(core.ILogicalNames)
        names.load(compressor.compress(graph, dataset.setup))
        
        self._termset = asp.interfaces.ITermSet(names)
        self._termset = self._termset.union(asp.ITermSet(dataset))

class PotasscoLearner(object):
    component.adapts(asp.ITermSet, potassco.IGringoGrounder, potassco.IClaspSolver)
    interface.implements(ILearner)
    
    def __init__(self, termset, gringo, clasp):
        super(PotasscoLearner, self).__init__()
        self.termset = termset
        self.gringo = gringo
        self.clasp = clasp
        self.grover = component.getMultiAdapter((gringo, clasp), asp.IGrounderSolver)
                
    @asp.cleanrun
    def learn(self, fit=0, size=0):
        reg = component.getUtility(asp.IEncodingRegistry, 'caspo')
        programs = [self.termset.to_file(), reg.get_encoding('learn.full')]
        
        self.grover.run("#hide. #show dnf/2.", grounder_args=programs, solver_args=["--quiet=1"])
        optimum = iter(self.grover).next()
        tolerance = ['-c maxrss=%s' % int(optimum.score[0] + optimum.score[0]*fit), '-c maxsize=%s' % (optimum.score[1] + size)]
        
        self.grover.run("#hide. #show dnf/2.", grounder_args=programs + tolerance, solver_args=["--opt-ignore", "0"])
        
    def __iter__(self):
        for termset in self.grover:
            yield core.ILogicalNetwork(termset)
