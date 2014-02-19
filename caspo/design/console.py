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
from caspo import core, design
 
def main(args):
    reader = component.getUtility(core.ICsvReader)
    reader.read(args.networks)
    networks = core.IBooleLogicNetworkSet(reader)
        
    reader.read(args.midas)
    dataset = core.IDataset(reader)
    
    solver = component.getUtility(asp.IGrounderSolver)
    instance = component.getMultiAdapter((networks, dataset.setup), asp.ITermSet)

    designer = component.getMultiAdapter((instance, solver), design.IDesigner)
    
    exps = designer.design()
    for d in exps:
        for c in sorted(d, key=lambda t: t.arg(0)):
            print c
            
        print d.score
            
    return 0

def run():    
    parser = argparse.ArgumentParser()
    parser.add_argument("networks",
                        help="logical networks in CSV format", metavar="N")

    parser.add_argument("midas", metavar="M",
                        help="experimental dataset in MIDAS file")
                        
    parser.add_argument("--clingo", dest="clingo", default="clingo",
                        help="clingo solver binary (Default to 'clingo')", metavar="C")

    parser.add_argument("--quiet", dest="quiet", action="store_true",
                        help="do not print anything to stdout")

    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
                            
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)
    
    args = parser.parse_args()

    if not args.quiet:
        print "Initializing caspo-design...\n"
    
    gsm = component.getGlobalSiteManager()

    clingo = potassco.Clingo(args.clingo)
    gsm.registerUtility(clingo, potassco.IClingo)
    
    return main(args)
