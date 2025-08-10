# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

class ConfigurationException(Exception):
    """An exception raised by `appsettings2` library."""
    def __init__(self, reason:str = None):
        super().__init__(reason)
