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

from pyzcasp import asp, potassco
from caspo import core, learn
 
def main(args):
    sif = component.getUtility(core.ISifReader)
    sif.read(args.pkn)
    graph = core.interfaces.IGraph(sif)
    
    midas = component.getUtility(learn.IMidasReader)
    midas.read(args.midas)        
    disc = component.createObject(args.discretization)
    disc.factor = args.factor
    point = learn.TimePoint(args.timepoint)
    
    dataset = component.getMultiAdapter((midas, disc, point), learn.IDataset)
    zipgraph = component.getMultiAdapter((graph, dataset.setup), core.IGraph)

    grounder = component.getUtility(asp.IGrounder)
    solver = component.getUtility(asp.ISolver)
    instance = component.getMultiAdapter((zipgraph, dataset), asp.ITermSet)
        
    learner = component.getMultiAdapter((instance, grounder, solver), learn.ILearner)
    learner.learn(args.fit, args.size)
    
    print "Models %s" % solver.__getstats__()['Models']
    
    behaviors =  component.getMultiAdapter((learner, dataset.setup, grounder, solver), learn.ILogicalBehaviorSet)
    #print len(behaviors)
    #print behaviors.mse(midas, args.timepoint)
        
    #analytics = component.getMultiAdapter((learner, grounder, solver), learn.IAnalytics)
    #for target, clause, freq in analytics.frequencies():
    #    print target, clause, freq
        
    #print "---"
    predictor = component.getMultiAdapter((learner, dataset.setup, grounder, solver), learn.ILogicalPredictorSet)
    print predictor.mse(midas, args.timepoint)
    clampings = list(predictor.core())
    print len(clampings) / (float)(2**(len(predictor.active_cues)))

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("pkn",
                        help="Prior knowledge network in SIF format")

    parser.add_argument("midas",
                        help="Experimental dataset in MIDAS file")
                        
    parser.add_argument("timepoint", type=int,
                        help="time point for the early-responde in the midas file")
                        
    parser.add_argument("--clasp", dest="clasp", default="clasp",
                        help="clasp solver binary (Default to 'clasp')", metavar="C")
                        
    parser.add_argument("--gringo", dest="gringo", default="gringo",
                        help="gringo grounder binary (Default to 'gringo')", metavar="G")
                        
    parser.add_argument("--fit", dest="fit", type=float, default=0.,
                        help="tolerance over fitness (Default to 0)", metavar="F")
                      
    parser.add_argument("--size", dest="size", type=int, default=0,
                        help="tolerance over size (Default to 0). Combined with --fit could lead to a huge number of models", 
                        metavar="S")
                        
    parser.add_argument("--factor", dest="factor", type=int, default=100, choices=[1, 10, 100, 1000],
                        help="discretization over [0,D] (Default to 100)", metavar="D")
                        
    parser.add_argument("--discretization", dest="discretization", default='round', choices=['round', 'floor', 'ceil'],
                        help="discretization function: round, floor, ceil (Default to round)", metavar="T")
    
    parser.add_argument('--version', action='version', version='caspo version %s' % pkg_resources.get_distribution("caspo").version)
    
    args = parser.parse_args()
    
    gsm = component.getGlobalSiteManager()

    grounder = potassco.GringoGrounder(args.gringo)
    gsm.registerUtility(grounder, potassco.IGringoGrounder)
    
    solver = potassco.ClaspSolver(args.clasp)
    gsm.registerUtility(solver, potassco.IClaspSolver)
    
    main(args)
