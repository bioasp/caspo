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
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-    
NODES_ATTR = {
    'DEFAULT':   {'color': 'black', 'fillcolor': 'white', 'style': 'filled, bold', 'fontname': 'Helvetica', 'fontsize': 18, 'shape': 'ellipse'},
    'STIMULI':   {'color': 'olivedrab3', 'fillcolor': 'olivedrab3'},
    'INHIBITOR': {'color': 'orangered',  'fillcolor': 'orangered'},
    'READOUT':   {'color': 'lightblue',  'fillcolor': 'lightblue'},
    'INHOUT':    {'color': 'orangered',  'fillcolor': 'SkyBlue2', 'style': 'filled, bold, diagonals'},
    'GATE' :     {'fillcolor': 'black', 'fixedsize': True, 'width': 0.2, 'height': 0.2, 'label': '.'}
}
    
EDGES_ATTR = {
    'DEFAULT': {'dir': 'forward', 'penwidth': 2.5},
     1  : {'color': 'forestgreen', 'arrowhead': 'normal'},
    -1  : {'color': 'red', 'arrowhead': 'tee'}
}
