import re
import datetime
import py
from mercurial import commands, ui, hg, error
from vcsdeploy.logic import AbstractLogic, UnknownRevisionError
from vcsdeploy.util import html2pdf

class MercurialRepo(object):

    def __init__(self, path, create=False):
        self.path = path
        self.repo = hg.repository(ui.ui(), str(path), create)
        self.ui = self.repo.ui

    def __getattr__(self, name):
        cmd = getattr(commands, name)
        def fn(*args, **kwds):
            newargs = []
            for arg in args:
                if isinstance(arg, py.path.local):
                    arg = str(arg)
                newargs.append(arg)
            self.ui.pushbuffer()
            cmd(self.ui, self.repo, *newargs, **kwds)
            return self.ui.popbuffer()
        return fn


class MercurialLogic(AbstractLogic):

    def __init__(self, config):
        self.config = config
        self.hg = MercurialRepo(config.path, create=False)

    def pull(self):
        self.hg.pull()

    def _get_hash_and_tag(self):
        out = self.hg.identify().strip()
        if ' ' not in out:
            return out, None
        hash, tag = out.split(' ', 1)
        return hash, tag

    def get_current_version(self):
        hash, tag = self._get_hash_and_tag()
        if tag is None:
            return None
        tag = tag.strip()
        if tag == 'tip':
            return 'Latest version'
        return tag

    def get_current_revision(self):
        hash, tag = self._get_hash_and_tag()
        return hash

    def get_list_of_versions(self):
        out = self.hg.tags()
        versions = []
        for line in out.splitlines():
            tag, rev = line.rsplit(' ', 1)
            tag = tag.strip()
            if re.match(self.config.version_regex, tag):
                versions.append(tag)
        return versions

    def update_to(self, version):
        try:
            self.hg.update(version)
        except (error.RepoLookupError, error.ParseError), e:
            raise UnknownRevisionError(str(e))
        #
        self.log_update()
        return self.generate_update_report_maybe()

    def log_update(self):
        logfile = self.config.logfile
        if logfile is None:
            return
        logfile = py.path.local(logfile)
        identify = self.hg.identify().strip()
        timestamp = datetime.datetime.now().strftime(self.config.timestamp_format)
        line = '[%s] updated to: %s\n' % (timestamp, identify)
        logfile.write(line, mode='a')

    def generate_update_report_maybe(self):
        if self.config.update_report_template is None:
            return None
        hash, tag = self._get_hash_and_tag()
        timestamp = datetime.datetime.now().strftime(self.config.timestamp_format)
        html = self.config.update_report_template.read()
        html = html.format(version=tag, revision=hash, timestamp=timestamp)
        if self.config.create_pdf:
            return html2pdf(html)
        else:
            return html
