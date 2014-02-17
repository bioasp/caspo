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
from caspo import core, learn
 
def main(args):
    sif = component.getUtility(core.IFileReader)
    sif.read(args.pkn)
    graph = core.IGraph(sif)
    
    reader = component.getUtility(core.ICsvReader)
    reader.read(args.midas[0])
    dataset = core.IDataset(reader)
    
    point = core.TimePoint(int(args.midas[1]))
    
    discretize = component.createObject(args.discretization, args.factor)
    discreteDS = component.getMultiAdapter((dataset, discretize), learn.IDiscreteDataset)
    
    zipgraph = component.getMultiAdapter((graph, dataset.setup), core.IGraph)

    solver = component.getUtility(asp.IGrounderSolver)
    instance = component.getMultiAdapter((zipgraph, point, discreteDS), asp.ITermSet)

    learner = component.getMultiAdapter((instance, solver), learn.ILearner)
    networks = learner.learn(args.fit, args.size)
    
    writer = core.ICsvWriter(networks)
    writer.write('networks.csv', args.outdir, args.quiet)
    
    return 0

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("pkn",
                        help="Prior knowledge network in SIF format")

    parser.add_argument("midas", nargs=2, metavar=("M","T"),
                        help="experimental dataset in MIDAS file and time-point to be used")
                        
    parser.add_argument("--clingo", dest="clingo", default="clingo",
                        help="clingo solver binary (Default to 'clingo')", metavar="C")
                        
    parser.add_argument("--fit", dest="fit", type=float, default=0.,
                        help="tolerance over fitness (Default to 0)", metavar="F")
                      
    parser.add_argument("--size", dest="size", type=int, default=0,
                        help="tolerance over size (Default to 0). Combined with --fit could lead to a huge number of models", 
                        metavar="S")
                        
    parser.add_argument("--factor", dest="factor", type=int, default=100, choices=[1, 10, 100, 1000],
                        help="discretization over [0,D] (Default to 100)", metavar="D")
                        
    parser.add_argument("--discretization", dest="discretization", default='round', choices=['round', 'floor', 'ceil'],
                        help="discretization function: round, floor, ceil (Default to round)", metavar="T")
                        
    parser.add_argument("--quiet", dest="quiet", action="store_true",
                        help="do not print anything to stdout")
                        
    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
    
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)
    
    args = parser.parse_args()
    
    if not args.quiet:
        print "Initializing caspo-learn...\n"
        
    gsm = component.getGlobalSiteManager()

    clingo = potassco.Clingo(args.clingo)
    gsm.registerUtility(clingo, potassco.IGrounderSolver)
    
    return main(args)
        