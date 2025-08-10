from abc import ABC, abstractmethod
import ctypes
from enum import Enum
from io import BufferedIOBase
from typing import Any, Dict, Generic, Iterable, List, Sequence, Tuple, TypeVar, Union

int8 = ctypes.c_char
int16 = ctypes.c_short
int32 = ctypes.c_int
int64 = ctypes.c_longlong

float32 = ctypes.c_float
float64 = ctypes.c_double
float128 = ctypes.c_longdouble

TVal = TypeVar("TVal", int8, int16, int32, int64, float32, float64, float128)

class DTypeEnum(Enum):
    INT8 = int8         # b
    INT16 = int16       # s
    INT32 = int32       # i
    INT64 = int64       # l
    FLOAT32 = float32   # f
    FLOAT64 = float64   # d
    FLOAT128 = float128 # q

def _getDType(dtype: str) -> DTypeEnum:
    return {
        "b": DTypeEnum.INT8,
        "s": DTypeEnum.INT16,
        "i": DTypeEnum.INT32,
        "l": DTypeEnum.INT64,
        "f": DTypeEnum.FLOAT32,
        "d": DTypeEnum.FLOAT64,
        "q": DTypeEnum.FLOAT128
    }[dtype]

def _dTypeToStr(dtype: DTypeEnum) -> str:
    return {
        DTypeEnum.INT8: "b",
        DTypeEnum.INT16: "s",
        DTypeEnum.INT32: "i",
        DTypeEnum.INT64: "l",
        DTypeEnum.FLOAT32: "f",
        DTypeEnum.FLOAT64: "d",
        DTypeEnum.FLOAT128: "q"
    }[dtype]

class Array2D(Generic[TVal]):
    def __init__(self, rows: int, cols: int, dtype:DTypeEnum, buffer:Union[None, memoryview, BufferedIOBase] = None):
        """Initialize a 2D array with given dimensions. Initializes all elements to 0."""
        self._r = rows
        self._c = cols
        self._dtype = dtype
        T = dtype.value * cols * rows
        L = self._r * self._c * ctypes.sizeof(dtype.value)
        if buffer is None:
            self._d = T()
        elif isinstance(buffer, memoryview):
            if len(buffer) != L:
                raise ValueError("Buffer size does not match array size.")
            self._d = T.from_buffer(buffer)
        elif isinstance(buffer, BufferedIOBase):
            self._d = T()
            buffer.readinto(self._d)
        else:
            raise TypeError(f"Buffer must be memoryview, BufferedReader, or None, but {type(buffer)} was given.")
    
    def __getitem__(self, index: Tuple[int, int]) -> TVal:
        return self._d[index[0]][index[1]]
    
    def __setitem__(self, index: Tuple[int, int], value: TVal):
        self._d[index[0]][index[1]] = value
    
    def size(self) -> int:
        """Return the number of elements in the array."""
        return self._r * self._c
    
    def __len__(self) -> int:
        return self._r

    def __iter__(self) -> Iterable[ctypes.Array]:
        return iter(self._d)
    
    @property
    def data(self) -> ctypes.Array:
        return self._d
    
    @property
    def rows(self) -> int:
        return self._r
    
    @property
    def cols(self) -> int:
        return self._c

class LabelArray2D(Array2D[TVal]):
    def __init__(self, rows: int, cols: int, type:DTypeEnum, labels:Iterable[str], buffer:Union[None, memoryview, BufferedIOBase] = None):
        """Initialize a 2D array with given dimensions. Initializes all elements to 0."""
        super().__init__(rows, cols, type, buffer)
        self._labels = {lb: i for i, lb in enumerate(labels)}
        if len(self._labels) != cols:
            raise ValueError("Label size must be equal to #columns.")
    
    def __getitem__(self, index: Tuple[Union[str,int], int]) -> TVal:
        if isinstance(index[0], str):
            return self._d[self._labels[index[0]]][index[1]]
        elif isinstance(index[0], int):
            return self._d[index[0]][index[1]]
        else:
            raise TypeError("Label must be str or int.")
    
    def __setitem__(self, index: Tuple[Union[str,int], int], value: TVal):
        if isinstance(index[0], str):
            self._d[self._labels[index[0]]][index[1]] = value
        elif isinstance(index[0], int):
            self._d[index[0]][index[1]] = value
        else:
            raise TypeError("Label must be str or int.")
    
    @property
    def head(self) -> List[str]:
        return list(self._labels.keys())
    
class Table(ABC, Generic[TVal]):
    @abstractmethod
    def __getitem__(self, index: Tuple[Union[str,int], int]) -> TVal: ...

    @abstractmethod
    def __setitem__(self, index: Tuple[Union[str,int], int], value: TVal): ...

    @abstractmethod
    def __len__(self) -> int: ...
    
    @abstractmethod
    def __iter__(self) -> Iterable[Any]: ...

    @abstractmethod
    def __init__(self, file: str): ...

    @abstractmethod
    def save(self, file: str): ...

    @property
    @abstractmethod
    def head(self) -> List[str]: ...

    @abstractmethod
    def row(self) -> Sequence[TVal]: ...

    @abstractmethod
    def col(self) -> List[TVal]: ...

