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

import os, sys, argparse, pkg_resources, random

def run():
    parser = argparse.ArgumentParser()

    parser.add_argument("--pkn", dest="pkn",
                        help="prior knowledge network in SIF format", metavar="P")
                        
    parser.add_argument("--midas", dest="midas",
                        help="experimental dataset in MIDAS file", metavar="M")

    parser.add_argument("--networks", dest="networks", 
                        help="logical networks in CSV format", metavar="N")

    parser.add_argument("--sample", dest="sample", type=int, default=0,
                        help="visualize a sample of N logical networks (default to 0 (all))", metavar="R")
                        
    parser.add_argument("--union", dest="union", action='store_true',
                        help="visualize the union of logical networks (default to False)")
                                                                        
    parser.add_argument("--strategies",
                        help="intervention stratgies in CSV format", metavar="S")
        
    parser.add_argument("--quiet", dest="quiet", action="store_true",
                        help="do not print anything to stdout")
                        
    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
    
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)
    
    args = parser.parse_args()

    if not args.quiet:
        print "Initializing caspo-visualize...\n"    
    
    from zope import component
    from caspo import core, visualize, control, learn

    reader = component.getUtility(core.ICsvReader)
    if args.midas:
        reader.read(args.midas)
        dataset = core.IDataset(reader)
        
        if args.pkn:
            sif = component.getUtility(core.IFileReader)
            sif.read(args.pkn)
            graph = core.IGraph(sif)
            
            zipgraph = component.getMultiAdapter((graph, dataset.setup), core.IGraph)
        
            if zipgraph.nodes != graph.nodes:
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(graph), dataset.setup), visualize.IDotWriter)
                writer.write('pkn-orig.dot', args.outdir, args.quiet)
            
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(zipgraph), dataset.setup), visualize.IDotWriter)
                writer.write('pkn-zip.dot', args.outdir, args.quiet)
            else:
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(graph), dataset.setup), visualize.IDotWriter)
                writer.write('pkn.dot', args.outdir, args.quiet)
    
        if args.networks:
            reader.read(args.networks)
            networks = core.IBooleLogicNetworkSet(reader)
            if args.sample:
                try:
                    sample = random.sample(networks, args.sample)
                except ValueError as e:
                    print "Warning: %s, there are only %s logical networks." % (str(e), len(networks))
                    sample = networks
            else:
                sample = networks
                
            for i, network in enumerate(sample):
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(network), dataset.setup), visualize.IDotWriter)
                writer.write('network-%s.dot' % i, args.outdir, args.quiet)
                
                
            if args.union:
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(networks), dataset.setup), visualize.IDotWriter)
                writer.write('networks.dot', args.outdir, args.quiet)
                    
    if args.strategies:
        reader.read(args.strategies)
        strategies = control.IStrategySet(reader)
        writer = visualize.IDotWriter(visualize.IDiGraph(strategies))
        writer.write('strategies.dot', args.outdir, args.quiet)
        
    return 0        