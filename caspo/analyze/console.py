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
from caspo import core, analyze
 
def main(args):
    reader = component.getUtility(core.ICsvReader)
    
    reader.read(args.networks)
    networks = core.IBooleLogicNetworkSet(reader)
    
    reader.read(args.midas)
    dataset = core.IDataset(reader)
    
    point = core.TimePoint(args.timepoint)
    
    stats = analyze.IStatsMappings(networks)
    writer = core.ICsvWriter(stats)
    writer.write('stats.csv', args.outdir)
    
    writer = component.getMultiAdapter((networks, dataset, point), core.ICsvWriter)
    writer.write('networks-mse.csv', args.outdir)
    
    grounder = component.getUtility(asp.IGrounder)
    solver = component.getUtility(asp.ISolver)
    behaviors =  component.getMultiAdapter((networks, dataset, grounder, solver), analyze.IBooleLogicBehaviorSet)
    multiwriter = component.getMultiAdapter((behaviors, point), core.IMultiFileWriter)
    multiwriter.write(['behaviors.csv', 'variances.csv', 'core.csv', 'summary.txt'], args.outdir)
    
    return 0

def run():    
    parser = argparse.ArgumentParser()
    parser.add_argument("networks",
                        help="Logical networks in CSV format")

    parser.add_argument("midas",
                        help="Experimental dataset in MIDAS file")
                        
    parser.add_argument("timepoint", type=int,
                        help="time point for the early-responde in the midas file")
                        
    parser.add_argument("--clasp", dest="clasp", default="clasp",
                        help="clasp solver binary (Default to 'clasp')", metavar="C")
                        
    parser.add_argument("--gringo", dest="gringo", default="gringo",
                        help="gringo grounder binary (Default to 'gringo')", metavar="G")

    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
                            
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)
    
    args = parser.parse_args()
    
    gsm = component.getGlobalSiteManager()

    grounder = potassco.GringoGrounder(args.gringo)
    gsm.registerUtility(grounder, potassco.IGringoGrounder)
    
    solver = potassco.ClaspSolver(args.clasp)
    gsm.registerUtility(solver, potassco.IClaspSolver)
    
    return main(args)
