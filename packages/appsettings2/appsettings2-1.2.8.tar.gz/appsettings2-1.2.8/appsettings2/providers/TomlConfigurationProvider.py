# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from .ConfigurationProvider import ConfigurationProvider
from ..Configuration import Configuration
from ..ConfigurationException import ConfigurationException
import os
import tomllib as _toml
from typing import Any

type FileDescriptor = int
type any = Any

class TomlConfigurationProvider(ConfigurationProvider):
    """
    Populates structured configuration data from TOML.
    """

    __obj:dict

    def __init__(self, filepath:str = None, *, toml:str = None, fd:FileDescriptor = None, required:bool = True):
        """
        The `filepath`, `toml`, and `fd` parameters are mutually exclusive.
        
        :param filepath: Optional path to a TOML file used as a configuration source, defaults to None.
        :param toml: Optional TOML string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        """
        if filepath:
            if os.path.isfile(filepath):
                with open(filepath, 'rt') as file:
                    toml = file.read()
            elif required:
                raise ConfigurationException(f'Missing required file: {filepath}')
        elif fd:
            with open(fd, 'rt') as file:
                toml = file.read()
        if toml:
            self.__obj = _toml.loads(toml)
        else:
            self.__obj = None

    def __populateRecursive(self, configuration:Configuration, prefix:str, o:dict):
        for kvp in o.items():
            if isinstance(kvp[1], dict):
                self.__populateRecursive(configuration, f'{prefix}__{kvp[0]}', kvp[1])
            else:
                configuration.set(f'{prefix}__{kvp[0]}', kvp[1])

    def populateConfiguration(self, configuration:Configuration):
        if self.__obj is None:
            return
        for kvp in self.__obj.items():
            if isinstance(kvp[1], dict):
                self.__populateRecursive(configuration, kvp[0], kvp[1])
            else:
                configuration.set(f'{kvp[0]}', kvp[1])
