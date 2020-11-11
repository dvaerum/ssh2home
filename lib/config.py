#!/usr/bin/env python3
# ex: set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab:

from typing import Dict, List
import os
import sys
import yaml
import unittest
from io import BytesIO
import logging as logger



class ConfigTemplate:
    def __init__(self, config: Dict[str, object]):
        self._validate_attr(config)

    def _validate_attr(self, config: Dict[str, object]):
        for key, value in config.items():
            if len(key) > 4 and key[0:2] == '__' and key[-2:] == '__':
                logger.error(f'The attribute/variable "{key}" is not allowed, '
                              'because it both starts and ends with "__", Exiting...')
                sys.exit(1)

            _attr = getattr(self, key, None)
            if hasattr(self, key):
                if isinstance(_attr, ConfigTemplate):
                    setattr(self, key, type(_attr)(value))
                else:
                    if self._validate_data(key, value):
                        setattr(self, key, value)
                    else:
                        logger.error(f'The data in the attribute/variable "{key}" is invalid. Exiting...')
                        sys.exit(1)
            else:
                logger.error(f'The attribute/variable "{key}" is invalid. Exiting...')
                sys.exit(1)

    def _validate_data(self, key: str, data: object) -> bool:
        logger.error(f'The function for _validate_data has not been overwritten!!!')
        sys.exit(1)



class Shell(ConfigTemplate):
    dot_file_path = ".config/.dot-files-timestamp"
    shells = [ "bash" ]
    update_interval = 48  # Hours

    def _validate_data(self, key: str, data: object):
        return {
            'dot_file_path': lambda x: isinstance(x, str) and not x.startswith('/') and not x.startswith('~/'),
            'shells': lambda shells: isinstance(shells, list) and all([isinstance(shell, str) for shell in shells]),
            'update_interval': lambda x: isinstance(x, int),

        }[key](data)



class Config(ConfigTemplate):
    port: int = 7654
    ssh_bin: str = "ssh"
    packages: Dict[str, List[str]] = {}
    password = None
    files = []
    host_files = {}

    shell = Shell({})

    def __init__(self, path: str = None, data: BytesIO = None):
        conf = None
        if path:
            with open(path) as f:
                # The FullLoader parameter handles the conversion from YAML
                # scalar values to Python the dictionary format
                super().__init__(yaml.load(f, Loader=yaml.FullLoader))

        elif data:
            super().__init__(yaml.load(data, Loader=yaml.FullLoader))

    def _validate_data(self, key: str, data: object):
        files = lambda files: [os.path.exists(file) if isinstance(file, str) else
                               ('src' in file.keys() and 'dst' in file.keys() and len(file) == 2 and
                                isinstance(file['src'], str) and isinstance(file['dst'], str) and os.path.exists(file['src']))
                               for file in files]

        r = {
            'port': lambda x: x > 1023 and x < 65536,
            'ssh_bin': lambda x: any([os.path.isfile(f'{path}/{x}') and os.access(f'{path}/{x}', os.X_OK)
                                      for path in os.environ['PATH'].split(':') + [os.path.dirname(x)]]),
            'packages': lambda packages: all([isinstance(package, str) and
                                              value if value is True else all(isinstance(v, str) for v in value)
                                              for package, value in packages.items()]),
            'password': lambda x: True,
            'files': files,
            'host_files': lambda x: all([isinstance(host, str) and files(f) for host, f in x.items()],)

        }[key](data)
        return r


class TestConfig(unittest.TestCase):
    def test_init(self):
        Config('config.example.yml')



