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

from pyzcasp import asp, potassco
from caspo import core

from zope import component
from zope.component.factory import Factory
from zope.component.interfaces import IFactory

gsm = component.getGlobalSiteManager()

gsm.registerAdapter(Midas2Dataset, (IMidasReader, IDiscretization, ITimePoint), IDataset)
gsm.registerAdapter(Dataset2TermSet)
gsm.registerAdapter(GraphDataset2TermSet)
gsm.registerAdapter(PotasscoLearner, (asp.ITermSet, potassco.IGringoGrounder, potassco.IClaspSolver), ILearner)
gsm.registerAdapter(CompressedGraph)

gsm.registerUtility(MidasReader(), IMidasReader)
gsm.registerUtility(Factory(Round), IFactory, 'round')
gsm.registerUtility(Factory(Floor), IFactory, 'floor')
gsm.registerUtility(Factory(Ceil), IFactory, 'ceil')

root = __file__.rsplit('/', 1)[0]
reg = component.getUtility(asp.IEncodingRegistry, 'caspo')
reg.register_encoding('learn.guess', root + '/encodings/guess.lp')
reg.register_encoding('learn.fixpoint', root + '/encodings/fixpoint.lp')
reg.register_encoding('learn.rss', root + '/encodings/residual.lp')
reg.register_encoding('learn.opt', root + '/encodings/optimization.lp')
reg.register_encoding('learn.rescale', root + '/encodings/rescale.lp')
reg.register_encoding('learn.enum', root + '/encodings/enumeration.lp')
