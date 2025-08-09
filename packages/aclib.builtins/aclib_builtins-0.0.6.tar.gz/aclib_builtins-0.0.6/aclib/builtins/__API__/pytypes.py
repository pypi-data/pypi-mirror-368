from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self, Callable, Any, Union, Iterator, SupportsIndex, Sequence, Iterable
    JsonableObj = Union[int, float, str, list, dict, bool, None]

from typing import overload
from collections import UserString

import re, json, base64, unicodedata, random, math


class Object:

    def __repr__(self: object, *key: str) -> str:
        items = (f'{k}={getattr(self, k).__repr__()}' for k in key or self.__dict__)
        return f'<{self.__class__.__name__} ({", ".join(items)})>'


def regexflag(flags):
    if isinstance(flags, int):
        return flags
    if isinstance(flags, str):
        _regexflag = 0
        for flag in flags.split('|'): _regexflag |= getattr(re, flag.upper())
        return _regexflag
    raise TypeError('a regexflag should be a int, str or Str.RegexFlag(re.RegexFlag)')

class Str(UserString, str):

    Match = re.Match
    RegexFlag = re.RegexFlag

    @classmethod
    def randomNumberLetter(cls, length: int = 1) -> Self:
        sequence = ''
        asciirange = ((ord('0'), ord('9')), (ord('a'), ord('z')), (ord('A'), ord('Z')))
        for i in range(length):
            asciimin, asciimax = asciirange[random.randint(0,2)]
            sequence += chr(random.randint(asciimin, asciimax))
        return cls(sequence)

    def __init__(self, obj: Any = ''):
        super().__init__(obj)

    def __getitem__(self, item) -> Self:
        return super().__getitem__(item)

    def len(self):
        return len(self)

    def enlen(self):
        return sum((1 + (unicodedata.east_asian_width(char) == 'W') for char in self), 0)

    def reverse(self) -> Self:
        return self[::-1]

    # region ============================================= 文本编码 =============================================
    def base64encode(self) -> Self:
        return self.__class__(base64.b64encode(self.encode()).decode())

    def base64decode(self) -> Self:
        return self.__class__(base64.b64decode(self).decode())

    def base16encode(self) -> Self:
        return self.__class__(base64.b16encode(self.encode()).decode())

    def base16decode(self) -> Self:
        return self.__class__(base64.b16decode(self).decode())

    def jsonencode(self: JsonableObj, unicode=False, indent=None) -> Self:
        return Str(json.dumps(self, ensure_ascii=unicode, indent=indent))

    def jsondecode(self) -> JsonableObj:
        return json.loads(self)
    # endregion ==========================================================================================

    # region ============================================= 正则匹配 =============================================
    class MatchList(list):
        def groupmap(self, group=0) -> list[str]:
            return [match.group(group) for match in self]
        def spanmap(self, group=0) -> list[tuple[int,int]]:
            return [match.span(group) for match in self]
        def startmap(self, group=0) -> list[int]:
            return [match.start(group) for match in self]
        def endmap(self, group=0) -> list[int]:
            return [match.end(group) for match in self]

    def reescape(self) -> Self:
        return self.__class__(re.escape(self))

    def rereplace(self, frompattern: str, tostr: str | Callable[[Match], str], count=0, flags: int | str | RegexFlag = 0) -> Self:
        return self.__class__(re.sub(frompattern, tostr, self, count, regexflag(flags)))

    def resplit(self, seppattern: str, maxsplit=0, flags: int | str | RegexFlag = 0) -> list[Self]:
        return [self.__class__(res) for res in re.split(seppattern, self, maxsplit, regexflag(flags))]

    def __rematch(self, PatternMethod, pattern, pos, endpos, flags):
        return PatternMethod(re.compile(pattern, regexflag(flags)), self, pos, len(self) if endpos is ... else endpos)

    def refind(self, pattern: str, pos=0, endpos=..., flags: int | str | RegexFlag = 0) -> int:
        match = self.__rematch(re.Pattern.search, pattern, pos, endpos, flags)
        return bool(match)-1 or match.start(0)

    def rematch(self, pattern: str, pos=0, endpos=..., flags: int | str | RegexFlag = 0) -> Match:
        return self.__rematch(re.Pattern.search, pattern, pos, endpos, flags)

    def rematchhead(self, pattern: str, pos=0, endpos=..., flags: int | str | RegexFlag = 0) -> Match:
        return self.__rematch(re.Pattern.match, pattern, pos, endpos, flags)

    def rematchfull(self, pattern: str, pos=0, endpos=..., flags: int | str | RegexFlag = 0) -> Match:
        return self.__rematch(re.Pattern.fullmatch, pattern, pos, endpos, flags)

    def rematchall(self, pattern: str, pos=0, endpos=..., flags: int | str | RegexFlag = 0) -> MatchList[Match]:
        return self.MatchList(self.__rematch(re.Pattern.finditer, pattern, pos, endpos, flags))

    def rematchiter(self, pattern: str, pos=0, endpos=..., flags: int | str | RegexFlag = 0) -> Iterator[Match]:
        return self.__rematch(re.Pattern.finditer, pattern, pos, endpos, flags)
    # endregion ==========================================================================================

    # region ============================================= 文本切割 =============================================
    def join(self, seq: Iterable[str]) -> Self:
        return self.__class__(super().join(seq))

    def split(self, sep: str=None, maxsplit=-1) -> list[Self]:
        return [self.__class__(part) for part in super().split(sep, maxsplit)]

    def rsplit(self, sep: str=None, maxsplit=-1) -> list[Self]:
        return [self.__class__(part) for part in super().rsplit(sep, maxsplit)]

    def splitlines(self, keepends=False) -> list[Self]:
        return [self.__class__(part) for part in super().splitlines(keepends)]

    def partition(self, sep: str) -> tuple[Self, Self, Self]:
        return tuple(self.__class__(part) for part in super().partition(sep)) # type: ignore

    def rpartition(self, sep: str) -> tuple[Self, Self, Self]:
        return tuple(self.__class__(part) for part in super().rpartition(sep)) # type: ignore

    def splitbylength(self, length: int) -> list[Self]:
        assert length > 0, 'split length must be a integer greater than 0'
        return [self[i:i+length] for i in range(0, len(self), length)]

    def rsplitbylength(self, length: int) -> list[Self]:
        assert length > 0, 'split length must be a integer greater than 0'
        extra = len(self)%length
        return [self[:extra], *self[extra:].splitbylength(length)]
    # endregion ==========================================================================================

    # region ============================================= 类型转换 =============================================
    def tostr(self) -> str:
        return str(self)

    def toint(self, base=0) -> int:
        return int(self, base)

    def toBin(self, base=0) -> Bin:
        return Bin(self, base)

    def toOct(self, base=0) -> Oct:
        return Oct(self, base)

    def toHex(self, base=0) -> Hex:
        return Hex(self, base)
    # endregion ==========================================================================================

    # region ============================================= 半角对齐 =============================================
    def __align(self, alignmethod: Callable, enwidth, fillchar) -> Self:
        if len(fillchar) != 1:
            raise TypeError('The fill character must be exactly one character long')
        selfenlen = self.enlen()
        if enwidth <= selfenlen:
            return self
        fillwidth = enwidth - selfenlen
        if alignmethod == self.ljusten:
            lfillw, rfillw = 0, fillwidth
        if alignmethod == self.rjusten:
            lfillw, rfillw = fillwidth, 0
        if alignmethod == self.centeren:
            lfillw = fillwidth // 2
            rfillw = fillwidth - lfillw
        fillcharenlen = self.__class__.enlen(fillchar)
        left  = lfillw % fillcharenlen * ' ' + lfillw // fillcharenlen * fillchar
        right = rfillw // fillcharenlen * fillchar + rfillw % fillcharenlen * ' '
        return left + self + right

    def centeren(self, enwidth: int, fillchar=' ') -> Self:
        return self.__align(self.centeren, enwidth, fillchar)

    def ljusten(self, enwidth: int, fillchar=' ') -> Self:
        return self.__align(self.ljusten, enwidth, fillchar)

    def rjusten(self, enwidth: int, fillchar=' ') -> Self:
        return self.__align(self.rjusten, enwidth, fillchar)
    # endregion ==========================================================================================

    def zip(self: Self | str, countDigitMap: Sequence[str] = ')!@#$%^&*(') -> Self:
        def zippedDigits(match: re.Match) -> str:
            char = match.group(1)
            nchars = match.end(0) - match.start(0)
            ncharscode = ''.join(countDigitMap[int(digit)] for digit in str(nchars))
            return char + ncharscode
        return Str(self).rereplace(r'(.)\1{2,}', zippedDigits)

    def unzip(self: Self | str, countDigitMap: Sequence[str] = ')!@#$%^&*(') -> Self:
        def unzippedchars(match: re.Match) -> str:
            char = match.group(1)
            ncharscode = match.group(2)
            nchars = int(''.join(str(countDigitMap.index(digit)) for digit in ncharscode))
            return char * nchars
        return Str(self).rereplace(rf'(.)([{re.escape("".join(countDigitMap))}]+)', unzippedchars)

