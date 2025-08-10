from abc import ABCMeta, abstractmethod
from functools import reduce
from operator import add, sub, mul, truediv, floordiv
from typing import Callable, Iterable, List, Optional, Tuple, Union, overload, Any
import math
import bisect
import xml.etree.ElementTree as ET
from .pq import PQueue


class TimeFunc(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self,time:int)->float: ...
    @abstractmethod
    def __str__(self)->str: ...
    def __add__(self,other:'FloatLike')->'TimeFunc':
        return calcFunc(self,other,'+')
    def __sub__(self,other:'TimeFunc')->'TimeFunc':
        return calcFunc(self,other,'-')
    def __mul__(self,other)->'TimeFunc':
        return calcFunc(self,other,'*')
    def __truediv__(self,other)->'TimeFunc':
        return calcFunc(self,other,'/')
    def __floordiv__(self,other)->'TimeFunc':
        return calcFunc(self,other,'//')

_oper_trans = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': truediv,
    '//': floordiv
}
_Oper = Callable[[float,float],float]
FloatLike = Union[TimeFunc,float,int]

class OverrideFunc(TimeFunc):
    '''A function returning predefined values normally, and returning an alternative value if set.'''
    def __init__(self,default:TimeFunc,override_val:Optional[float] = None):
        self._val:TimeFunc=default
        self._override:Optional[float] = override_val
    
    def __call__(self,t:int)->float:
        if self._override is not None: return self._override
        return self._val(t)
    
    def setOverride(self,overval:float):
        '''Set the alternative value'''
        self._override=overval
    
    def clearOverride(self):
        '''Clear the alternative value'''
        self._override=None
    
    def __repr__(self):
        if self._override is None: return f"OverrideF<{self._val}>"
        return f"OverrideF<O={self._override}>"

    def __str__(self):
        if self._override is None: return str(self._val)
        return str(self._override)+"(Override)"

class PlusFunc(TimeFunc):
    def __init__(self,f1:TimeFunc,f2:TimeFunc): self._f1=f1; self._f2=f2
    def __call__(self,_t:int)->float: return self._f1(_t)+self._f2(_t)
    def __repr__(self)->str: return f"PlusFunc({self._f1},{self._f2})"
    def __str__(self)->str: return repr(self)

class QuickSumFunc(TimeFunc):
    def __init__(self,funcs:'List[TimeFunc]'): self._fs=funcs
    def __call__(self,_t:int)->float: return sum(f(_t) for f in self._fs)
    def __repr__(self)->str: return f"QuickSumFunc({self._fs})"
    def __str__(self)->str: return repr(self)

class MinusFunc(TimeFunc):
    def __init__(self,f1:TimeFunc,f2:TimeFunc): self._f1=f1; self._f2=f2
    def __call__(self,_t:int)->float: return self._f1(_t)-self._f2(_t)
    def __repr__(self)->str: return f"MinusFunc({self._f1},{self._f2})"
    def __str__(self)->str: return repr(self)

class MulFunc(TimeFunc):
    def __init__(self,f1:TimeFunc,f2:TimeFunc): self._f1=f1; self._f2=f2
    def __call__(self,_t:int)->float: return self._f1(_t)*self._f2(_t)
    def __repr__(self)->str: return f"MulFunc({self._f1},{self._f2})"
    def __str__(self)->str: return repr(self)

class QuickMulFunc(TimeFunc):
    def __init__(self,funcs:'List[TimeFunc]'): self._fs=funcs
    def __call__(self,_t:int)->float: return reduce(mul, (f(_t) for f in self._fs))
    def __repr__(self)->str: return f"QuickMulFunc({self._fs})"
    def __str__(self)->str: return repr(self)

class TrueDivFunc(TimeFunc):
    def __init__(self,f1:TimeFunc,f2:TimeFunc): self._f1=f1; self._f2=f2
    def __call__(self,_t:int)->float: return self._f1(_t)/self._f2(_t)
    def __repr__(self)->str: return f"TrueDivFunc({self._f1},{self._f2})"
    def __str__(self)->str: return repr(self)

class FloorDivFunc(TimeFunc):
    def __init__(self,f1:TimeFunc,f2:TimeFunc): self._f1=f1; self._f2=f2
    def __call__(self,_t:int)->float: return self._f1(_t)//self._f2(_t)
    def __repr__(self)->str: return f"FloorDivFunc({self._f1},{self._f2})"
    def __str__(self)->str: return repr(self)

