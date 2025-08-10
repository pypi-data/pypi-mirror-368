# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from .ConfigurationProvider import ConfigurationProvider
from ..Configuration import Configuration
import sys

class CommandLineConfigurationProvider(ConfigurationProvider):
    """
    Populates configuration data from Command-Line arguments.
    """

    __argv:list[str]

    def __init__(self, argv:list[str] = None):
        """
        :param argv: Optional arg list used in lieu of `sys.argv`, defaults to None.
        """
        self.__argv = argv if argv is not None else sys.argv

    def populateConfiguration(self, configuration:Configuration):
        if self.__argv is None:
            return
        pending_key = None
        for arg in self.__argv:
            safe_arg = arg.lstrip('-')
            eqidx = safe_arg.find('=')
            if pending_key is not None:
                if (not arg.startswith('-')) and (eqidx < 1):
                    v = safe_arg.lstrip('=')
                    configuration.set(pending_key, v)
                    pending_key = None
                else:
                    configuration.set(pending_key, True)
                    pending_key = None
            if eqidx > 0:
                k = safe_arg[0:eqidx]
                v = safe_arg[eqidx+1:len(safe_arg)]
                configuration.set(k, v)
            else:
                pending_key = safe_arg.lstrip('=')
        if pending_key is not None:
            configuration.set(pending_key, True)