def _split_string_skip_quotes(s: str) -> List[str]:
    """Split a string by commas, ignoring commas inside double quotes."""
    result = []
    current = []
    in_quotes = False
    for char in s:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            result.append(''.join(current))
            current = []
        else:
            current.append(char)
    result.append(''.join(current))
    return result

class ArrayTable(LabelArray2D, Table):
    def __init__(self, file:str, dtype: DTypeEnum = DTypeEnum.FLOAT32):
        """
        Initialize a table from a file. The file can be in .sdt, .sdt.gz, or .csv format.
        If the file is in .csv format, dtype must be specified.
        """
        file_ = file.lower()
        if file_.endswith(".sdt"):
            buffer = open(file, "rb")
        elif file_.endswith(".sdt.gz"):
            import gzip
            buffer = gzip.open(file, "rb")
        elif file_.endswith(".csv"):
            buffer = None
        else:
            raise ValueError("File format not supported. Supported formats are .sdt, .sdt.gz, and .csv.")
        if buffer is not None:
            hlen = int.from_bytes(buffer.read(4), "little")
            header = buffer.read(hlen).decode("utf-8")
            dtype = _getDType(header[0])
            labels = header[1:].split("|")
            cols = len(labels)
            if file_.endswith(".sdt"):
                cpos = buffer.tell()
                buffer.seek(0, 2)
                rows = (buffer.tell() - cpos) // (ctypes.sizeof(dtype.value) * cols)
                buffer.seek(cpos)
                super().__init__(rows, cols, dtype, labels, buffer)
            else:
                content = buffer.read()
                rows = len(content) // (ctypes.sizeof(dtype.value) * cols)
                super().__init__(rows, cols, dtype, labels, memoryview(content))
            buffer.close()
        else:
            with open(file, "r") as f:
                header = f.readline().rstrip()
                labels = header.split(",")
                cols = len(labels)
                content = f.readlines()
                rows = len(content)
                f.seek(0)
                super().__init__(rows, cols, dtype, labels, None)
                for i, line in enumerate(content):
                    values = _split_string_skip_quotes(line.rstrip())
                    for j, value in enumerate(values):
                        if dtype in [DTypeEnum.INT8, DTypeEnum.INT16, DTypeEnum.INT32, DTypeEnum.INT64]:
                            self._d[i][j] = dtype.value(int(value))
                        else:
                            self._d[i][j] = dtype.value(float(value)) # type: ignore
    
    def save(self, file: str):
        file_ = file.lower()
        if file_.endswith(".sdt"):
            buffer = open(file, "wb")
        elif file_.endswith(".sdt.gz"):
            import gzip
            buffer = gzip.open(file, "wb")
        elif file_.endswith(".csv"):
            buffer = None
        else:
            raise ValueError("File format not supported. Supported formats are .sdt, .sdt.gz, and .csv.")
        if buffer is not None:
            header = f"{_dTypeToStr(self._dtype)}{'|'.join(self.head)}".encode("utf-8")
            header += b" " * ((4 - len(header) % 4) % 4)
            buffer.write(len(header).to_bytes(4, "little"))
            buffer.write(header)
            buffer.write(self._d)
            buffer.close()
        else:
            with open(file, "w") as f:
                f.write(",".join(self.head) + "\n")
                for i in range(self.rows):
                    f.write(",".join(str(self._d[i][j]) for j in range(self.cols)) + "\n")
    
    def row(self, i:int):
        return self._d[i]
    
    def col(self, j:Union[int,str]):
        if isinstance(j, str): j = self._labels[j]
        return [ln[j] for ln in self._d]
    
    def at(self, col_name: str, row_id: int) -> TVal:
        """Get the data at the row with index row_id and the column named col_name"""
        return self._d[row_id][self._labels[col_name]]
            
    def to_dict_of_list(self) -> "Dict[str, List[TVal]]":
        """Convert the table to a dictionary of lists"""
        ret = {}
        for i, h in enumerate(self.head):
            ret[h] = self.col(i)
        return ret

    def to_list_of_dict(self) -> "List[Dict[str,TVal]]":
        """Convert the table to a list of dictionaries"""
        return [{h: r[i] for i, h in enumerate(self.head)} for r in self._d]


class ReadOnlyTable(ArrayTable):
    def __setitem__(self, index, item): raise NotImplementedError


__all__ = [
    "ReadOnlyTable", "ArrayTable", "Table", "DTypeEnum", 
    "int8", "int16", "int32", "int64",
    "float32", "float64", "float128", 
    "TVal", "Array2D", "LabelArray2D"
]