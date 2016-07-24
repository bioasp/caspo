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
from networkx.drawing.nx_pydot import write_dot

from caspo import core, learn, design, control, visualize

def configure_mt(args, proxy, overwrite=None):
    proxy.solve.parallel_mode = args.threads
    proxy.configuration = args.conf
    if overwrite:
        overwrite(args, proxy)

def learn_handler(args):
    graph = core.Graph.read_sif(args.pkn)
    dataset = core.Dataset(args.midas, args.time)
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

    df = None
    for i,od in enumerate(designer.designs):
        df_od = od.to_dataframe(setup.stimuli, setup.inhibitors)
        df_od = pd.concat([pd.Series([i]*len(df_od), name='id'), df_od], axis=1)

        df = pd.concat([df,df_od], ignore_index=True)

    df.to_csv(os.path.join(args.out, 'designs.csv'), index=False)

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
        logger.info("Analyzing %s logical networks..." % len(networks))

        if args.netstats:
            with open(os.path.join(args.out,'stats-networks.csv'),'wb') as fd:
                w = csv.DictWriter(fd,["mapping","frequency","exclusive","inclusive"])
                w.writeheader()
                exclusive, inclusive = networks.combinatorics()
                for k,f in networks.frequencies_iter():
                    row = dict(mapping="%s=%s" % k, frequency="%.4f" % f)
                    if k in exclusive:
                        row["exclusive"] = ";".join(map(lambda m: "%s=%s" % m, exclusive[k]))

                    if k in inclusive:
                        row["inclusive"] = ";".join(map(lambda m: "%s=%s" % m, inclusive[k]))

                    w.writerow(row)

        if args.midas:
            dataset = core.Dataset(args.midas[0], int(args.midas[1]))

            if args.netstats:
                networks.to_csv(os.path.join(args.out,'networks-mse-len.csv'), size=True, dataset=dataset)

            configure = ft.partial(configure_mt, args) if args.threads else None

            behaviors = learn.io(networks, dataset.setup, args.threads if args.threads else 1, configure)

            setup = dataset.setup.filter(behaviors)

            behaviors.to_csv(os.path.join(args.out,'behaviors.csv'))
            behaviors.to_csv(os.path.join(args.out,'behaviors-mse-len.csv'), known_eq=True, dataset=dataset)
            behaviors.variances(setup).to_csv(os.path.join(args.out,'variances.csv'), index=False)

            cc = learn.core_clampings(behaviors, setup, configure)
            cc.to_csv(os.path.join(args.out,'core.csv'), setup.stimuli, setup.inhibitors)

            logger.info("\tI/O logical behaviors: %s" % len(behaviors))
            logger.info("\tWeighted MSE: %.4f" % behaviors.weighted_mse(dataset))
            logger.info("\tCore predictions: %.2f%%" % ((100. * len(cc)) / 2**(len(setup.cues()))))

        logger.info("done.")


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

        logger.info("done.")

    if args.designs and args.behaviors and args.setup:
        behaviors = core.LogicalNetworkList.from_csv(args.behaviors)

        logger.info("Analyzing experimental designs with respect to %s I/O logical behaviors..." % len(behaviors))

        setup = core.Setup.from_json(args.setup)

        df = None
        for i,od in pd.read_csv(args.designs).groupby("id"):
            clampings = core.ClampingList.from_dataframe(od.drop("id", axis=1), setup.inhibitors)

            df_od = clampings.differences(behaviors, setup.readouts)
            df_od = pd.concat([pd.Series([i]*len(df_od), name='id'), df_od], axis=1)
            df = pd.concat([df,df_od], ignore_index=True)

        df.to_csv(os.path.join(args.out,'stats-designs.csv'), index=False)
        logger.info("done.")

    return 0

def visualize_handler(args):
    logger = logging.getLogger("caspo")

    if args.setup:
        setup = core.Setup.from_json(args.setup)
    else:
        setup = core.Setup([],[],[])

    if args.pkn:
        graph = core.Graph.read_sif(args.pkn)
        gc = visualize.ColouredNetwork(graph, setup)
        write_dot(gc.graph, os.path.join(args.out,'pkn.dot'))

        zipped = graph.compress(setup)
        if zipped.nodes != graph.nodes:
            zc = visualize.ColouredNetwork(zipped, setup)
            write_dot(zc.graph, os.path.join(args.out,'pkn-zip.dot'))

    if args.networks:
        networks = core.LogicalNetworkList.from_csv(args.networks)
        if args.sample:
            try:
                sample = random.sample(networks, args.sample)
            except ValueError as e:
                logger.warning("Warning: %s, there are only %s logical networks." % (str(e), len(networks)))
                sample = networks
        else:
            sample = networks

        for i, network in enumerate(sample):
            nc = visualize.ColouredNetwork(network, setup)
            write_dot(nc.graph, os.path.join(args.out,'network-%s.dot' % i))

        if args.union:
            nc = visualize.ColouredNetwork(networks, setup)
            write_dot(nc.graph, os.path.join(args.out,'networks-union.dot'))

        if args.designs:
            df = None
            for i,od in pd.read_csv(args.designs).groupby("ID"):
                clampings = core.ClampingList.from_dataframe(od.drop("ID", axis=1), setup.inhibitors)

                dc = visualize.ColouredClamping(clampings)
                write_dot(dc.graph, os.path.join(args.out, "design-%s.dot" % i))

    if args.strategies:
        strategies = core.ClampingList.from_csv(args.strategies)

        sc = visualize.ColouredClamping(strategies, "CONSTRAINTS", "GOALS")
        write_dot(sc.graph, os.path.join(args.out,'strategies.dot'))

    return 0
