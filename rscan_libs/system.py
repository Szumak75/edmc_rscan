# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 18.12.2023

  Purpose:
"""


import ctypes

import logging
import os
import platform
import subprocess
import sys
import tempfile

from inspect import currentframe
from logging.handlers import RotatingFileHandler
from queue import Queue
from typing import Optional, Union, List, Callable
from jsktoolbox.libs.base_data import BData, BClasses
from jsktoolbox.raisetool import Raise
from jsktoolbox.attribtool import ReadOnlyClass


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys container class."""

    COPY = "_copy_"
    PASTE = "_paste_"

    WINDOWS = "Windows"
    DARWIN = "Darwin"
    LINUX = "Linux"
    NT = "nt"
    MAC = "mac"
    POSIX = "posix"
    BIT32 = "32-bit"
    BIT64 = "64-bit"
    X86_64 = "x86_64"

    DIR = "__dir__"

    HOME = "__home__"
    TMP = "__tmp__"

    NAME = "__name__"
    ENGINE = "__engine__"
    LOGLVL = "__lvl__"
    QUEUE = "__quq__"


class Clip(BData):
    """System clipboard tool."""

    def __init__(self):
        """Create instance of class."""
        setcb = getcb = None
        if os.name == _Keys.NT or platform.system() == _Keys.WINDOWS:
            getcb = self.__win_get_clipboard
            setcb = self.__win_set_clipboard
        elif os.name == _Keys.MAC or platform.system() == _Keys.DARWIN:
            getcb = self.__mac_get_clipboard
            setcb = self.__mac_set_clipboard
        elif os.name == _Keys.POSIX or platform.system() == _Keys.LINUX:
            xclipExists = os.system("which xclip > /dev/null") == 0
            if xclipExists:
                getcb = self.__xclip_get_clipboard
                setcb = self.__xclip_set_clipboard
            else:
                xselExists = os.system("which xsel > /dev/null") == 0
                if xselExists:
                    getcb = self.__xsel_get_clipboard
                    setcb = self.__xsel_set_clipboard
                try:
                    import gtk

                    getcb = self.__gtk_get_clipboard
                    setcb = self.__gtk_set_clipboard
                except Exception:
                    try:
                        import PyQt4.QtCore
                        import PyQt4.QtGui

                        app = PyQt4.QApplication([])
                        cb = PyQt4.QtGui.QApplication.clipboard()
                        getcb = self.__qt_get_clipboard
                        setcb = self.__qt_set_clipboard
                    except:
                        print(
                            Raise.message(
                                "Pyperclip requires the gtk or PyQt4 module installed, or the xclip command.",
                                self._c_name,
                                currentframe(),
                            )
                        )
        self._data[_Keys.COPY] = setcb
        self._data[_Keys.PASTE] = getcb

    @property
    def is_tool(self) -> bool:
        """Return True if the tool is avaiable."""
        return (
            self._data[_Keys.COPY] is not None and self._data[_Keys.PASTE] is not None
        )

    @property
    def copy(self) -> Callable:
        """Return copy handler."""
        return self._data[_Keys.COPY]

    @property
    def paste(self) -> Callable:
        """Return paste handler."""
        return self._data[_Keys.PASTE]

    def __win_get_clipboard(self) -> str:
        """Get windows clipboard data."""
        ctypes.windll.user32.OpenClipboard(0)
        pcontents = ctypes.windll.user32.GetClipboardData(1)  # 1 is CF_TEXT
        data = ctypes.c_char_p(pcontents).value
        # ctypes.windll.kernel32.GlobalUnlock(pcontents)
        ctypes.windll.user32.CloseClipboard()
        return data

    def __win_set_clipboard(self, text: str) -> None:
        """Set windows clipboard data."""
        text = str(text)
        GMEM_DDESHARE = 0x2000
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        try:
            # works on Python 2 (bytes() only takes one argument)
            hCd = ctypes.windll.kernel32.GlobalAlloc(
                GMEM_DDESHARE, len(bytes(text)) + 1
            )
        except TypeError:
            # works on Python 3 (bytes() requires an encoding)
            hCd = ctypes.windll.kernel32.GlobalAlloc(
                GMEM_DDESHARE, len(bytes(text, "ascii")) + 1
            )
        pchData = ctypes.windll.kernel32.GlobalLock(hCd)
        try:
            # works on Python 2 (bytes() only takes one argument)
            ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text))
        except TypeError:
            # works on Python 3 (bytes() requires an encoding)
            ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text, "ascii"))
        ctypes.windll.kernel32.GlobalUnlock(hCd)
        ctypes.windll.user32.SetClipboardData(1, hCd)
        ctypes.windll.user32.CloseClipboard()

    def __mac_set_clipboard(self, text: str) -> None:
        """Set MacOS clipboard data."""
        text = str(text)
        outf = os.popen("pbcopy", "w")
        outf.write(text)
        outf.close()

    def __mac_get_clipboard(self) -> str:
        """Get MacOS clipboard data."""
        outf = os.popen("pbpaste", "r")
        content = outf.read()
        outf.close()
        return content

    def __gtk_get_clipboard(self) -> str:
        """Get GTK clipboard data."""
        return gtk.Clipboard().wait_for_text()

    def __gtk_set_clipboard(self, text: str) -> None:
        """Set GTK clipboard data."""
        global cb
        text = str(text)
        cb = gtk.Clipboard()
        cb.set_text(text)
        cb.store()

    def __qt_get_clipboard(self) -> str:
        """Get QT clipboard data."""
        return str(cb.text())

    def __qt_set_clipboard(self, text: str) -> None:
        """Set QT clipboard data."""
        text = str(text)
        cb.setText(text)

    def __xclip_set_clipboard(self, text: str) -> None:
        """Set xclip clipboard data."""
        text = str(text)
        outf = os.popen("xclip -selection c", "w")
        outf.write(text)
        outf.close()

    def __xclip_get_clipboard(self) -> str:
        """Get xclip clipboard data."""
        outf = os.popen("xclip -selection c -o", "r")
        content = outf.read()
        outf.close()
        return content

    def __xsel_set_clipboard(self, text: str) -> None:
        """Set xsel clipboard data."""
        text = str(text)
        outf = os.popen("xsel -i", "w")
        outf.write(text)
        outf.close()

    def __xsel_get_clipboard(self) -> str:
        """Get xsel clipboard data."""
        outf = os.popen("xsel -o", "r")
        content = outf.read()
        outf.close()
        return content


