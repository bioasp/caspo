We are going to test adapters to ``IGraph``::

    >>> from caspo import core, learn

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

Lines and tabs can be mixed::

    >>> graph2 = core.IGraph(fake_sif2)
    >>> ('b','c',-1) in graph2.edges
    True

Next, let's check that invalid SIF files are well handled. First a file providing non integer relation between nodes::

    >>> graph3 = core.IGraph(fake_sif_err1)
    Traceback (most recent call last):
    ...
    IOError: Cannot read line a	activates	c in SIF file: invalid literal for int() with base 10: 'activates'
