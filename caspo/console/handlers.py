# Copyright (c) 2014-2016, Santiago Videla
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

import os, logging, csv, ntpath, random
import functools as ft
import pandas as pd

from caspo import core, learn, classify, design, control, visualize

def configure_mt(args, proxy, overwrite=None):
    proxy.solve.parallel_mode = args.threads
    proxy.configuration = args.conf
    if overwrite:
        overwrite(args, proxy)

def learn_handler(args):
    logger = logging.getLogger("caspo")
    
    graph = core.Graph.read_sif(args.pkn)
    dataset = core.Dataset(args.midas, args.time)
    zipped = graph.compress(dataset.setup)

    learner = learn.Learner(zipped, dataset, args.length, args.discretization, args.factor)

    configure = ft.partial(configure_mt,args) if args.threads else None
    learner.learn(args.fit, args.size, configure)

    logger.info("Weighted MSE: %.4f" % learner.networks.weighted_mse(dataset))
    
    rows = []
    exclusive, inclusive = learner.networks.combinatorics()
    for m,f in learner.networks.frequencies_iter():
        row = dict(mapping="%s" % str(m), frequency=f)
        if m in exclusive:
            row["exclusive"] = ";".join(map(str, exclusive[m]))

        if m in inclusive:
            row["inclusive"] = ";".join(map(str, inclusive[m]))

        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(args.out,'stats-networks.csv'), index=False)
    
    visualize.mappings_frequency(df, args.out)

    df = learner.networks.to_dataframe(dataset=dataset, size=True)
    df.to_csv(os.path.join(args.out,'networks.csv'), index=False)
    
    visualize.networks_distribution(df, args.out)

    return 0
    
def classify_handler(args):
    logger = logging.getLogger("caspo")
    
    configure = ft.partial(configure_mt, args) if args.threads else None
    
    networks = core.LogicalNetworkList.from_csv(args.networks)
    setup = core.Setup.from_json(args.setup)
    
    classifier = classify.Classifier(networks, setup)
    
    logger.info("Classifying %s logical networks..." % len(networks))
    
    behaviors = classifier.classify(configure=configure)
    
    logger.info("Input-Output logical behaviors: %s" % len(behaviors))
    
    setup = setup.filter(behaviors)
    
    if args.midas:
        dataset = core.Dataset(args.midas[0], int(args.midas[1]))
        logger.info("Weighted MSE: %.4f" % behaviors.weighted_mse(dataset))
        
        df = behaviors.to_dataframe(known_eq=True, dataset=dataset)
        df.to_csv(os.path.join(args.out,'behaviors.csv'), index=False)
    else:
        df = behaviors.to_dataframe(known_eq=True)
        df.to_csv(os.path.join(args.out,'behaviors.csv'), index=False)
        
    visualize.behaviors_distribution(df, args.out)
    
def predict_handler(args):
    logger = logging.getLogger("caspo")
    
    networks = core.LogicalNetworkList.from_csv(args.networks)
    if len(networks) > 100:
        logger.warning("""
Your networks family has more than 100 networks and this can take a while to finish.
You may want to use 'caspo classify' in order to extract representative networks
having unique input-output behaviors first.
        """)

    setup = core.Setup.from_json(args.setup)
    
    logger.info("Computing all predictions and their variance for %s logical networks..." % len(networks))
    df = networks.predictions(setup.filter(networks))
    
    df.to_csv(os.path.join(args.out,'predictions.csv'), index=False)
    visualize.predictions_variance(df, args.out)

    return 0

def design_handler(args):
    networks = core.LogicalNetworkList.from_csv(args.networks)
    setup = core.Setup.from_json(args.setup)
    listing = core.ClampingList.from_csv(args.list) if args.list else None

    designer = design.Designer(networks, setup, listing)

    configure = ft.partial(configure_mt,args) if args.threads else None
    designer.design(args.stimuli, args.inhibitors, args.experiments, args.relax, configure)

    df = None
    for i,od in enumerate(designer.designs):
        df_od = od.to_dataframe(setup.stimuli, setup.inhibitors)
        df_od = pd.concat([pd.Series([i]*len(df_od), name='id'), df_od], axis=1)

        df = pd.concat([df,df_od], ignore_index=True)

    visualize.experimental_designs(df, args.out)
    df.to_csv(os.path.join(args.out, 'designs.csv'), index=False)
    
    diff = None
    for i,d in df.groupby("id"):
        clampings = core.ClampingList.from_dataframe(d.drop("id", axis=1), setup.inhibitors)

        dd = clampings.differences(networks, setup.readouts)
        dd['id'] = i
        
        diff = dd if diff is None else pd.concat([diff,dd], ignore_index=True)
        
    visualize.differences_distribution(diff, args.out)
    diff.to_csv(os.path.join(args.out,'stats-designs.csv'), index=False)

    return 0

