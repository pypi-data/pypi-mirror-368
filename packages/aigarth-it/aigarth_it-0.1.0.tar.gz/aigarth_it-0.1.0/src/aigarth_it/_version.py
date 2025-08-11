from packaging.version import parse

version = parse("0.1.0")

__version__ = version.public
__version_info__ = version.release
