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
from zope.component.factory import Factory
from zope.component.interfaces import IFactory

gsm = component.getGlobalSiteManager()

gsm.registerAdapter(Dataset2DiscreteDataset)
gsm.registerAdapter(Dataset2TermSet)
gsm.registerAdapter(GraphDataset2TermSet)
gsm.registerAdapter(PotasscoLearner, (asp.ITermSet, potassco.IGringoGrounder, potassco.IClaspSolver), ILearner)
gsm.registerAdapter(CompressedGraph)

gsm.registerUtility(Factory(Round), IFactory, 'round')
gsm.registerUtility(Factory(Floor), IFactory, 'floor')
gsm.registerUtility(Factory(Ceil), IFactory, 'ceil')

root = __file__.rsplit('/', 1)[0]
reg = component.getUtility(asp.IEncodingRegistry)
reg.register('caspo.learn.guess', root + '/encodings/gringo3/guess.lp', potassco.IGringo3)
reg.register('caspo.learn.fixpoint', root + '/encodings/gringo3/fixpoint.lp', potassco.IGringo3)
reg.register('caspo.learn.rss', root + '/encodings/gringo3/residual.lp', potassco.IGringo3)
reg.register('caspo.learn.opt', root + '/encodings/gringo3/optimization.lp', potassco.IGringo3)
reg.register('caspo.learn.rescale', root + '/encodings/gringo3/rescale.lp', potassco.IGringo3)
reg.register('caspo.learn.enum', root + '/encodings/gringo3/enumeration.lp', potassco.IGringo3)

reg.register('caspo.learn.guess', root + '/encodings/gringo4/guess.lp', potassco.IGringo4)
reg.register('caspo.learn.fixpoint', root + '/encodings/gringo4/fixpoint.lp', potassco.IGringo4)
reg.register('caspo.learn.rss', root + '/encodings/gringo4/residual.lp', potassco.IGringo4)
reg.register('caspo.learn.opt', root + '/encodings/gringo4/optimization.lp', potassco.IGringo4)
reg.register('caspo.learn.rescale', root + '/encodings/gringo4/rescale.lp', potassco.IGringo4)
reg.register('caspo.learn.enum', root + '/encodings/gringo4/enumeration.lp', potassco.IGringo4)