def control_handler(args):
    networks = core.LogicalNetworkList.from_csv(args.networks)
    scenarios = control.ScenarioList(args.scenarios, args.iconstraints, args.igoals)

    controller = control.Controller(networks, scenarios)

    configure = ft.partial(configure_mt,args) if args.threads else None
    controller.control(args.size, configure)

    controller.strategies.to_csv(os.path.join(args.out, 'strategies.csv'))
    visualize.intervention_strategies(controller.strategies.to_dataframe(), args.out)

    return 0

def analyze_handler(args):
    logger = logging.getLogger("caspo")

    if args.networks:
        networks = core.LogicalNetworkList.from_csv(args.networks)
        logger.info("Analyzing %s logical networks..." % len(networks))

        if args.netstats:
            with open(os.path.join(args.out,'stats-networks.csv'),'wb') as fd:
                w = csv.DictWriter(fd,["mapping","frequency","exclusive","inclusive"])
                w.writeheader()
                exclusive, inclusive = networks.combinatorics()
                for m,f in networks.frequencies_iter():
                    row = dict(mapping="%s" % str(m), frequency="%.4f" % f)
                    if m in exclusive:
                        row["exclusive"] = ";".join(map(str, exclusive[m]))

                    if m in inclusive:
                        row["inclusive"] = ";".join(map(str, inclusive[m]))

                    w.writerow(row)

        if args.midas:
            dataset = core.Dataset(args.midas[0], int(args.midas[1]))

            networks.to_csv(os.path.join(args.out,'networks.csv'), size=True, dataset=dataset)

            configure = ft.partial(configure_mt, args) if args.threads else None
            
            classifier = classify.Classifier(networks, dataset.setup)
            behaviors = classifier.classify(configure=configure)
            
            behaviors.to_csv(os.path.join(args.out,'behaviors.csv'), known_eq=True, dataset=dataset)
            behaviors.predictions(dataset.setup.filter(behaviors)).to_csv(os.path.join(args.out,'predictions.csv'), index=False)

            logger.info("I/O logical behaviors: %s" % len(behaviors))
            logger.info("Weighted MSE: %.4f" % behaviors.weighted_mse(dataset))

    if args.strategies:
        strategies = core.ClampingList.from_csv(args.strategies)
        logger.info("Analyzing %s intervention strategies..." % len(strategies))

        with open(os.path.join(args.out,'stats-strategies.csv'),'wb') as fd:
            w = csv.DictWriter(fd,["literal","frequency","exclusive","inclusive"])
            w.writeheader()
            exclusive, inclusive = strategies.combinatorics()
            for l,f in strategies.frequencies_iter():
                row = dict(literal="%s=%s" % l, frequency="%.4f" % f)
                if l in exclusive:
                    row["exclusive"] = ";".join(map(lambda m: "%s=%s" % m, exclusive[l]))

                if l in inclusive:
                    row["inclusive"] = ";".join(map(lambda m: "%s=%s" % m, inclusive[l]))

                w.writerow(row)

    if args.designs and args.behaviors and args.setup:
        behaviors = core.LogicalNetworkList.from_csv(args.behaviors)

        logger.info("Analyzing experimental designs with respect to %s I/O logical behaviors..." % len(behaviors))

        setup = core.Setup.from_json(args.setup)

        df = None
        for i,od in pd.read_csv(args.designs).groupby("id"):
            clampings = core.ClampingList.from_dataframe(od.drop("id", axis=1), setup.inhibitors)

            df_od = clampings.differences(behaviors, setup.readouts)
            df_od['id'] = i
            
            df = pd.concat([df,df_od], ignore_index=True)

        df.to_csv(os.path.join(args.out,'stats-designs.csv'), index=False)

    return 0

def visualize_handler(args):
    logger = logging.getLogger("caspo")

    if args.setup:
        setup = core.Setup.from_json(args.setup)
    else:
        setup = core.Setup([],[],[])

    if args.pkn:
        graph = core.Graph.read_sif(args.pkn)
        visualize.coloured_network(graph, setup, os.path.join(args.out,'pkn.dot'))

        zipped = graph.compress(setup)
        if zipped.nodes != graph.nodes:
            visualize.coloured_network(zipped, setup, os.path.join(args.out,'pkn-zip.dot'))

    if args.networks:
        networks = core.LogicalNetworkList.from_csv(args.networks)
        
        if args.sample > -1:
            try:
                sample = random.sample(networks, args.sample)
            except ValueError as e:
                logger.warning("Warning: %s, there are only %s logical networks." % (str(e), len(networks)))
                sample = networks

            for i, network in enumerate(sample):
                visualize.coloured_network(network, setup, os.path.join(args.out,'network-%s.dot' % i))

        nc = visualize.coloured_network(networks, setup, os.path.join(args.out,'networks-union.dot'))

    if args.designs:
        visualize.experimental_designs(pd.read_csv(args.designs), args.out)

    if args.strategies:
        visualize.intervention_strategies(pd.read_csv(args.strategies), args.out)

    return 0
