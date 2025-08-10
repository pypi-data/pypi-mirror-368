import py
from PyQt4 import QtGui, QtCore, Qt, QtWebKit

def html2pdf(html, name='output.pdf', orientation=None):
    tmpdir = py.path.local.mkdtemp()
    pdffile = tmpdir.join(name)
    printer = QtGui.QPrinter()
    printer.setPageSize(QtGui.QPrinter.A4)
    if orientation:
        printer.setOrientation(orientation)
    printer.setOutputFileName(str(pdffile))
    doc = QtWebKit.QWebView()
    doc.setHtml(html)
    doc.print_(printer)
    return pdffile


def openfile(parent, path):
    if path.check(exists=False):
        QtGui.QMessageBox.critical(parent,
                                   'Could not open file',
                                   '%s does not exist' % path)
    #
    # support for windows shares
    #
    path = str(path)
    if not path.startswith(r'\\'):
        url = QtCore.QUrl.fromLocalFile(path)
    else:
        url = QtCore.QUrl(path, QtCore.QUrl.TolerantMode)
    QtGui.QDesktopServices.openUrl(url)
