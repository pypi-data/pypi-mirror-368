# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from .Configuration import Configuration
from .ConfigurationException import ConfigurationException
from .providers import *
import typing

type FileDescriptor = int
type any = typing.Any

class ConfigurationBuilder:
    """
    Builds a :py:class:`~appsettings2.Configuration` object from one or more :py:class:`~appsettings2.providers.ConfigurationProvider` instances.
    """

    __normalize:bool
    __providers:list[ConfigurationProvider]

    def __init__(self, *, normalize:bool = False, scrubkeys:bool = False):
        """
        :param normalize: Option indicating whether or not attribute names should be normalized to upper-case on the resulting :py:class:`~appsettings2.Configuration` object, defaults to False.
        :param scrubkeys: Option indicating whether or not attribute names should be scrubbed to be compatible with the Python lexer, defaults to False.
        """
        self.__normalize = normalize
        self.__scrubkeys = scrubkeys
        self.__providers = []

    def addProvider(self, provider:ConfigurationProvider) -> 'ConfigurationBuilder':
        """
        Adds the specified `ConfigurationProvider` object to the builder.
        Can be called multiple times to add multiple providers.

        :param provider: A class implementing the `ConfigurationProvider` abstract class.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        if provider is None or not issubclass(type(provider), ConfigurationProvider):
            raise ConfigurationException('Missing/Invalid argument: provider')
        self.__providers.append(provider)
        return self
    
    def addCommandLine(self, argv=None) -> 'ConfigurationBuilder':
        """
        Adds a :py:class:`~appsettings2.providers.CommandLineConfigurationProvider`, optionally overriding ``argv``.

        :param argv: Optional override of ``sys.argv``, defaults to None.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.addProvider(CommandLineConfigurationProvider(argv=argv))

    def addEnvironment(self) -> 'ConfigurationBuilder':
        """
        Adds a :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider`.

        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.addProvider(EnvironmentConfigurationProvider())

    def addJson(self, filepath:str = None, *, json:str = None, fd:FileDescriptor = None, required:bool = True) -> 'ConfigurationBuilder':
        """
        Adds a :py:class:`~appsettings2.providers.JsonConfigurationProvider`.
        The `filepath`, `json`, and `fd` parameters are mutually exclusive.
        
        :param filepath: Optional path to a JSON file used as a configuration source, defaults to None.
        :param json: Optional JSON string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.addProvider(JsonConfigurationProvider(filepath=filepath, json=json, fd=fd, required=required))

    def addToml(self, filepath:str = None, *, toml:str = None, fd:FileDescriptor = None, required:bool = True) -> 'ConfigurationBuilder':
        """
        Adds a :py:class:`~appsettings2.providers.TomlConfigurationProvider`.
        The `filepath`, `toml`, and `fd` parameters are mutually exclusive.
        
        :param filepath: Optional path to a TOML file used as a configuration source, defaults to None.
        :param toml: Optional TOML string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.addProvider(TomlConfigurationProvider(filepath=filepath, toml=toml, fd=fd, required=required))

    def addYaml(self, filepath:str = None, *, yaml:str = None, fd:FileDescriptor = None, required:bool = True) -> 'ConfigurationBuilder':
        """
        Adds a :py:class:`~appsettings2.providers.YamlConfigurationProvider`.
        The `filepath`, `yaml`, and `fd` parameters are mutually exclusive.
        
        :param filepath: Optional path to a YAML file used as a configuration source, defaults to None.
        :param yaml: Optional YAML string used as a configuration source, defaults to None.
        :param fd: Optional file descriptor (int) to be used as a configuration source, defaults to None.
        :param required: Optional parameter indicating whether the configuration source will raise `ConfigurationException` if the specified configuration source is missing, defaults to True.
        :return: Returns :py:class:`~appsettings2.ConfigurationBuilder` for method chaining.
        """
        return self.addProvider(YamlConfigurationProvider(filepath=filepath, yaml=yaml, fd=fd, required=required))

    def build(self) -> Configuration:
        """
        Builds a `Configuration` object using the providers which have been added to the builder.

        :return: A `Configuration` object, populated with configuration data.
        """
        configuration = Configuration(normalize=self.__normalize, scrubkeys=self.__scrubkeys)
        for provider in self.__providers:
            provider.populateConfiguration(configuration)
        return configuration
