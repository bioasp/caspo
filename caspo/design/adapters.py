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

class PotasscoDesigner(object):
    component.adapts(asp.ITermSet, potassco.IClingo)
    interface.implements(IDesigner)
    
    def __init__(self, termset, clingo):
        self.termset = termset
        self.clingo = clingo
        
    @asp.cleanrun
    def design(self, max_stimuli=-1, max_inhibitors=-1, max_experiments=20):
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.clingo.grounder)

        grounder_args = component.getUtility(asp.IArgumentRegistry).arguments(self.clingo.grounder)
        solver_args = component.getUtility(asp.IArgumentRegistry).arguments(self.clingo.solver)
        
        opt = encodings('caspo.design.opt')
        
        programs = [self.termset.to_file(), opt, iclingo]
        constraints = map(lambda arg: arg.format(stimuli=max_stimuli, inhibitors=max_inhibitors, imax=max_experiments), 
                          grounder_args('caspo.design.opt'))

        solutions = self.clingo.run("#show clamped/3.", 
                            grounder_args=programs + constraints, 
                            solver_args=solver_args('caspo.design.opt'))
        
        return set(solutions)
        