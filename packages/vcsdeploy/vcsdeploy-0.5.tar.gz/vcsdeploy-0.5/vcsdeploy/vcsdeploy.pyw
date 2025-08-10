#!/usr/bin/env python

import autopath
import sys
from PyQt4 import QtGui, QtCore
import vcsdeploy.makefile
from vcsdeploy.MainWindow import MainWindow
from vcsdeploy.logic import DefaultConfig, load_config

def main(configfile):
    config = load_config(configfile)
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":

    # this seems necessary to silence the warning "QCoreApplication::exec: The
    # event loop is already running" when running pdb
    import PyQt4.QtCore
    PyQt4.QtCore.pyqtRemoveInputHook()

    if len(sys.argv) < 2:
        print 'Usage: %s configfile [options]' % sys.argv[0]
        sys.exit(1)
    configfile = sys.argv.pop(1)
    main(configfile)

