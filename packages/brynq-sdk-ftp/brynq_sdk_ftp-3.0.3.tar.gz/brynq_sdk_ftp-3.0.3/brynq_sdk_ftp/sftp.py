from brynq_sdk_brynq import BrynQ
from io import StringIO
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko import RSAKey
from paramiko.sftp_attr import SFTPAttributes
from typing import Union, List, Literal, Optional
from stat import S_ISREG
import os


class SFTP(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug=False):
        """
        Init the SFTP class
        :param label: The label of the connector
        :param debug: If you want to see debug messages
        """
        super().__init__()
        self.debug = debug

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

        # Try to fetch credentials from BrynQ; if not present, attributes remain unset
        try:
            credentials = self.interfaces.credentials.get(system="sftp", system_type=system_type)
            credentials = credentials.get('data')
            if credentials:
                if self.debug:
                    print(credentials)
                self.host = credentials['host']
                self.port = 22 if credentials.get('port') is None else credentials.get('port')
                self.username = credentials.get('username')
                self.password = credentials.get('password')
                self.private_key_path = credentials.get('private_key_password', None)
                self.private_key_passphrase = credentials.get('private_key_password', None)
                self.private_key = None
                if credentials.get('private_key'):
                    self.private_key = RSAKey(file_obj=StringIO(credentials.get('private_key')), password=self.private_key_passphrase)
        except ValueError:
            print("No credentials found for SFTP. If this was intended, use _set_credentials() to set the credentials to pass variables ['host', 'port', 'username', 'password', 'private_key', 'private_key_password']")

    def _set_credentials(self, credentials: dict):
        """
        When a child class(ex:Meta4) needs to set the credentials, use this method.
        Set SFTP connection credentials programmatically.

        Expected keys in credentials dict:
        - host (str)
        - port (int, optional; defaults to 22)
        - username (str)
        - password (str, optional)
        - private_key (str, optional; PEM string)
        - private_key_password (str, optional; passphrase for private_key)
        """
        # Core connection parameters
        self.host = credentials['host']
        self.port = 22 if credentials.get('port') is None else credentials.get('port')
        self.username = credentials.get('username')
        self.password = credentials.get('password')

        # Key options
        self.private_key_path = credentials.get('private_key_password')
        self.private_key_passphrase = credentials.get('private_key_password')
        if credentials.get('private_key'):
            self.private_key = RSAKey(file_obj=StringIO(credentials.get('private_key')), password=self.private_key_passphrase)



    def upload_file(self, local_filepath, remote_filepath, confirm=True) -> SFTPAttributes:
        """
        Upload a single file to a remote location. If there is no Private key
        :param local_filepath: The file and the full path on your local machine
        :param remote_filepath: The path and filename on the remote location
        :param confirm: If you want to confirm the upload
        :return: status
        """
        self.client.connect(hostname=self.host, port=self.port, username=self.username, password=self.password, pkey=self.private_key, passphrase=self.private_key_passphrase)
        sftp = self.client.open_sftp()
        response = sftp.put(local_filepath, remote_filepath, confirm=confirm)
        self.client.close()

        return response

    def list_dir(self, remote_filepath, get_folders: bool = False) -> List[str]:
        """
        Read the files and folders an a certain location
        :param remote_filepath: The full path where you want to get the content from
        :return: a list with files and folders in the given location
        """
        self.client.connect(hostname=self.host, port=self.port, username=self.username, pkey=self.private_key, password=self.password)
        sftp = self.client.open_sftp()
        sftp.chdir(remote_filepath)
        list_files = sftp.listdir_attr()
        list_files = [file.filename for file in list_files if S_ISREG(file.st_mode) or get_folders]
        self.client.close()

        return list_files

    def download_file(self, remote_path, remote_file, local_path):
        """
        Download a single file
        :param remote_path: the path where the remote file exists
        :param remote_file: the remote file itself
        :param local_path: the path where the file needs to be downloaded to
        :return: a file object
        """
        self.client.connect(hostname=self.host, port=self.port, username=self.username, pkey=self.private_key, password=self.password)
        sftp = self.client.open_sftp()
        sftp.get(remotepath=f'{remote_path}{remote_file}', localpath=f'{local_path}/{remote_file}')
        self.client.close()

    def make_dir(self, remote_path, new_dir_name):
        """
        Create a new folder on a remote location
        :param remote_path: The location where you want to create the new folder
        :param new_dir_name: The name of the new folder
        :return: a status if creating succeeded or not
        """
        self.client.connect(hostname=self.host, port=self.port, username=self.username, pkey=self.private_key, password=self.password)
        sftp = self.client.open_sftp()
        sftp.chdir(remote_path)
        sftp.mkdir(new_dir_name)
        self.client.close()

    def remove_file(self, remote_file):
        """
        Remove a file on a remote location
        :param remote_file: the full path of the file that needs to be removed
        :return: a status if deleting succeeded or not
        """
        self.client.connect(hostname=self.host, port=self.port, username=self.username, pkey=self.private_key, password=self.password)
        sftp = self.client.open_sftp()
        sftp.remove(remote_file)
        self.client.close()

    def move_file(self, old_file_path: str, new_file_path: str):
        """
        Move or rename a file on a remote location
        :param old_file_path: the full path of the file that needs to be moved or renamed
        :param new_file_path: the full path of the new location of the file
        :return:
        """
        self.client.connect(hostname=self.host, port=self.port, username=self.username, pkey=self.private_key, password=self.password)
        sftp = self.client.open_sftp()
        sftp.rename(oldpath=old_file_path, newpath=new_file_path)
        self.client.close()

    def rename_file(self, old_file_path: str, new_file_path: str):
        self.move_file(old_file_path=old_file_path, new_file_path=new_file_path)
