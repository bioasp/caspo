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

gsm.registerAdapter(NetworksSetup2TermSet)
gsm.registerAdapter(PotasscoDesigner)

root = __file__.rsplit('/', 1)[0]
reg = component.getUtility(asp.IEncodingRegistry)
reg.register('caspo.design.opt', root + '/encodings/gringo4/idesign.lp', potassco.IGringo4)

reg = component.getUtility(asp.IArgumentRegistry)
reg.register('caspo.design.opt', ['-c maxstimuli={stimuli}', '-c maxinhibitors={inhibitors}', '-c imax={imax}'], potassco.IGringoGrounder)
reg.register('caspo.design.opt', ["--quiet=1"], potassco.IClasp3)
