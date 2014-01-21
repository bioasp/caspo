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
from collections import namedtuple
from zope import interface
from interfaces import *

class Constraints(frozenset):
    interface.implements(IConstraints)
    
    def __init__(self, literals=[]):
        super(Constraints, self).__init__(frozenset(literals))

class Goals(frozenset):
    interface.implements(IGoals)
    
    def __init__(self, literals=[]):
        super(Goals, self).__init__(frozenset(literals))

class Scenario(namedtuple('Scenario', ['constraints', 'goals'])):
    interface.implements(IScenario)