class Directory(BData):
    """Container class to store the directory path."""

    def is_directory(self, path_string: str) -> bool:
        """Check if the given string is a directory.

        path_string: str        path string to check
        return:      bool       True, if exists and is directory,
                                False in the other case.
        """
        return os.path.exists(path_string) and os.path.isdir(path_string)

    @property
    def dir(self) -> Optional[str]:
        """Property that returns directory string."""
        if _Keys.DIR not in self._data:
            self._data[_Keys.DIR] = None
        return self._data[_Keys.DIR]

    @dir.setter
    def dir(self, arg: str) -> None:
        """Setter for directory string.

        given path must exists.
        """
        if self.is_directory(arg):
            self._data[_Keys.DIR] = arg


class Env(BData):
    """Environmental class."""

    def __init__(self) -> None:
        """Initialize Env class."""
        home = os.getenv("HOME")
        if home is None:
            home = os.getenv("HOMEPATH")
            if home is not None:
                home = f"{os.getenv('HOMEDRIVE')}{home}"
        self._data[_Keys.HOME] = home

        tmp = os.getenv("TMP")
        if tmp is None:
            tmp = os.getenv("TEMP")
            if tmp is None:
                tmp = tempfile.gettempdir()
        self._data[_Keys.TMP] = tmp

    def check_dir(self, directory: str) -> str:
        """Check if dir exists, return dir or else HOME."""
        if not Directory().is_directory(directory):
            return self.home
        return directory

    def os_arch(self) -> str:
        """Return multiplatform os architecture."""
        os_arch = _Keys.BIT32
        if os.name == _Keys.NT:
            output = subprocess.check_output(["wmic", "os", "get", "OSArchitecture"])
            os_arch = output.split()[1]
        else:
            output = subprocess.check_output(["uname", "-m"])
            if _Keys.X86_64 in output:
                os_arch = _Keys.BIT64
            else:
                os_arch = _Keys.BIT32
        return os_arch

    @property
    def is_64bits(self) -> bool:
        """Check 64bits platform."""
        return sys.maxsize > 2**32

    @property
    def home(self) -> str:
        """Property that returns home directory string."""
        return self._data[_Keys.HOME]

    @property
    def tmpdir(self) -> str:
        """Property that returns tmp directory string."""
        return self._data[_Keys.TMP]

    @property
    def plugin_dir(self) -> str:
        """Return plugin dir path."""
        return f"{os.path.dirname(os.path.dirname(__file__))}"