class ConstFunc(TimeFunc):
    def __init__(self,const:float): self._val:float=const
    def __call__(self,time:int)->float: return self._val
    def __repr__(self)->str: return f"ConstFunc({self._val})"
    def __str__(self)->str: return str(self._val)

class SegFunc(TimeFunc):
    '''Segmented const function'''
    _tl:'List[int]'
    _d:'List[float]'
    
    @overload
    def __init__(self, time_line:'List[int]', data:'List[float]'): ...
    @overload
    def __init__(self, time_line:'List[Tuple[int,float]]'): ...
    @overload
    def __init__(self): ...

    def __init__(self, time_line = None, data = None):
        if data is None and time_line is None:
            self.__init1([])
        elif data is None and time_line is not None:
            assert isinstance(time_line, list)
            self.__init1(time_line)
        elif data is not None and time_line is not None:
            assert isinstance(time_line, list) and isinstance(data, list)
            self.__init0(time_line, data)
        else:
            raise ValueError(f"Invalid arguments: {time_line}, {data}")
        self._rep = 1
        self._per = 0

    def __init0(self, time_line:'List[int]', data:'List[float]'):
        if len(time_line) != len(data):
            raise ValueError(f"Time line length {len(time_line)} is not equal to data length {len(data)}.")
        for i in range(1, len(time_line)):
            if time_line[i] <= time_line[i-1]:
                raise ValueError(f"Time must be strictly increasing: [{i}]={time_line[i]}<=[{i-1}]={time_line[i-1]}")
        self._tl = time_line
        self._d = data
    
    def __init1(self, time_line:'List[Tuple[int,float]]'):
        self._tl = [t for t, _ in time_line]
        self._d = [d for _, d in time_line]
        for i in range(1, len(self._tl)):
            if self._tl[i] <= self._tl[i-1]:
                raise ValueError(f"Time must be strictly increasing: [{i}]={self._tl[i]}<=[{i-1}]={self._tl[i-1]}")
    
    def __len__(self)->int: return len(self._d)

    def __iter__(self): return zip(self._tl,self._d)

    def __call__(self, time:int)->float:
        if len(self._tl) == 0: return 0
        if time < self._tl[0]:
            raise ValueError(f"Time {time} must be later than the start time {self._tl[0]}.")
        return self._d[bisect.bisect_right(self._tl, time) - 1]

    def value_at(self, time:int) -> float:
        """
        Return the value of the function at the given time.
        This method is similar to __call__, but does not raise an error if the time is before the start time.
        Instead, it returns 0 if the time is before the start time.
        """
        if len(self._d) == 0: return 0
        if time < self._tl[0]: return 0
        return self._d[bisect.bisect_right(self._tl, time) - 1]
    
    def __repr__(self)->str:
        return f"SegFunc({[(t,d) for t,d in self]})"

    def __str__(self)->str:
        return str([(t,d) for t,d in self])
    
    def toXML(self, tag_name:str="seg", tag_item:str="item", 
               attr_time:str="time", attr_value:str="val",
               value_trans:Optional[Callable[[int, float],str]]=None) -> str:
        return ET.tostring(self.toXMLNode(tag_name,tag_item,attr_time,attr_value,value_trans), "unicode")
        
    def toXMLNode(self, tag_name:str="seg", tag_item:str="item", 
                    attr_time:str="time", attr_value:str="val",
                    value_trans:Optional[Callable[[int, float],str]]=None) -> ET.Element:
        e = ET.Element(tag_name)
        if self._per > 0:
            e.attrib["repeat"] = str(self._rep)
            e.attrib["period"] = str(self._per)
        for t, d in self:
            if t >= self._per and self._per > 0: break
            if value_trans is not None:
                vs = value_trans(t, d)
            else:
                vs = str(d)
            e.append(ET.Element(tag_item,{attr_time:str(t),attr_value:vs}))
        return e
    
    def add(self, time:int, val:float):
        """Add a new time and value to the function. The time must be greater than the last time."""
        assert len(self._tl) == 0 or time > self._tl[-1]
        self._tl.append(time)
        self._d.append(val)
        self._rep = 1
        self._per = 0

    def repeat(self, times:int, period:int)->'SegFunc':
        """Repeat the function `times` times, with a period of `period`."""
        if len(self._tl) == 0: return SegFunc()
        if times == 1: return SegFunc(self._tl,self._d)
        if times < 1: raise ValueError(f"times must be greater than 0, but got {times}.")
        if period <= self._tl[-1]: raise ValueError(f"period {period} must be greater than the last time {self._tl[-1]}.")
        ret = SegFunc()
        for i in range(times):
            for t,d in self:
                ret.add(t+i*period,d)
        ret._rep = times
        ret._per = period
        return ret
    
    @staticmethod
    def qs(v:'List[SegFunc]') -> 'SegFunc':
        """Quickly sum a list of SegFunc, and return a new SegFunc"""
        ret = SegFunc()
        pq:'PQueue[Tuple[int, int]]' = PQueue()
        sum = 0
        n = len(v)
        for i in range(n):
            if len(v[i]) > 0: pq.push(v[i]._tl[0], (i, 0))
        ctime = -1
        while not pq.empty():
            htime, (idx, prog) = pq.top
            pq.pop()
            if ctime != htime:
                if ctime >= 0:
                    ret.add(ctime, sum)
                ctime = htime
            if prog > 0:
                sum = sum - v[idx]._d[prog - 1] + v[idx]._d[prog]
            else:
                sum += v[idx]._d[prog]
            if prog < len(v[idx]) - 1:
                pq.push(v[idx]._tl[prog + 1], (idx, prog + 1))
        if len(ret._tl) == 0:
            ret.add(0, sum)
        elif ctime >= 0 and ctime != ret._tl[-1]:
            ret.add(ctime, sum)
        return ret
    
    def value_trans(self,func:Callable[[int, float],float])->'SegFunc':
        return SegFunc(self._tl,[func(t, d) for t, d in zip(self._tl,self._d)])

    def __neg__(self)->'SegFunc':
        return SegFunc(self._tl, [-d for d in self._d])
    
    @overload
    def __add__(self, other: float) -> 'SegFunc': ...
    @overload
    def __add__(self, other: int) -> 'SegFunc': ...
    @overload
    def __add__(self, other: ConstFunc) -> 'SegFunc': ...
    @overload
    def __add__(self, other: 'SegFunc') -> 'SegFunc': ...
    @overload
    def __add__(self, other: 'TimeFunc') -> 'TimeFunc': ...

    def __add__(self,other:'FloatLike') -> 'TimeFunc':
        if isinstance(other,(float,int)):
            return SegFunc(self._tl,[d + other for d in self._d])
        elif isinstance(other,ConstFunc):
            return SegFunc(self._tl,[d + other._val for d in self._d])
        elif isinstance(other,SegFunc):
            return SegFunc.qs([self, other])
        else:
            return PlusFunc(self, other)
        
    @overload
    def __sub__(self, other: float) -> 'SegFunc': ...
    @overload
    def __sub__(self, other: int) -> 'SegFunc': ...
    @overload
    def __sub__(self, other: ConstFunc) -> 'SegFunc': ...
    @overload
    def __sub__(self, other: 'SegFunc') -> 'SegFunc': ...
    @overload
    def __sub__(self, other: 'TimeFunc') -> 'TimeFunc': ...

    def __sub__(self, other:'FloatLike') -> 'TimeFunc':
        if isinstance(other,(float,int)):
            return SegFunc(self._tl,[d - other for d in self._d])
        elif isinstance(other,ConstFunc):
            return SegFunc(self._tl,[d - other._val for d in self._d])
        elif isinstance(other,SegFunc):
            return SegFunc.qs([self, -other])
        else:
            return MinusFunc(self, other)
    
    def slice(self, start=-math.inf, end=math.inf)->'SegFunc':
        """Slice the function to the range [start, end]."""
        if end == -1: end = math.inf
        if start > end: start, end = end, start
        assert len(self._tl) > 0, "Cannot slice an empty TimeSeg"
        if self._tl[0] >= start and self._tl[-1] <= end: return self
        ret = SegFunc()
        l = 0 
        while l < len(self._tl) and self._tl[l] < start:
            l += 1
        if l >= len(self._tl):
            ret.add(int(start), self._d[-1])
            return ret
        if l > 0 and self._tl[l] != start:
            ret.add(int(start), self._d[l - 1])
        r = len(self._tl) - 1
        while r >= 0 and self._tl[r] > end:
            r -= 1
        if r < 0: return ret
        if l <= r:
            ret._tl.extend(self._tl[l:r+1])
            ret._d.extend(self._d[l:r+1])
        return ret
    
    def average(self, tl:int, tr:int)->float:
        """Return the average value of the function in the range [tl, tr]."""
        if len(self._d) == 0:
            return 0
        if tl == tr:
            return self.value_at(tl)
        lp = bisect.bisect_left(self._tl, tl)
        rp = bisect.bisect_right(self._tl, tr)
        if lp == len(self._tl):
            return 0
        if rp == 0:
            return 0
        if lp == rp:
            return self._d[lp]
        s = 0
        if self._tl[lp] > tl and lp > 0:
            s = self._d[lp - 1] * (self._tl[lp] - tl)
        for i in range(lp,rp):
            if len(self._tl) <= i+1:
                s += self._d[i] * (tr - self._tl[i])
            else:
                s += self._d[i] * (self._tl[i+1] - self._tl[i])
        s/=(tr-tl)
        return s
    
    def interpolate(self, tl:int, tr:int) -> "SegFunc":
        """
        Interpolate the function in the range [tl, tr] to ensure that the neighboring items are:
            continuous in time, i.e. the time of last item is exactly 1 less than the time of the next item;
            or, if the time is not continuous, the value is the same as the last value.
        """
        ret = SegFunc()
        if len(self._tl) == 0:
            ret.add(tl, 0)
            return ret
        if self._tl[0] > tl:
            ret.add(tl, 0)
        for i in range(len(self)):
            if len(ret) > 0 and self._tl[i] - ret._tl[-1] > 1:
                ret.add(self._tl[i] - 1, self._d[i-1])
            ret.add(self._tl[i], self._d[i])
        if tr!=-1 and len(self._d) > 0 and ret._tl[-1] < tr: 
            ret.add(tr,self._d[-1])
        return ret
    
    def values_at(self, times:'List[int]')->List[float]:
        """Return the values of the function at the given times."""
        if len(self._d) == 0:
            return [0] * len(times)
        ret = []
        i = 0
        for time in times:
            while i < len(self._tl) and self._tl[i] < time:
                i += 1
            if i == len(self._tl):
                ret.append(self._d[-1])
            elif self._tl[i] == time:
                ret.append(self._d[i])
            elif i == 0:
                ret.append(0)
            else:
                ret.append(self._d[i-1])
        return ret

    def min(self)->Tuple[int,float]:
        """Return the time and value of the minimum value in the function"""
        if len(self._d) == 0:
            return 0, 0
        return min(zip(self._tl, self._d), key=lambda x:x[1])
    
    def max(self)->Tuple[int,float]:
        """Return the time and value of the maximum value in the function"""
        if len(self._d) == 0:
            return 0, 0
        return max(zip(self._tl, self._d), key=lambda x:x[1])
    
    def mean(self,tl:int,tr:int)->float:
        """Return the mean value of the function in the range [tl, tr]."""
        if len(self._d) == 0:
            return 0
        if tl == tr:
            return self.value_at(tl)
        lp = bisect.bisect_left(self._tl, tl)
        rp = bisect.bisect_right(self._tl, tr)
        if lp == len(self._tl):
            return 0
        if rp == 0:
            return 0
        if lp == rp:
            return self._d[lp]
        if self._tl[lp] > tl and lp > 0:
            s = self._d[lp - 1] * (self._tl[lp] - tl)
        for i in range(lp,rp):
            if len(self._tl) <= i+1:
                s += self._d[i] * (tr - self._tl[i])
            else:
                s += self._d[i] * (self._tl[i+1] - self._tl[i])
        s/=(tr-tl)
        return s
    
    @property
    def time(self) -> List[int]:
        return self._tl
    
    @property
    def data(self) -> List[float]:
        return self._d
    
    @staticmethod
    def cross_interpolate(segs:'List[SegFunc]')-> 'Tuple[List[int],List[List[float]]]':
        '''
        Extract the time line of all the given SegFunc.
        And then interpolate the values of all the SegFunc with the same time line.
        Return a tuple of time line and the values of all the SegFunc with the same time line.
        '''
        times = set()
        for seg in segs:
            times.update(seg._tl)
        times = sorted(list(times))
        return times, [seg.values_at(times) for seg in segs]


