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

from pyzcasp import asp, potassco
from caspo import core

from zope import component

gsm = component.getGlobalSiteManager()

gsm.registerAdapter(BoolLogicNetworkSet2BooleLogicBehaviorSet, (core.IBooleLogicNetworkSet, core.IDataset, potassco.IGrounderSolver), IBooleLogicBehaviorSet)
gsm.registerAdapter(LogicalNetworkSet2Stats)
gsm.registerAdapter(StatsMappings2CsvWriter)
gsm.registerAdapter(BooleLogicBehaviorSet2MultiCsvWriter)
gsm.registerAdapter(StrategySet2Stats)

root = os.path.dirname(__file__)
reg = component.getUtility(asp.IEncodingRegistry)
reg.register('caspo.analyze.guess',    os.path.join(root, 'encodings/gringo3/guess.lp'),    potassco.IGringo3)
reg.register('caspo.analyze.fixpoint', os.path.join(root, 'encodings/gringo3/fixpoint.lp'), potassco.IGringo3)
reg.register('caspo.analyze.diff',     os.path.join(root, 'encodings/gringo3/diff.lp'),     potassco.IGringo3)

reg.register('caspo.analyze.guess',    os.path.join(root, 'encodings/gringo4/guess.lp'),    potassco.IGringo4)
reg.register('caspo.analyze.fixpoint', os.path.join(root, 'encodings/gringo4/fixpoint.lp'), potassco.IGringo4)
reg.register('caspo.analyze.diff',     os.path.join(root, 'encodings/gringo4/diff.lp'),     potassco.IGringo4)
