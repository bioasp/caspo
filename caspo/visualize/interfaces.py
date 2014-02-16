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
from caspo import core

class IDiGraph(interface.Interface):
    """
    """
    nxGraph = interface.Attribute("NetworkX DiGraph instance")


class IMultiDiGraph(interface.Interface):
    """
    """
    nxGraph = interface.Attribute("NetworkX MultiDiGraph instance")
    
class IDotWriter(core.IFileWriter):
    """
    Dot writer
    """
