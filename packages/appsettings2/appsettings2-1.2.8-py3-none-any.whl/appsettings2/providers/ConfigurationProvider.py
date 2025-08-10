# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from ..Configuration import Configuration
from abc import ABC as abstract, abstractmethod

class ConfigurationProvider(abstract):
    """
    The abstract base class which all Configuration Providers implement.
    """

    @abstractmethod
    def populateConfiguration(self, configuration:Configuration) -> None:
        """
        Populates the provided :py:class:`~appsettings2.Configuration` object using provider-specific methods.
        """
        pass
