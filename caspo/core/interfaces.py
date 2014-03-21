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

from zope import interface

class IFile(interface.Interface):
    """
    File object
    """
    
    fd = interface.Attribute("File descriptor")
    
    def open(self, filename, mode='rbU'):
        """
        It opens `filename` with `mode`. The resulting file descriptor is
        saved in `self.fd`.
        
        :param str filename: the path to a file
        :param str mode: a valid mode for standard python `open`
        """
        
    def close(self):
        """
        It closes the file pointed by `self.fd`.
        """
        
class IFileReader(IFile):
    """
    File reader
    """
    
    def read(self, filename):
        """
        It opens `filename` in read-only mode
        
        :param str filename: the path to a file
        """

    def __iter__(self):
        """
        Returns an iterator over `self.fd`
        """

class IFileWriter(IFile):
    """
    File writer
    """
    
    header = interface.Attribute("Header")
    iterable = interface.Attribute("Contents to be written")
    
    def load(self, iterable, header=""):
        """
        It loads an iterable to be dumped to the file.
        
        :param iterable iterable: an interable object
        :param str header: an optional header title
        """
        
    def write(self, filename, path="./"):
        """
        It writes the loaded contents
        
        :param str filename: file where to write
        :param str path: optional path to be joined with `filename`
        """
    
class ICsvReader(IFileReader):
    """
    CSV file reader
    """
    
    fieldnames = interface.Attribute("")
    
class ICsvWriter(IFileWriter):
    """
    CSV file writer
    """
    
class IMultiFileWriter(interface.Interface):
    """
    Multiple files writer
    """
    
    def write(self, filenames, path="./"):
        """"""
        
class IGraphReader(IFileReader):
    """
    Interaction graph file reader
    """

class ISifReader(IGraphReader):
    """
    SIF file reader marker interface
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

class ITimePoint(interface.Interface):
    """
    """
    
class IDataset(interface.Interface):
    """
    Experimental dataset
    """
    
    setup = interface.Attribute("Experimental setup")
    
    times = interface.Attribute("Time points")
    nobs = interface.Attribute("Number of observations per time point")
    nexps = interface.Attribute("Number of experiments")
    
    cues = interface.Attribute("Iterable over experimental cues")
    readouts = interface.Attribute("Iterable over experimental readouts")
    
    def at(self, time):
        """"""
        
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
    
    def __len__(self):
        """"""
    
class IClamping(interface.Interface):
    """
    """
    
    def __iter__(self):
        """"""
        
    def difference(self, iterable):
        """"""
    
class IClampingList(interface.Interface):
    """
    """
    
    clampings = interface.Attribute("List of clampings")
    
class IBooleLogicNetwork(ILogicalNetwork):
    """
    Boolean logic network
    """
    
    def prediction(self, var, clamping):
        """"""
            
class ILogicalHeaderMapping(interface.Interface):
    """
    """
    
    def __iter__(self):
        """"""
    
class ILogicalMapping(interface.Interface):
    """"""
    
    mapping = interface.Attribute("")
    
class ILogicalNetworkSet(interface.Interface):
    """
    Set of Logical Networks
    """
    
    networks = interface.Attribute("")
    
    def __iter__(self):
        """"""
        
    def __len__(self):
        """"""
        
class IBooleLogicNetworkSet(ILogicalNetworkSet):
    """
    """
    
    def itermses(self, dataset, time):
        """"""

class IPrinter(interface.Interface):
    """
    """
    
    quiet = interface.Attribute("")
    
    def iprint(self, msg):
        """"""
        
    def pprint(self, msg):
        """"""
        