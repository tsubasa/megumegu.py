# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import argparse
import re
import importlib
import json
from collections import MutableMapping

import six

# args
parser = argparse.ArgumentParser(description='ウェブサイト更新情報取得スクリプト')
parser.add_argument('-C', '--config', required=True, help='任意の設定ファイルを指定')
parser.add_argument('-L', '--log-level', type=str, default='WARNING', help='ロギングレベルを指定')
args = parser.parse_args()

# define
if args.log_level.upper() in {'CRITICAL', 'FATAL', '50'}:
    LOG_LEVEL = 50
elif args.log_level.upper() in {'ERROR', '40'}:
    LOG_LEVEL = 40
elif args.log_level.upper() in {'WARNING', 'WARN', '30'}:
    LOG_LEVEL = 30
elif args.log_level.upper() in {'INFO', '20'}:
    LOG_LEVEL = 20
elif args.log_level.upper() in {'DEBUG', '10'}:
    LOG_LEVEL = 10
elif args.log_level.upper() in {'NOTSET', '0'}:
    LOG_LEVEL = 0
else:
    LOG_LEVEL = 30

# class
class BaseSettings(MutableMapping):

    def __init__(self):
        self.attributes = {}

    def __setitem__(self, name, value):
        self.attributes[name] = value

    def __getitem__(self, name):
        if name not in self.attributes:
            return None
        return self.attributes[name]

    def __delitem__(self, name):
        if name in self.attributes:
            del self.attributes[name]

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def __contains__(self, name):
        return name in self.attributes

    def get(self, name, default=None):
        return self.attributes[name] if self.attributes[name] is not None else default

    def set(self, name, value):
        self.attributes[name] = value

    def getbool(self, name, default=False):
        if name not in self.attributes:
            return default
        try:
            return bool(int(self.attributes[name]))
        except ValueError:
            if self.attributes[name] in ('True', 'true'):
                return True
            if self.attributes[name] in ('False', 'false'):
                return False

    def getint(self, name, default=0):
        return int(self.get(name, default))

    def getlist(self, name, default=None):
        value = self.get(name, default or [])
        if isinstance(value, six.string_types):
            value = value.split(',')
        return list(value)

    def getdict(self, name, default=None):
        value = self.get(name, default or {})
        if isinstance(value, six.string_types):
            value = json.loads(value)
        return dict(value)

    def setdict(self, values):
        self.update(values)

    def update(self, values):
        if isinstance(values, six.string_types):
            values = json.loads(values)
        if values is not None:
            for name, value in values.items():
                self.set(name, value)

class Settings(BaseSettings):

    def __init__(self, default={}):
        BaseSettings.__init__(self)
        self.update(default)

    def read(self, filenames, encoding=None):
        if isinstance(filenames, str):
            filenames = [filenames]
        read_ok = []
        for filename in filenames:
            try:
                with open(filename, encoding=encoding) as fp:
                    self._read(fp, filename)
            except IOError:
                continue
            read_ok.append(filename)
        return read_ok

    def _read(self, fp, fpname):

        lineno = 0

        for lineno, line in enumerate(fp, start=1):
            try:
                if not line.strip():
                    continue

                line = line[:line.find('#')].strip()

                if line.find('=') != -1:
                    for k, v in [line.split('=')]:
                        if k and v:
                            self.set(k.strip(), v.strip())
            except Exception:
                raise ValueError

if not (os.path.isfile(args.config)):
    raise FileNotFoundError(args.config)

settings = Settings()
settings.read(args.config)
settings.set('LOG_LEVEL', LOG_LEVEL)

# plugins
def load_plugins():
    pysearchre = re.compile(r'^(?!__).+.py$', re.IGNORECASE)
    pluginfiles = filter(pysearchre.search, os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')))
    plugins = map(lambda fp: '.' + os.path.splitext(fp)[0], pluginfiles)
    importlib.import_module('megumegu.plugins')
    modules = []
    for plugin in plugins:
        modules.append(importlib.import_module(plugin, package='megumegu.plugins'))
    return modules

plugins = load_plugins()
