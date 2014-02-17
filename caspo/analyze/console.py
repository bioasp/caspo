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
from caspo import core, analyze, learn, control
 
def main(args):
    reader = component.getUtility(core.ICsvReader)

    lines = []
    if args.networks:
        reader.read(args.networks)
        networks = core.IBooleLogicNetworkSet(reader)
        
        stats = analyze.IStats(networks)
        writer = core.ICsvWriter(stats)
        writer.write('networks-stats.csv', args.outdir, args.quiet)
        lines.append("Total Boolean logic networks: %s" % len(networks))
        
        if args.midas:
            reader.read(args.midas[0])
            dataset = core.IDataset(reader)
            point = core.TimePoint(int(args.midas[1]))
    
            writer = component.getMultiAdapter((networks, dataset, point), core.ICsvWriter)
            writer.write('networks-mse.csv', args.outdir, args.quiet)
    
            grounder = component.getUtility(asp.IGrounder)
            solver = component.getUtility(asp.ISolver)
            behaviors =  component.getMultiAdapter((networks, dataset, grounder, solver), analyze.IBooleLogicBehaviorSet)
            multiwriter = component.getMultiAdapter((behaviors, point), core.IMultiFileWriter)
            multiwriter.write(['behaviors.csv', 'behaviors-mse-len.csv', 'variances.csv', 'core.csv'], args.outdir, args.quiet)
            
            lines.append("Total I/O Boolean logic behaviors: %s" % len(behaviors))
            lines.append("Weighted MSE: %.4f" % behaviors.mse(point.time))
            lines.append("Core predictions: %.2f%%" % ((100. * len(behaviors.core())) / 2**(len(behaviors.active_cues))))
    
    if args.strategies:
        reader.read(args.strategies)
        strategies = control.IStrategySet(reader)
        stats = analyze.IStats(strategies)
        writer = core.ICsvWriter(stats)
        writer.write('strategies-stats.csv', args.outdir, args.quiet)
        
        lines.append("Total intervention strategies: %s" % len(strategies))

    writer = component.getUtility(core.IFileWriter)
    writer.load(lines, "caspo analytics summary")
    writer.write('summary.txt', args.outdir, args.quiet)
    
    if not args.quiet:
        print "\ncaspo analytics summary"
        print "======================="
        for line in lines:
            print line
        
    return 0

def run():    
    parser = argparse.ArgumentParser()
    parser.add_argument("--networks", dest="networks",
                        help="logical networks in CSV format", metavar="N")

    parser.add_argument("--midas", dest="midas", nargs=2, metavar=("M","T"),
                        help="experimental dataset in MIDAS file and time-point to be used")
                        
    parser.add_argument("--strategies",
                        help="intervention stratgies in CSV format", metavar="S")
                        
    parser.add_argument("--clasp", dest="clasp", default="clasp",
                        help="clasp solver binary (Default to 'clasp')", metavar="C")
                        
    parser.add_argument("--gringo", dest="gringo", default="gringo",
                        help="gringo grounder binary (Default to 'gringo')", metavar="G")
                        
    parser.add_argument("--gringo-series", dest="gringo_series", default=3, choices=[3,4], type=int,
                        help="gringo series (Default to 3)", metavar="S")

    parser.add_argument("--quiet", dest="quiet", action="store_true",
                        help="do not print anything to stdout")

    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
                            
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)
    
    args = parser.parse_args()

    if not args.quiet:
        print "Initializing caspo-analyze...\n"
    
    gsm = component.getGlobalSiteManager()

    if args.gringo_series == 3:
        grounder = potassco.Gringo3(args.gringo)
        gsm.registerUtility(grounder, potassco.IGringo3)
    else:
        grounder = potassco.Gringo4(args.gringo)
        gsm.registerUtility(grounder, potassco.IGringo4)
    
    solver = potassco.Clasp2(args.clasp)
    gsm.registerUtility(solver, potassco.IClasp2)
    
    return main(args)
