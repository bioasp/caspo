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
from zope import component
from pyzcasp import asp
from caspo import core

from interfaces import *

def designer(networks, setup, flist, isolver):
    solver = component.getUtility(isolver)
    reader = component.getUtility(core.ICsvReader)
    
    if not flist:
        instance = component.getMultiAdapter((networks, setup), asp.ITermSet)
        instance.add(asp.Term("mode", [1]))
    else:
        reader.read(flist)
        clist = core.IClampingList(reader)
        instance = component.getMultiAdapter((networks, setup, clist), asp.ITermSet)
        instance.add(asp.Term("mode", [2]))
        
    return component.getMultiAdapter((instance, solver), IDesigner)
