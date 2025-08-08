__version__ = '0.6.5'


from pathlib import Path as _Path


EMAIL_CONTACT = 'liminal_cl_installer@liminalbios.com'
LIMINAL_CLI_NAME = 'liminal_cl'
LIMINAL_DIR = _Path.home() / '.liminal-tools'
LIMINAL_DIR.mkdir(exist_ok=True)
LIMINAL_BIN = LIMINAL_DIR / 'bin'


LIMINAL_PACKAGE_VERSION = __version__
