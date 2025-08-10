import py

def load_config(configfile, classname='Config'):
    """
    Load a class named Config from ``configfile``.

    If the class Config does not inherit from DefaultConfig, a new class
    inheriting from Config and DefaultConfig is automatically created. This
    way, we are sure that DefaultConfig is always in the __mro__
    """
    dic = {}
    execfile(configfile, dic)
    Config = dic[classname]
    if DefaultConfig not in Config.__bases__:
        newbases = (Config, DefaultConfig)
        Config = type('Config', newbases, {})
    if Config.root is None:
        Config.root = py.path.local(configfile).dirpath()
    return Config()


class DefaultConfig(object):
    vcs = 'hg'
    version_regex = '^Version'
    editable_revision = False
    show_revision = False
    create_pdf = True # useful to set it to false in tests
    timestamp_format = '%Y-%m-%d %H:%M'
    #
    # all the options below are paths relative to root. If root is not
    # specified, it is automatically set by load_config to the directory where
    # the config file is.
    root = None # automatically set by load_config
    path = None
    logfile = None
    logo = None
    update_report_template = None

    def __init__(self):
        self.root = py.path.local(self.root)
        for attrname in ['path', 'logfile', 'logo', 'update_report_template']:
            value = getattr(self, attrname)
            if value is not None:
                value = self.root.join(value, abs=True)
                setattr(self, attrname, value)
