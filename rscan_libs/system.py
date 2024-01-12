# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 18.12.2023

  Purpose:
"""

import ctypes
import inspect
import logging
import os
import platform
import subprocess
import sys
import tempfile
from typing import Union, Optional, List, Dict
from distutils.spawn import find_executable
from logging.handlers import RotatingFileHandler
from queue import Queue, SimpleQueue
from attribtool.ndattrib import NoDynamicAttributes
from raisetool.formatter import Raise


class Clip(NoDynamicAttributes):
    """System clipboard tool."""

    __copy = None
    __paste = None

    def __init__(self):
        """Create instance of class."""
        setcb = getcb = None
        if os.name == "nt" or platform.system() == "Windows":
            import ctypes

            getcb = self.__win_get_clipboard
            setcb = self.__win_set_clipboard
        elif os.name == "mac" or platform.system() == "Darwin":
            getcb = self.__mac_get_clipboard
            setcb = self.__mac_set_clipboard
        elif os.name == "posix" or platform.system() == "Linux":
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
                                self.__class__.__name__,
                                inspect.currentframe(),
                                "Pyperclip requires the gtk or PyQt4 module installed, or the xclip command.",
                            )
                        )
        self.__copy = setcb
        self.__paste = getcb

    @property
    def is_tool(self):
        """Return True if the tool is avaiable."""
        return self.__copy is not None and self.__paste is not None

    @property
    def copy(self):
        """Return copy handler."""
        return self.__copy

    @property
    def paste(self):
        """Return paste handler."""
        return self.__paste

    def __win_get_clipboard(self):
        """Get windows clipboard data."""
        ctypes.windll.user32.OpenClipboard(0)
        pcontents = ctypes.windll.user32.GetClipboardData(1)  # 1 is CF_TEXT
        data = ctypes.c_char_p(pcontents).value
        # ctypes.windll.kernel32.GlobalUnlock(pcontents)
        ctypes.windll.user32.CloseClipboard()
        return data

    def __win_set_clipboard(self, text):
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

    def __mac_set_clipboard(self, text):
        """Set MacOS clipboard data."""
        text = str(text)
        outf = os.popen("pbcopy", "w")
        outf.write(text)
        outf.close()

    def __mac_get_clipboard(self):
        """Get MacOS clipboard data."""
        outf = os.popen("pbpaste", "r")
        content = outf.read()
        outf.close()
        return content

    def __gtk_get_clipboard(self):
        """Get GTK clipboard data."""
        return gtk.Clipboard().wait_for_text()

    def __gtk_set_clipboard(self, text):
        """Set GTK clipboard data."""
        global cb
        text = str(text)
        cb = gtk.Clipboard()
        cb.set_text(text)
        cb.store()

    def __qt_get_clipboard(self):
        """Get QT clipboard data."""
        return str(cb.text())

    def __qt_set_clipboard(self, text):
        """Set QT clipboard data."""
        text = str(text)
        cb.setText(text)

    def __xclip_set_clipboard(self, text):
        """Set xclip clipboard data."""
        text = str(text)
        outf = os.popen("xclip -selection c", "w")
        outf.write(text)
        outf.close()

    def __xclip_get_clipboard(self):
        """Get xclip clipboard data."""
        outf = os.popen("xclip -selection c -o", "r")
        content = outf.read()
        outf.close()
        return content

    def __xsel_set_clipboard(self, text):
        """Set xsel clipboard data."""
        text = str(text)
        outf = os.popen("xsel -i", "w")
        outf.write(text)
        outf.close()

    def __xsel_get_clipboard(self):
        """Get xsel clipboard data."""
        outf = os.popen("xsel -o", "r")
        content = outf.read()
        outf.close()
        return content


class Directory(NoDynamicAttributes):
    """Container class to store the directory path."""

    __dir = None

    def is_directory(self, path_string: str) -> bool:
        """Check if the given string is a directory.

        path_string: str        path string to check
        return:      bool       True, if exists and is directory,
                                False in the other case.
        """
        return os.path.exists(path_string) and os.path.isdir(path_string)

    @property
    def dir(self) -> str:
        """Property that returns directory string."""
        return self.__dir

    @dir.setter
    def dir(self, arg: str):
        """Setter for directory string.

        given path must exists.
        """
        if self.is_directory(arg):
            self.__dir = arg


class Env(NoDynamicAttributes):
    """Environmental class."""

    __tmp = None
    __home = None

    def __init__(self):
        """Initialize Env class."""
        home = os.getenv("HOME")
        if home is None:
            home = os.getenv("HOMEPATH")
            if home is not None:
                home = f"{os.getenv('HOMEDRIVE')}{home}"
        self.__home = home

        tmp = os.getenv("TMP")
        if tmp is None:
            tmp = os.getenv("TEMP")
            if tmp is None:
                tmp = tempfile.gettempdir()
        self.__tmp = tmp

    def check_dir(self, directory: str) -> str:
        """Check if dir exists, return dir or else HOME."""
        if not Directory().is_directory(directory):
            return self.home
        return directory

    def os_arch(self) -> str:
        """Return multiplatform os architecture."""
        os_arch = "32-bit"
        if os.name == "nt":
            output = subprocess.check_output(["wmic", "os", "get", "OSArchitecture"])
            os_arch = output.split()[1]
        else:
            output = subprocess.check_output(["uname", "-m"])
            if "x86_64" in output:
                os_arch = "64-bit"
            else:
                os_arch = "32-bit"
        return os_arch

    @property
    def is_64bits(self) -> bool:
        """Check 64bits platform."""
        return sys.maxsize > 2**32

    @property
    def home(self) -> str:
        """Property that returns home directory string."""
        return self.__home

    @property
    def tmpdir(self) -> str:
        """Property that returns tmp directory string."""
        return self.__tmp


class Log(NoDynamicAttributes):
    """Create Log container class."""

    __data = None
    __level = None

    def __init__(self, level):
        """Class constructor."""
        self.__data = []
        ll_test = LogLevels()
        if isinstance(level, int) and ll_test.has_key(level):
            self.__level = level
        else:
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"Int type level expected, '{type(level)}' received.",
            )

    @property
    def loglevel(self) -> int:
        """Return loglevel."""
        return self.__level

    @property
    def log(self) -> List:
        """Get list of logs."""
        return self.__data

    @log.setter
    def log(self, arg):
        """Set data log."""
        if arg is None or (isinstance(arg, List) and not bool(arg)):
            self.__data = None
            self.__data = []
        if isinstance(arg, List):
            for msg in arg:
                self.__data.append(f"{msg}")
        elif arg is None:
            pass
        else:
            self.__data.append(f"{arg}")


class LogProcessor(NoDynamicAttributes):
    """Log processor access API."""

    __name = None
    __engine = None
    __loglevel = None

    def __init__(self, name: str):
        """Create instance class object for processing single message."""
        # name of app
        self.__name = name
        self.loglevel = LogLevels().notset
        self.__logger_init()

    def __del__(self):
        """Destroy log instance."""
        self.close()

    def __logger_init(self):
        """Initialize logger engine."""
        self.close()

        self.__engine = logging.getLogger(self.__name)
        self.__engine.setLevel(LogLevels().debug)

        hlog = RotatingFileHandler(
            filename=os.path.join(Env().tmpdir, f"{self.__name}.log"),
            maxBytes=100000,
            backupCount=5,
        )

        hlog.setLevel(self.loglevel)
        hlog.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        self.__engine.addHandler(hlog)
        self.__engine.info("Logger initialization complete")

    def close(self):
        """Close log subsystem."""
        if self.__engine is not None:
            for handler in self.__engine.handlers:
                handler.close()
                self.__engine.removeHandler(handler)
            self.__engine = None

    def send(self, message: Log):
        """Send single message to log engine."""
        lgl = LogLevels()
        if isinstance(message, Log):
            if message.loglevel == lgl.critical:
                for msg in message.log:
                    self.__engine.critical("%s", msg)
            elif message.loglevel == lgl.debug:
                for msg in message.log:
                    self.__engine.debug("%s", msg)
            elif message.loglevel == lgl.error:
                for msg in message.log:
                    self.__engine.error("%s", msg)
            elif message.loglevel == lgl.info:
                for msg in message.log:
                    self.__engine.info("%s", msg)
            elif message.loglevel == lgl.warning:
                for msg in message.log:
                    self.__engine.warning("%s", msg)
            else:
                for msg in message.log:
                    self.__engine.notset("%s", msg)
        else:
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"Log type expected, {type(message)} received.",
            )

    @property
    def loglevel(self) -> int:
        """Property that returns loglevel."""
        return self.__loglevel

    @loglevel.setter
    def loglevel(self, arg: int):
        """Setter for log level parameter."""
        if self.__loglevel == arg:
            log = Log(LogLevels().debug)
            log.log = "LogLevel has not changed"
            self.send(log)
            return
        ll_test = LogLevels()
        if isinstance(arg, int) and ll_test.has_key(arg):
            self.__loglevel = arg
        else:
            tmp = "Unable to set LogLevel to {}, defaulted to INFO"
            log = Log(LogLevels().warning)
            log.log = tmp.format(arg)
            self.send(log)
            self.__loglevel = LogLevels().info
        self.__logger_init()


class LogClient(NoDynamicAttributes):
    """Log client class API."""

    __queue = None

    def __init__(self, queue: Union[Queue, SimpleQueue]):
        """Create instance class object."""
        if isinstance(queue, (Queue, SimpleQueue)):
            self.__queue = queue
        else:
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe,
                f"Queue or SimpleQueue type expected, '{type(queue)}' received.",
            )

    @property
    def queue(self) -> Union[Queue, SimpleQueue]:
        """Give me queue object."""
        return self.__queue

    @property
    def critical(self) -> str:
        """Property that returns nothing."""
        return ""

    @critical.setter
    def critical(self, message: Union[str, List]):
        """Setter for critical messages.

        message: [str|list]
        """
        log = Log(LogLevels().critical)
        log.log = message
        self.__queue.put(log)

    @property
    def debug(self) -> str:
        """Property that returns nothing."""
        return ""

    @debug.setter
    def debug(self, message: Union[str, List]):
        """Setter for debug messages.

        message: [str|list]
        """
        log = Log(LogLevels().debug)
        log.log = message
        self.__queue.put(log)

    @property
    def error(self) -> str:
        """Property that returns nothing."""
        return ""

    @error.setter
    def error(self, message: Union[str, List]):
        """Setter for error messages.

        message: [str|list]
        """
        log = Log(LogLevels().error)
        log.log = message
        self.__queue.put(log)

    @property
    def info(self) -> str:
        """Property that returns nothing."""
        return ""

    @info.setter
    def info(self, message: Union[str, List]):
        """Setter for info messages.

        message: [str|list]
        """
        log = Log(LogLevels().info)
        log.log = message
        self.__queue.put(log)

    @property
    def warning(self) -> str:
        """Property that returns nothing."""
        return ""

    @warning.setter
    def warning(self, message: Union[str, List]):
        """Setter for warning messages.

        message: [str|list]
        """
        log = Log(LogLevels().warning)
        log.log = message
        self.__queue.put(log)

    @property
    def notset(self) -> str:
        """Property that returns nothing."""
        return ""

    @notset.setter
    def notset(self, message: Union[str, List]):
        """Setter for notset level messages.

        message: [str|list]
        """
        log = Log(LogLevels().notset)
        log.log = message
        self.__queue.put(log)


class LogLevels(NoDynamicAttributes):
    """Log levels keys.

    This is a container class with properties that return the proper
    logging levels defined in the logging module.
    """

    __keys = None
    __txt = None

    def __init__(self):
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

    def get(self, level: Union[int, str]) -> Optional[int]:
        """Get int log level."""
        if level in self.__txt:
            return self.__txt[level]
        return None

    def has_key(self, level: Union[int, str]) -> bool:
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
