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

import os, sys, argparse, pkg_resources

from zope import component

from caspo import core, visualize
 
def main(args):
    
    if args.pkn and args.midas:
        sif = component.getUtility(core.IFileReader)
        sif.read(args.pkn)
        graph = core.IGraph(sif)
        
        reader = component.getUtility(core.ICsvReader)
        reader.read(args.midas)
        dataset = core.IDataset(reader)
        
        writer = component.getMultiAdapter((visualize.IMultiDiGraph(graph), dataset.setup), visualize.IDotWriter)
        writer.write('pkn.dot')
    
    if args.networks and args.midas:
        reader.read(args.networks)
        networks = core.IBooleLogicNetworkSet(reader)
        for i, network in enumerate(networks):
            writer = component.getMultiAdapter((visualize.IMultiDiGraph(network), dataset.setup), visualize.IDotWriter)
            writer.write('network-%s.dot' % i)
            
        writer = component.getMultiAdapter((visualize.IMultiDiGraph(networks), dataset.setup), visualize.IDotWriter)
        writer.write('networks.dot')
        
        
    return 0

def run():
    parser = argparse.ArgumentParser()

    parser.add_argument("--pkn", dest="pkn",
                        help="Prior knowledge network in SIF format", metavar="P")
                        
    parser.add_argument("--midas", dest="midas",
                        help="Experimental dataset in MIDAS file", metavar="M")

    parser.add_argument("--networks", dest="networks", 
                        help="Logical networks in CSV format", metavar="N")
                        
    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
    
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)
    
    args = parser.parse_args()
        
    return main(args)
        