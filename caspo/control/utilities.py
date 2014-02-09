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

from caspo import core

from interfaces import *
from impl import *

class MultiScenarioReader(core.CsvReader):
    interface.implements(IMultiScenarioReader)
    
    def read(self, filename):
        super(MultiScenarioReader, self).read(filename)
        species = self.reader.fieldnames
    
        self.constraints = map(lambda name: name[3:], filter(lambda name: name.startswith('SC:'), species))
        self.goals = map(lambda name: name[3:], filter(lambda name: name.startswith('SG:'), species))
        
        self.__constraints = []
        self.__goals = []
        
        for row in self.reader:
            literals = []
            for c in self.constraints:
                if row['SC:' + c] != '0':
                    literals.append(core.Literal(c, int(row['SC:' + c])))
                 
            cclamping = core.Clamping(literals)
            
            literals = []
            for g in self.goals:
                if row['SG:' + g] != '0':
                    literals.append(core.Literal(g, int(row['SG:' + g])))

            gclamping = core.Clamping(literals)        
                
            self.__constraints.append(cclamping)
            self.__goals.append(gclamping)
                
    def __iter__(self):
        return iter(zip(self.__constraints, self.__goals))
