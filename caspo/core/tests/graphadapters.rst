We are going to test adapters to ``IGraph``::

    >>> from caspo import core

We can adapt a SIF file reader to a graph::

    >>> graph1 = core.IGraph(fake_sif)
    
Let's check everything has been parsed correctly::

    >>> sorted(graph1.nodes)
    ['a', 'b', 'c', 'd']
    >>> ('a','c',1) in graph1.edges
    True
    >>> ('b','c',-1) in graph1.edges
    True
    >>> ('c','d',1) in graph1.edges
    True
    >>> len(graph1.edges)
    3        
    >>> ('a',1) in graph1.predecessors('c')
    True
    >>> ('b',-1) in graph1.predecessors('c')
    True

Next, let's check that invalid SIF files are well handled. First a file providing non integer relation between nodes::

    >>> graph3 = core.IGraph(fake_sif_err1)
    Traceback (most recent call last):
    ...
    IOError: Cannot read line a	activates	c in SIF file: invalid literal for int() with base 10: 'activates'
    
Second, a line not separated by tabs::

    >>> graph4 = core.IGraph(fake_sif_err2)
    Traceback (most recent call last):
    ...
    IOError: Cannot read line b	-1 c in SIF file: need more than 2 values to unpack

Finally, we can adapt a ``LogicalHeaderMapping`` which in this case must result in the same graph as above::
    
    >>> graph2 = core.IGraph(fake_header)
    >>> graph1.nodes == graph2.nodes
    True
    >>> graph1.edges == graph2.edges
    True
