"""
Huti Functions Module
"""

__all__ = (
    "exec_module_from_file",
    "find_file",
    "parent",
    "stdout",
    "superproject",
    "supertop",

    "aioclosed",
    "aiocommand",
    "aiodmg",
    "aiogz",
    "aioloop",
    "aioloopid",
    "aiorunning",
    "allin",
    "ami",
    "anyin",
    "cache",
    "chdir",
    "cmdrun",
    "cmdsudo",
    "command",
    "current_task_name",
    "dependencies",
    "requirements",
    "dict_sort",
    "distribution",
    "dmg",
    "effect",
    "elementadd",
    "exif_rm_tags",
    "filterm",
    "findup",
    "firstfound",
    "flatten",
    "framesimple",
    "from_latin9",
    "fromiter",
    "getpths",
    "getsitedir",
    "getstdout",
    "group_user",
    "gz",
    "noexc",
    "pdf_diff",
    "pdf_from_picture",
    "pdf_linearize",
    "pdf_reduce",
    "pdf_scan",
    "pdf_to_picture",
    "python_latest",
    "python_version",
    "python_versions",
    "request_x_api_key_json",
    "sourcepath",
    "split_pairs",
    "stdquiet",
    "strip",
    "suppress",
    "syssudo",
    "tag_latest",
    "tardir",
    "tilde",
    "timestamp_now",
    "toiter",
    "to_latin9",
    "tomodules",
    "top",
    "tox",
    "version",
    "which",
)

import asyncio
import collections
import contextlib
import difflib
import fnmatch
import functools
import getpass
import grp
import importlib.metadata
import inspect
import io
import os
import pathlib
import platform
import pwd
import random
import re
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import time
import types
from pathlib import Path
from typing import (
    Any,
    AnyStr,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    Literal,
    MutableMapping,
    Optional,
    OrderedDict,
    ParamSpec,
    TextIO,
    TypeVar,
    cast,
)

import bs4
import fitz
import jsonpickle
import packaging.requirements
import requests
import semver
import strip_ansi
import structlog
import toml
from ppip import command as command
from ppip import exec_module_from_file as exec_module_from_file
from ppip import find_file as find_file
from ppip import parent as parent
from ppip import stdout as stdout
from ppip import superproject as superproject
from ppip import supertop as supertop

from huti.alias import RunningLoop
from huti.classes import CalledProcessError, CmdError, FrameSimple, GroupUser, TempDir
from huti.constants import HUTI_DATA, PDF_REDUCE_THRESHOLD, PYTHON_FTP, SCAN_PREFIX, venv
from huti.datas import Top
from huti.enums import FileName, PathIs, PathSuffix
from huti.env import USER, VIRTUAL_ENV
from huti.exceptions import CommandNotFound, InvalidArgument
from huti.typings import AnyPath, ExcType, StrOrBytesPath
from huti.variables import EXECUTABLE, EXECUTABLE_SITE, PW_ROOT, PW_USER


_KT = TypeVar("_KT")
_T = TypeVar("_T")
_VT = TypeVar("_VT")
_cache_which = {}




def aioclosed() -> bool:
    """check if event loop is closed"""
    return asyncio.get_event_loop().is_closed()



async def aiodmg(src: Path | str, dest: Path | str) -> None:
    """
    Async Open dmg file and copy the app to dest

    Examples:
        # >>> await dmg(Path("/tmp/JetBrains.dmg"), Path("/tmp/JetBrains"))

    Args:
        src: dmg file
        dest: path to copy to

    Returns:
        CompletedProcess
    """
    with TempDir() as tmpdir:
        await aiocmd("hdiutil", "attach", "-mountpoint", tmpdir, "-nobrowse", "-quiet", src)
        for item in src.iterdir():
            if item.name.endswith(".app"):
                await aiocmd("cp", "-r", tmpdir / item.name, dest)
                await aiocmd("xattr", "-r", "-d", "com.apple.quarantine", dest)
                await aiocmd("hdiutil", "detach", tmpdir, "-force")
                break


async def aiogz(src: Path | str, dest: Path | str = ".") -> Path:
    """
    Async ncompress .gz src to dest (default: current directory)

    It will be uncompressed to the same directory name as src basename.
    Uncompressed directory will be under dest directory.

    Examples:
        >>> from huti.classes import TempDir
        >>> from huti.functions import aiogz
        >>>
        >>> cwd = Path.cwd()
        >>> with TempDir() as workdir:
        ...     os.chdir(workdir)
        ...     with TempDir() as compress:
        ...         file = compress / "test.txt"
        ...         file.touch()  # doctest: +ELLIPSIS
        ...         compressed = tardir(compress)
        ...         with TempDir() as uncompress:
        ...             uncompressed = asyncio.run(aiogz(compressed, uncompress))
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: file to uncompress
        dest: destination directory to where uncompress directory will be created (default: current directory)

    Returns:
        Absolute Path of the Uncompressed Directory
    """
    return await asyncio.to_thread(gz, src, dest)


