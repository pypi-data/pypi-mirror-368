"""
Provides utilities for BigDFT logging events
"""

import logging
import os
import pprint
import warnings


def format_iterable(iterable,
                    exclude=None) -> str:
    return '|\n' + '\n'.join(['  ' + l for
                              l in pprint.pformat(iterable).split('\n')])


class LogHandler:
    """
    Log handler for PyBigDFT events

    Arguments:
        file (str):
            Filename or absolute filepath
        level (str):
            String format of logging level: `debug`, `info`, ...
        overwrite (bool):
            Overwrites the log file at instantiation. Appends, otherwise

    This class allows updating of the logging features, and explicit log
    messages for debugging.

    Before any BigDFT modules are imported, you have the opportunity to hook
    into the logger and change options:

    >>> import BigDFT
    >>> BigDFT.Logger.level = 'debug'  # set the log level to DEBUG
    >>> BigDFT.Logger.overwrite = True  # force a new file each time
    >>> BigDFT.Logger.path = './logs'  # place the log in a dir named 'log'
    """

    _levels = {'CRITICAL': logging.CRITICAL,
               'ERROR': logging.ERROR,
               'WARNING': logging.WARNING,
               'INFO': logging.INFO,
               'DEBUG': logging.DEBUG}

    def __init__(self,
                 file: str = None,
                 level: str = None,
                 overwrite: bool = None):

        self._logger = logging.getLogger('BigDFT')
        self._external = logging.getLogger('BigDFT.EXTERNAL')
        self._external.setLevel(10)  # always log external calls

        self._path = None
        self._mode = 'a'
        self.path = self._setval(file, 'file path',
                                 os.path.join(os.getcwd(),
                                              'BigDFT_log.yaml'), 'logpath')
        self.level = self._setval(level, 'logging level',
                                  'WARNING', 'loglvl')
        self.overwrite = self._setval(overwrite, 'overwrite',
                                      False, 'overwrite')

        self._logger.info('#' * 12 + ' creating new logger ' + '#' * 12)

    def _setval(self,
                value,
                name,
                default=None,
                environment_suffix=None):
        """
        Set value to inp, in a prioritised order
        """
        envkey = f'BigDFT_{environment_suffix}'
        if value is not None:
            print(f'manually set {name} to {value}')
            return value
        elif environment_suffix is not None and envkey in os.environ.keys():
            value = os.environ[envkey]
            print(f'{name} set to {value} from environment variables')
            return value
        else:
            # print(f'{name} set to default value of {default}')
            return default

    @property
    def level(self):
        """
        Return the string format of the current logging level
        """
        return self._level

    @level.setter
    def level(self, level):
        level = level.upper()
        if level not in LogHandler._levels.keys():
            raise ValueError('log level must be one of '
                             f'{list(LogHandler._levels.keys())}')
        self._logger.setLevel(LogHandler._levels[level])
        self._level = level

    @property
    def path(self):
        """
        Attribute determining the current log path
        """
        return self._path

    @path.setter
    def path(self, file):
        newpath = os.path.abspath(file)
        if '.yaml' not in newpath:
            newpath = os.path.join(newpath, 'BigDFT_log.yaml')
        for item in os.path.split(newpath)[:-1]:
            path_to_dir = os.path.isdir(os.path.abspath(item))
            if not path_to_dir:
                os.mkdir(os.path.abspath(item))

        self._path = newpath

        self._update_handlers()

    @property
    def overwrite(self):
        """
        Attribute determining the write mode of the logfiles

        Set True before any logging is done to utilise a new file
        """
        return self._mode == 'w'

    @overwrite.setter
    def overwrite(self, mode):
        if mode not in [True, False]:
            raise ValueError(f'non boolean value: {type(mode)}')
        if mode:
            self._mode = 'w'
        else:
            self._mode = 'a'

        self._update_handlers()

    def _update_handlers(self):
        """
        refresh handlers attached to the logger
        """
        for handler in self._logger.handlers:
            self._logger.removeHandler(handler)
        try:
            file_handler = logging.FileHandler(self._path, mode=self._mode)
        except PermissionError:
            warnings.warn('BigDFT does not have the required permissions '
                          f'to create a logfile at {self._path}')
            file_handler = logging.NullHandler()
        formatter = logging.Formatter('%(asctime)s - '
                                      '%(levelname)s - '
                                      '%(name)s.%(funcName)s: '
                                      '%(message)s',
                                      datefmt='%Y-%m-%d %H-%M-%S')

        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def debug(self, *args, **kwargs):
        """Direct passthrough for `debug` logging method"""
        self._external.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        """Direct passthrough for `info` logging method"""
        self._external.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """Direct passthrough for `warning` logging method"""
        self._external.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        """Direct passthrough for `error` logging method"""
        self._external.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        """Direct passthrough for `critical` logging method"""
        self._external.critical(*args, **kwargs)
