from caspo import core

mockGraph = core.Graph(['a','b','c','d'], [('a','c',1),('b','c',-1),('c','d',1)])
mockSetup = core.Setup(['a','b'],['c'],['d'])
mockNetwork1 = core.LogicalNetwork(['a','b','c','d'],
        {'c': [core.Clause([core.Literal('a',1), core.Literal('b',-1)])], 'd': [core.Clause([core.Literal('c',1)])]})
mockNetwork2 = core.LogicalNetwork(['a','b','c','d'],
        {'c': [core.Clause([core.Literal('a',1)]), core.Clause([core.Literal('b',-1)])], 'd': [core.Clause([core.Literal('c',1)])]})

def setup_test(test):
    test.globs['fake_graph'] = mockGraph
    test.globs['fake_setup'] = mockSetup
    test.globs['fake_network1'] = mockNetwork1
    test.globs['fake_network2'] = mockNetwork2
        
setup_test.__test__ = False