def aioloop() -> RunningLoop | None:
    """Get running loop"""
    return noexc(RuntimeError, asyncio.get_running_loop)


def aioloopid() -> int | None:
    """Get running loop id"""
    try:
        return asyncio.get_running_loop()._selector
    except RuntimeError:
        return None


def aiorunning() -> bool:
    """Check if event loop is running"""
    return asyncio.get_event_loop().is_running()


def allin(origin: Iterable, destination: Iterable) -> bool:
    """
    Checks all items in origin are in destination iterable.

    Examples:
        >>> from huti.functions import allin
        >>> from huti.variables import BUILTIN_CLASS
        >>>
        >>> class Int(int):
        ...     pass
        >>> allin(tuple.__mro__, BUILTIN_CLASS)
        True
        >>> allin(Int.__mro__, BUILTIN_CLASS)
        False
        >>> allin('tuple int', 'bool dict int')
        False
        >>> allin('bool int', ['bool', 'dict', 'int'])
        True
        >>> allin(['bool', 'int'], ['bool', 'dict', 'int'])
        True

    Args:
        origin: origin iterable.
        destination: destination iterable to check if origin items are in.

    Returns:
        True if all items in origin are in destination.
    """
    origin = toiter(origin)
    destination = toiter(destination)
    return all(x in destination for x in origin)


def anyin(origin: Iterable, destination: Iterable) -> Any | None:
    """
    Checks any item in origin are in destination iterable and return the first found.

    Examples:
        >>> from huti.functions import anyin
        >>> from huti.variables import BUILTIN_CLASS
        >>>
        >>> class Int(int):
        ...     pass
        >>> anyin(tuple.__mro__, BUILTIN_CLASS)
        <class 'tuple'>
        >>> assert anyin('tuple int', BUILTIN_CLASS) is None
        >>> anyin('tuple int', 'bool dict int')
        'int'
        >>> anyin('tuple int', ['bool', 'dict', 'int'])
        'int'
        >>> anyin(['tuple', 'int'], ['bool', 'dict', 'int'])
        'int'

    Args:
        origin: origin iterable.
        destination: destination iterable to check if any of origin items are in.

    Returns:
        First found if any item in origin are in destination.
    """
    origin = toiter(origin)
    destination = toiter(destination)
    for item in toiter(origin):
        if item in destination:
            return item


class _CacheWrapper(Generic[_T]):
    __wrapped__: Callable[..., _T]

    def __call__(self, *args: Any, **kwargs: Any) -> _T | Coroutine[Any, Any, _T]:
        ...


