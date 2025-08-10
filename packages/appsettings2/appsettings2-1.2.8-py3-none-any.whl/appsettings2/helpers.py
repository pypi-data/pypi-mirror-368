# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from .Configuration import Configuration
from .ConfigurationBuilder import ConfigurationBuilder
from .providers import *

def getConfiguration(baseName:str = 'appsettings', json:bool = True, toml:bool = True, yaml:bool = True, cli:bool = True, environment:bool = True, variations:list[str] = ['', 'prod', 'production', 'stage', 'staging', 'qa', 'dev', 'development', 'local']) -> Configuration:
    builder:ConfigurationBuilder = ConfigurationBuilder()
    variations = variations if variations is not None and len(variations) > 0 else [None]
    for variation in variations:
        variation = f'.{variation}' if variation is not None and len(variation) > 0 else ''
        if json:
            builder.addJson(f'{baseName}{variation}.json', required=False)
        if toml:
            builder.addToml(f'{baseName}{variation}.toml', required=False)
        if yaml:
            builder.addYaml(f'{baseName}{variation}.yaml', required=False)
    if cli:
        builder.addCommandLine()
    if environment:
        builder.addEnvironment()
    return builder.build()
