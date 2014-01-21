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

from caspo import core

from interfaces import *
from impl import *

class ConstraintsReader(core.CsvReader):
    interface.implements(IConstraintsReader)
        
    def __iter__(self):
        for row in self.reader:
            cl = map(lambda (k,v): core.Literal(k,int(v)), filter(lambda (k,v): v!='0', row.iteritems()))
            yield Constraints(cl)
            
class GoalsReader(core.CsvReader):
    interface.implements(IGoalsReader)
        
    def __iter__(self):
        for row in self.reader:
            gl = map(lambda (k,v): core.Literal(k,int(v)), filter(lambda (k,v): v!='0', row.iteritems()))
            yield Goals(gl)