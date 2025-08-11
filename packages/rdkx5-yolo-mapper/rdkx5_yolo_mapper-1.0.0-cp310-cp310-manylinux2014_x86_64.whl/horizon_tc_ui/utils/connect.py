#!/usr/bin/env python
# Copyright (c) 2022 Horizon Robotics.All Rights Reserved.
#
# The material in this file is confidential and contains trade secrets
# of Horizon Robotics Inc. This is proprietary information owned by
# Horizon Robotics Inc. No part of this work may be disclosed,
# reproduced, copied, transmitted, or used in any way for any purpose,
# without the express written permission of Horizon Robotics Inc.

import logging
import os
import re
import sys
import traceback
from stat import S_ISDIR
from typing import Tuple

import paramiko
from paramiko.channel import ChannelFile, ChannelStderrFile, ChannelStdinFile


class Board:
    def __init__(self,
                 host: str,
                 port: int = 22,
                 username: str = "root",
                 password: str = "") -> None:
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._client = None
        self.sftp = None

    def __enter__(self) -> 'Board':
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def _connect(self) -> None:
        logging.debug(f"Board ip: {self._host}")
        logging.debug(f"Board port: {self._port}")
        logging.debug(f"Username: {self._username}")
        logging.debug(f"Password: {self._password}")
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if not self._password:
            try:
                # Connect without password must use Transport object.
                # Getting the Transport first requires
                # trying to connect to the board
                self._client.connect(hostname=self._host,
                                     port=self._port,
                                     username=self._username,
                                     allow_agent=False,
                                     timeout=None)
            except Exception:
                try:
                    transport = self._client.get_transport()
                    logging.debug('Get transport successful')
                    transport.auth_none(username=self._username)
                except paramiko.SSHException:
                    raise paramiko.SSHException(
                        f'Connect to {self._host} without password failed!'
                        'Please make sure you can connect the board '
                        'with ssh command')
        else:
            try:
                self._client.load_system_host_keys()
                self._client.connect(hostname=self._host,
                                     port=self._port,
                                     username=self._username,
                                     password=self._password,
                                     allow_agent=False,
                                     timeout=None)
            except paramiko.BadHostKeyException:
                raise paramiko.AuthenticationException(
                    f'Connect to {self._host} '
                    f'with host key failed!'
                    'Please make sure you can connect the board '
                    'with ssh command')
            except paramiko.AuthenticationException:
                raise paramiko.AuthenticationException(
                    f'Connect to {self._host} '
                    f'with username {self._username} and '
                    f'password {self._password} failed!')
        self.sftp = self._client.open_sftp()

    def _is_dir(self, remote_path: str) -> bool:
        try:
            return S_ISDIR(self.sftp.stat(remote_path).st_mode)
        except IOError:
            raise ValueError(f"{remote_path} not exists")

    def download_dir(self,
                     remote_path: str,
                     local_path: str,
                     regex: str = "") -> None:
        """Download remote files form a dir.
        This function does not support recursive downloads,
        and will skip folders in the remote_path.

        Args:
            remote_path (str): remote dir path
            local_path (str): local dir path
            regex (str, optional): regex pattern. Defaults to "".
        """
        if not os.path.exists(local_path):
            raise ValueError(f"Local path {local_path} is not exists.")
        file_list = self.sftp.listdir(remote_path)
        if regex:
            file_list = [
                file for file in file_list if re.compile(regex).match(file)
            ]

        remote_path_list = [os.path.join(remote_path, i) for i in file_list]

        local_path_list = [os.path.join(local_path, i) for i in file_list]
        for idx, file_path in enumerate(remote_path_list):
            if self._is_dir(remote_path=file_path):
                logging.warning(f"Skip {file_path} download with it's a dir")
                continue
            self.sftp.get(remotepath=file_path, localpath=local_path_list[idx])
            logging.debug(
                f"Download {file_path} to {local_path_list[idx]} Success")

    def download(self, remote_path: str, local_path: str) -> None:
        try:
            local_path = os.path.join(local_path,
                                      os.path.basename(remote_path))
            logging.debug('Downloading ' + remote_path + ' to ' + local_path)
            self.sftp.get(remote_path, local_path)
        except Exception:
            traceback.print_exc()
            logging.critical('Error occurs when downloading file ' +
                             remote_path + ' from BPU')
            sys.exit(1)

    def upload(self, localpath, remotepath) -> None:
        try:
            remotepath = os.path.join(remotepath, os.path.basename(localpath))
            logging.debug('Uploading ' + localpath + ' to ' + remotepath)
            self.sftp.put(localpath, remotepath)
        except Exception:
            traceback.print_exc()
            logging.critical('Error occurs when uploading file ' + localpath +
                             ' to Board')
            sys.exit(1)

    def exec_command(
        self, command
    ) -> Tuple[ChannelStdinFile, ChannelFile, ChannelStderrFile]:
        stdin, stdout, stderr = self._client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            error = stderr.read().decode('utf-8')
            raise paramiko.SSHException(
                f'Execute command {command} failed: {error}')
        logging.info('REMOTE: executing [' + command + ']')
        return stdin, stdout, stderr

    def close(self) -> None:
        if self._client:
            self._client.close()
