# Copyright (c) 2014-2016, Santiago Videla
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

class Literal(namedtuple('Literal', ['variable', 'signature'])):
    """
    Literal class describing a variable or its negation
    
    Attributes
    ----------
        variable : str
    
        signature : int (either 1 or -1)
    """
    
    @classmethod
    def from_str(klass, string):
        """
        Creates a literal from a string
        
        Parameters
        ----------
        string : str
            If the string starts with '!', it's interpreted as a negated variable
            
        Returns
        -------
        caspo.core.literal.Literal
            Created object instance
        """
        if string[0] == '!':
            signature = -1
            variable = string[1:]
        else:
            signature = 1
            variable = string
            
        return klass(variable, signature)
        
    def __str__(self):
        """
        Returns the string representation of the literal
        
        Returns
        -------
        str
            String representation of the literal
        """
        if self.signature == 1:
            return self.variable
        else:
            return '!' + self.variable
