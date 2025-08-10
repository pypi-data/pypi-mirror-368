# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from .ConfigurationProvider import ConfigurationProvider
from ..Configuration import Configuration
import os

class EnvironmentConfigurationProvider(ConfigurationProvider):
    """
    Populates configuration data from Environment variables.
    """

    def populateConfiguration(self, configuration:Configuration):
        for k in os.environ:
            configuration.set(k, os.environ[k])
