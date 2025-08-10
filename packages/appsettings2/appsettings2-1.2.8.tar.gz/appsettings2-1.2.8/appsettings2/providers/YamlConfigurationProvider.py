# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from .ConfigurationProvider import ConfigurationProvider
from ..Configuration import Configuration
from ..ConfigurationException import ConfigurationException
from io import StringIO
import os
from typing import Any
import yaml as _yaml

type FileDescriptor = int
type any = Any

class YamlConfigurationProvider(ConfigurationProvider):
    """
    Populates structured configuration data from YAML.
    """

    __obj:dict

    def __init__(self, filepath:str = None, *, yaml:str = None, fd:FileDescriptor = None, required:bool = True):
        """
        The `filepath`, `yaml`, and `fd` parameters are mutually exclusive.
        
        :param filepath: Optional path to a TAML file used as a configuration source, defaults to None.
        :param yaml: Optional TAML string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        """
        self.__obj = None
        if filepath:
            if os.path.isfile(filepath):
                with open(filepath, 'rt') as file:
                    self.__obj = _yaml.safe_load(file)
            elif required:
                raise ConfigurationException(f'Missing required file: {filepath}')
        elif fd:
            with open(fd, 'rt') as file:
                self.__obj = _yaml.safe_load(file)
        elif yaml:
            stream = StringIO(yaml)
            self.__obj = _yaml.safe_load(stream)
            stream.close()

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
