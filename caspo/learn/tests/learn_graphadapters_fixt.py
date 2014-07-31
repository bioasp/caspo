from zope import interface
from caspo import core

class MockSIFReader(object):
    interface.implements(core.IFileReader)
    
    def __iter__(self):
        lines = ["a\t1\tc","b\t-1\tc","c\t1\td"]
        return iter(lines)

class MockSIFReader2(object):
    interface.implements(core.IFileReader)
    
    def __iter__(self):
        lines = ["a\t1\tc","b\t-1 c","c\t1\td"]
        return iter(lines)

class MockSIFReaderErr1(object):
    interface.implements(core.IFileReader)
    
    def __iter__(self):
        lines = ["a\tactivates\tc","b\t-1\tc","c\t1\td"]
        return iter(lines)

def setup_test(test):
    test.globs['fake_sif'] = MockSIFReader()
    test.globs['fake_sif2'] = MockSIFReader2()
    test.globs['fake_sif_err1'] = MockSIFReaderErr1()
    
setup_test.__test__ = False
