import py
from vcsdeploy.config import DefaultConfig, load_config

def test_load_config(tmpdir):
    configfile = tmpdir.join('config.py')
    configfile.write(py.code.Source("""
        class MyConfig(object):
             x = 42
             version_regex = 'foo'
        """))
    config = load_config(str(configfile), 'MyConfig')
    assert config.x == 42
    assert config.path is None # from DefaultConfig
    assert config.version_regex == 'foo' # from Config
    #
    Config = config.__class__    # the class created by load_config
    mro = Config.__mro__
    assert len(mro) == 4
    assert mro[0] is Config
    assert mro[1].__name__ == 'MyConfig'
    assert mro[2] is DefaultConfig
    assert mro[3] is object