def cache(
        func: Callable[..., _T | Coroutine[Any, Any, _T]] = ...
) -> Callable[[Callable[..., _T]], _CacheWrapper[_T]] | _T | Coroutine[Any, Any, _T] | Any:
    """
    Caches previous calls to the function if object can be encoded.

    Examples:
        >>> import asyncio
        >>> from typing import cast
        >>> from typing import Coroutine
        >>> from environs import Env as Environs
        >>> from collections import namedtuple
        >>> from huti.functions import cache
        >>>
        >>> @cache
        ... def test(a):
        ...     print(True)
        ...     return a
        >>>
        >>> @cache
        ... async def test_async(a):
        ...     print(True)
        ...     return a
        >>>
        >>> test({})
        True
        {}
        >>> test({})
        {}
        >>> asyncio.run(cast(Coroutine, test_async({})))
        True
        {}
        >>> asyncio.run(cast(Coroutine, test_async({})))
        {}
        >>> test(Environs())
        True
        <Env {}>
        >>> test(Environs())
        <Env {}>
        >>> asyncio.run(cast(Coroutine, test_async(Environs())))
        True
        <Env {}>
        >>> asyncio.run(cast(Coroutine, test_async(Environs())))
        <Env {}>
        >>>
        >>> @cache
        ... class Test:
        ...     def __init__(self, a):
        ...         print(True)
        ...         self.a = a
        ...
        ...     @property
        ...     @cache
        ...     def prop(self):
        ...         print(True)
        ...         return self
        >>>
        >>> Test({})  # doctest: +ELLIPSIS
        True
        <....Test object at 0x...>
        >>> Test({})  # doctest: +ELLIPSIS
        <....Test object at 0x...>
        >>> Test({}).a
        {}
        >>> Test(Environs()).a
        True
        <Env {}>
        >>> Test(Environs()).prop  # doctest: +ELLIPSIS
        True
        <....Test object at 0x...>
        >>> Test(Environs()).prop  # doctest: +ELLIPSIS
        <....Test object at 0x...>
        >>>
        >>> Test = namedtuple('Test', 'a')
        >>> @cache
        ... class TestNamed(Test):
        ...     __slots__ = ()
        ...     def __new__(cls, *args, **kwargs):
        ...         print(True)
        ...         return super().__new__(cls, *args, **kwargs)
        >>>
        >>> TestNamed({})
        True
        TestNamed(a={})
        >>> TestNamed({})
        TestNamed(a={})
        >>> @cache
        ... class TestNamed(Test):
        ...     __slots__ = ()
        ...     def __new__(cls, *args, **kwargs): return super().__new__(cls, *args, **kwargs)
        ...     def __init__(self): super().__init__()
        >>> TestNamed({}) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        TypeError: __init__() takes 1 positional argument but 2 were given
    """
    memo = {}
    log = structlog.get_logger()
    structlog.configure(logger_factory=structlog.stdlib.LoggerFactory())
    coro = inspect.iscoroutinefunction(func)
    if coro:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            """Async Cache Wrapper."""
            key = None
            save = True
            try:
                key = jsonpickle.encode((args, kwargs))
                if key in memo:
                    return memo[key]
            except Exception as exception:
                log.warning("Not cached", func=func, args=args, kwargs=kwargs, exception=exception)
                save = False
            value = await func(*args, **kwargs)
            if key and save:
                memo[key] = value
            return value
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Cache Wrapper."""
            key = None
            save = True
            try:
                key = jsonpickle.encode((args, kwargs))
                if key in memo:
                    return memo[key]
            except Exception as exception:
                log.warning("Not cached", func=func, args=args, kwargs=kwargs, exception=exception)
                save = False
            value = func(*args, **kwargs)
            if key and save:
                memo[key] = value
            return value
    return wrapper





def current_task_name() -> str:
    """Current asyncio task name"""
    return asyncio.current_task().get_name() if aioloop() else ""


def dict_sort(
        data: dict[_KT, _VT], ordered: bool = False, reverse: bool = False
) -> dict[_KT, _VT] | OrderedDict[_KT, _VT]:
    """
    Order a dict based on keys.

    Examples:
        >>> from collections import OrderedDict
        >>> from huti.functions import dict_sort
        >>>
        >>> d = {"b": 2, "a": 1, "c": 3}
        >>> dict_sort(d)
        {'a': 1, 'b': 2, 'c': 3}
        >>> dict_sort(d, reverse=True)
        {'c': 3, 'b': 2, 'a': 1}
        >>> v = platform.python_version()
        >>> if "rc" not in v:
        ...     # noinspection PyTypeHints
        ...     assert dict_sort(d, ordered=True) == OrderedDict([('a', 1), ('b', 2), ('c', 3)])

    Args:
        data: dict to be ordered.
        ordered: OrderedDict.
        reverse: reverse.

    Returns:
        Union[dict, collections.OrderedDict]: Dict sorted
    """
    data = {key: data[key] for key in sorted(data.keys(), reverse=reverse)}
    if ordered:
        return collections.OrderedDict(data)
    return data




def dmg(src: Path | str, dest: Path | str) -> None:
    """
    Open dmg file and copy the app to dest

    Examples:
        # >>> await dmg(Path("/tmp/JetBrains.dmg"), Path("/tmp/JetBrains"))

    Args:
        src: dmg file
        dest: path to copy to

    Returns:
        CompletedProcess
    """
    with TempDir() as tmpdir:
        cmd("hdiutil", "attach", "-mountpoint", tmpdir, "-nobrowse", "-quiet", src)
        for item in src.iterdir():
            if item.name.endswith(".app"):
                cmd("cp", "-r", tmpdir / item.name, dest)
                cmd("xattr", "-r", "-d", "com.apple.quarantine", dest)
                cmd("hdiutil", "detach", tmpdir, "-force")
                break


def effect(apply: Callable, *args: Iterable) -> None:
    """
    Perform function on iterable.

    Examples:
        >>> from types import SimpleNamespace
        >>> from huti.functions import effect
        >>> simple = SimpleNamespace()
        >>> effect(lambda x: simple.__setattr__(x, dict()), 'a b', 'c')
        >>> assert simple.a == {}
        >>> assert simple.b == {}
        >>> assert simple.c == {}

    Args:
        apply: Function to apply.
        *args: Iterable to perform function.

    Returns:
        No Return.
    """
    for arg in toiter(args):
        for item in arg:
            apply(item)


def elementadd(name: str | tuple[str, ...], closing: bool | None = False) -> str:
    """
    Converts to HTML element.
    >>> from huti.functions import elementadd
    >>>
    >>> assert elementadd('light-black') == '<light-black>'
    >>> assert elementadd('light-black', closing=True) == '</light-black>'
    >>> assert elementadd(('green', 'bold',)) == '<green><bold>'
    >>> assert elementadd(('green', 'bold',), closing=True) == '</green></bold>'

    Args:
        name: text or iterable text.
        closing: True if closing/end, False if opening/start.

    Returns:
        Str
    """
    return "".join(f'<{"/" if closing else ""}{i}>' for i in ((name,) if isinstance(name, str) else name))


def exif_rm_tags(file: Path | str):
    """Removes tags with exiftool in pdf"""
    which("exiftool", raises=True)

    subprocess.check_call(["exiftool", "-q", "-q", "-all=", "-overwrite_original", file])


def filterm(
        d: MutableMapping[_KT, _VT], k: Callable[..., bool] = lambda x: True, v: Callable[..., bool] = lambda x: True
) -> MutableMapping[_KT, _VT]:
    """
    Filter Mutable Mapping.

    Examples:
        >>> from huti.functions import filterm
        >>>
        >>> assert filterm({'d':1}) == {'d': 1}
        >>> # noinspection PyUnresolvedReferences
        >>> assert filterm({'d':1}, lambda x: x.startswith('_')) == {}
        >>> # noinspection PyUnresolvedReferences
        >>> assert filterm({'d': 1, '_a': 2}, lambda x: x.startswith('_'), lambda x: isinstance(x, int)) == {'_a': 2}

    Returns:
        Filtered dict with
    """
    # noinspection PyArgumentList
    return d.__class__({x: y for x, y in d.items() if k(x) and v(y)})

# TODO: findup, top, requirements with None, requirements install and upgrade y GitHub Actions

def firstfound(data: Iterable, apply: Callable) -> Any:
    """
    Returns first value in data if apply is True.

    Examples:
        >>> from huti.functions import firstfound
        >>>
        >>> assert firstfound([1, 2, 3], lambda x: x == 2) == 2
        >>> assert firstfound([1, 2, 3], lambda x: x == 4) is None

    Args:
        data: iterable.
        apply: function to apply.

    Returns:
        Value if found.
    """
    for i in data:
        if apply(i):
            return i


def framesimple(data: inspect.FrameInfo | types.FrameType | types.TracebackType) -> FrameSimple | None:
    """
    :class:`rc.FrameSimple`.

    Examples:
        >>> import inspect
        >>> from huti.functions import framesimple
        >>>
        >>> frameinfo = inspect.stack()[0]
        >>> finfo = framesimple(frameinfo)
        >>> ftype = framesimple(frameinfo.frame)
        >>> assert frameinfo.frame.f_code == finfo.code
        >>> assert frameinfo.frame == finfo.frame
        >>> assert frameinfo.filename == str(finfo.path)
        >>> assert frameinfo.lineno == finfo.lineno
        >>> fields_frame = list(FrameSimple._fields)
        >>> fields_frame.remove('vars')
        >>> for attr in fields_frame:
        ...     assert getattr(finfo, attr) == getattr(ftype, attr)

    Returns:
        :class:`FrameSimple`.
    """
    if isinstance(data, inspect.FrameInfo):
        frame = data.frame
        back = frame.f_back
        lineno = data.lineno
    elif isinstance(data, types.FrameType):
        frame = data
        back = data.f_back
        lineno = data.f_lineno
    elif isinstance(data, types.TracebackType):
        frame = data.tb_frame
        back = data.tb_next
        lineno = data.tb_lineno
    else:
        return

    code = frame.f_code
    f_globals = frame.f_globals
    f_locals = frame.f_locals
    function = code.co_name
    v = f_globals | f_locals
    name = v.get("__name__") or function
    return FrameSimple(
        back=back,
        code=code,
        frame=frame,
        function=function,
        globals=f_globals,
        lineno=lineno,
        locals=f_locals,
        name=name,
        package=v.get("__package__") or name.split(".")[0],
        path=sourcepath(data),
        vars=v,
    )


def from_latin9(*args) -> str:
    """
    Converts string from latin9 hex

    Examples:
        >>> from huti.functions import from_latin9
        >>>
        >>> from_latin9("f1")
        'ñ'
        >>>
        >>> from_latin9("4a6f73e920416e746f6e696f205075e972746f6c6173204d6f6e7461f1e973")
        'José Antonio Puértolas Montañés'
        >>>
        >>> from_latin9("f1", "6f")
        'ño'

    Args:
        args:

    Returns:
        str
    """
    rv = ""
    if len(args) == 1:
        pairs = split_pairs(args[0])
        for pair in pairs:
            rv += bytes.fromhex("".join(pair)).decode("latin9")
    else:
        for char in args:
            rv += bytes.fromhex(char).decode("latin9")
    return rv


def fromiter(data, *args):
    """
    Gets attributes from Iterable of objects and returns dict with

    Examples:
        >>> from types import SimpleNamespace as Simple
        >>> from huti.functions import fromiter
        >>>
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], 'a', 'b', 'c') == {'a': [1, 2], 'b': [1]}
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], ('a', 'b', ), 'c') == {'a': [1, 2], 'b': [1]}
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], 'a b c') == {'a': [1, 2], 'b': [1]}

    Args:
        data: object.
        *args: attributes.

    Returns:
        Tuple
    """
    value = {k: [getattr(C, k) for C in data if hasattr(C, k)] for i in args for k in toiter(i)}
    return {k: v for k, v in value.items() if v}

def getstdout(func: Callable, *args: Any, ansi: bool = False, new: bool = True, **kwargs: Any) -> str | Iterable[str]:
    """
    Redirect stdout for func output and remove ansi and/or new line.

    Args:
        func: callable.
        *args: args to callable.
        ansi: strip ansi.
        new: strip new line.
        **kwargs: kwargs to callable.

    Returns:
        str | Iterable[str, str]:
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        func(*args, **kwargs)
    return strip(buffer.getvalue(), ansi=ansi, new=new) if ansi or new else buffer.getvalue()



