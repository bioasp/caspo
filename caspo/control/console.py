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

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("networks",
                        help="Logical networks in CSV format")

    parser.add_argument("scenarios",
                        help="intervention scenarios in csv format")
                        
    parser.add_argument("--solver", dest="solver", default="hclasp", choices=["hclasp","claspD"],
                        help="solver (Default to 'hclasp')", metavar="H")
                        
    parser.add_argument("--hclasp", dest="hclasp", default="hclasp",
                        help="hclasp solver binary (Default to 'hclasp')", metavar="H")
                        
    parser.add_argument("--claspD", dest="claspD", default="claspD",
                        help="claspD solver binary (Default to 'claspD')", metavar="D")
                        
    parser.add_argument("--gringo", dest="gringo", default="gringo",
                        help="gringo grounder binary (Default to 'gringo')", metavar="G")
                        
    parser.add_argument("--gringo-series", dest="gringo_series", default=3, choices=[3,4], type=int,
                        help="gringo series (Default to 3)", metavar="S")
    
    parser.add_argument("--size", dest="size", type=int, default=0,
                        help="maximum size for interventions strategies (Default to 0 (no limit))", metavar="M")

    parser.add_argument("--allow-constraints", dest="iconstraints", action='store_true',
                        help="allow intervention over side constraints (Default to False)")
                        
    parser.add_argument("--allow-goals", dest="igoals", action='store_true',
                        help="allow intervention over goals (Default to False)")

    parser.add_argument("--quiet", dest="quiet", action="store_true",
                        help="do not print anything to stdout")

    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
                        
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)

    args = parser.parse_args()

    if not args.quiet:
        print "Initializing caspo-control...\n"
    
    from zope import component

    from pyzcasp import potassco, asp
    from caspo import core, control

    if args.gringo_series == 3:
        gringo = potassco.Gringo3(args.gringo)
    else:
        gringo = potassco.Gringo4(args.gringo)
    
    if args.solver == 'hclasp':
        clasp = potassco.ClaspHSolver(args.hclasp)
    else:
        clasp = potassco.ClaspDSolver(args.claspD)
    
    reader = component.getUtility(core.ICsvReader)
    
    reader.read(args.networks)
    networks = core.ILogicalNetworkSet(reader)
    
    reader.read(args.scenarios)
    multiscenario = control.IMultiScenario(reader)
    multiscenario.allow_constraints = args.iconstraints
    multiscenario.allow_goals = args.igoals
    
    instance = component.getMultiAdapter((networks, multiscenario), asp.ITermSet)

    controller = component.getMultiAdapter((instance, gringo, clasp), control.IController)
    strategies = controller.control(args.size)
    
    writer = core.ICsvWriter(strategies)
    writer.write('strategies.csv', args.outdir, args.quiet)
        
    return 0
