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
import os, csv
from collections import defaultdict
from itertools import chain, combinations

from zope import component

from interfaces import *
from impl import *

class File(object):
    interface.implements(IFile)
    
    def open(self, filename, mode='rbU'):
        self.fd = open(filename, mode)

class FileReader(File):
    interface.implements(IFileReader)
    
    def open(self, filename, mode='rbU'):
        raise NotImplementedError("Call %s.read('%s')" % (str(self), filename))
    
    def read(self, filename):
        super(FileReader, self).open(filename)
    
    def __iter__(self):
        return iter(self.fd)
        
class FileWriter(File):
    interface.implements(IFileWriter)
    
    def open(self, filename, mode='rbU'):
        raise NotImplementedError("Call %s.read('%s')" % (str(self), filename))
        
    def _mkdir(self, path):
        if not path.endswith('/'):
            path = path + '/'
            
        if not os.path.exists(path):
            os.mkdir(path)
            
        return path
        
    def write(self, filename, iterable, path="./"):
        self.open(self._mkdir(path) + filename, mode='wb')
        
        for line in iterable:
            self.fd.write(line + '\n')            

class CsvReader(FileReader):
    interface.implements(ICsvReader)
    
    def read(self, filename):
        super(CsvReader, self).read(filename)
        self.reader = csv.DictReader(self.fd)
    
    @property
    def fieldnames(self):
        return self.reader.fieldnames
    
    def __iter__(self):
        return iter(self.reader)
        
class CsvWriter(FileWriter):
    interface.implements(ICsvWriter)
    
    def write(self, filename, iterable, header, path="./"):
        self.open(self._mkdir(path) + filename, mode='wb')
        self.writer = csv.DictWriter(self.fd, header)
        
        for row in iterable:
            self.writer.writerow(row)
        
class LogicalNames(object):
    interface.implements(ILogicalNames)
    
    def __init__(self):
        self.__reset()

    def __reset(self):
        self.__variables = list()
        self.__clauses_seq = list()
        self.__clauses = dict()    
        self.__mappings = defaultdict(list)
        self.__formulas_seq = list()
        self.__formulas = dict()
        
    def load(self, graph):
        self.__reset()
        self.__variables = list(graph.nodes)
        
        for v in self.__variables:
            preds = list(graph.predecessors(v))
            l = len(preds)
            for litset in chain.from_iterable(combinations(preds, r+1) for r in xrange(l)):
                literals = map(lambda (n,s): Literal(n,s), litset)
                
                d = defaultdict(set)
                valid = True
                for lit in literals:
                    d[lit.variable].add(lit.signature)
                    if len(d[lit.variable]) > 1:
                        valid = False
                        break
                        
                if valid:
                    clause = Clause(literals)
                    if clause not in self.__clauses:
                        clause_name = len(self.__clauses_seq)
                        self.__clauses_seq.append(clause)
                        self.__clauses[clause] = clause_name
                    
                    self.__mappings[v].append(clause)
       

    def iterclauses(self, var):
        for clause in self.__mappings[var]:
            yield self.__clauses[clause], clause
            
    def add(self, formulas):
        for formula in formulas:
            if formula not in self.__formulas:
                formula_name = len(self.__formulas_seq)
                self.__formulas_seq.append(formula)
                self.__formulas[formula] = formula_name

    def get_variable(self, name):
        return self.__variables[name]
        
    def get_clause(self, name):
        return self.__clauses_seq[name]
        
    def get_variable_name(self, variable):
        return self.__variables.index(variable)
        
    def get_clause_name(self, clause):
        return self.__clauses[clause]
        
    def get_formula_name(self, formula):
        return self.__formulas[formula]

    @property
    def variables(self):
        return self.__variables
        
    @property
    def clauses(self):
        return self.__clauses_seq
            
    @property
    def formulas(self):
        return self.__formulas_seq
        