def gz(src: Path | str, dest: Path | str = ".") -> Path:
    """
    Uncompress .gz src to dest (default: current directory)

    It will be uncompressed to the same directory name as src basename.
    Uncompressed directory will be under dest directory.

    Examples:
        >>> from huti.classes import TempDir
        >>> from huti.functions import gz
        >>> cwd = Path.cwd()
        >>> with TempDir() as workdir:
        ...     os.chdir(workdir)
        ...     with TempDir() as compress:
        ...         file = compress / "test.txt"
        ...         file.touch()  # doctest: +ELLIPSIS
        ...         compressed = tardir(compress)
        ...         with TempDir() as uncompress:
        ...             uncompressed = gz(compressed, uncompress)
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: file to uncompress
        dest: destination directory to where uncompress directory will be created (default: current directory)

    Returns:
        Absolute Path of the Uncompressed Directory
    """
    dest = Path(dest)
    with tarfile.open(src, "r:gz") as tar:
        tar.extractall(dest)
        return (dest / tar.getmembers()[0].name).parent.absolute()


def noexc(
        func: Callable[..., _T], *args: Any, default_: Any = None, exc_: ExcType = Exception, **kwargs: Any
) -> _T | Any:
    """
    Execute function suppressing exceptions.

    Examples:
        >>> from huti.functions import noexc
        >>> assert noexc(dict(a=1).pop, 'b', default_=2, exc_=KeyError) == 2

    Args:
        func: callable.
        *args: args.
        default_: default value if exception is raised.
        exc_: exception or exceptions.
        **kwargs: kwargs.

    Returns:
        Any: Function return.
    """
    try:
        return func(*args, **kwargs)
    except exc_:
        return default_

