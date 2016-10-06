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

import logging

class Predictor(object):
    """
    Predictor of all possible experimental conditions over a given experimental setup
    using a given list of logical networks.

    Parameters
    ----------
    networks: :class:`caspo.core.logicalnetwork.LogicalNetworkList`
        The list of logical networks used to generate the ensemble of predictions

    setup: :class:`caspo.core.setup.Setup`
        The experimental setup to generate possible experimental conditions


    Attributes
    ----------
    networks: :class:`caspo.core.logicalnetwork.LogicalNetworkList`
    setup: :class:`caspo.core.setup.Setup`
    """

    def __init__(self, networks, setup):
        self.networks = networks
        self.setup = setup

        self._logger = logging.getLogger("caspo")
        if len(networks) > 100:
            self._logger.warning("""
Your networks family has more than 100 networks and this can take a while to finish.
If you haven't yet, you may want to use 'caspo classify' in order to extract
representative networks having unique input-output behaviors first.""")

    def predict(self):
        """
        Computes all possible weighted average predictions and their variances

        Example::

            >>> from caspo import core, predict

            >>> networks = core.LogicalNetworkList.from_csv('behaviors.csv')
            >>> setup = core.Setup.from_json('setup.json')

            >>> predictor = predict.Predictor(networks, setup)
            >>> df = predictor.predict()

            >>> df.to_csv('predictions.csv'), index=False)


        Returns
        --------
        `pandas.DataFrame`_
            DataFrame with the weighted average predictions and variance of all readouts for each possible clamping


        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
        """
        self._logger.info("Computing all predictions and their variance for %s logical networks...", len(self.networks))

        return self.networks.predictions(self.setup.filter(self.networks))
