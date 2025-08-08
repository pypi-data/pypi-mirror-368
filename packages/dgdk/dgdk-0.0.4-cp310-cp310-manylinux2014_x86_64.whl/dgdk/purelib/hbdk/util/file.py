r"""
File utilities
"""

import os
import errno
import shutil


def force_symlink(file1, file2):
    try:
        os.symlink(file1, file2)
    except OSError as e:
        if e.errno == errno.EEXIST:
            if os.path.isfile(file2) or os.path.islink(file2):
                os.remove(file2)
            else:
                shutil.rmtree(file2)
            os.symlink(file1, file2)