def pdf_diff(file1: Path | str, file2: Path | str) -> list[bytes]:
    """
    Show diffs of two pdfs

    Args:
        file1:
        file2:

    Returns:
        True if equals
    """
    return list(
        difflib.diff_bytes(
            difflib.unified_diff, Path(file1).read_bytes().splitlines(), Path(file2).read_bytes().splitlines(), n=1
        )
    )


def pdf_from_picture(file: Path | str, picture: Path | str, rm: bool = True) -> Path:
    """
    Creates pdf from image

    Args:
        file: pdf file
        picture: image file
        rm: remove image file (default: True)
    """
    doc = fitz.Document()
    doc.new_page()
    page = doc[0]
    page.insert_image(page.rect, filename=picture)
    doc.save(Path(file))
    if rm:
        Path(picture).unlink()
    return file


def pdf_linearize(file: Path | str):
    """linearize pdf (overwrites original)"""
    which("qpdf")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir) / "tmp.pdf"
        subprocess.run(["qpdf", "--linearize", file, tmp])
        Path(tmp).replace(file)


def pdf_reduce(
        path: Path | str,
        level: Literal["/default", "/prepress", "ebook", "/screen"] = "/prepress",
        threshold: int | None = PDF_REDUCE_THRESHOLD,
):
    """
    Compress pdf

    https://www.adobe.com/acrobat/hub/how-to-compress-pdf-in-linux.html

    Examples:
        >>> import shutil
        >>> from huti.constants import HUTI_DATA_TESTS
        >>> from huti.functions import pdf_reduce
        >>>
        >>> original = HUTI_DATA_TESTS / "5.2M.pdf"
        >>> backup = HUTI_DATA_TESTS / "5.2M-bk.pdf"
        >>>
        >>> shutil.copyfile(original, backup)  # doctest: +ELLIPSIS
        PosixPath('.../huti/data/tests/5.2M-bk.pdf')
        >>> original_size = original.stat().st_size
        >>> pdf_reduce(original, level="/screen")
        >>> reduced_size = original.stat().st_size
        >>> assert original_size != reduced_size  # doctest: +SKIP
        >>> shutil.move(backup, original)  # doctest: +ELLIPSIS
        PosixPath('.../huti/data/tests/5.2M.pdf')

    Args:
        path:
        threshold: limit in MB to reduce file size, None to reuce any pdf
        level: /default is selected by the system, /prepress 300 dpi, ebook 150 dpi, screen 72 dpi

    Returns:

    """
    if threshold is None or Path(path).stat().st_size > threshold:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir) / "tmp.pdf"
            subprocess.check_call(
                [
                    "gs",
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                    f"-dPDFSETTINGS={level}",
                    "-dNOPAUSE",
                    "-dQUIET",
                    "-dBATCH",
                    f"-sOutputFile={tmp}",
                    path,
                ]
            )
            Path(tmp).replace(path)


