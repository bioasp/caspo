# Copyright (c) 2015, Santiago Videla
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

import os, logging, csv
import functools as ft
from caspo import core, learn, design, control, analyze

def configure_mt(args, proxy):
    proxy.solve.parallel_mode = args.threads
    proxy.configuration = args.conf

def learn_handler(args):
    graph = core.Graph.read_sif(args.pkn)
    dataset = learn.Dataset(args.midas, args.time)
    zipped = graph.compress(dataset.setup)
    
    learner = learn.Learner(zipped, dataset, args.length, args.discretization, args.factor)
    
    configure = ft.partial(configure_mt,args) if args.threads else None
    learner.learn(args.fit, args.size, configure)
    
    learner.networks.to_csv(os.path.join(args.out, 'networks.csv'))
    
    return 0

def design_handler(args):
    networks = core.LogicalNetworkList.from_csv(args.networks)
    setup = core.Setup.from_json(args.setup)
    listing = core.ClampingList.from_csv(args.list) if args.list else None
    
    designer = design.Designer(networks, setup, listing)
    
    configure = ft.partial(configure_mt,args) if args.threads else None
    designer.design(args.stimuli, args.inhibitors, args.experiments, args.relax, configure)
    
    if designer.designs:
        for i,d in enumerate(designer.designs):
            d.to_csv(os.path.join(args.out, 'opt-design-%s.csv' % i))
    else:
       print "There is no solutions matching your experimental design criteria."
        
    return 0

def control_handler(args):
    networks = core.LogicalNetworkList.from_csv(args.networks)
    scenarios = control.ScenarioList(args.scenarios, args.iconstraints, args.igoals)
    
    controller = control.Controller(networks, scenarios)
    
    configure = ft.partial(configure_mt,args) if args.threads else None
    controller.control(args.size, configure)
    
    controller.strategies.to_csv(os.path.join(args.out, 'strategies.csv'))
    
    return 0
    
def analyze_handler(args):
    logger = logging.getLogger("caspo")
    
    if args.networks:
        networks = core.LogicalNetworkList.from_csv(args.networks)
        
        if args.netstats:
            with open(os.path.join(args.out,'networks-stats.csv'),'wb') as fd:
                w = csv.DictWriter(fd,["key","frequency","exclusive","inclusive"])
                w.writeheader()
                exclusive, inclusive = networks.combinatorics()        
                for k,f in networks.frequencies_iter():
                    row = dict(key="%s=%s" % k, frequency="%.4f" % f)
                    if k in exclusive:
                        row["exclusive"] = ";".join(map(lambda m: "%s=%s" % m, exclusive[k]))
                
                    if k in inclusive:
                        row["inclusive"] = ";".join(map(lambda m: "%s=%s" % m, inclusive[k]))
                        
                    w.writerow(row)

        logger.info("Analyzing %s logical networks" % len(networks))
        
        if args.midas:
            dataset = learn.Dataset(args.midas[0], int(args.midas[1]))
            
            if args.netstats:
                networks.to_csv(os.path.join(args.out,'networks-mse-len.csv'), size=True, dataset=dataset)
            
            configure = ft.partial(configure_mt, args) if args.threads else None
                
            #multiwriter = component.getMultiAdapter((behaviors, point), core.IMultiFileWriter)
            #multiwriter.write(['behaviors.csv', 'behaviors-mse-len.csv', 'variances.csv', 'core.csv'], args.outdir)
            
            behaviors = analyze.learn_behaviors(networks, dataset.setup, configure, args.threads)
            behaviors.to_csv(os.path.join(args.out,'behaviors.csv'))
            behaviors.to_csv(os.path.join(args.out,'behaviors-mse-len.csv'), known_eq=True, dataset=dataset)
            behaviors.variances(dataset.setup).to_csv(os.path.join(args.out,'variances.csv'))
            
            logger.info("%s I/O logical behaviors were found" % len(behaviors))
            #logger.info("Weighted MSE: %.4f" % behaviors.mse(dataset, point.time))
            #logger.info("Core predictions: %.2f%%" % ((100. * len(behaviors.core())) / 2**(len(behaviors.active_cues))))
    
    #if args.strategies:
    #    reader.read(args.strategies)
    #    strategies = control.IStrategySet(reader)
    #    stats = analyze.IStats(strategies)
    #    writer = core.ICsvWriter(stats)
    #    writer.write('strategies-stats.csv', args.outdir)
        
    #    lines.append("Total intervention strategies: %s" % len(strategies))

    return 0
    
def visualize_handler(args):
    import os
    from zope import component
    from caspo import core, visualize, control, learn
    import random

    reader = component.getUtility(core.ICsvReader)
    printer = component.getUtility(core.IPrinter)
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
                writer.write('pkn-orig.dot', args.outdir)
            
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(zipgraph), dataset.setup), visualize.IDotWriter)
                writer.write('pkn-zip.dot', args.outdir)
            else:
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(graph), dataset.setup), visualize.IDotWriter)
                writer.write('pkn.dot', args.outdir)
    
        if args.networks:
            reader.read(args.networks)
            networks = core.IBooleLogicNetworkSet(reader)
            if args.sample:
                try:
                    sample = random.sample(networks, args.sample)
                except ValueError as e:
                    printer.pprint("Warning: %s, there are only %s logical networks." % (str(e), len(networks)))
                    sample = networks
            else:
                sample = networks
            
            printer = component.getUtility(core.IPrinter)
            for i, network in enumerate(sample):
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(network), dataset.setup), visualize.IDotWriter)
                printer.quiet = True
                writer.write('network-%s.dot' % (i+1), args.outdir)
                printer.quiet = False
                printer.iprint("Wrote %s to %s" % (os.path.join(args.outdir, 'network-1.dot'), os.path.join(args.outdir, 'network-%s.dot' % (i+1))))
            
            printer.pprint("")                
            if args.union:
                writer = component.getMultiAdapter((visualize.IMultiDiGraph(networks), dataset.setup), visualize.IDotWriter)
                writer.write('networks-union.dot', args.outdir)
                    
    if args.strategies:
        reader.read(args.strategies)
        strategies = control.IStrategySet(reader)
        writer = visualize.IDotWriter(visualize.IDiGraph(strategies))
        writer.write('strategies.dot', args.outdir)
        
    return 0
