#!/usr/bin/env python

# stdlib imports
import pathlib
from io import BytesIO
from unittest.mock import Mock, patch

from esi_utils_transfer.securesender import SecureSender


def test_copy_file():
    ssh_attrs = {
        "load_system_host_keys.return_value": None,
        "connect.return_value": None,
        "get_transport.return_value": None,
        "close.return_value": None,
        "exec_command.return_value": None,
    }

    scp_attrs = {
        "put.return_value": None,
        "close.return_value": None,
    }

    props = {
        "remote_host": "remotehost.ftp.host",
        "remote_directory": "data/dir",
        "private_key": "/home/user/privatekey.pri",
    }

    # create a mocked SSH *object*
    mock_ssh = Mock(**ssh_attrs)

    # create a mocked SCP *object*
    mock_scp = Mock(**scp_attrs)

    # patch the SecureSender _check_remote_folder() method
    with patch.object(SecureSender, "_check_remote_folder") as mocked_check:
        mocked_check.return_value = (True, True)
        with patch.object(SecureSender, "_make_remote_folder") as mocked_make:
            mocked_make.return_value = (True, True)
            with patch("esi_utils_transfer.securesender.SSHClient") as mocked_ssh:
                # tell the patched FTP class to return our mocked FTP object
                # instead of a real FTP object
                mocked_ssh.return_value = mock_ssh
                with patch("esi_utils_transfer.securesender.SCPClient") as mocked_scp:
                    mocked_scp.return_value = mock_scp
                    sender = SecureSender(properties=props)
                    sender._copy_file_with_path(
                        mock_scp, mock_ssh, "local_file", "remote_folder"
                    )


def test_check_remote_folder():
    zero_io1 = BytesIO(b"0")
    zero_io2 = BytesIO(b"0")
    ssh_attrs = {
        "load_system_host_keys.return_value": None,
        "connect.return_value": None,
        "get_transport.return_value": None,
        "close.return_value": None,
        "exec_command.side_effect": [("", zero_io1, ""), ("", zero_io2, "")],
    }

    scp_attrs = {
        "put.return_value": None,
        "close.return_value": None,
    }

    props = {
        "remote_host": "remotehost.ftp.host",
        "remote_directory": "data/dir",
        "private_key": "/home/user/privatekey.pri",
    }

    # create a mocked SSH *object*
    mock_ssh = Mock(**ssh_attrs)

    # create a mocked SCP *object*
    mock_scp = Mock(**scp_attrs)

    # patch the SSHClient *class*
    with patch("esi_utils_transfer.securesender.SSHClient") as mocked_ssh:
        # tell the patched FTP class to return our mocked FTP object
        # instead of a real FTP object
        mocked_ssh.return_value = mock_ssh
        with patch("esi_utils_transfer.securesender.SCPClient") as mocked_scp:
            mocked_scp.return_value = mock_scp
            sender = SecureSender(properties=props)
            exists, isdir = sender._check_remote_folder(mock_ssh, "")
            assert exists
            assert isdir


def test_make_remote_folder():
    zero_io1 = BytesIO(b"0")
    zero_io2 = BytesIO(b"0")
    props = {
        "remote_host": "remotehost.ftp.host",
        "remote_directory": "data/dir",
        "private_key": "/home/user/privatekey.pri",
    }

    ssh_attrs = {
        "load_system_host_keys.return_value": None,
        "connect.return_value": None,
        "get_transport.return_value": None,
        "close.return_value": None,
        "exec_command.side_effect": [("", zero_io1, "")],
    }

    scp_attrs = {
        "put.return_value": None,
        "close.return_value": None,
    }

    # create a mocked SSH *object*
    mock_ssh = Mock(**ssh_attrs)

    # create a mocked SCP *object*
    mock_scp = Mock(**scp_attrs)

    # patch the SecureSender _check_remote_folder() method
    with patch.object(SecureSender, "_check_remote_folder") as mocked_method:
        mocked_method.side_effect = [(False, False), (True, True)]
        with patch("esi_utils_transfer.securesender.SSHClient") as mocked_ssh:
            # tell the patched FTP class to return our mocked FTP object
            # instead of a real FTP object
            mocked_ssh.return_value = mock_ssh
            with patch("esi_utils_transfer.securesender.SCPClient") as mocked_scp:
                mocked_scp.return_value = mock_scp
                sender = SecureSender(properties=props)
                assert sender._make_remote_folder(mock_scp, mock_ssh, "")

    ssh_attrs = {
        "load_system_host_keys.return_value": None,
        "connect.return_value": None,
        "get_transport.return_value": None,
        "close.return_value": None,
        "exec_command.side_effect": [("", zero_io1, ""), ("", zero_io2, "")],
    }

    # create a mocked SSH *object*
    mock_ssh = Mock(**ssh_attrs)

    # test the other branch in the make_remote_folder method
    with patch.object(SecureSender, "_check_remote_folder") as mocked_method:
        mocked_method.side_effect = [(True, False), (True, True)]
        with patch("esi_utils_transfer.securesender.SSHClient") as mocked_ssh:
            # tell the patched FTP class to return our mocked FTP object
            # instead of a real FTP object
            mocked_ssh.return_value = mock_ssh
            with patch("esi_utils_transfer.securesender.SCPClient") as mocked_scp:
                mocked_scp.return_value = mock_scp
                sender = SecureSender(properties=props)
                assert sender._make_remote_folder(mock_scp, mock_ssh, "")