class BaseNumberMeta(type):
    nan = property(lambda self: _nan)
    def __new__(mcs, name, base, attr):
        attr['nan'] = mcs.nan
        return super().__new__(mcs, name, base, attr)

class BaseNumber(object, metaclass=BaseNumberMeta):
    nan: BaseNumber

    @classmethod
    def __int2base(cls, x: int, base: int) -> str:
        digits = '0123456789abcdefghijklmnopqrstuvwxyz'
        result = ''
        while x:
            result = digits[x % base] + result
            x = x // base
        return result or '0'

    def __new__(cls, x: str | SupportsIndex = 0, xbase=0, tobase=0, tondigits=0) -> Self:
        if isinstance(x, BaseNumber):
            xbase, xvalue, xndigits = x.base, x.value, x.ndigits
        elif hasattr(x, '__index__'):
            xbase, xvalue, xndigits = 10, int(x), 0
        elif isinstance(x, str):
            xbase = xbase or {'0b':2, '0o':8, '0x':16}.get(x[:2].lower(), 0) or tobase or 10
            try: xvalue = int(x, xbase)
            except ValueError: return cls.nan
            xndigits = len(x.replace({2:'0b', 8:'0o', 16:'0x'}.get(xbase, ''), '').replace('_', ''))
        else: raise TypeError('please give a integer or string represents a integer')
        if xvalue != xvalue: return x
        tobase = tobase or xbase
        tondigits = tondigits or xndigits and math.ceil(math.log(xbase, tobase)*xndigits)
        self = super().__new__(cls)
        self.__intvalue = xvalue
        self.__strvalue = self.__int2base(self.__intvalue, tobase).zfill(tondigits)
        self.__ndigits = len(self.__strvalue)
        self.__base = tobase
        return self

    def __repr__(self):
        if self is self.__class__.nan: return '<BaseNumber.nan>'
        return f'<{self.__class__.__name__}({self.base}) {self.data}>'

    def __index__(self):
        return self.__intvalue

    @property
    def base(self) -> int: return self.__base

    @property
    def value(self) -> int: return self.__intvalue

    @property
    def data(self) -> str: return self.__strvalue

    @property
    def ndigits(self) -> int: return self.__ndigits

    def __calculate(self, method, other):
        ndigits = self.__ndigits
        if isinstance(other, BaseNumber):
            other, ndigits = other.value, max(ndigits, other.ndigits)
        result = method(self.__intvalue, other)
        if type(result) == int:
            return self.__class__(result, tobase=self.base, tondigits=ndigits)
        return result

    def __bool__(self) -> bool: return self.__intvalue.__bool__()
    def __eq__(self, other)->bool: return self.__calculate(float.__eq__, other)
    def __ne__(self, other)->bool: return self.__calculate(float.__ne__, other)
    def __le__(self, other)->bool: return self.__calculate(float.__le__, other)
    def __ge__(self, other)->bool: return self.__calculate(float.__ge__, other)
    def __lt__(self, other)->bool: return self.__calculate(float.__lt__, other)
    def __gt__(self, other)->bool: return self.__calculate(float.__gt__, other)
    def __add__(self, other)->Self: return self.__calculate(int.__add__, other)
    def __sub__(self, other)->Self: return self.__calculate(int.__sub__, other)
    def __mul__(self, other)->Self: return self.__calculate(int.__mul__, other)
    def __truediv__(self, other)->Self: return self.__calculate(int.__truediv__, other)
    def __floordiv__(self, other)->Self: return self.__calculate(int.__floordiv__, other)
    def __and__(self, other)->Self: return self.__calculate(int.__and__, other)
    def __or__(self, other)->Self: return self.__calculate(int.__or__, other)
    def __xor__(self, other)->Self: return self.__calculate(int.__xor__, other)
    def __radd__(self, other)->Self: return self.__calculate(int.__radd__, other)
    def __rsub__(self, other)->Self: return self.__calculate(int.__rsub__, other)
    def __rmul__(self, other)->Self: return self.__calculate(int.__rmul__, other)
    def __rtruediv__(self, other)->Self: return self.__calculate(int.__rtruediv__, other)
    def __rfloordiv__(self, other)->Self: return self.__calculate(int.__rfloordiv__, other)
    def __rand__(self, other)->Self: return self.__calculate(int.__rand__, other)
    def __ror__(self, other)->Self: return self.__calculate(int.__ror__, other)
    def __rxor__(self, other)->Self: return self.__calculate(int.__rxor__, other)

    def toint(self) -> int:
        return self.__intvalue

    def tostr(self, prefix=False) -> str:
        prefix = {2:'0b', 8:'0o', 16:'0x'}.get(self.base, '') if prefix else ''
        return prefix + self.__strvalue

    def toStr(self, prefix=False) -> Str:
        return Str(self.tostr(prefix))

    def toBin(self) -> Bin:
        return Bin(self)

    def toOct(self) -> Oct:
        return Oct(self)

    def toHex(self) -> Hex:
        return Hex(self)

    def tobase(self, base: int) -> BaseNumber:
        return BaseNumber(self, tobase=base)

    def tondigits(self, numberOfDigits) -> Self:
        return self.__class__(self, tondigits=numberOfDigits)

