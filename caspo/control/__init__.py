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
import os

from interfaces import *
from utilities import *
from adapters import *
from impl import *

from zope import component
from pyzcasp import asp, potassco

gsm = component.getGlobalSiteManager()

gsm.registerAdapter(CsvReader2MultiScenario)
gsm.registerAdapter(MultiScenario2TermSet)
gsm.registerAdapter(NetworksMultiScenario2TermSet)
gsm.registerAdapter(PotasscoDisjunctiveController, (asp.ITermSet, potassco.IGringoGrounder, potassco.IDisjunctiveSolver), IController)
gsm.registerAdapter(PotasscoHeuristicController, (asp.ITermSet, potassco.IGrounderSolver), IController)
gsm.registerAdapter(AnswerSet2Strategy)
gsm.registerAdapter(Strategies2CsvWriter)
gsm.registerAdapter(CsvReader2StrategySet)

root = os.path.dirname(__file__)
reg = component.getUtility(asp.IEncodingRegistry)
reg.register('caspo.control.full',      os.path.join(root, 'encodings/gringo3/encoding.lp'),  potassco.IGringo3)
reg.register('caspo.control.full',      os.path.join(root, 'encodings/gringo4/encoding.lp'),  potassco.IGringo4)

reg = component.getUtility(asp.IArgumentRegistry)
reg.register('caspo.control.enum', ['-c maxsize={size}'],                                                      potassco.IGringoGrounder)
reg.register('caspo.control.enum', ["--dom-mod=5,16", "--heu=domain", "--opt-mode=ignore", "--enum-mode=domRec", "0"], potassco.IClasp3)
