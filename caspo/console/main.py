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

import os, sys, shutil, argparse, pkg_resources, logging

import caspo
from handlers import *


VERSION = pkg_resources.get_distribution("caspo").version
LICENSE = """
Copyright (C) Santiago Videla
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
caspo is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\n
"""

def run():
    clingo_parser = argparse.ArgumentParser(add_help=False)
    clingo_parser.add_argument("--threads", dest="threads", type=int, metavar="T", help="run parallel search with given number of threads")
    clingo_parser.add_argument("--conf", dest="conf", default="many", metavar="C", help="threads configurations (Default to many)")

    parser = argparse.ArgumentParser("caspo", formatter_class=argparse.RawTextHelpFormatter,
                                     description="Reasoning on the response of logical signaling networks with ASP")

    subparsers = parser.add_subparsers(title='caspo subcommands', dest='cmd',
                                       description='for specific help on each subcommand use: caspo {cmd} --help')

    learn = subparsers.add_parser("learn", parents=[clingo_parser])
    learn.add_argument("pkn", help="prior knowledge network in SIF format")
    learn.add_argument("midas", help="experimental dataset in MIDAS file")
    learn.add_argument("time", type=int, help="time-point to be used in MIDAS")
    learn.add_argument("--fit", dest="fit", type=float, default=0., help="tolerance over fitness (Default to 0)", metavar="F")
    learn.add_argument("--size", dest="size", type=int, default=0, help="tolerance over size (Default to 0)", metavar="S")
    learn.add_argument("--factor", dest="factor", type=int, default=100, choices=[1, 10, 100, 1000], help="discretization over [0,D] (Default to 100)", metavar="D")
    learn.add_argument("--discretization", dest="discretization", default='round', choices=['round', 'floor', 'ceil'], help="discretization function: round, floor, ceil (Default to round)", metavar="T")
    learn.add_argument("--length", dest="length", type=int, default=0, help="max length for conjunctions (hyperedges) (Default to 0; unbounded)", metavar="L")
    learn.set_defaults(handler=learn_handler)

    design = subparsers.add_parser("design", parents=[clingo_parser])
    design.add_argument("networks", help="logical networks in CSV format")
    design.add_argument("setup", help="experimental setup in JSON format")
    design.add_argument("--stimuli", dest="stimuli", type=int, default=-1,help="maximum number of stimuli per experiment", metavar="S")
    design.add_argument("--inhibitors", dest="inhibitors", type=int, default=-1, help="maximum number of inhibitors per experiment", metavar="I")
    design.add_argument("--nexp", dest="experiments", type=int, default=10, help="maximum number of experiments (Default to 10)", metavar="E")
    design.add_argument("--list", dest="list", help="list of possible experiments", metavar="L")
    design.add_argument("--relax", dest="relax", action='store_true', help="relax full pairwise discrimination (Default to False)")
    design.set_defaults(handler=design_handler)

    control = subparsers.add_parser("control", parents=[clingo_parser])
    control.add_argument("networks", help="logical networks in CSV format")
    control.add_argument("scenarios", help="intervention scenarios in CSV format")
    control.add_argument("--size", dest="size", type=int, default=0, help="maximum size for interventions strategies (Default to 0 (no limit))", metavar="M")
    control.add_argument("--allow-constraints", dest="iconstraints", action='store_true', help="allow intervention over side constraints (Default to False)")
    control.add_argument("--allow-goals", dest="igoals", action='store_true', help="allow intervention over goals (Default to False)")
    control.set_defaults(handler=control_handler)

    analyze = subparsers.add_parser("analyze", parents=[clingo_parser])
    analyze.add_argument("--networks", dest="networks", help="logical networks in CSV format", metavar="N")
    analyze.add_argument("--midas", dest="midas", nargs=2, metavar=("M","T"), help="experimental dataset in MIDAS file and time-point to be used")
    analyze.add_argument("--strategies", help="intervention strategies in CSV format", metavar="S")
    analyze.add_argument("--networks-stats", dest="netstats", action='store_true', help="compute mutually inclusive/exclusive modules and MSE for each logical network (Default to False)")
    analyze.add_argument("--behaviors", dest="behaviors", help="logical behaviors in CSV format", metavar="B")
    analyze.add_argument("--designs", help="experimental designs in CSV format", metavar="D")
    analyze.add_argument("--setup", help="experimental setup in JSON format", metavar="S")
    analyze.set_defaults(handler=analyze_handler)

    visualize = subparsers.add_parser("visualize")
    visualize.add_argument("--pkn", dest="pkn", help="prior knowledge network in SIF format", metavar="P")
    visualize.add_argument("--setup", help="experimental setup in JSON format", metavar="S")
    visualize.add_argument("--networks", dest="networks", help="logical networks in CSV format", metavar="N")
    visualize.add_argument("--sample", dest="sample", type=int, default=0, help="visualize a sample of R logical networks (Default to all)", metavar="R")
    visualize.add_argument("--union", dest="union", action='store_true', help="visualize the union of logical networks (Default to False)")
    visualize.add_argument("--strategies", help="intervention strategies in CSV format", metavar="S")
    visualize.add_argument("--designs", help="experimental designs in CSV format", metavar="D")
    visualize.set_defaults(handler=visualize_handler)

    test = subparsers.add_parser("test", parents=[clingo_parser])
    test.add_argument("--testcase", help="testcase name", choices=["Toy", "LiverToy", "LiverDREAM", "ExtLiver"], default="Toy")

    parser.add_argument("--quiet", dest="quiet", action="store_true", help="do not print anything to standard output")
    parser.add_argument("--out", dest="out", default='out', help="output directory path (Default to './out')", metavar="O")
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION + '\n' + LICENSE)

    args = parser.parse_args()

    logger = logging.getLogger("caspo")
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    if args.quiet:
        ch.setLevel(logging.CRITICAL)
    else:
        ch.setLevel(logging.INFO)

    logger.addHandler(ch)


    if args.cmd != "test":
        logger.info("Running caspo %s..." % args.cmd)
        if not os.path.exists(args.out):
            os.mkdir(args.out)

        return args.handler(args)
    else:
        testcase = args.testcase
        out = args.out
        threads = args.threads
        conf = args.conf

        logger.info("Testing caspo subcommands using test case %s.\n" % testcase)
        from subprocess import check_call

        if os.path.exists(out):
            shutil.rmtree(out)

        os.mkdir(out)
        path = os.path.dirname(caspo.__file__)
        logger.info("Copying files for running tests:")
        logger.info("\tPrior knowledge network: pkn.sif")
        logger.info("\tPhospho-proteomics dataset: dataset.csv")
        logger.info("\tExperimental setup: setup.json")
        logger.info("\tIntervention scenarios: scenarios.csv")
        logger.info("")

        shutil.copy(os.path.join(path, 'data', args.testcase, 'pkn.sif'), out)
        shutil.copy(os.path.join(path, 'data', args.testcase, 'dataset.csv'), out)
        shutil.copy(os.path.join(path, 'data', args.testcase, 'setup.json'), out)
        shutil.copy(os.path.join(path, 'data', args.testcase, 'scenarios.csv'), out)

        testcases = {
            "Toy":        ('10', '0.1' , '5'),
            "LiverToy":   ('10', '0.1' , '5'),
            "LiverDREAM": ('30', '0.1' , '2'),
            "ExtLiver":   ('30', '0.02', '0'),
        }

        params = testcases[testcase]

        ###### LEARN ######
        if threads:
            args = parser.parse_args(['--out', out, 'learn',
                                      os.path.join(out, 'pkn.sif'),
                                      os.path.join(out, 'dataset.csv'),
                                      params[0], '--fit', params[1], '--size', params[2],
                                      '--threads', str(threads), '--conf', conf])
        else:
            args = parser.parse_args(['--out', out, 'learn',
                                      os.path.join(out, 'pkn.sif'),
                                      os.path.join(out, 'dataset.csv'),
                                      params[0], '--fit', params[1], '--size', params[2]])

        cmdline = "$ caspo --out {out} learn {pkn} {midas} {time} --fit {fit} --size {size}"
        if threads:
            cmdline += " --threads {threads}"


        cmdline += "\n"
        logger.info(cmdline.format(out=out, pkn=os.path.join(out, 'pkn.sif'), midas=os.path.join(out, 'dataset.csv'),
                                      time=params[0], fit=params[1], size=params[2], threads=threads))
        try:
            args.handler(args)
        except Exception as e:
            logger.info(e)
            logger.info("Testing on caspo %s has failed." % args.cmd)

        ###### CONTROL ######

        if threads:
            args = parser.parse_args(['--out', out, 'control',
                                      os.path.join(out, 'networks.csv'),
                                      os.path.join(out, 'scenarios.csv'),
                                      '--threads', str(threads), '--conf', conf])
        else:
            args = parser.parse_args(['--out', out, 'control',
                                      os.path.join(out, 'networks.csv'),
                                      os.path.join(out, 'scenarios.csv')])

        cmdline = "\n$ caspo --out {out} control {networks} {scenarios}"
        if threads:
            cmdline += " --threads {threads}"

        cmdline += "\n"
        logger.info(cmdline.format(out=out, networks=os.path.join(out, 'networks.csv'),
                                      scenarios=os.path.join(out, 'scenarios.csv'), threads=threads))
        try:
            args.handler(args)
        except Exception as e:
            logger.info(e)
            logger.info("Testing on caspo %s has failed." % args.cmd)

        ###### ANALYZE ######

        if threads:
            args = parser.parse_args(['--out', out, 'analyze',
                                      '--networks', os.path.join(out, 'networks.csv'),
                                      '--midas', os.path.join(out, 'dataset.csv'),
                                      params[0], '--networks-stats', '--threads', str(threads)])
        else:
            args = parser.parse_args(['--out', out, 'analyze',
                                      '--networks', os.path.join(out, 'networks.csv'),
                                      '--midas', os.path.join(out, 'dataset.csv'),
                                      params[0], '--networks-stats'])

        cmdline = "\n$ caspo --out {out} analyze --networks {networks} --midas {midas} {time}"
        if threads:
            cmdline += " --threads {threads}"

        cmdline += "\n"
        logger.info(cmdline.format(out=out, networks=os.path.join(out, 'networks.csv'), midas=os.path.join(out, 'dataset.csv'),
                                      time=params[0], threads=threads))

        try:
            args.handler(args)
        except Exception as e:
            logger.info(e)
            logger.info("Testing on caspo %s has failed." % args.cmd)

        ###### DESIGN ######

        if threads:
            args = parser.parse_args(['--out', out, 'design',
                                      os.path.join(out, 'behaviors.csv'),
                                      os.path.join(out, 'setup.json'),
                                      '--threads', str(threads), '--conf', conf])
        else:
            args = parser.parse_args(['--out', out, 'design',
                                      os.path.join(out, 'behaviors.csv'),
                                      os.path.join(out, 'setup.json')])

        cmdline = "\n$ caspo --out {out} design {behaviors} {setup}"
        if threads:
            cmdline += " --threads {threads}"

        cmdline += "\n"
        logger.info(cmdline.format(out=out, behaviors=os.path.join(out, 'behaviors.csv'),
                                      setup=os.path.join(out, 'setup.json'), threads=threads))

        try:
            args.handler(args)
        except Exception as e:
            logger.info(e)
            logger.info("Testing on caspo %s has failed." % args.cmd)


        ###### ANALYZE ######

        if threads:
            args = parser.parse_args(['--out', out, 'analyze',
                                      '--behaviors', os.path.join(out, 'behaviors.csv'),
                                      '--setup', os.path.join(out, 'setup.json'),
                                      '--strategies', os.path.join(out, 'strategies.csv'),
                                      '--designs', os.path.join(out, 'designs.csv'),
                                      '--threads', str(threads)])
        else:
            args = parser.parse_args(['--out', out, 'analyze',
                                      '--behaviors', os.path.join(out, 'behaviors.csv'),
                                      '--setup', os.path.join(out, 'setup.json'),
                                      '--strategies', os.path.join(out, 'strategies.csv'),
                                      '--designs', os.path.join(out, 'designs.csv')])

        cmdline = "\n$ caspo --out {out} analyze --behaviors {behaviors} --setup {setup} --strategies {strategies} --designs {designs}"
        if threads:
            cmdline += " --threads {threads}"

        cmdline += "\n"
        logger.info(cmdline.format(out=out, behaviors=os.path.join(out, 'behaviors.csv'), setup=os.path.join(out, 'setup.json'),
                                   strategies=os.path.join(out, 'strategies.csv'), designs=os.path.join(out, 'designs.csv'), threads=threads))

        try:
            args.handler(args)
        except Exception as e:
            logger.info(e)
            logger.info("Testing on caspo %s has failed." % args.cmd)

        ###### VISUALIZE ######

        args = parser.parse_args(['--out', out, 'visualize',
                                  '--pkn', os.path.join(out, 'pkn.sif'),
                                  '--networks', os.path.join(out, 'networks.csv'),
                                  '--setup', os.path.join(out, 'setup.json'),
                                  '--strategies', os.path.join(out, 'strategies.csv'),
                                  '--designs', os.path.join(out, 'designs.csv'),
                                  '--union'])

        cmdline = "\n$ caspo --out {out} visualize --pkn {pkn} --networks {networks} --setup {setup} --strategies {strategies} --designs {designs} --union\n"
        logger.info(cmdline.format(out=out, pkn=os.path.join(out, 'pkn.sif'), networks=os.path.join(out, 'networks.csv'),
                                   setup=os.path.join(out, 'setup.json'), strategies=os.path.join(out, 'strategies.csv'),
                                   designs=os.path.join(out, 'designs.csv')))
        try:
            args.handler(args)
        except Exception as e:
            logger.info(e)
            logger.info("Testing on caspo %s has failed." % args.cmd)
