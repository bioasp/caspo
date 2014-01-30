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

from zope import interface

class IFile(interface.Interface):
    """
    File object
    """
    
    def open(self, filename, mode='rbU'):
        """"""
        
class IFileReader(interface.Interface):
    """
    File reader
    """
    
    def read(self, filename):
        """"""

    def __iter__(self):
        """"""

class ICsvReader(IFileReader):
    """
    CSV file reader
    """

class ISifReader(IFileReader):
    """
    SIF file reader
    """
    
class ILogicalNetworksReader(IFileReader):
    """
    Logical Networks reader
    """

class IGraph(interface.Interface):
    """
    Interaction graph
    """
    
    nodes = interface.Attribute("Set of nodes in the graph")
    edges = interface.Attribute("Set of edges")
    
    def predecessors(self, node):
        """
        Return predecessors of a node in the graph
        """
    
class ISetup(interface.Interface):
    """
    Experimental setup
    """
    
    stimuli = interface.Attribute("Iterable over stimuli")
    inhibitors = interface.Attribute("Iterable over inhibitors")
    readouts = interface.Attribute("Iterable over readouts")
        
class ILiteral(interface.Interface):
    """
    """
    
    variable = interface.Attribute("Literal variable")
    signature = interface.Attribute("Literal signature")
    
    def __str__(self):
        """"""
        
    def __iter__(self):
        """"""
    
class IClause(interface.Interface):
    """
    Conjuctive clause
    """
    
    def __iter__(self):
        """"""
    
    def __hash__(self):
        """"""
        
    def __str__(self):
        """"""
    
class ILogicalNames(interface.Interface):
    """
    """
    variables = interface.Attribute("")
    clauses = interface.Attribute("")
    formulas = interface.Attribute("")

    def get_variable(self, name):
        """"""
        
    def get_variable_name(self, variable):
        """"""
                
    def get_clause(self, name):
        """"""
        
    def get_clause_name(self, clause):
        """"""
        
    def get_formula_name(self, formula):
        """"""
        
    def iterclauses(self, var):
        """"""    
                
class ILogicalNetwork(interface.Interface):
    """
    Basic logical network
    """
    
    variables = interface.Attribute("Variables in the network")
    mapping = interface.Attribute("Mapping from variables to sets of clauses")
    
class IClamping(interface.Interface):
    """
    """
    
class IClampingList(interface.Interface):
    """
    """
    
    clampings = interface.Attribute("List of clampings")
    
class IBooleLogicNetwork(ILogicalNetwork):
    """
    Boolean logic network
    """
    
class IFixPoint(interface.Interface):
    """
    """
    
    def __getitem__(self, item):
        """"""
        
class IFixPointer(interface.Interface):
    """
    """
    
    def fixpoint(self, clamping):
        """
        """

class IBooleFixPointer(IFixPointer):
    """
    """
        
class ILogicalHeaderMapping(interface.Interface):
    """
    """
    
    def __iter__(self):
        """"""
    
class ILogicalNetworkSet(interface.Interface):
    """
    Set of Logical Networks
    """
    
    networks = interface.Attribute("")
    
    def __iter__(self):
        """"""