class TimeImplictFunc(TimeFunc):
    '''A special TimeFunc, whose value is only determined by when it is called. Parameter `time` in __call__ is ignored.'''
    def __init__(self,func:'Callable[[],float]'):self._f=func
    def __call__(self,time:int)->float:return self._f()
    def __repr__(self)->str:return f"TimeImplictFunc({self._f})"
    def __str__(self)->str: return repr(self)


class ComFunc(TimeFunc):
    '''Wrap a Python function as a TimeFunc'''
    def __init__(self,func:'Callable[[int],float]'):self._f=func
    def __call__(self,time:int)->float:return self._f(time)
    def __repr__(self)->str:return f"ComFunc({self._f})"
    def __str__(self)->str: return repr(self)


class ManualFunc(TimeFunc):
    '''A const function with a manually changeable value'''
    def __init__(self,init_val:float):self._v=init_val
    def setManual(self,val:float):self._v=val
    def __call__(self,time:int)->float:return self._v
    def __repr__(self)->str:return f"ManualFunc({self._v})"
    def __str__(self)->str: return str(self._v)+"(Manual)"

def __calc_c0(f1:'Union[ConstFunc,float]',f2:float,op:_Oper)->float:
    if isinstance(f1,float): return op(f1,f2)
    elif isinstance(f1,ConstFunc): return op(f1._val,f2)
    else: raise TypeError(f1)

