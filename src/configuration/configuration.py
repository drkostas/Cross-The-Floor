import _io
from io import StringIO
from io import TextIOWrapper
from typing import Dict

import yaml


class Configuration:
    """
    Configuration class that stores all the basic settings.
    """

    def __init__(self, config_file):
        if isinstance(config_file, TextIOWrapper):
            config = yaml.load(config_file, Loader=yaml.BaseLoader)
            self.input_path = config_file.name
        elif isinstance(config_file, StringIO):
            config = yaml.load(config_file)
            self.input_path = "StringIO"
        elif isinstance(config_file, str):
            with open(config_file) as f:
                config = yaml.load(f)
            self.input_path = config_file
        else:
            raise TypeError('Config file must be TextIOWrapper or path to a file')
        self.config = config

        self.source = config['source']

        self.target = config['target']

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def get_source(self) -> Dict:
        return self.source['config']

    def get_target(self) -> Dict:
        return self.target['config']

    def get_source_type(self) -> Dict:
        return self.source['type']

    def get_target_type(self) -> Dict:
        return self.target['type']

    def to_yml(self, fn) -> None:
        """
        Writes the configuration to a stream. For example a file.
        :param fn:
        :param include_tag:
        :return: None
        """
        dict_conf = {
            'source': self.source,
            'target': self.target
        }

        if isinstance(fn, str):
            with open(fn, 'w') as f:
                yaml.dump(dict_conf, f, default_flow_style=False)
        elif isinstance(fn, _io.TextIOWrapper):
            yaml.dump(dict_conf, fn, default_flow_style=False)
        else:
            raise TypeError('Expected str or _io.TextIOWrapper not %s' % (type(fn)))

    to_yaml = to_yml

    def to_json(self) -> Dict:
        return {
            'source': self.source,
            'target': self.target
        }


class ConfigurationError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
