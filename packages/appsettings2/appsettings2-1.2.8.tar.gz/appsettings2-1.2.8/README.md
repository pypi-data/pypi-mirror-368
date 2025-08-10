# `appsettings2`

A python library that unifies configuration sources into a `Configuration` object that can be bound to complex types, or accessed directly for configuration data.

It can be installed from [PyPI](https://pypi.org/project/appsettings2/) through the usual methods.

This README is a high-level overview of core features. For complete documentation please visit [https://appsettings2.readthedocs.io/](https://appsettings2.readthedocs.io/).

## Quick Start

Using `appsettings2` is straightforward:

1. Construct a `ConfigurationBuilder` object.
2. Add one or more `ConfigurationProvider` objects to it.
3. Call `build(...)` to get a `Configuration` object populated with configuration data.

```python
from appsettings2 import *
from appsettings2.providers import *

config = ConfigurationBuilder()\
    .addProvider(JsonConfigurationProvider(f'appsettings.json'))\
    .addProvider(JsonConfigurationProvider(f'appsettings.Development.json', required=False))\
    .addProvider(EnvironmentConfigurationProvider())\
    .build()

print(config)
```

In the above example two JSON Configuration Providers are added to the builder. The first will fail if "appsettings.json" is not found, the second will succeed whether or not the "appsettings.Development.json" exists (because `required=False`). This allows for an optional development configuration to exist on development workstations without requiring a code change.

A third Configuration Provider is also added, an `EnvironmentConfigurationProvider`, which allows configuration to be loaded from Environment Variables.

The order of providers determines precedence of configuration data. Providers added last will take precedence over providers added first. Values which are not provided by later registrations will not override values provided by earlier registrations.

Given the example above, this means that configuration data provided via Environment Variables will override configuration data provided via JSON files.

## Accessing Configuration Data

There are multiple ways of accessing Configuration data:

* Using dynamic attributes which represent your configuration data.
* Using configuration keys by calling `get(...)` and `set(...)` methods.
* A dictionary-like interface exposing configuration data via indexer syntax.
* Binding the configuration data to a class/object you define.

### Direct Access via `Configuration` object

Consider the following code which demonstrates the first three methods mentioned above. All three of these methods are equivalent and return the same underlying value.

```python
# access `Configuration` attributes
value = configuration.ConnectionStrings.SampleDb
# access using `get(...)`
value = configuration.get('ConnectionStrings__SampleDb')
value = configuration.get('ConnectionStrings:SampleDb')
value = configuration.get('ConnectionStrings').get('SampleDb')
# access using indexer
value = configuration['ConnectionStrings__SampleDb']
value = configuration['ConnectionStrings:SampleDb']
value = configuration['ConnectionStrings']['SampleDb']
```

When accessing hierarchical data by "key" you can use a double-underscore delimiter or a colon delimiter, they are equivalent.

Devs and Ops from different walks will likely prefer one form over the other, so both are supported.

Additionally, keys are case-insensitive (attribute names are not.)

### Binding `Configuration` to Objects

It's possible to bind configuration data to complex types. While some of the implementation is currently naive, it should work well for the vast majority of use cases. If you find your particular case does not work well please reach out to me and I will work with you to implement a sensible solution.  Consider the following Python code:

```python
json = """{
  "ConnectionStrings": {
    "SampleDb": "my_cxn_string"
  },
  "EnableSwagger": true,
  "MaxBatchSize": 100
}"""

class ConnStrs:
    """An ugly class name to demonstrate the class name does not matter."""
    SampleDB:str

class AppSettings:
    ConnectionStrings:ConnStrs
    EnableSwagger:bool
    MaxBatchSize:int

configuration = ConfigurationBuilder()\
    .addProvider(JsonConfigurationProvider(json=json))
    .build()

settings = AppSettings()
configuration.bind(settings)

print(settings.ConnectionStrings.SampleDB) # prints "my_cxn_string"
```

The resulting `settings` object will contain all of the configuration data properly typed according to type hints.

It is also possible to bind to a subset of a configuration, building upon the above, consider the following:

```python
connectionStrings = configuration.bind(ConnStrs(), 'ConnectionStrings')
print(connectionStrings.SampleDB)
```

Lastly, a cautious eye may have noticed that the input configuration and class definition have a casing difference. `SampleDb` vs `SampleDB` -- by design binding is case-insensitive. This ensures that automation/configuration systems which can only communicate in upper-case can be used to populate complex objects which follow a strict naming convention without burdening devs/devops with extra work.

### Accessing `Configuration` Dictionary-like

`Configuration` is dict-like and in most cases can be used as if it were a dict where strict type checks would not otherwise prevent it.

### Transform `Configuration` to Dictionary

You can transform a `Configuration` instance into a dictionary (as a copy.) If you have some chunk of code that can consume a dictionary but can't consume a Python object (it happens) then you can get at a proper dictionary instance as follows:

```python
configuration = builder.build()
d = configuration.toDictionary()
print(d)
```

## Providers

* Command-Line args, via [CommandLineConfigurationProvider](https://appsettings2.readthedocs.io/en/latest/ref/providers/CommandLineConfigurationProvider.html).
* Environment variables, via [EnvironmentConfigurationProvider](https://appsettings2.readthedocs.io/en/latest/ref/providers/EnvironmentConfigurationProvider.html).
* JSON, via [JsonConfigurationProvider](https://appsettings2.readthedocs.io/en/latest/ref/providers/JsonConfigurationProvider).
* TOML, via [TomlConfigurationProvider](https://appsettings2.readthedocs.io/en/latest/ref/providers/TomlConfigurationProvider).
* YAML, via [YamlConfigurationProvider](https://appsettings2.readthedocs.io/en/latest/ref/providers/YamlConfigurationProvider).

### Custom Provider Development

You can implement custom Configuration Providers by subclassing `ConfigurationProvider` and implementing `populateConfiguration(...)`.

For a peek at the simplicity of provider implementation, this is `ConfigurationProvider`:

```python
class ConfigurationProvider(abstract):

    @abstractmethod
    def populateConfiguration(self, configuration:Configuration) -> None:
        """The ConfigurationProvider will populate the provided Configuration instance."""
        pass
```

Essentially, you read your configuration source and write the configuration data into the specified `Configuration` object. Much of the complexity in dealing with hierarchy and allocation is encapsulated within the impl of `Configuration`. As a result, most providers are less than 20 lines of functional code.

## Helpers

There are several helpers available which simplify loading configurations. Consider the following example:

```python
import appsettings2

config = appsettings2.getConfiguration()
```

You can read more about `getConfiguration` in [the docs](https://appsettings2.readthedocs.io/en/latest/ref/helpers/getConfiguration.html).

## Contact

You can reach me on [Discord](https://discordapp.com/users/307684202080501761) or [open an Issue on Github](https://github.com/wilson0x4d/appsettings2/issues/new/choose).
