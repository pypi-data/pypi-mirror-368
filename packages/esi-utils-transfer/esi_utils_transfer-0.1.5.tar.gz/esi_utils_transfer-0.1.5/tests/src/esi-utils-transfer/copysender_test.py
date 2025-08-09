#!/usr/bin/env python

# stdlib imports
import os.path
import tempfile
import shutil

from esi_utils_transfer.copysender import CopySender


def test_files():
    print("Testing basic file system copy with a file...")
    thisfile = os.path.abspath(__file__)
    tempdir = tempfile.mkdtemp()
    cancelfile = "foo.cancel"
    try:
        cpsender = CopySender(
            properties={"remote_directory": tempdir},
            local_files=[thisfile],
            cancelfile=cancelfile,
        )
        nfiles, send_msg = cpsender.send()
        assert os.path.isfile(os.path.join(tempdir, thisfile))
        delete_msg = cpsender.cancel()
        assert os.path.isfile(os.path.join(tempdir, cancelfile))
        print("Passed basic file system copy.")
    except Exception:
        raise Exception("Failed to copy or delete a file.")
    finally:
        shutil.rmtree(tempdir)


def test_directory():
    print("Testing basic file system copy with folders...")
    homedir = os.path.dirname(os.path.abspath(__file__))  # where is this script?
    root, last_folder = os.path.split(homedir)
    thisfile = os.path.abspath(__file__)
    tempdir = tempfile.mkdtemp()
    cancelfile = "foo.cancel"
    cancelmessage = "This event has been canceled"
    try:
        cpsender = CopySender(
            properties={"remote_directory": tempdir},
            local_directory=homedir,
            cancelfile=cancelfile,
        )
        nfiles, send_msg = cpsender.send()
        assert os.path.isfile(os.path.join(tempdir, thisfile))
        cancel_msg = cpsender.cancel()
        assert os.path.isfile(os.path.join(tempdir, cancelfile))
        print("Passed basic file system copy.")

        cpsender = CopySender(
            properties={"remote_directory": tempdir},
            local_directory=homedir,
            cancelfile=cancelfile,
        )
        nfiles = cpsender.send()
        assert os.path.isfile(os.path.join(tempdir, thisfile))
        cancel_msg = cpsender.cancel(cancel_content=cancelmessage)
        assert os.path.isfile(os.path.join(tempdir, cancelfile))
        assert (
            open(os.path.join(tempdir, cancelfile), "rt").read().strip()
            == cancelmessage
        )

    except Exception:
        raise Exception("Failed to copy or delete a directory.")
    finally:
        shutil.rmtree(tempdir)


if __name__ == "__main__":
    test_files()
    test_directory()
