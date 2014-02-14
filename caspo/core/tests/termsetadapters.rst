Here we are going to test adapters to ``asp.ITermSet``::

    >>> from pyzcasp import asp
    
Let's start by adapting a simple graph::

    >>> termset = asp.ITermSet(fake_graph)    
    >>> nodes = filter(lambda t: t.pred == 'node', termset)
    >>> len(nodes)
    4
    >>> sorted(map(lambda t: t.arg(0), nodes))
    ['a', 'b', 'c', 'd']
    >>> edges = filter(lambda t: t.pred == 'edge', termset)
    >>> len(edges)
    3
    >>> asp.Term('edge',['a','c',1]) in edges
    True
    >>> asp.Term('edge',['b','c',-1]) in edges
    True
    >>> asp.Term('edge',['c','d',1]) in edges
    True
    
Now, let's adapt an experimental setup::

    >>> termset = asp.ITermSet(fake_setup)
    >>> len(termset)
    4
    >>> asp.Term('stimulus',['a']) in termset and asp.Term('stimulus',['b']) in termset
    True
    >>> asp.Term('inhibitor',['c']) in termset
    True
    >>> asp.Term('readout',['d']) in termset
    True

Next, let's load a graph into the LogicalNames utility::
    
    >>> from zope import component
    >>> from caspo import core
    >>> names = component.getUtility(core.ILogicalNames)
    >>> names.load(fake_graph)

Now we check how it's adapted to a termset::

    >>> termset = asp.ITermSet(names)
    >>> c_name = names.get_variable_name('c')
    >>> asp.Term('node',['c',c_name]) in termset
    True
    >>> hypers = filter(lambda t: t.pred == 'hyper' and t.arg(0) == c_name, termset)
    >>> len(hypers)
    3
    >>> iedges = map(lambda t: t.arg(1), hypers)
    >>> edges = filter(lambda t: t.pred == 'edge' and t.arg(0) in iedges, termset)
    >>> from collections import defaultdict
    >>> fx = defaultdict(set)
    >>> for edge in edges:
    ...     fx[edge.arg(0)].add((edge.arg(1), edge.arg(2)))
    ...
    >>> set([('a',1)]) in fx.values()
    True
    >>> set([('b',-1)]) in fx.values()
    True
    >>> set([('a',1), ('b',-1)]) in fx.values()
    True

Next, we adapt a logical network::

    >>> termset = asp.ITermSet(fake_network1)
    >>> variables = sorted(filter(lambda t: t.pred == 'variable', termset), key=lambda t: t.arg(0))
    >>> ['a','b','c','d'] == map(lambda t: t.arg(0), variables)
    True
    >>> c_forms = filter(lambda t: t.pred == 'formula' and t.arg(0) == 'c', termset)
    >>> len(c_forms)
    1
    >>> c_form = c_forms[0].arg(1)
    >>> dnfs = filter(lambda t: t.pred == 'dnf' and t.arg(0) == c_form, termset)
    >>> len(dnfs)
    1
    >>> c_dnf = dnfs[0].arg(1)
    >>> clauses = filter(lambda t: t.pred == 'clause' and t.arg(0) == c_dnf, termset)
    >>> len(clauses)
    2
    >>> asp.Term('clause', [c_dnf,'a',1]) in clauses
    True
    >>> asp.Term('clause', [c_dnf,'b',-1]) in clauses
    True

and a set of logical networks::
    
    >>> pair = core.LogicalNetworkSet([fake_network1, fake_network2])
    >>> termset = asp.ITermSet(pair)
    >>> c_forms = filter(lambda t: t.pred == 'formula' and t.arg(1) == 'c', termset)
    >>> len(c_forms)
    2
    >>> idnfs = map(lambda t: t.arg(2), c_forms)
    >>> dnfs = filter(lambda t: t.pred == 'dnf' and t.arg(0) in idnfs, termset)
    >>> len(dnfs)
    3
    >>> ddnf = defaultdict(set)
    >>> for d in dnfs:
    ...     ddnf[d.arg(0)].add(d.arg(1))
    ...
    >>> sortednfs = sorted(ddnf.values(), key=len)

One network has ``a and not b``::
    
    >>> dnf1 = list(sortednfs[0])
    >>> len(dnf1)
    1
    >>> clauses = filter(lambda t: t.pred == 'clause' and t.arg(0) == dnf1[0], termset)
    >>> len(clauses)
    2
    >>> asp.Term('clause', [dnf1[0],'a',1]) in clauses
    True
    >>> asp.Term('clause', [dnf1[0],'b',-1]) in clauses
    True

and the other has ``a OR not b``::
    
    >>> dnf2 = list(sortednfs[1])
    >>> len(dnf2)
    2
    >>> clauses = filter(lambda t: t.pred == 'clause' and t.arg(0) in dnf2, termset)
    >>> len(clauses)
    2
    >>> (asp.Term('clause', [dnf2[0],'a',1]) in clauses) != (asp.Term('clause', [dnf2[1],'a',1]) in clauses)
    True
    >>> (asp.Term('clause', [dnf2[0],'b',-1]) in clauses) != (asp.Term('clause', [dnf2[1],'b',-1]) in clauses)
    True
