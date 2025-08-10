from threading import Thread
from PyQt4 import QtGui, QtCore
from Ui_MainWindow import Ui_MainWindow
from vcsdeploy.logic import UnknownRevisionError
from vcsdeploy.util import openfile


class MainWindow(QtGui.QDialog, Ui_MainWindow):
    def __init__(self, config):
        QtGui.QDialog.__init__(self)
        Ui_MainWindow.__init__(self)
        self.logic = self.create_logic(config)
        self.setupUi(self)
        self.connect(self.btnUpdate, QtCore.SIGNAL("clicked()"), self.do_update)
        self.config_ui(config)
        self.init()

    def create_logic(self, config):
        if config.vcs == 'hg':
            from vcsdeploy.hg import MercurialLogic
            return MercurialLogic(config)
        elif config.vcs == 'git':
            from vcsdeploy.gitlogic import GitLogic
            return GitLogic(config)
        else:
            raise ValueError("Unknown vcs: %s" % config.vcs)

    def config_ui(self, config):
        self.cmbUpdateTo.setEditable(config.editable_revision)
        self.lblCurrentRevision.setVisible(config.show_revision)
        self.lblCurrentRevisionValue.setVisible(config.show_revision)
        #
        # display the logo (if any)
        logo = QtGui.QPixmap(str(config.logo))
        self.imgLogo.setPixmap(logo)
        self.imgLogo.setVisible(not logo.isNull())


    def init(self):
        self.pull_repo()
        self.sync_current_version()
        versions = self.logic.get_list_of_versions()
        self.cmbUpdateTo.clear()
        self.cmbUpdateTo.addItems(versions)

    def sync_current_version(self):
        current_ver = self.logic.get_current_version()
        current_rev = self.logic.get_current_revision()
        if current_ver is None:
            current_ver = 'Unknown'
        self.lblCurrentVersion.setText(current_ver)
        self.lblCurrentRevisionValue.setText(current_rev)

    def pull_repo(self):
        import time
        app = QtCore.QCoreApplication.instance()
        bar = QtGui.QProgressDialog('Please wait', QtCore.QString(), 0, 0)
        bar.show()
        bar.setRange(0, 0)
        thread = Thread(target=self.logic.pull)
        thread.start()
        app.processEvents()
        while thread.is_alive():
            time.sleep(0.01)
            app.processEvents()

    def do_update(self):
        version = str(self.cmbUpdateTo.currentText())
        try:
            pdf = self.logic.update_to(version)
        except UnknownRevisionError, e:
            msg = 'Cannot update to the specified revision: %s\n[%s]' % (version, e)
            QtGui.QMessageBox.warning(self, 'Error', msg)
        self.sync_current_version()
        if pdf is not None:
            openfile(self, pdf)