def __calc_c1(f1:SegFunc,f2:float,op:_Oper)->SegFunc:
    return SegFunc(f1._tl,[op(d,f2) for d in f1._d])

def __calc_c2(f1:TimeImplictFunc,f2:float,op:_Oper)->TimeImplictFunc:
    return TimeImplictFunc(lambda: op(f1._f(),f2))

def quicksum(funcs:Iterable[TimeFunc])->TimeFunc:
    ret = list(funcs)
    if len(ret)==0: return ConstFunc(0)
    consts = []
    segs = []
    others = []
    for f in ret:
        if isinstance(f,ConstFunc): consts.append(f._val)
        elif isinstance(f,SegFunc): segs.append(f)
        else: others.append(f)
    if len(others)==0:
        if len(segs)==0: return ConstFunc(sum(consts))
        else: return SegFunc.qs(segs) + sum(consts)
    if len(segs)==0 and len(consts)==0:
        return QuickSumFunc(others)
    elif len(segs)==0:
        others.append(ConstFunc(sum(consts)))
        return QuickSumFunc(others)
    elif len(consts)==0:
        others.append(SegFunc.qs(segs))
        return QuickSumFunc(others)
    else:
        s = SegFunc.qs(segs) + sum(consts)
        others.append(s)
        return QuickSumFunc(others)

