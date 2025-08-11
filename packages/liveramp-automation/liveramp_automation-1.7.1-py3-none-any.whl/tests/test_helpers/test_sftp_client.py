from unittest import TestCase
from unittest.mock import patch

import paramiko
import pysftp

from liveramp_automation.helpers.sftp_client import SFTPClient


class TestSFTPClient(TestCase):
    @patch("liveramp_automation.helpers.sftp_client.pysftp.Connection")
    def test_context_manager_connection_success(self, mock_connection):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()
        cnopts = pysftp.CnOpts()
        with SFTPClient(
            username="user", password="pass", hostname="host", cnopts=cnopts
        ) as client:
            self.assertIsNotNone(client.sftp)
            mock_connection.assert_called_once_with(
                host="host",
                username="user",
                password="pass",
                port=22,
                private_key=None,
                private_key_pass=None,
                cnopts=cnopts,
            )
        mock_logger.info.assert_any_call("Successfully connected to host")
        mock_logger.info.assert_any_call("Disconnected from host")

    def test_context_manager_connection_failure(self):
        with self.assertRaises(paramiko.ssh_exception.AuthenticationException):
            with SFTPClient(username="user", password="pass"):
                pass

    @patch("liveramp_automation.helpers.sftp_client.pysftp.Connection")
    def test_download_file_success(self, mock_connection):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()
        mock_sftp = mock_connection.return_value
        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.download_file("remote.txt", "local.txt")
            self.assertTrue(result)
            mock_sftp.get.assert_called_once_with(
                remotepath="remote.txt", localpath="local.txt"
            )
        mock_logger.info.assert_any_call("SFTP Download successful")

    @patch("liveramp_automation.helpers.sftp_client.pysftp.Connection")
    def test_download_file_failure(self, mock_connection):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()
        mock_sftp = mock_connection.return_value
        mock_sftp.get.side_effect = Exception("Download error")
        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.download_file("remote.txt", "local.txt")
            self.assertFalse(result)
        mock_logger.error.assert_called_with("Error downloading file: Download error")

    @patch("liveramp_automation.helpers.sftp_client.pysftp.Connection")
    def test_upload_file_success(self, mock_connection):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()
        mock_sftp = mock_connection.return_value
        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.upload_file("local.txt", "remote.txt")
            self.assertTrue(result)
            mock_sftp.put.assert_called_once_with(
                localpath="local.txt", remotepath="remote.txt"
            )
        mock_logger.info.assert_any_call("SFTP Upload successful")

    @patch("liveramp_automation.helpers.sftp_client.pysftp.Connection")
    def test_upload_file_failure(self, mock_connection):
        mock_sftp = mock_connection.return_value
        mock_sftp.put.side_effect = Exception("Upload error")
        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.upload_file("local.txt", "remote.txt")
            self.assertFalse(result)

    @patch("liveramp_automation.helpers.sftp_client.pysftp.Connection")
    def test_list_files_success(self, mock_connection):
        mock_sftp = mock_connection.return_value
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]
        mock_sftp.isdir.side_effect = lambda path: path == "dir1"
        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, ["file1.txt", "file2.txt"])

    @patch("liveramp_automation.helpers.sftp_client.pysftp.Connection")
    def test_list_files_failure(self, mock_connection):
        mock_sftp = mock_connection.return_value
        mock_sftp.listdir.side_effect = Exception("List error")
        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, [])
