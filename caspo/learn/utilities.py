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

import math
from zope import component
from pyzcasp import asp 
from caspo import core
from interfaces import *

class Discretization(object):
    def __init__(self, factor=1):
        self.factor = factor

class Round(Discretization):
    interface.implements(IDiscretization)
    
    def __call__(self, data):
        return int(round(data * self.factor))

class Floor(Discretization):
    interface.implements(IDiscretization)
    
    def __call__(self, data):
        return int(math.floor(data * self.factor))

class Ceil(Discretization):
    interface.implements(IDiscretization)
    
    def __call__(self, data):
        return int(math.ceil(data * self.factor))


def learner(pkn, midas, time, length, isolver, discretization='round', factor=100, compress=True):
    solver = component.getUtility(isolver)
    point = core.TimePoint(time)
    length = core.Length(length)
    
    discretize = component.createObject(discretization, factor)
    discreteDS = component.getMultiAdapter((midas, discretize), IDiscreteDataset)
    
    if compress:
        pkn = component.getMultiAdapter((pkn, midas.setup), core.IGraph)

    instance = component.getMultiAdapter((pkn, length, point, discreteDS), asp.ITermSet)
    learner = component.getMultiAdapter((instance, solver), ILearner)

    return learner
    