# Copyright (c) 2015, Santiago Videla
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

from literal import Literal

class Clause(frozenset):
    """
    A conjunction clause is a frozenset of :class:`caspo.core.literal.Literal` object instances
    """

    @classmethod
    def from_str(klass, string):
        """
        Creates a clause from a given string of the form `a+!b` which translates to `a AND NOT b`.
        
        Returns
        -------
        caspo.core.clause.Clause
            Created object instance
        """
        return klass(map(lambda lit: Literal.from_str(lit), string.split('+')))
        
    def __str__(self):
        """
        Returns the string representation of the clause
        """
        return "+".join(map(str, sorted(self)))

    def bool(self, state):
        """
        Returns the Boolean evaluation of the clause with respect to a given state
        
        Parameters
        ----------
        state : dict
            Key-value mapping describing a Boolean state
        
        Returns
        -------
        boolean
            The evaluation of the clause with respect to the given state
        """
        and_value = 1
        for source, sign in self:
            and_value = and_value and (state[source] if sign == 1 else not state[source])
            if not and_value: break
            
        return and_value