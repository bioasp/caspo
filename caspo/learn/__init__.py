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
from zope.component.factory import Factory
from zope.component.interfaces import IFactory

gsm = component.getGlobalSiteManager()

gsm.registerAdapter(Sif2Graph)
gsm.registerAdapter(Dataset2DiscreteDataset)
gsm.registerAdapter(Dataset2TermSet)
gsm.registerAdapter(AnswerSet2BooleLogicNetwork)
gsm.registerAdapter(GraphDataset2TermSet)
gsm.registerAdapter(PotasscoLearner, (asp.ITermSet, asp.IGrounderSolver), ILearner)
gsm.registerAdapter(CompressedGraph)
gsm.registerAdapter(BooleLogicNetworkSet2CsvWriter)

gsm.registerUtility(Factory(Round), IFactory, 'round')
gsm.registerUtility(Factory(Floor), IFactory, 'floor')
gsm.registerUtility(Factory(Ceil),  IFactory, 'ceil')

root = os.path.dirname(__file__)
reg = component.getUtility(asp.IEncodingRegistry)
reg.register('caspo.learn.guess',    os.path.join(root, 'encodings/gringo3/guess.lp'),         potassco.IGringo3)
reg.register('caspo.learn.fixpoint', os.path.join(root, 'encodings/gringo3/fixpoint.lp'),     potassco.IGringo3)
reg.register('caspo.learn.rss',      os.path.join(root, 'encodings/gringo3/residual.lp'),     potassco.IGringo3)
reg.register('caspo.learn.opt',      os.path.join(root, 'encodings/gringo3/optimization.lp'), potassco.IGringo3)
reg.register('caspo.learn.rescale',  os.path.join(root, 'encodings/gringo3/rescale.lp'),      potassco.IGringo3)
reg.register('caspo.learn.enum',     os.path.join(root, 'encodings/gringo3/enumeration.lp'),  potassco.IGringo3)

reg.register('caspo.learn.guess',    os.path.join(root, 'encodings/gringo4/guess.lp'),        potassco.IGringo4)
reg.register('caspo.learn.fixpoint', os.path.join(root, 'encodings/gringo4/fixpoint.lp'),     potassco.IGringo4)
reg.register('caspo.learn.rss',      os.path.join(root, 'encodings/gringo4/residual.lp'),     potassco.IGringo4)
reg.register('caspo.learn.opt',      os.path.join(root, 'encodings/gringo4/optimization.lp'), potassco.IGringo4)
reg.register('caspo.learn.rescale',  os.path.join(root, 'encodings/gringo4/rescale.lp'),      potassco.IGringo4)
reg.register('caspo.learn.enum',     os.path.join(root, 'encodings/gringo4/enumeration.lp'),  potassco.IGringo4)

reg = component.getUtility(asp.IArgumentRegistry)
reg.register('caspo.learn.enum',    ['-c maxrss={rss}', '-c maxsize={size}'],          potassco.IGringoGrounder)
reg.register('caspo.learn.opt',     ["--quiet=1", "--opt-strategy=4"],                 potassco.IClasp3)
reg.register('caspo.learn.rescale', ["--quiet=2,1"],                                   potassco.IClasp3)
reg.register('caspo.learn.enum',    ["--opt-mode=ignore", "0", "--conf=jumpy"],        potassco.IClasp3)
