import ConfigParser
import numpy as np
import logging


class Config(ConfigParser.ConfigParser):
    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)
        self._config = ConfigParser.RawConfigParser()
        self._dispatcher = {'common': self.__get_common,
                            'array': self.__get_array,
                            'arange': self.__get_arange}
        self._logger = logging.getLogger('default')
        self._log_prefix = '[CONFIG] '

    def __get_common(self, section, param):
        return self._config.get(section, param)

    def get_param(self, section, param, **kwargs):
        if kwargs is None:
            return self._dispatcher['common'](section, param)

        try:
            return self._dispatcher[kwargs.get('type')](section, param, **kwargs)
        except KeyError:
            logging.error(self._log_prefix, 'Type not supported')
            raise KeyError('Type not supported')

    def __get_arange(self, section, param, **kwargs):
        # TODO: Research how to use dtype to create ranges from different types
        arg_range = [int(x) for x in self.get(section, param).split(':')]

        if len(arg_range) == 2:
            return np.arange(arg_range[0], arg_range[1], dtype=int)
        elif len(arg_range) == 3:
            return np.arange(arg_range[0], arg_range[1],
                             arg_range[2], dtype=int)

    def __get_array(self, section, param, **kwargs):
        # TODO: Research how to use dtype to create ranges from different types
        return np.fromstring(self.get(section, param), dtype=int, sep=',')
