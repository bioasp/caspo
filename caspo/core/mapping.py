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
from itertools import izip
from collections import defaultdict
from clause import Clause

class MappingList(object):
    """
    A list of indexed tuples of the form (:class:`caspo.core.clause.Clause`, str).    
    
    Parameters
    ----------
    mappings : [(:class:`caspo.core.clause.Clause`, str)]
        The list of logical mappings
    
    indexes : [int]
        An optional list of integers to use as indexes
    """
    
    def __init__(self, mappings, indexes=None):
        self.mappings = mappings
        self.indexes = defaultdict(dict)
        
        if indexes is None:
            it = enumerate(mappings)
        else:
            if len(mappings) != len(set(indexes)):
                raise ValueError("Invalid index")
                
            it = izip(indexes,mappings)
            
        for i, (clause,target) in it:
            self.indexes[clause][target] = i
            
    def __len__(self):
        """
        Returns the number of mappings
        
        Returns
        -------
        int
            Number of mappings
        """
        return len(self.mappings)
        
    def __iter__(self):
        """
        Iterates over mappings
        
        Yields
        ------
        (caspo.core.clause.Clause, str)
            The next pair (caspo.core.clause.Clause, str)
        """
        return iter(self.mappings)
            
    def __getitem__(self, index):
        """
        A list of mappings can be indexed by:
    
        1. a tuple (:class:`caspo.core.clause.Clause`, str) to get its corresponding index
        2. a list of integers to get all the corresponding mappings (tuples)
        3. a single integer to get its corresponding mapping (tuple)
        
        Returns
        -------
        object
            An integer, a MappingList or a single mapping
        """
        if isinstance(index,tuple) and isinstance(index[0], Clause) and isinstance(index[1], str):
            clause,target = index
            try:
                return self.indexes[clause][target]
            except KeyError:
                raise KeyError("Mapping not found: %s" % index)
        else:
            try:
                return MappingList([self.mappings[i] for i in index], index)
            except TypeError:
                try:
                    return self.mappings[index]
                except TypeError:
                    raise TypeError("Mapping object can be indexed by either a tuple of the form (Clause,str), an iterable of integers or an integer")
                
    def iteritems(self):
        """
        Iterates over all mappings
        
        
        Yields
        ------
        (int,(caspo.core.clause.Clause, str))
            The next pair (index, mapping)
        """
        for clause,target in self.mappings:
            yield self.indexes[clause][target], (clause,target)
