import os
from typing import List, Optional

import pysftp

from liveramp_automation.utils.log import Logger


class SFTPClient:
    """
    Encapsulates an SFTP session, providing methods for file upload and download.
    """

    def __init__(
        self,
        username: str,
        password: str,
        hostname: str = "files.liveramp.com",
        port: int = 22,
        private_key: Optional[str] = None,
        key_pass: Optional[str] = None,
        cnopts: Optional[pysftp.CnOpts] = None,
    ):
        """
        Initializes the SFTP session.

        Args:
            hostname: The hostname or IP address of the SFTP server.
            username: The username for authentication.
            password: The password for password authentication.
            port: The SFTP server port (default: 22).
            private_key: Path to the private key file for key authentication (optional).
            key_pass: Password for the private key (optional).
            cnopts: Optional CnOpts object for custom connection options.
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.private_key = private_key
        self.key_pass = key_pass
        self.cnopts: pysftp.CnOpts = cnopts
        self.sftp = None  # Initialize sftp connection

    def __enter__(self):
        """
        Context manager entry: Establishes the SFTP connection.
        """
        if not self.cnopts:
            self.cnopts = pysftp.CnOpts()
            self.cnopts.hostkeys = None

        try:
            self.sftp = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                private_key=self.private_key,
                private_key_pass=self.key_pass,
                cnopts=self.cnopts,
            )
            Logger.info(f"Successfully connected to {self.hostname}")
            return self  # Return the instance so you can access self.sftp
        except pysftp.ConnectionException as e:
            Logger.error(f"SFTP Connection error: {e}")
            raise  # Re-raise the exception to be caught by the caller

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit: Closes the SFTP connection.
        """
        if self.sftp:
            self.sftp.close()
            Logger.info(f"Disconnected from {self.hostname}")

    def download_file(
        self, remote_filepath: str, local_filepath: str, use_getfo: bool = False
    ) -> bool:
        """
        Downloads a file from the SFTP server to a local path.

        Args:
            remote_filepath: The path to the file on the SFTP server.
            local_filepath: The local path where the file should be saved.
            use_getfo: If True, uses getfo() for file-like object handling.
                       If False, uses get(). (default: False)

        Returns:
            True on success, False on failure.
        """
        try:
            Logger.info(
                f"SFTP Downloading: {remote_filepath} from {self.hostname} to local: {local_filepath}"
            )
            # Ensure the local directory exists, create it if necessary
            if use_getfo:
                # Use getfo() for downloading into a file-like object
                Logger.info("Using getfo() for file-like object handling.")
                with open(local_filepath, "wb") as lf:
                    self.sftp.getfo(remotepath=remote_filepath, flo=lf)
            else:
                # Use get() for direct file download
                Logger.info("Using get() for file download.")
                self.sftp.get(remotepath=remote_filepath, localpath=local_filepath)
            Logger.info("SFTP Download successful")
            return True
        except Exception as e:
            # Log any other unexpected errors
            Logger.error(f"Error downloading file: {e}")
            return False

    def upload_file(
        self, local_filepath: str, remote_filepath: str, use_putfo: bool = False
    ) -> bool:
        """
        Uploads a file from a local path to the SFTP server.

        Args:
            local_filepath: The local path to the file to upload.
            remote_filepath: The path to save the file on the SFTP server.
            use_putfo: If True, uses putfo() for file-like object handling.
                       If False, uses put(). (default: False)

        Returns:
            True on success, False on failure.
        """
        try:
            Logger.info(
                f"SFTP Uploading: {local_filepath} from local to {self.hostname}: {remote_filepath}"
            )
            if use_putfo:
                # Use putfo() for uploading from a file-like object
                with open(local_filepath, "rb") as f:
                    self.sftp.putfo(f, remote_filepath)
            else:
                # Use put() for direct file upload
                self.sftp.put(localpath=local_filepath, remotepath=remote_filepath)
            # Log success message
            Logger.info("SFTP Upload successful")
            return True
        except Exception as e:
            # Log any other unexpected errors
            Logger.info(f"Error uploading file: {e}")
            return False

    def upload_directory(
        self, local_dir: str, remote_dir: str, recursive: bool = False, **kwargs
    ) -> bool:
        """
        Uploads a directory from a local path to the SFTP server.

        Args:
            local_dir: The local path to the directory to upload.
            remote_dir: The path to save the directory on the SFTP server.
            recursive: If True, recursively uploads subdirectories. (default: False)

        Returns:
            True on success, False on failure.
        """
        try:
            Logger.info(
                f"SFTP Uploading directory: {local_dir} from local to {self.hostname}: {remote_dir}, recursive={recursive}"
            )
            # Determine the appropriate method to use based on the recursive flag
            method_name = "put_r" if recursive else "put_d"
            # Dynamically call the appropriate method (put_r for recursive, put_d for non-recursive)
            getattr(self.sftp, method_name)(
                remotepath=remote_dir, localpath=local_dir, **kwargs
            )
            Logger.info("SFTP Directory Upload successful")
            return True
        except Exception as e:
            Logger.error(f"Error uploading directory: {e}")
            return False

    def download_directory(
        self, remote_dir: str, local_dir: str, recursive: bool = False, **kwargs
    ) -> bool:
        """
        Downloads a directory from the SFTP server to a local path.

        Args:
            remote_dir: The path to the directory on the SFTP server.
            local_dir: The local path where the directory should be saved.
            recursive: If True, recursively downloads subdirectories. (default: False)

        Returns:
            True on success, False on failure.
        """
        try:
            Logger.info(
                f"SFTP Downloading directory: {remote_dir} from {self.hostname} to local: {local_dir}, recursive={recursive}"
            )

            # Determine the appropriate method to use based on the recursive flag
            method_name = "get_r" if recursive else "get_d"

            # Dynamically call the appropriate method (get_r for recursive, get_d for non-recursive)
            getattr(self.sftp, method_name)(
                remotepath=remote_dir, localpath=local_dir, **kwargs
            )
            Logger.info("SFTP Directory Download successful")
            return True
        except Exception as e:
            # Log any other unexpected errors
            Logger.info(f"Error downloading directory: {e}")
            return False

    def list_files(self, remote_dir: str) -> List[str]:
        """
        Lists the files in a directory on the SFTP server.

        Args:
            remote_dir: The path to the directory on the SFTP server.

        Returns:
            A list of strings, where each string is a filename in the directory.
            Returns an empty list on error.
        """
        try:
            files = self.sftp.listdir(remote_dir)
            return [
                f for f in files if not self.sftp.isdir(os.path.join(remote_dir, f))
            ]
        except Exception as e:
            Logger.error(f"Error listing files: {e}")
            return []

    def list_directories(self, remote_dir: str) -> List[str]:
        """
        Lists the directories in a directory on the SFTP server.

        Args:
            remote_dir: The path to the directory on the SFTP server.

        Returns:
            A list of strings, where each string is a directory name in the directory.
            Returns an empty list on error.
        """
        try:
            directories = self.sftp.listdir(remote_dir)
            return [
                d for d in directories if self.sftp.isdir(os.path.join(remote_dir, d))
            ]
        except Exception as e:
            print(f"Error listing directories: {e}")
            return []


"""
if __name__ == "__main__":
    # Example usage
    username = "username"
    password = "password"
    with SFTPClient(username=username, password=password) as sftp:
        sftp.download_file(
            remote_filepath="/uploads/br_delete_me/uploaded_from_local_file.txt",
            local_filepath="file.txt",
        )
        sftp.upload_file(
            local_filepath="file.txt",
            remote_filepath="/uploads/br_delete_me/file.txt",
        )
        sftp.upload_directory(
            local_dir="/path/to/local/dir",
            remote_dir="/path/to/remote/dir",
            recursive=True,
        )
        sftp.download_directory(
            remote_dir="/path/to/remote/dir",
            local_dir="/path/to/local/dir",
            recursive=True,
        )
        Logger.info(sftp.list_files(remote_dir="/uploads/br_delete_me/"))
        Logger.info(sftp.list_directories(remote_dir="/uploads/br_delete_me/"))
"""