def pdf_scan(file: Path, directory: Optional[Path] = None) -> Path:
    """
    Looks like scanned, linearize and sets tag color

    Examples:
        >>> from pathlib import Path
        >>> from huti.constants import HUTI_DATA
        >>> from huti.constants import HUTI_DATA_TESTS
        >>> from huti.constants import SCAN_PREFIX
        >>> from huti.functions import pdf_scan
        >>>
        >>> for f in Path(HUTI_DATA_TESTS).iterdir():
        ...     if f.is_file() and f.suffix == ".pdf":
        ...         assert f"generated/{SCAN_PREFIX}" in str(pdf_scan(f, HUTI_DATA_TESTS / "generated"))

    Args:
        file: path of file to be scanned
        directory: destination directory (Default: file directory)

    Returns:
        Destination file
    """
    rotate = round(random.uniform(*random.choice([(-0.9, -0.5), (0.5, 0.9)])), 2)

    file = Path(file)
    filename = f"{SCAN_PREFIX}{file.stem}{file.suffix}"
    if directory:
        directory = Path(directory)
        if not directory.is_dir():
            directory.mkdir(parents=True, exist_ok=True)
        dest = directory / filename
    else:
        dest = file.with_name(filename)

    which("convert", raises=True)

    subprocess.check_call(
        [
            "convert",
            "-density",
            "120",
            file,
            "-attenuate",
            "0.4",
            "+noise",
            "Gaussian",
            "-rotate",
            str(rotate),
            "-attenuate",
            "0.03",
            "+noise",
            "Uniform",
            "-sharpen",
            "0x1.0",
            dest,
        ]
    )
    return dest


def pdf_to_picture(file: Path | str, dpi: int = 300, fmt: Literal["jpeg", "png"] = "jpeg") -> Path:
    """Creates a file with jpeg in the same directory from first page of pdf"""
    which("pdftoppm")

    file = Path(file)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir) / "tmp"
        subprocess.run(["pdftoppm", f"-{fmt}", "-r", str(dpi), "-singlefile", file, tmp])
        suffix = f".{fmt}" if fmt == "png" else ".jpg"
        if not (dest := tmp.with_suffix(suffix)).exists():
            raise FileNotFoundError(f"File not found {dest}")
        return shutil.copy(dest, file.with_suffix(suffix))


