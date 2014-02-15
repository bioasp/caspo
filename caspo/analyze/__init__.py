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

from interfaces import *
from utilities import *
from adapters import *
from impl import *

from pyzcasp import asp, potassco
from caspo import core

from zope import component

gsm = component.getGlobalSiteManager()

gsm.registerAdapter(BoolLogicNetworkSet2BooleLogicBehaviorSet, (core.IBooleLogicNetworkSet, core.IDataset, potassco.IGringoGrounder, potassco.IClaspSolver), IBooleLogicBehaviorSet)
gsm.registerAdapter(BooleLogicNetworkSet2StatsMappings)
gsm.registerAdapter(StatsMappings2CsvWriter)
gsm.registerAdapter(BooleLogicBehaviorSet2MultiCsvWriter)

root = __file__.rsplit('/', 1)[0]
reg = component.getUtility(asp.IEncodingRegistry)
reg.register('caspo.analyze.guess', root + '/encodings/guess.lp', potassco.IGringo3)
reg.register('caspo.analyze.fixpoint', root + '/encodings/fixpoint.lp', potassco.IGringo3)
reg.register('caspo.analyze.diff', root + '/encodings/diff.lp', potassco.IGringo3)
