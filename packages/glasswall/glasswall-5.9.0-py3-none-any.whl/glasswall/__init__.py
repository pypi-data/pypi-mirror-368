

import os
import pathlib
import platform
import tempfile

__version__ = "5.9.0"

_OPERATING_SYSTEM = platform.system()
_PYTHON_VERSION = platform.python_version()
_ROOT = os.path.dirname(__file__)
_TEMPDIR = str(pathlib.Path(os.environ.get("AGENT_TEMPDIRECTORY", tempfile.gettempdir())).joinpath("glasswall").resolve())

from glasswall import config, content_management, determine_file_type, utils
from glasswall.libraries.archive_manager.archive_manager import ArchiveManager
from glasswall.libraries.editor.editor import Editor
from glasswall.libraries.rebuild.rebuild import Rebuild
from glasswall.libraries.security_tagging.security_tagging import SecurityTagging
from glasswall.libraries.word_search.word_search import WordSearch


class GwReturnObj:
    """ An object intended mostly for internal use that has different
    attributes depending on which library and functionality utilises it, such
    as `status`, `buffer`, and `buffer_bytes`
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