class Log(BClasses):
    """Create Log container class."""

    __data = None
    __level = None

    def __init__(self, level: int) -> None:
        """Constructor."""
        self.__data = []
        ll_test = LogLevels()
        if isinstance(level, int) and ll_test.has_key(level):
            self.__level = level
        else:
            raise Raise.error(
                f"Expected Int type, received: '{type(level)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def loglevel(self) -> int:
        """Return loglevel."""
        return self.__level

    @property
    def log(self) -> Optional[List[str]]:
        """Get list of logs."""
        return self.__data

    @log.setter
    def log(self, arg: Optional[Union[List, str, int, float]]):
        """Set data log."""
        if arg is None or (isinstance(arg, list) and not bool(arg)):
            self.__data = None
            self.__data = []
        if isinstance(arg, list):
            for msg in arg:
                self.__data.append(f"{msg}")
        elif arg is None:
            pass
        else:
            self.__data.append(f"{arg}")


class LogProcessor(BData):
    """Log processor access API."""

    def __init__(self, name: str) -> None:
        """Create instance class object for processing single message."""
        # name of app
        self._data[_Keys.NAME] = name
        self.loglevel = LogLevels().notset
        self.__logger_init()

    def __del__(self) -> None:
        """Destroy log instance."""
        self.close()

    def __logger_init(self) -> None:
        """Initialize logger engine."""
        self.close()

        self._data[_Keys.ENGINE] = logging.getLogger(self._data[_Keys.NAME])
        self._data[_Keys.ENGINE].setLevel(LogLevels().debug)

        hlog = RotatingFileHandler(
            filename=os.path.join(Env().tmpdir, f"{self._data[_Keys.NAME]}.log"),
            maxBytes=100000,
            backupCount=5,
        )

        hlog.setLevel(self.loglevel)
        hlog.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        self._data[_Keys.ENGINE].addHandler(hlog)
        self._data[_Keys.ENGINE].info("Logger initialization complete")

    def close(self) -> None:
        """Close log subsystem."""
        if _Keys.ENGINE in self._data and self._data[_Keys.ENGINE] is not None:
            for handler in self._data[_Keys.ENGINE].handlers:
                handler.close()
                self._data[_Keys.ENGINE].removeHandler(handler)
            self._data[_Keys.ENGINE] = None

    def send(self, message: Log) -> None:
        """Send single message to log engine."""
        if _Keys.ENGINE not in self._data:
            # skip
            return
        lgl = LogLevels()
        if isinstance(message, Log):
            if message.loglevel == lgl.critical:
                for msg in message.log:
                    self._data[_Keys.ENGINE].critical("%s", msg)
            elif message.loglevel == lgl.debug:
                for msg in message.log:
                    self._data[_Keys.ENGINE].debug("%s", msg)
            elif message.loglevel == lgl.error:
                for msg in message.log:
                    self._data[_Keys.ENGINE].error("%s", msg)
            elif message.loglevel == lgl.info:
                for msg in message.log:
                    self._data[_Keys.ENGINE].info("%s", msg)
            elif message.loglevel == lgl.warning:
                for msg in message.log:
                    self._data[_Keys.ENGINE].warning("%s", msg)
            else:
                for msg in message.log:
                    self._data[_Keys.ENGINE].notset("%s", msg)
        else:
            raise Raise.error(
                f"Expected Log type, received: {type(message)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def loglevel(self) -> int:
        """Property that returns loglevel."""
        if _Keys.LOGLVL not in self._data:
            self._data[_Keys.LOGLVL] = 0
        return self._data[_Keys.LOGLVL]

    @loglevel.setter
    def loglevel(self, arg: int) -> None:
        """Setter for log level parameter."""
        if self._data[_Keys.LOGLVL] == arg:
            log = Log(LogLevels().debug)
            log.log = "LogLevel has not changed"
            self.send(log)
            return
        ll_test = LogLevels()
        if isinstance(arg, int) and ll_test.has_key(arg):
            self._data[_Keys.LOGLVL] = arg
        else:
            tmp = "Unable to set LogLevel to {}, defaulted to INFO"
            log = Log(LogLevels().warning)
            log.log = tmp.format(arg)
            self.send(log)
            self._data[_Keys.LOGLVL] = LogLevels().info
        self.__logger_init()


class LogClient(BData):
    """Log client class API."""

    def __init__(self, queue: Queue) -> None:
        """Create instance class object."""
        if isinstance(queue, Queue):
            self._data[_Keys.QUEUE] = queue
        else:
            raise Raise.error(
                f"Expected Queue type, received: '{type(queue)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def queue(self) -> Queue:
        """Give me queue object."""
        return self._data[_Keys.QUEUE]

    @property
    def critical(self) -> str:
        """Property that returns nothing."""
        return ""

    @critical.setter
    def critical(self, message: Union[str, List]) -> None:
        """Setter for critical messages.

        message: [str|list]
        """
        log = Log(LogLevels().critical)
        log.log = message
        self._data[_Keys.QUEUE].put(log)

    @property
    def debug(self) -> str:
        """Property that returns nothing."""
        return ""

    @debug.setter
    def debug(self, message: Union[str, List]) -> None:
        """Setter for debug messages.

        message: [str|list]
        """
        log = Log(LogLevels().debug)
        log.log = message
        self._data[_Keys.QUEUE].put(log)

    @property
    def error(self) -> str:
        """Property that returns nothing."""
        return ""

    @error.setter
    def error(self, message: Union[str, List]) -> None:
        """Setter for error messages.

        message: [str|list]
        """
        log = Log(LogLevels().error)
        log.log = message
        self._data[_Keys.QUEUE].put(log)

    @property
    def info(self) -> str:
        """Property that returns nothing."""
        return ""

    @info.setter
    def info(self, message: Union[str, List]) -> None:
        """Setter for info messages.

        message: [str|list]
        """
        log = Log(LogLevels().info)
        log.log = message
        self._data[_Keys.QUEUE].put(log)

    @property
    def warning(self) -> str:
        """Property that returns nothing."""
        return ""

    @warning.setter
    def warning(self, message: Union[str, List]) -> None:
        """Setter for warning messages.

        message: [str|list]
        """
        log = Log(LogLevels().warning)
        log.log = message
        self._data[_Keys.QUEUE].put(log)

    @property
    def notset(self) -> str:
        """Property that returns nothing."""
        return ""

    @notset.setter
    def notset(self, message: Union[str, List]) -> None:
        """Setter for notset level messages.

        message: [str|list]
        """
        log = Log(LogLevels().notset)
        log.log = message
        self._data[_Keys.QUEUE].put(log)


class LogLevels(BData):
    """Log levels keys.

    This is a container class with properties that return the proper
    logging levels defined in the logging module.
    """

    __keys = None
    __txt = None

    def __init__(self) -> None:
        """Create Log instance."""
        # loglevel initialization database
        self.__keys = {
            self.info: True,
            self.debug: True,
            self.warning: True,
            self.error: True,
            self.notset: True,
            self.critical: True,
        }
        self.__txt = {
            "INFO": self.info,
            "DEBUG": self.debug,
            "WARNING": self.warning,
            "ERROR": self.error,
            "CRITICAL": self.critical,
            "NOTSET": self.notset,
        }

    def get(self, level: str) -> Optional[int]:
        """Get int log level."""
        if level in self.__txt:
            return self.__txt[level]
        return None

    def has_key(self, level: int) -> bool:
        """Check, if level is in proper keys."""
        if level in self.__keys or level in self.__txt:
            return True
        return False

    @property
    def info(self) -> int:
        """Return info level."""
        return logging.INFO

    @property
    def debug(self) -> int:
        """Return debug level."""
        return logging.DEBUG

    @property
    def warning(self) -> int:
        """Return warning level."""
        return logging.WARNING

    @property
    def error(self) -> int:
        """Return error level."""
        return logging.ERROR

    @property
    def critical(self) -> int:
        """Return critical level."""
        return logging.CRITICAL

    @property
    def notset(self) -> int:
        """Return notset level."""
        return logging.NOTSET


# #[EOF]#######################################################################
