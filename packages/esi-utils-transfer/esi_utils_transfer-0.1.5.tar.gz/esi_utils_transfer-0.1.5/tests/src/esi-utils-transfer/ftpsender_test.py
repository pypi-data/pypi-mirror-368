#!/usr/bin/env python

# stdlib imports
import pathlib
from unittest.mock import Mock, patch

# local imports
from esi_utils_transfer.ftpsender import FTPSender


def test_send():
    base_attrs = {
        "login.return_value": None,
        "quit.return_value": None,
        "cwd.return_value": None,
        "mkd.return_value": None,
        "storbinary.return_value": None,
        "rename.return_value": None,
    }

    props = {
        "remote_host": "remotehost.ftp.host",
        "remote_directory": "data/dir",
        "user": "remote_user",
        "password": "remote_pword",
    }

    local_file = pathlib.Path(__file__)
    local_directory = local_file.parent

    # create a mocked FTP *object*
    mock_ftp = Mock(**base_attrs)
    # patch the FTP *class*
    with patch("esi_utils_transfer.ftpsender.FTP") as mocked_ftp:
        # tell the patched FTP class to return our mocked FTP object
        # instead of a real FTP object
        mocked_ftp.return_value = mock_ftp
        # this should succeed
        sender = FTPSender(properties=props, local_files=[local_file])
        nfiles, _ = sender.send()
        assert nfiles == 1

        # this should succeed
        tmp_files = list(local_directory.glob("**/*"))
        cmp_files = []
        for tmpfile in tmp_files:
            if tmpfile.is_dir():
                continue
            cmp_files.append(tmpfile)
        sender = FTPSender(properties=props, local_directory=str(local_directory))
        nfiles, _ = sender.send()
        assert nfiles == len(cmp_files)

        # this should succeed
        with patch("esi_utils_transfer.ftpsender.FTP") as mocked_ftp:
            # tell the patched FTP class to return our mocked FTP object
            # instead of a real FTP object
            mocked_ftp.return_value = mock_ftp
            # this should succeed
            sender = FTPSender(properties=props, local_files=[local_file])
            msg = sender.cancel()
            assert "file succesfully placed on" in msg


if __name__ == "__main__":
    test_send()
