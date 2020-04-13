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

import os
import logging

import pandas as pd

import clingo

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

    @staticmethod
    def __clamping_list__(df):
        return core.ClampingList([core.Clamping([core.Literal(v, s) for v, s in row[row != 0].items()]) for _, row in df.iterrows()])

    @property
    def constraints(self):
        return self.__clamping_list__(self.df_cons)

    @property
    def goals(self):
        return self.__clamping_list__(self.df_goals)

    def to_funset(self):
        """
        Converts the intervention scenarios to a set of `clingo.Function`_ instances

        Returns
        -------
        set
            Representation of the intervention scenarios as a set of `clingo.Function`_ instances


        .. _clingo.Function: https://potassco.github.io/clingo/python-api/current/clingo.html#-Function
        """
        return self.constraints.to_funset("scenario", "constrained").union(self.goals.to_funset("scenario", "goal"))


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
        for v in (n for n in networks.hg.nodes if n not in scenarios.exclude):
            fs.add(clingo.Function("candidate", [v]))

        self.instance = ". ".join(map(str, fs)) + ". #show intervention/2."

        root = os.path.dirname(__file__)
        self.encodings = {
            'control':    os.path.join(root, 'encodings/control/encoding.lp')
        }

        self.stats = {
            'time_optimum': None,
            'time_enumeration': None
        }

        self._strategies = None
        self._logger = logging.getLogger("caspo")

    def __save__(self, model):
        tuples = (f.arguments for f in model.symbols(shown=True))
        self._strategies.append(core.Clamping.from_tuples(((v.string, s.number) for v, s in tuples)))

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

        solver = clingo.Control(['-c maxsize=%s' % size])

        solver.configuration.solve.models = '0'
        if configure:
            def overwrite(args, proxy):
                for i in range(args.threads):
                    proxy.solver[i].no_lookback = 'false'
                    proxy.solver[i].heuristic = 'domain'
                    proxy.solver[i].dom_mod = '5,16'

            configure(solver.configuration, overwrite)
        else:
            solver.configuration.solver.no_lookback = 'false'
            solver.configuration.solver.heuristic = 'domain'
            solver.configuration.solver.dom_mod = '5,16'

        solver.configuration.solve.enum_mode = 'domRec'

        solver.add("base", [], self.instance)
        solver.load(self.encodings['control'])

        solver.ground([("base", [])])
        solver.solve(on_model=self.__save__)

        self.stats['time_optimum'] = solver.statistics['summary']['times']['solve']
        self.stats['time_enumeration'] = solver.statistics['summary']['times']['total']

        self._logger.info("%s optimal intervention strategies found in %.4fs", len(self._strategies), self.stats['time_enumeration'])

        self.strategies = core.ClampingList(self._strategies)
