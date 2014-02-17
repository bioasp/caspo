We are going to test adapters to ``IGraph``::

    >>> from caspo import core

We can adapt a ``LogicalHeaderMapping`` to ``IGraph``::

    >>> graph = core.IGraph(fake_header)
    
Let's check everything has been parsed correctly::

    >>> sorted(graph.nodes)
    ['a', 'b', 'c', 'd']
    >>> ('a','c',1) in graph.edges
    True
    >>> ('b','c',-1) in graph.edges
    True
    >>> ('c','d',1) in graph.edges
    True
    >>> len(graph.edges)
    3        
    >>> ('a',1) in graph.predecessors('c')
    True
    >>> ('b',-1) in graph.predecessors('c')
    True
