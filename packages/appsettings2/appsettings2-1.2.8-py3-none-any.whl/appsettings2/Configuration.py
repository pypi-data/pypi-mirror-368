# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import logging
from .ConfigurationException import ConfigurationException
import json
import re
import types
import typing
import unicodedata

type any = typing.Any
Configuration = typing.ForwardRef('Configuration')

class Configuration:
    """
    The :py:class:`~appsettings2.Configuration` class is how applications access configuration data populated by :py:class:`~appsettings2.providers.ConfigurationProvider` objects. It exposes configuration data through dynamic object attributes as well as a dictionary-like interface.
    """

    __key_scrub_re:re.Pattern
    __keys:dict[str, str]
    __normalize:bool

    def __init__(self, *, normalize:bool = False, scrubkeys:bool = False):
        """
        :param normalize: Option indicating whether or not attribute names should be normalized to upper-case on the resulting :py:class:`~appsettings2.Configuration` object, defaults to False.
        :param scrubkeys: Option indicating whether or not attribute names should be scrubbed to be compatible with the Python lexer, defaults to False.
        """
        self.__keys = {}
        self.__logger = logging.getLogger('appsettings2')
        self.__normalize = normalize
        self.__key_scrub_re = None if not scrubkeys else re.compile(r'[^A-Za-z0-9_]', re.IGNORECASE | re.UNICODE)

    def __delitem__(self, key:str) -> None:
        key = key.upper()
        k = self.__keys.get(key)
        if k is not None:
            delattr(self, k)
            self.__keys.pop(key)

    def __getitem__(self, key:str) -> any:
        """
        Gets the configuration data associated with the specified `key`.

        :param key: The configuration key to get data for. Supports `__` and `:` hierarchical delimiters.
        :return: The configuration data associated with `key`, otherwise raises `KeyError` if `key` was not found.
        """
        parts = key.replace(':', '__').split('__')
        o = self
        for part in parts:
            if o == self:
                k = self.__keys.get(part.upper())
                if k is None:
                    raise KeyError()
                else:
                    o = getattr(o, self.__scrub_key(k))
            else:
                o = o[part]
        return o

    def __iter__(self):
        return iter(self.__keys.values())

    def __len__(self) -> int:
        return len(self.__keys)

    def __recursiveBind(self, target:object, source:Configuration|dict) -> any:
        if target is None:
            return None
        if hasattr(target, '__class__'):
            targetTypeHints = typing.get_type_hints(getattr(target, '__class__'))
        else:
            targetTypeHints = typing.get_type_hints(target)
        names = set(dir(target) | targetTypeHints.keys())
        for aname in names:
            if aname.startswith('_'):
                continue
            lval = None if not hasattr(target, aname) else getattr(target, aname)
            if isinstance(lval, types.FunctionType) or isinstance(lval, types.MethodType):
                continue
            ahint = targetTypeHints.get(aname)
            rval = source.get(aname)
            if ahint is None:
                # attr has no type hints, attempt to treat as a property
                prop = getattr(type(target), aname)
                if hasattr(prop, 'fget') and getattr(prop, 'fget') is not None:
                    try:
                        lval = getattr(target, aname)
                    except AttributeError:
                        lval = None
                        self.__logger.debug(f'Failed to bind {aname}', exc_info=True)
                if (not hasattr(prop, 'fset') or getattr(prop, 'fset') is None):
                    # NOTE: lval is not settable
                    if rval is None:
                        # no assigment attempt will be made
                        continue
                    elif lval is not None:
                        if rval is not None and lval == rval:
                            # same value, no need to assign
                            continue
                        elif not (issubclass(type(lval), list) and issubclass(type(rval), list)):
                            # non-list values cannot be merged
                            raise Exception(f'Cannot bind `None` to attribute `{aname}`')
                phints = typing.get_type_hints(getattr(prop, 'fget'))
                if phints is None or (not issubclass(type(phints), dict)):
                    # NOTE: can't get hints from getter, can't bind
                    continue
                ahint = phints.get('return')
                if ahint is None:
                    # NOTE: fget hint missing return spec, can't bind
                    continue
            if rval is None:
                setattr(target, aname, None)
            elif ahint is float:
                v = float(rval)
                setattr(target, aname, v)
            elif ahint is int:
                v = int(rval)
                setattr(target, aname, v)
            elif ahint is str:
                v = str(rval)
                setattr(target, aname, v)
            elif isinstance(rval, Configuration):
                if typing.get_origin(ahint) is dict:
                    lval = rval.toDictionary()
                    setattr(target, aname, lval)
                else:
                    if lval is None:
                        lval = ahint()
                        setattr(target, aname, lval)
                    self.__recursiveBind(lval, rval)
            elif typing.get_origin(ahint) is list:
                elementType = ahint.__args__[0]
                if lval is None:
                    lval = ahint()
                    setattr(target, aname, lval)
                for e in rval:
                    v = self.__recursiveBindType(elementType, e)
                    lval.append(v)
            else:
                setattr(target, aname, rval)
        return target

    def __recursiveBindType(self, elementType:type, source:any) -> any:
        if isinstance(source, elementType):
            return source
        elif elementType is float:
            return float(source)
        elif elementType is int:
            return int(source)
        elif elementType is str:
            return str(source)
        elif isinstance(source, Configuration | dict):
            v = elementType()
            return self.__recursiveBind(v, source)       
        else:
            raise ConfigurationException(f'Recursive bind to type `{elementType}` from `{type(source)}` is not supported.')

    def __scrub_key(self, key:str) -> str:
        """Scrubs a key for use as an attribute/identifier according to the Python lexer/standard."""
        key = key.replace(':', '__').replace('.', '_')
        return key if None == self.__key_scrub_re else \
            self.__key_scrub_re.sub(
                self.__scrub_uc,
                unicodedata.normalize(
                    'NFKC',
                    key))

    def __scrub_uc(self, m:re.Match) -> str:
        match unicodedata.category(m[0]):
            case 'Lu' | 'Ll' | 'Lt' | 'Lm' | 'Lo' | 'Nl' | 'Mn' | 'Mc' | 'Nd' | 'Pc' :
                return m[0]
            case _:
                return '_'

    def __setitem__(self, key:str, value:any) -> None:
        self.set(key, value)

    def __str__(self) -> str:
        return json.dumps(self.toDictionary())

    def bind(self, target:object, key:str|None = None) -> any:
        """
        Binds the configuration values into the target object.
        Can optionally specify a configuration key to bind from.

        :param target: The object to bind configuration data into.
        :param key: An optional confguration key to bind to, defaults to None which binds to the configuration root.
        :return: The original `target` object, modified in-place.
        """
        if target is None:
            raise ConfigurationException('Missing required argument: target')
        if key is None:
            return self.__recursiveBind(target, self)
        else:
            source = self.get(key)
            if source is not None:
                sourceType = type(source)
                if sourceType is Configuration or sourceType is dict:
                    return self.__recursiveBind(target, source)
                else:
                    raise ConfigurationException(f'Bind of source type `{type(source)}` is not supported.')
            return target

    def clear(self) -> None:
        while len(self.__keys) > 0:
            t = self.__keys.popitem()
            delattr(self, t[1])

    @staticmethod
    def fromDictionary(source:dict, *, normalize:bool = False, scrubkeys:bool = False) -> Configuration:
        """
        Constructs a :py:class:`~appsettings2.Configuration` instance from the supplied dictionary `source`.

        :param source: The dictionary object to populate from.
        :param normalize: Option indicating whether or not attribute names should be normalized to upper-case on the resulting :py:class:`~appsettings2.Configuration` object, defaults to False.
        :param scrubkeys: Option indicating whether or not attribute names should be scrubbed to be compatible with the Python lexer, defaults to False.
        :return: A :py:class:`~appsettings2.Configuration` object derived from the `source` parameter.
        """
        config:Configuration = Configuration(normalize=normalize, scrubkeys=scrubkeys)
        for kvp in source.items():
            v = kvp[1]
            if issubclass(type(v), dict):
                v = Configuration.fromDictionary(v, normalize=normalize, scrubkeys=scrubkeys)
            config.set(kvp[0], v)
        return config

    def get(self, key:str, default:any = None) -> any:
        """
        Gets the configuration data associated with the specified `key`.

        :param key: The configuration key to get data for. Supports `__` and `:` hierarchical delimiters.
        :param default: The value to be returned if `key` does not exist, defaults to None
        :return: The configuration data associated with `key`, otherwise `default`.
        """
        parts = key.replace(':', '__').split('__')
        o = self
        for part in parts:
            if o == self:
                k = self.__keys.get(part.upper())
                if k is None:
                    return default
                else:
                    o = getattr(o, self.__scrub_key(k))
            else:
                o = o.get(part, default)
        return o

    def has_key(self, key:str) -> bool:
        return self.__keys.get(key.upper()) is not None

    def items(self) -> list[tuple[str,any]]:
        it = []
        for k in self.keys():
            v = self.get(k)
            it.append((k, v))
        return it

    def keys(self) -> list[str]:
        return self.__keys.values()

    def pop(self, key:str) -> any:
        value = self[key]
        del self[key]
        return value

    def set(self, key:str, value:any) -> None:
        """
        Sets the configuration data for the specified `key`.

        :param key: The key to associate the configuration data.
        :param value: The configuration data so be associated with `key`.
        """
        if self.__normalize:
            key = key.upper()
        parts = key.replace(':', '__').split('__')
        o = self
        for i in range(len(parts) - 1):
            if o == self:
                k = self.__keys.get(parts[i].upper())
                if k is None:
                    c = Configuration(normalize=self.__normalize, scrubkeys=(None != self.__key_scrub_re))
                    setattr(o, self.__scrub_key(parts[i]), c)
                    self.__keys[parts[i].upper()] = parts[i]
                    o = c
                else:
                    o = getattr(self, self.__scrub_key(k))
            else:
                if not o.has_key(parts[i]):
                    c = Configuration(normalize=self.__normalize, scrubkeys=(None != self.__key_scrub_re))
                    o.set(parts[i], c)
                    o = c
                else:
                    o = o.get(parts[i])
        vtype = type(value)
        if issubclass(vtype, dict):
            value = Configuration.fromDictionary(value, normalize=self.__normalize, scrubkeys=self.__key_scrub_re is not None)
        elif issubclass(vtype, list):
            l = []
            for e in value:
                if issubclass(type(e), dict):
                    l.append(Configuration.fromDictionary(e, normalize=self.__normalize, scrubkeys=self.__key_scrub_re is not None))
                else:
                    l.append(e)
            value = l
        key = parts[-1]
        if o == self:
            k = self.__keys.get(key.upper())
            if k is not None:
                setattr(self, self.__scrub_key(k), value)
            else:
                self.__keys[key.upper()] = key
                setattr(self, self.__scrub_key(key), value)
        else:
            o.set(key, value)

    def toDictionary(self) -> dict:
        """
        Creates a dictionary from the `Configuration` object.

        :return: A dictionary containing all keys and their associated values, in a structure that mimics the structure if the data contained within the `Configuration` object.
        """
        result = {}
        for k in self.__keys.values():
            v = getattr(self, self.__scrub_key(k))
            if isinstance(v, Configuration):
                result[k] = v.toDictionary()
            elif issubclass(type(v), list):
                tmp = []
                for e in v:
                    if isinstance(e, Configuration):
                        tmp.append(e.toDictionary())
                    else:
                        tmp.append(e)
                result[k] = tmp
            else:
                result[k] = v
        return result

    def values(self) -> list[any]:
        values = []
        for k in self.__keys.values():
            v = getattr(self, self.__scrub_key(k))
            values.append(v)
        return values
