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
from interfaces import *
from utilities import *
from adapters import *
from impl import *

from zope import component
from pyzcasp import asp

gsm = component.getGlobalSiteManager()

gsm.registerAdapter(MultiScenarioReader2MultiScenario)
gsm.registerAdapter(MultiScenario2TermSet)
gsm.registerAdapter(NetworksMultiScenario2TermSet)
gsm.registerAdapter(PotasscoDisjunctiveController, (asp.ITermSet, potassco.IGringoGrounder, potassco.IClaspDSolver), IController)
gsm.registerAdapter(PotasscoHeuristicController, (asp.ITermSet, potassco.IGringoGrounder, potassco.IClaspHSolver), IController)
gsm.registerAdapter(TermSet2Strategy)

gsm.registerUtility(MultiScenarioReader(), IMultiScenarioReader)

root = __file__.rsplit('/', 1)[0]
reg = component.getUtility(asp.IEncodingRegistry, 'caspo')
reg.register_encoding('control.full', root + '/encodings/encoding.lp')
reg.register_encoding('control.heuristic', root + '/encodings/heuristic.lp')
