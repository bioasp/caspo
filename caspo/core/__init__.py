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
from adapters import *
from utilities import *

from pyzcasp import asp, potassco

from zope.component import getGlobalSiteManager
from zope import interface

gsm = getGlobalSiteManager()
gsm.registerAdapter(Sif2Graph)
gsm.registerAdapter(LogicalHeaderMapping2Graph)
gsm.registerAdapter(Graph2TermSet)
gsm.registerAdapter(Setup2TermSet)
gsm.registerAdapter(LogicalNames2TermSet)
gsm.registerAdapter(LogicalNetwork2TermSet)
gsm.registerAdapter(TermSet2LogicalNetwork)
gsm.registerAdapter(LogicalNetworksReader2LogicalNetworkSet)
gsm.registerAdapter(LogicalNetworkSet2TermSet)
gsm.registerAdapter(TermSet2FixPoint)
gsm.registerAdapter(ClampingTerm2TermSet)
gsm.registerAdapter(ClampingTermInClampingList2TermSet)
gsm.registerAdapter(Clamping2TermSet)
gsm.registerAdapter(ClampingInClampingList2TermSet)
gsm.registerAdapter(BooleLogicNetwork2FixPointer)

gsm.registerUtility(SifReader(), ISifReader)
gsm.registerUtility(LogicalNetworksReader(), ILogicalNetworksReader)
gsm.registerUtility(LogicalNames(), ILogicalNames)

root = __file__.rsplit('/', 1)[0]
reg = component.getUtility(asp.IEncodingRegistry)
reg.register('caspo.core.boole', root + '/encodings/boole.lp', potassco.IGringoGrounder)

