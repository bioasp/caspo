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

import os, logging

import itertools as it
import pandas as pd

import gringo

from caspo import core

class ScenarioList(object):
    """
    List of intervention scenarios

    Parameters
    ----------
    filename : str
        Absolute PATH to a CSV file specifying several intervention scenarios

    allow_constraints : boolean
        Either to allow intervention over constraints or not

    allow_goals : boolean
        Either to allow intervention over goals or not

    Attributes
    ----------
        constraints : :class:`caspo.core.clamping.ClampingList`
        goals : :class:`caspo.core.clamping.ClampingList`
    """

    def __init__(self, filename, allow_constraints=False, allow_goals=False):
        df = pd.read_csv(filename)

        self.df_cons = df.filter(regex='^SC').rename(columns=lambda c: c[3:])
        self.df_goals = df.filter(regex='^SG').rename(columns=lambda c: c[3:])

        self.exclude = set()
        if not allow_constraints:
            self.exclude = self.exclude.union(self.df_cons.columns)

        if not allow_goals:
            self.exclude = self.exclude.union(self.df_goals.columns)

    def __clamping_list__(self, df):
        return core.ClampingList([core.Clamping(map(lambda (v,s): core.Literal(v,s), row[row != 0].iteritems())) for _,row in df.iterrows()])

    @property
    def constraints(self):
        return self.__clamping_list__(self.df_cons)

    @property
    def goals(self):
        return self.__clamping_list__(self.df_goals)

    def to_funset(self):
        """
        Converts the intervention scenarios to a set of `gringo.Fun`_ instances

        Returns
        -------
        set
            Representation of the intervention scenarios as a set of `gringo.Fun`_ instances


        .. _gringo.Fun: http://potassco.sourceforge.net/gringo.html#Fun
        """
        return self.constraints.to_funset("scenario","constrained").union(self.goals.to_funset("scenario","goal"))


class Controller(object):
    """
    Controller of logical networks family for various intervention scenarios

    Parameters
    ----------
    networks : :class:`caspo.core.logicalnetwork.LogicalNetworkList`
        List of logical networks

    scenarios : :class:`caspo.control.ScenarioList`
        List of intervention scenarios

    Attributes
    ----------
        networks : :class:`caspo.core.logicalnetwork.LogicalNetworkList`
        scenarios : :class:`caspo.control.ScenarioList`
        strategies : :class:`caspo.core.clamping.ClampingList`
        instance : str
        encodings : dict
        stats : dict
    """
    def __init__(self, networks, scenarios):
        self.networks = networks
        self.scenarios = scenarios
        self.strategies = core.ClampingList()

        fs = networks.to_funset().union(scenarios.to_funset())
        for v in it.ifilter(lambda n: n not in scenarios.exclude, networks.hg.nodes):
            fs.add(gringo.Fun("candidate",[v]))

        self.instance = ". ".join(map(str, fs)) + ". #show intervention/2."

        root = os.path.dirname(__file__)
        self.encodings = {
            'control':    os.path.join(root, 'encodings/control/encoding.lp')
        }

        self.stats = {
            'time_optimum': None,
            'time_enumeration': None
        }

        self._logger = logging.getLogger("caspo")

    def __save__(self,model):
        tuples = (f.args() for f in model.atoms())
        self._strategies.append(core.Clamping.from_tuples(tuples))

    def control(self, size=0, configure=None):
        """
        Finds all inclusion-minimal intervention strategies up to the given size.
        Intervention strategies found are saved in the attribute :attr:`strategies`
        as a :class:`caspo.core.clamping.ClampingList` object instance.

        Example::

            >>> from caspo import core, control

            >>> networks = core.LogicalNetworkList.from_csv('networks.csv')
            >>> scenarios = control.ScenarioList('scenarios.csv')

            >>> controller = control.Controller(networks, scenarios)
            >>> controller.control()

            >>> controller.strategies.to_csv('strategies.csv')

        Parameters
        ----------
        size : int
            Maximum number of intervention per intervention strategy

        configure : callable
            Callable object responsible of setting clingo configuration
        """
        self._strategies = []

        clingo = gringo.Control(['-c maxsize=%s' % size])

        clingo.conf.solve.models = '0'
        if configure:
            def overwrite(args, proxy):
                for i in xrange(args.threads):
                    proxy.solver[i].no_lookback = 'false'
                    proxy.solver[i].heuristic = 'domain'
                    proxy.solver[i].dom_mod = '5,16'

            configure(clingo.conf, overwrite)
        else:
            clingo.conf.solver.no_lookback = 'false'
            clingo.conf.solver.heuristic = 'domain'
            clingo.conf.solver.dom_mod = '5,16'

        clingo.conf.solve.enum_mode = 'domRec'

        clingo.add("base", [], self.instance)
        clingo.load(self.encodings['control'])

        clingo.ground([("base", [])])
        clingo.solve(on_model=self.__save__)

        self.stats['time_optimum'] = clingo.stats['time_solve']
        self.stats['time_enumeration'] = clingo.stats['time_total']
        self._logger.info("%s optimal intervention strategies found in %.4fs" % (len(self._strategies),self.stats['time_enumeration']))

        self.strategies = core.ClampingList(self._strategies)
