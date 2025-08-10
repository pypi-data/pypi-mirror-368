import sys
from PyQt4 import QtGui, QtCore
import vcsdeploy.makefile
from vcsdeploy.MainWindow import MainWindow
from vcsdeploy.config import DefaultConfig, load_config

def start_app(config):
    # this seems necessary to silence the warning "QCoreApplication::exec: The
    # event loop is already running" when running pdb
    import PyQt4.QtCore
    PyQt4.QtCore.pyqtRemoveInputHook()
    #
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())

def main():
    if len(sys.argv) < 2:
        print 'Usage: %s configfile [options]' % sys.argv[0]
        sys.exit(1)
    configfile = sys.argv.pop(1)
    config = load_config(configfile)
    start_app(config)