def quickmul(funcs:Iterable[TimeFunc])->TimeFunc:
    ret = list(funcs)
    if len(ret)==0: return ConstFunc(1)
    if len(ret)==1: return ret[0]
    if len(ret)==2: return MulFunc(ret[0],ret[1])
    return QuickMulFunc(ret)

def calcFunc(f1:FloatLike,f2:FloatLike,op:str)->TimeFunc:
    _op = _oper_trans[op]
    if isinstance(f2,ConstFunc): f2=f2._val
    if isinstance(f2,(float,int)):
        if isinstance(f1,(ConstFunc,float,int)): return ConstFunc(__calc_c0(f1,f2,_op))
        elif isinstance(f1,SegFunc): return __calc_c1(f1,f2,_op)
        elif isinstance(f1,TimeImplictFunc): return __calc_c2(f1,f2,_op)
        else: f2 = ConstFunc(f2)
    if isinstance(f1,(float,int)): f1 = ConstFunc(f1)
    if isinstance(f1,ConstFunc) and op in ['+','*']:
        if isinstance(f2,SegFunc): return __calc_c1(f2,f1._val,_op)
        elif isinstance(f2,TimeImplictFunc): return __calc_c2(f2,f1._val,_op)
    assert isinstance(f1,TimeFunc) and isinstance(f2,TimeFunc)
    if op=='+': return PlusFunc(f1,f2)
    elif op=='-': return MinusFunc(f1,f2)
    elif op=='*': return MulFunc(f1,f2)
    elif op=='/': return TrueDivFunc(f1,f2)
    elif op=='//': return FloorDivFunc(f1,f2)
    else: raise ValueError(op)

def makeFunc(time_line:'List[int]',data:list)->TimeFunc:
    '''Make SegFunc or ConstFunc from time_line and data'''
    if len(time_line)!=len(data):
        raise ValueError(f"Time line length {len(time_line)} is not equal to data length {len(data)}.")
    if len(data)==1: return ConstFunc(data[0])
    else: return SegFunc(time_line,data)


__all__ = [
    "FloatLike", "quicksum", "quickmul", "calcFunc", "makeFunc",
    "TimeFunc", "OverrideFunc", "ConstFunc", "TimeImplictFunc", "ComFunc", "ManualFunc", "SegFunc",
    "PlusFunc", "QuickSumFunc", "MinusFunc", "MulFunc", "QuickMulFunc", "TrueDivFunc", "FloorDivFunc"
]