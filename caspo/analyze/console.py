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

from pyzcasp import asp, potassco
from caspo import core, analyze, control
 
def main(args):
    reader = component.getUtility(core.ICsvReader)

    lines = []
    if args.networks:
        reader.read(args.networks)
        networks = core.IBooleLogicNetworkSet(reader)
        
        stats = analyze.IStats(networks)
        writer = core.ICsvWriter(stats)
        writer.write('networks-stats.csv', args.outdir)
        lines.append("Total Boolean logic networks: %s" % len(networks))
        
        if args.midas and args.timepoint:
            reader.read(args.midas)
            dataset = core.IDataset(reader)
            point = core.TimePoint(args.timepoint)
    
            writer = component.getMultiAdapter((networks, dataset, point), core.ICsvWriter)
            writer.write('networks-mse.csv', args.outdir)
    
            grounder = component.getUtility(asp.IGrounder)
            solver = component.getUtility(asp.ISolver)
            behaviors =  component.getMultiAdapter((networks, dataset, grounder, solver), analyze.IBooleLogicBehaviorSet)
            multiwriter = component.getMultiAdapter((behaviors, point), core.IMultiFileWriter)
            multiwriter.write(['behaviors.csv', 'variances.csv', 'core.csv'], args.outdir)
            
            lines.append("Total I/O Boolean logic behaviors: %s" % len(behaviors))
            lines.append("Weighted MSE: %.4f" % behaviors.mse(point.time))
            lines.append("Core predictions: %.2f%%" % ((100. * len(list(behaviors.core()))) / 2**(len(behaviors.active_cues))))
    
    if args.strategies:
        reader.read(args.strategies)
        strategies = control.IStrategySet(reader)
        stats = analyze.IStats(strategies)
        writer = core.ICsvWriter(stats)
        writer.write('strategies-stats.csv', args.outdir)
        
        lines.append("Total intervention strategies: %s" % len(strategies))

    writer = component.getUtility(core.IFileWriter)
    writer.load(lines, "caspo analytics summary")
    writer.write('summary.txt', args.outdir)
    
    return 0

def run():    
    parser = argparse.ArgumentParser()
    parser.add_argument("--networks", dest="networks",
                        help="logical networks in CSV format", metavar="N")

    parser.add_argument("--midas", dest="midas",
                        help="experimental dataset in MIDAS file", metavar="M")
                        
    parser.add_argument("--timepoint", dest="timepoint", type=int,
                        help="time point for the early-responde in the midas file", metavar="T")

    parser.add_argument("--strategies",
                        help="intervention stratgies in CSV format", metavar="S")
                        
    parser.add_argument("--clasp", dest="clasp", default="clasp",
                        help="clasp solver binary (Default to 'clasp')", metavar="C")
                        
    parser.add_argument("--gringo", dest="gringo", default="gringo",
                        help="gringo grounder binary (Default to 'gringo')", metavar="G")
                        
    parser.add_argument("--gringo-series", dest="gringo_series", default=3, choices=[3,4], type=int,
                        help="gringo series (Default to 3)", metavar="S")

    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
                            
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)
    
    args = parser.parse_args()
    
    gsm = component.getGlobalSiteManager()

    if args.gringo_series == 3:
        grounder = potassco.Gringo3(args.gringo)
        gsm.registerUtility(grounder, potassco.IGringo3)
    else:
        grounder = potassco.Gringo4(args.gringo)
        gsm.registerUtility(grounder, potassco.IGringo4)
    
    solver = potassco.ClaspSolver(args.clasp)
    gsm.registerUtility(solver, potassco.IClaspSolver)
    
    return main(args)
