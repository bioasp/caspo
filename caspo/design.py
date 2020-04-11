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
import itertools as it

import clingo

from caspo import core

class Designer(object):
    """
    Experimental designer to discriminate among a list of logical networks
    (input-output behaviors representatives)

    Parameters
    ----------
    networks : :class:`caspo.core.logicalnetwork.LogicalNetworkList`
        List of logical networks to discriminate

    setup : :class:`caspo.core.setup.Setup`
        Experimental setup

    candidates : :class:`caspo.core.clamping.ClampingList`
        Optional list of candidate experiments given as a list of clampings

    Attributes
    ----------
        networks : :class:`caspo.core.logicalnetwork.LogicalNetworkList`
        setup : :class:`caspo.core.setup.Setup`
        candidates : :class:`caspo.core.clamping.ClampingList`
        designs : list[:class:`caspo.core.clamping.ClampingList`]
        instance : str
        encodings : dict
        stats : dict
    """
    def __init__(self, networks, setup, candidates=None):
        self.networks = networks
        self.setup = setup
        self.candidates = candidates
        self.designs = []

        fs = networks.to_funset().union(setup.to_funset())
        if candidates:
            fs = fs.union(self.candidates.to_funset("listing", "listed"))
            fs.add(clingo.Function("mode", [2]))
        else:
            fs.add(clingo.Function("mode", [1]))

        self.instance = ". ".join(map(str, fs)) + ". #show clamped/3."

        root = os.path.dirname(__file__)
        self.encodings = {
            'design': os.path.join(root, 'encodings/design/idesign.lp')
        }
        self.__optimum__ = None

        self.stats = {
            'time_optimum': None,
            'time_enumeration': None
        }

        self._logger = logging.getLogger("caspo")

    def __save__(self, model):
        if self.__optimum__ == model.cost:
            clampings = []
            keyfunc = lambda i_v_s: i_v_s[0].number
            for i, c in it.groupby(sorted((f.arguments for f in model.symbols(shown=True)), key=keyfunc), keyfunc):
                clampings.append(core.Clamping.from_tuples(((v.string, s.number) for _, v, s in c)))

            self.designs.append(core.ClampingList(clampings))
        else:
            self.__optimum__ = model.cost

    def design(self, max_stimuli=-1, max_inhibitors=-1, max_experiments=10, relax=False, configure=None):
        """
        Finds all optimal experimental designs using up to :attr:`max_experiments` experiments, such that each experiment has
        up to :attr:`max_stimuli` stimuli and :attr:`max_inhibitors` inhibitors. Each optimal experimental design is appended in the
        attribute :attr:`designs` as an instance of :class:`caspo.core.clamping.ClampingList`.

        Example::

            >>> from caspo import core, design
            >>> networks = core.LogicalNetworkList.from_csv('behaviors.csv')
            >>> setup = core.Setup.from_json('setup.json')

            >>> designer = design.Designer(networks, setup)
            >>> designer.design(3, 2)

            >>> for i,d in enumerate(designer.designs):
            ...     f = 'design-%s' % i
            ...     d.to_csv(f, stimuli=self.setup.stimuli, inhibitors=self.setup.inhibitors)



        Parameters
        ----------
        max_stimuli : int
            Maximum number of stimuli per experiment

        max_inhibitors : int
            Maximum number of inhibitors per experiment

        max_experiments : int
            Maximum number of experiments per design

        relax : boolean
            Whether to relax the full-pairwise networks discrimination (True) or not (False).
            If relax equals True, the number of experiments per design is fixed to :attr:`max_experiments`

        configure : callable
            Callable object responsible of setting clingo configuration
        """
        self.designs = []

        args = ['-c maxstimuli=%s' % max_stimuli, '-c maxinhibitors=%s' % max_inhibitors, '-Wno-atom-undefined']

        solver = clingo.Control(args)
        solver.configuration.solve.opt_mode = 'optN'
        if configure is not None:
            configure(solver.configuration)

        solver.add("base", [], self.instance)
        solver.load(self.encodings['design'])

        solver.ground([("base", [])])

        if relax:
            parts = [("step", [step]) for step in range(1, max_experiments+1)]
            parts.append(("diff", [max_experiments + 1]))

            solver.ground(parts)
            ret = solver.solve(on_model=self.__save__)
        else:
            step, sat = 0, False
            while step <= max_experiments and not sat:
                parts = []
                parts.append(("check", [step]))
                if step > 0:
                    solver.release_external(clingo.Function("query", [step-1]))
                    parts.append(("step", [step]))
                    solver.cleanup()

                solver.ground(parts)
                solver.assign_external(clingo.Function("query", [step]), True)
                sat, step = solver.solve(on_model=self.__save__).satisfiable, step + 1

        self.stats['time_optimum'] = solver.statistics['summary']['times']['solve']
        self.stats['time_enumeration'] = solver.statistics['summary']['times']['total']

        self._logger.info("%s optimal experimental designs found in %.4fs", len(self.designs), self.stats['time_enumeration'])
