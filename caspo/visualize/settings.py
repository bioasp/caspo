    
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