def python_latest(start: str | int | None = None) -> semver.VersionInfo:
    """
    Python latest version avaialble

    Examples:
        >>> import platform
        >>> from huti.functions import python_latest
        >>>
        >>> v = platform.python_version()
        >>> if "rc" not in v:
        ...     assert python_latest(v).match(f">={v}")
        ...     assert python_latest(v.rpartition(".")[0]).match(f">={v}")
        ...     assert python_latest(sys.version_info.major).match(f">={v}")
        >>>
        >>> assert python_latest("3.12").minor == 12

    Args:
        start: version startswith match, i.e.: "3", "3.10", "3.10", 3 or None to use `PYTHON_VERSION`
          environment variable or :obj:``sys.version`` if not set (Default: None).

    Returns:
        Latest Python Version
    """
    if start is None:
        start = python_version()
    start = str(start)
    start = start.rpartition(".")[0] if len(start.split(".")) == 3 else start
    return sorted([i for i in python_versions() if str(i).startswith(start)])[-1]


def python_version() -> str:
    """
    Major and Minor Python Version from ``PYTHON_VERSION`` environment variable, or
     ``PYTHON_REQUIRES`` environment variable or :obj:`sys.version`

    Examples:
        >>> import os
        >>> import platform
        >>> from huti.functions import python_version
        >>>
        >>> v = python_version()
        >>> assert platform.python_version().startswith(v)
        >>> assert len(v.split(".")) == 2
        >>>
        >>> os.environ["PYTHON_VERSION"] = "3.10"
        >>> assert python_version() == "3.10"
        >>>
        >>> os.environ["PYTHON_VERSION"] = "3.12-dev"
        >>> assert python_version() == "3.12-dev"
        >>>
        >>> os.environ["PYTHON_VERSION"] = "3.12.0b4"
        >>> assert python_version() == "3.12"

    Returns:
        str
    """
    p = platform.python_version()
    ver = os.environ.get("PYTHON_VERSION", p) or os.environ.get("PYTHON_REQUIRES", p)
    if len(ver.split(".")) == 3:
        return ver.rpartition(".")[0]
    return ver


def python_versions() -> list[semver.VersionInfo, ...]:
    """
    Python versions avaialble

    Examples:
        >>> import platform
        >>> from huti.functions import python_versions
        >>>
        >>> v = platform.python_version()
        >>> if not "rc" in v:
        ...     assert v in python_versions()

    Returns:
        Tuple of Python Versions
    """
    rv = []
    for link in bs4.BeautifulSoup(requests.get(PYTHON_FTP, timeout=2).text, "html.parser").find_all("a"):
        if link := re.match(r"((3\.([7-9]|[1-9][0-9]))|4).*", link.get("href").rstrip("/")):
            rv.append(semver.VersionInfo.parse(link.string))
    return sorted(rv)


def request_x_api_key_json(url, key: str = "") -> dict[str, str] | None:
    """
    API request helper with API Key and returning json

    Examples:
        >>> from huti.functions import request_x_api_key_json
        >>>
        >>> request_x_api_key_json("https://api.iplocation.net/?ip=8.8.8.8", \
                "rn5ya4fp/tzI/mENxaAvxcMo8GMqmg7eMnCvUFLIV/s=")
        {'ip': '8.8.8.8', 'ip_number': '134744072', 'ip_version': 4, 'country_name': 'United States of America',\
 'country_code2': 'US', 'isp': 'Google LLC', 'response_code': '200', 'response_message': 'OK'}

    Args:
        url: API url
        key: API Key

    Returns:
        response json
    """
    headers = {"headers": {"X-Api-Key": key}} if key else {}
    response = requests.get(url, **headers, timeout=2)
    if response.status_code == requests.codes.ok:
        return response.json()


def sourcepath(data: Any) -> Path:
    """
    Get path of object.

    Examples:
        >>> import asyncio
        >>> import huti.__init__
        >>> from huti.functions import sourcepath
        >>>
        >>> finfo = inspect.stack()[0]
        >>> globs_locs = (finfo.frame.f_globals | finfo.frame.f_locals).copy()
        >>> assert sourcepath(sourcepath) == Path(__file__)
        >>> assert sourcepath(asyncio.__file__) == Path(asyncio.__file__)
        >>> assert sourcepath(dict(a=1)) == Path("{'a': 1}")

    Returns:
        Path.
    """
    if isinstance(data, MutableMapping):
        f = data.get("__file__")
    elif isinstance(data, inspect.FrameInfo):
        f = data.filename
    else:
        try:
            f = inspect.getsourcefile(data) or inspect.getfile(data)
        except TypeError:
            f = None
    return Path(f or str(data))