class Bin(BaseNumber):
    @overload
    def __new__(cls, x: str | SupportsIndex = 0, xbase=0, tondigits=0) -> Self: ...
    def __new__(cls, x: str | SupportsIndex = 0, xbase=0, tondigits=0, **kwargs):
        return super().__new__(cls, x, xbase, 2, tondigits)

class Oct(BaseNumber):
    @overload
    def __new__(cls, x: str | SupportsIndex = 0, xbase=0, tondigits=0) -> Self: ...
    def __new__(cls, x: str | SupportsIndex = 0, xbase=0, tondigits=0, **kwargs):
        return super().__new__(cls, x, xbase, 8, tondigits)

class Hex(BaseNumber):
    @overload
    def __new__(cls, x: str | SupportsIndex = 0, xbase=0, tondigits=0) -> Self: ...
    def __new__(cls, x: str | SupportsIndex = 0, xbase=0, tondigits=0, **kwargs):
        return super().__new__(cls, x, xbase, 16, tondigits)

_nan = BaseNumber()
setattr(_nan, '_BaseNumber__intvalue', float('nan'))
setattr(_nan, '_BaseNumber__strvalue', '')
setattr(_nan, '_BaseNumber__base', 10)
setattr(_nan, '_BaseNumber__ndigits', 0)
