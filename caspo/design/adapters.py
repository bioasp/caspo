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
import itertools as it
from math import log
from collections import defaultdict

from zope import component
from pyzcasp import asp, potassco

from caspo import core
from interfaces import *

class NetworksSetup2TermSet(asp.TermSetAdapter):
    component.adapts(core.IBooleLogicNetworkSet, core.ISetup)
    
    def __init__(self, networks, setup):
        super(NetworksSetup2TermSet, self).__init__()
        
        self._termset = asp.ITermSet(networks)
        self._termset = self._termset.union(asp.ITermSet(setup))

class NetworksSetupClampings2TermSet(asp.TermSetAdapter):
    component.adapts(core.IBooleLogicNetworkSet, core.ISetup, core.IClampingList)
    
    def __init__(self, networks, setup, clist):
        super(NetworksSetupClampings2TermSet, self).__init__()
        
        self._termset = asp.ITermSet(networks)
        self._termset = self._termset.union(asp.ITermSet(setup))
        
        for c in clist.clampings:
            self._termset = self._termset.union(component.getMultiAdapter((c, clist, asp.Term('listed')), asp.ITermSet))

class PotasscoDesigner(object):
    component.adapts(asp.ITermSet, potassco.IClingo)
    interface.implements(IDesigner)
    
    def __init__(self, termset, clingo):
        self.termset = termset
        self.clingo = clingo
        
    @asp.cleanrun
    def design(self, max_stimuli=-1, max_inhibitors=-1, max_experiments=10, relax=0):
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.clingo.grounder)

        grounder_args = component.getUtility(asp.IArgumentRegistry).arguments(self.clingo.grounder)
        solver_args = component.getUtility(asp.IArgumentRegistry).arguments(self.clingo.solver)
        
        iopt = encodings('caspo.design.iopt')
        opt = encodings('caspo.design.opt')
        
        programs = [self.termset.to_file()]
        
        if not relax:
            programs.append(iopt)
            constraints = map(lambda arg: arg.format(stimuli=max_stimuli, inhibitors=max_inhibitors, imax=max_experiments),
                              grounder_args('caspo.design.iopt'))
        else:
            programs.append(opt)                 
            constraints = map(lambda arg: arg.format(stimuli=max_stimuli, inhibitors=max_inhibitors, nexp=max_experiments), 
                              grounder_args('caspo.design.opt'))

        solutions = self.clingo.run("#show clamped/3.", 
                            grounder_args=programs + constraints, 
                            solver_args=solver_args('caspo.design.opt'),
                            adapter=core.IClampingList)
                            
        if self.clingo.optimum:
            return solutions
        
class ClampingList2CsvWriter(object):
    component.adapts(core.IBooleLogicNetworkSet, core.IClampingList, core.ISetup)
    interface.implements(core.ICsvWriter)
    
    def __init__(self, networks, clist, setup):
        self.networks = networks
        self.clist = clist
        self.setup = setup
        
    def clampings(self, header):
        for clamping in self.clist.clampings:
            dc = dict(clamping)
            nrow = dict.fromkeys(header, 0)
            for inh in self.setup.inhibitors:
                if inh in dc:
                    nrow[inh + 'i'] = 1

            for sti in self.setup.stimuli:
                if dc[sti] == 1:
                    nrow[sti] = dc[sti]
                    
            for m1,m2 in it.combinations(self.networks, 2):
                cd = False
                for r in self.setup.readouts:
                    if m1.prediction(r,clamping) != m2.prediction(r,clamping):
                        nrow[r] += 1
                        cd = True
                if cd:
                    nrow['pairs'] += 1            

            yield nrow    
        
    def write(self, filename, path="./"):
        writer = component.getUtility(core.ICsvWriter)
        header = self.setup.stimuli + map(lambda i: i+'i', self.setup.inhibitors) + self.setup.readouts + ['pairs']
        
        writer.load(self.clampings(header), header)
        writer.write(filename, path)
        
class ClampingListEntropy(object):
    component.adapts(core.IBooleLogicNetworkSet, core.IClampingList, core.ISetup)
    interface.implements(IClampingListEntropy)
    
    
    def __init__(self, networks, clist, setup):
        self.networks = networks
        self.clist = clist
        self.setup = setup
    
    @property
    def clampings(self):
        return self.clist.clampings
            
    def entropy(self):
        L = float(len(self.networks))
        total = 0
        for clamping in self.clist.clampings:
            outputs = defaultdict(int)
            for net in self.networks:
                out = dict.fromkeys(self.setup.readouts, 0)
                for r in self.setup.readouts:
                    out[r] = net.prediction(r,clamping)
                
                outputs[frozenset(out.items())] += 1
            
            ec = 0    
            for s,c in outputs.iteritems():
                ps = c / L
                ec += ps * log(ps,2)
                
            total -= ec
            
        return total