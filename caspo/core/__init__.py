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
from adapters import *
from utilities import *

from pyzcasp import asp, potassco

from zope.component import getGlobalSiteManager
from zope import interface

gsm = getGlobalSiteManager()

gsm.registerAdapter(LogicalHeaderMapping2Graph)
gsm.registerAdapter(Setup2TermSet)
gsm.registerAdapter(LogicalNames2TermSet)
gsm.registerAdapter(LogicalNetwork2TermSet)
gsm.registerAdapter(LogicalMapping2LogicalNetwork)
gsm.registerAdapter(LogicalMapping2BooleLogicNetwork, (ILogicalMapping, ), IBooleLogicNetwork)
gsm.registerAdapter(CsvReader2LogicalNetworkSet)
gsm.registerAdapter(CsvReader2BooleLogicNetworkSet, (ICsvReader,), IBooleLogicNetworkSet)
gsm.registerAdapter(LogicalNames2HeaderMapping)
gsm.registerAdapter(LogicalNetwork2LogicalMapping)
gsm.registerAdapter(LogicalNetworkSet2CsvWriter)
gsm.registerAdapter(LogicalNetworkSet2TermSet)
gsm.registerAdapter(CsvReader2Dataset, (ICsvReader,), IDataset)
gsm.registerAdapter(CsvReader2Dataset, (ICsvReader,), IClampingList)
gsm.registerAdapter(ClampingTerm2TermSet)
gsm.registerAdapter(ClampingTermInClampingList2TermSet)
gsm.registerAdapter(Clamping2TermSet)
gsm.registerAdapter(ClampingInClampingList2TermSet)
gsm.registerAdapter(AnswerSet2Clamping)
gsm.registerAdapter(AnswerSet2ClampingList)
gsm.registerAdapter(TermSet2LogicalNetwork)

gsm.registerUtility(FileReader(), IFileReader)
gsm.registerUtility(CsvReader(), ICsvReader)
gsm.registerUtility(FileWriter(), IFileWriter)
gsm.registerUtility(CsvWriter(), ICsvWriter)
gsm.registerUtility(LogicalNames(), ILogicalNames)
