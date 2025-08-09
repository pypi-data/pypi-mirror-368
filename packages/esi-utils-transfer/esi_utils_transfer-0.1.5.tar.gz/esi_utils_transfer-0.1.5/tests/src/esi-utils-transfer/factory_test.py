#!/usr/bin/env python

# stdlib imports
import os.path
import tempfile
import shutil

from esi_utils_transfer.factory import get_sender_class


def test():
    print("Testing basic file system copy...")
    thisfile = os.path.abspath(__file__)
    tempdir = tempfile.mkdtemp()
    try:
        sender_class = get_sender_class("copy")
        cpsender = sender_class(
            properties={"remote_directory": tempdir}, local_files=[thisfile]
        )
        nfiles = cpsender.send()
        nfiles = cpsender.cancel()
    except Exception:
        raise IOError("Failed to copy or delete a file.")
    shutil.rmtree(tempdir)
    print("Passed basic file system copy.")


if __name__ == "__main__":
    test()
