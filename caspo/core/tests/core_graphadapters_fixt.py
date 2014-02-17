from zope import interface
from caspo import core

mockLogicHeaderMapping = core.LogicalHeaderMapping(["a=c","!b=c","a+!b=c","c=d"])

def setup_test(test):
    test.globs['fake_header'] = mockLogicHeaderMapping
        
setup_test.__test__ = False