def test_send():
    ssh_attrs = {
        "load_system_host_keys.return_value": None,
        "connect.return_value": None,
        "get_transport.return_value": None,
        "close.return_value": None,
    }

    scp_attrs = {
        "put.return_value": None,
        "close.return_value": None,
    }

    props = {
        "remote_host": "remotehost.ftp.host",
        "remote_directory": "data/dir",
        "private_key": "/home/user/privatekey.pri",
    }

    local_file = pathlib.Path(__file__)
    local_directory = local_file.parent

    # create a mocked SSH *object*
    mock_ssh = Mock(**ssh_attrs)

    # create a mocked SCP *object*
    mock_scp = Mock(**scp_attrs)

    # patch the _copy_file_with_path() method of SecureSender
    with patch.object(SecureSender, "_copy_file_with_path") as mocked_copy:
        mocked_copy.return_value = None
        with patch.object(SecureSender, "_make_remote_folder") as mocked_make:
            mocked_make.return_value = True
            # patch the SSHClient *class*
            with patch("esi_utils_transfer.securesender.SSHClient") as mocked_ssh:
                # tell the patched FTP class to return our mocked FTP object
                # instead of a real FTP object
                mocked_ssh.return_value = mock_ssh
                with patch("esi_utils_transfer.securesender.SCPClient") as mocked_scp:
                    mocked_scp.return_value = mock_scp
                    # this should succeed
                    sender = SecureSender(properties=props, local_files=[local_file])
                    nfiles, _ = sender.send()
                    assert nfiles == 1

    # patch the _copy_file_with_path() method of SecureSender
    tmp_files = list(local_directory.glob("**/*"))
    cmp_files = []
    for tmpfile in tmp_files:
        if tmpfile.is_dir():
            continue
        cmp_files.append(tmpfile)
    with patch.object(SecureSender, "_copy_file_with_path") as mocked_copy:
        mocked_copy.return_value = None
        with patch.object(SecureSender, "_make_remote_folder") as mocked_make:
            mocked_make.return_value = True
            # patch the SSHClient *class*
            with patch("esi_utils_transfer.securesender.SSHClient") as mocked_ssh:
                # tell the patched FTP class to return our mocked FTP object
                # instead of a real FTP object
                mocked_ssh.return_value = mock_ssh
                with patch("esi_utils_transfer.securesender.SCPClient") as mocked_scp:
                    mocked_scp.return_value = mock_scp
                    # this should succeed
                    sender = SecureSender(
                        properties=props, local_directory=local_directory
                    )
                    nfiles, _ = sender.send()
                    assert nfiles == len(cmp_files)


def test_cancel():
    zero_io1 = BytesIO(b"0")
    zero_io2 = BytesIO(b"0")
    ssh_attrs = {
        "load_system_host_keys.return_value": None,
        "connect.return_value": None,
        "get_transport.return_value": None,
        "close.return_value": None,
        "exec_command.side_effect": [("", zero_io1, ""), ("", zero_io2, "")],
    }

    scp_attrs = {
        "put.return_value": None,
        "close.return_value": None,
    }

    props = {
        "remote_host": "remotehost.ftp.host",
        "remote_directory": "data/dir",
        "private_key": "/home/user/privatekey.pri",
    }

    local_file = pathlib.Path(__file__)

    # create a mocked SSH *object*
    mock_ssh = Mock(**ssh_attrs)

    # create a mocked SCP *object*
    mock_scp = Mock(**scp_attrs)

    # patch the _copy_file_with_path() method of SecureSender
    with patch.object(SecureSender, "_copy_file_with_path") as mocked_copy:
        mocked_copy.return_value = None
        with patch.object(SecureSender, "_make_remote_folder") as mocked_make:
            mocked_make.return_value = True
            # patch the SSHClient *class*
            with patch("esi_utils_transfer.securesender.SSHClient") as mocked_ssh:
                # tell the patched FTP class to return our mocked FTP object
                # instead of a real FTP object
                mocked_ssh.return_value = mock_ssh
                with patch("esi_utils_transfer.securesender.SCPClient") as mocked_scp:
                    mocked_scp.return_value = mock_scp
                    # this should succeed
                    sender = SecureSender(properties=props, local_files=[local_file])
                    msg = sender.cancel()
                    assert "A .cancel file has been placed in remote" in msg


if __name__ == "__main__":
    test_check_remote_folder()
    test_make_remote_folder()
    test_copy_file()
    test_send()
    test_cancel()
