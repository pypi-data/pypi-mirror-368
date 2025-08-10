import sys
import py

def autopath():
    thisdir = py.path.local(__file__).dirpath()
    parentdir = thisdir.dirpath()
    print 'Inserting %s in sys.path' % parentdir
    sys.path.insert(0, str(parentdir))


autopath()
