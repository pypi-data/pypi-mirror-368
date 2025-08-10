import py
import pytest
import git
from vcsdeploy.config import DefaultConfig
from vcsdeploy.logic import UnknownRevisionError
from vcsdeploy.hg import MercurialLogic, MercurialRepo
from vcsdeploy.gitlogic import GitLogic

class BaseTestLogic(object):

    LogicClass = None

    @pytest.fixture
    def logic(self, request):
        self.tmpdir = request.getfuncargvalue('tmpdir')
        self.create_test_repo(self.tmpdir)
        self.fill_test_repo(self.tmpdir)
        config = DefaultConfig()
        config.path = self.tmpdir
        self.logic = self.LogicClass(config)
        return self.logic

    def fill_test_repo(self, tmpdir):
        myfile = tmpdir.join('myfile.py')
        myfile.write('version = 1.0')
        self.commit_file(myfile, 'initial checkin', tag='Version_1.0')
        myfile.write("ops, that's a bug")
        self.commit_file(myfile, 'introduce a bug', tag='intermediate_tag')
        myfile.write('version = 1.1')
        self.commit_file(myfile, 'fix the bug', tag='Version_1.1')
        myfile.write('version = none')
        self.commit_file(myfile, 'one untagged commit')
        myfile.write('version = latest')
        self.commit_file(myfile, 'latest untagged commit')

    def test_get_current_version(self, logic):
        assert logic.get_current_version() == 'Latest version'
        self.update_test_repo('Version_1.1')
        assert logic.get_current_version() == 'Version_1.1'
        self.update_test_repo('Version_1.0')
        assert logic.get_current_version() == 'Version_1.0'
        self.update_test_repo()
        assert logic.get_current_version() == 'Latest version'
        self.update_test_repo(rev=1)
        assert logic.get_current_version() is None

    def test_get_list_of_versions(self, logic):
        assert logic.get_list_of_versions() == ['Version_1.1', 'Version_1.0']

    def test_update_to(self, logic):
        myfile = logic.config.path.join('myfile.py')
        logic.update_to('Version_1.0')
        assert myfile.read() == 'version = 1.0'
        logic.update_to('Version_1.1')
        assert myfile.read() == 'version = 1.1'

    def test_unknown_revision(self, logic):
        py.test.raises(UnknownRevisionError, "logic.update_to('foobar')")
        py.test.raises(UnknownRevisionError, "logic.update_to('xxx 1.2.3')")

    def test_get_current_revision(self, logic):
        rev0 = logic.get_current_revision()
        logic.update_to('Version_1.0')
        rev1 = logic.get_current_revision()
        assert rev0 != rev1
        logic.update_to(rev0)
        assert logic.get_current_revision() == rev0

    def test_pull(self, tmpdir):
        # setup a "remote" repo where the "development" will go on, and a "local"
        # one where the program is installed. The idea is that the local will pull
        # from the remote
        remotedir = tmpdir.join('remote')
        localdir = tmpdir.join('local')
        self.create_test_repo(remotedir)
        self.fill_test_repo(remotedir)
        self.clone_test_repo(localdir)

        # simulate some development
        myfile_remote = remotedir.join('myfile.py')
        myfile_remote.write('version = 1.2')
        self.commit_file(myfile_remote, 'new fancy features', tag='Version_1.2')

        # use Version_1.1 in production
        config = DefaultConfig()
        config.path = localdir
        logic = self.LogicClass(config)
        logic.update_to('Version_1.1')
        assert logic.get_current_version() == 'Version_1.1'

        # now, let's look for updates
        logic.pull()
        assert logic.get_current_version() == 'Version_1.1'
        assert logic.get_list_of_versions() == ['Version_1.2', 'Version_1.1', 'Version_1.0']
        logic.update_to('Version_1.2')
        assert logic.get_current_version() == 'Version_1.2'

    def test_log(self, logic):
        logfile = self.tmpdir.join('log')
        config = DefaultConfig()
        config.path = logic.hg.path
        config.logfile = str(logfile)
        logic = MercurialLogic(config)
        #
        logic.update_to('Version_1.0')
        rev0 = logic.get_current_revision()
        logic.update_to('Version_1.1')
        rev1 = logic.get_current_revision()
        #
        lines = logfile.readlines()
        assert len(lines) == 2
        assert lines[0].endswith('updated to: %s Version_1.0\n' % rev0)
        assert lines[1].endswith('updated to: %s Version_1.1\n' % rev1)



class TestHgLogic(BaseTestLogic):
    LogicClass = MercurialLogic

    def create_test_repo(self, tmpdir):
        self._hg = MercurialRepo(tmpdir, create=True)

    def commit_file(self, fname, message, tag=None):
        self._hg.add(fname)
        self._hg.commit(message=message)
        if tag:
            self._hg.tag(tag)

    def clone_test_repo(self, dst):
        self._hg.clone(dst)

    def update_test_repo(self, rev=None):
        self.logic.hg.update(rev=rev)


class TestGitLogic(BaseTestLogic):
    LogicClass = GitLogic

    def create_test_repo(self, tmpdir):
        self.r = git.Repo.init(str(tmpdir))

    def commit_file(self, fname, message, tag=None):
        self.r.index.add([str(fname)])
        self.r.index.commit(message)
        if tag:
            self.r.create_tag(tag)

    def update_test_repo(self, rev=None):
        if rev is None:
            rev = 'master'
        if rev == 1:
            rev = 'HEAD~1'
        self.r.git.checkout(rev)

    def clone_test_repo(self, dst):
        self.r.clone(str(dst))

    @pytest.mark.skip('implement me')
    def test_log(self, logic):
        pass