def split_pairs(text):
    """
    Split text in pairs for even length

    Examples:
        >>> from huti.functions import split_pairs
        >>>
        >>> split_pairs("123456")
        [('1', '2'), ('3', '4'), ('5', '6')]

    Args:
        text:

    Returns:

    """
    return list(zip(text[0::2], text[1::2]))



@contextlib.contextmanager
def stdquiet() -> tuple[TextIO, TextIO]:
    """
    Redirect stdout/stderr to StringIO objects to prevent console output from
    distutils commands.

    Returns:
        Stdout, Stderr
    """

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    new_stdout = sys.stdout = io.StringIO()
    new_stderr = sys.stderr = io.StringIO()
    try:
        yield new_stdout, new_stderr
    finally:
        new_stdout.seek(0)
        new_stderr.seek(0)
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def strip(obj: str | Iterable[str], ansi: bool = False, new: bool = True) -> str | Iterable[str]:
    """
    Strips ``\n`` And/Or Ansi from string or Iterable.

    Args:
        obj: object or None for redirect stdout
        ansi: ansi (default: False)
        new: newline (default: True)

    Returns:
        Same type with NEWLINE removed.
    """

    def rv(x):
        if isinstance(x, str):
            x = x.removesuffix("\n") if new else x
            x = strip_ansi.strip_ansi(x) if ansi else x
        if isinstance(x, bytes):
            x = x.removesuffix(b"\n") if new else x
        return x

    cls = type(obj)
    if isinstance(obj, str):
        return rv(obj)
    return cls(rv(i) for i in obj)



def tardir(src: Path | str) -> Path:
    """
    Compress directory src to <basename src>.tar.gz in cwd

    Examples:
        >>> from huti.classes import TempDir
        >>> from huti.functions import tardir
        >>> cwd = Path.cwd()
        >>> with TempDir() as workdir:
        ...     os.chdir(workdir)
        ...     with TempDir() as compress:
        ...         file = compress / "test.txt"
        ...         file.touch()  # doctest: +ELLIPSIS
        ...         compressed = tardir(compress)
        ...         with TempDir() as uncompress:
        ...             uncompressed = gz(compressed, uncompress)
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: directory to compress

    Raises:
        FileNotFoundError: No such file or directory
        ValueError: Can't compress current working directory

    Returns:
        Compressed Absolute File Path
    """
    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(f"{src}: No such file or directory")

    if src.resolve() == Path.cwd().resolve():
        raise ValueError("Can't compress current working directory")

    name = Path(src).name + ".tar.gz"
    dest = Path(name)
    with tarfile.open(dest, "w:gz") as tar:
        for root, _, files in os.walk(src):
            for file_name in files:
                tar.add(os.path.join(root, file_name))
        return dest.absolute()


def tilde(path: str | Path = ".") -> str:
    """
    Replaces $HOME with ~

    Examples:
        >>> from huti.functions import tilde
        >>> assert tilde(f"{Path.home()}/file") == f"~/file"

    Arguments
        path: path to replace (default: '.')

    Returns:
        str
    """
    return str(path).replace(str(Path.home()), "~")


def timestamp_now(file: Path | str):
    """set modified and create date of file to now"""
    now = time.time()
    os.utime(file, (now, now))

def to_latin9(chars: str) -> str:
    """
    Converts string to latin9 hex

    Examples:
        >>> from huti.constants import JOSE
        >>> from huti.functions import to_latin9
        >>>
        >>> to_latin9("ñ")
        'f1'
        >>>
        >>> to_latin9(JOSE)
        '4a6f73e920416e746f6e696f205075e972746f6c6173204d6f6e7461f1e973'

    Args:
        chars:

    Returns:
        hex str
    """
    rv = ""
    for char in chars:
        rv += char.encode("latin9").hex()
    return rv


def tomodules(obj: Any, suffix: bool = True) -> str:
    """
    Converts Iterable to A.B.C

    >>> from huti.functions import tomodules
    >>> assert tomodules('a b c') == 'a.b.c'
    >>> assert tomodules('a b c.py') == 'a.b.c'
    >>> assert tomodules('a/b/c.py') == 'a.b.c'
    >>> assert tomodules(['a', 'b', 'c.py']) == 'a.b.c'
    >>> assert tomodules('a/b/c.py', suffix=False) == 'a.b.c.py'
    >>> assert tomodules(['a', 'b', 'c.py'], suffix=False) == 'a.b.c.py'

    Args:
        obj: iterable.
        suffix: remove suffix.

    Returns:
        String A.B.C
    """
    split = "/" if isinstance(obj, str) and "/" in obj else " "
    return ".".join(i.removesuffix(Path(i).suffix if suffix else "") for i in toiter(obj, split=split))

