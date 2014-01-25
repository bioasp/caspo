#!python
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

from pyzcasp import potassco, asp
from caspo import core, control

def main(args):
    networks_reader = component.getUtility(core.ILogicalNetworksReader)
    networks_reader.read(args.networks)
    networks = core.ILogicalNetworkSet(networks_reader)
    
    scenarios = component.getUtility(control.IMultiScenarioReader)
    scenarios.read(args.scenarios)    
    multiscenario = control.IMultiScenario(scenarios)
    
    grounder = component.getUtility(asp.IGrounder)
    solver = component.getUtility(asp.ISubsetMinimalSolver)
    instance = component.getMultiAdapter((networks, multiscenario), asp.ITermSet)

    controller = component.getMultiAdapter((instance, grounder, solver), control.IController)
    controller.control(args.size)
    print "\n=========\n"
    for strategy in controller:
        print strategy
        print "\n=========\n"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("networks",
                        help="family of networks in csv format (as the output from caspo-learn.py)")

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
    
    parser.add_argument("--size", dest="size", type=int, default=0,
                        help="maximum size for interventions strategies (Default to 0 (no limit))", metavar="M")

    parser.add_argument("--allow-constraints", dest="iconstraints", action='store_true',
                        help="allow intervention over side constraints (Default to False)")
                        
    parser.add_argument("--allow-goals", dest="igoals", action='store_true',
                        help="allow intervention over goals (Default to False)")
                        
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)

    args = parser.parse_args()
    
    gsm = component.getGlobalSiteManager()

    grounder = potassco.GringoGrounder(args.gringo)
    gsm.registerUtility(grounder, potassco.IGringoGrounder)
    
    if args.solver == 'hclasp':
        solver = potassco.ClaspHSolver(args.hclasp)
    else:
        solver = potassco.ClaspDSolver(args.claspD)
    
    gsm.registerUtility(solver, potassco.IClaspSubsetMinimalSolver)
    
    main(args)

    