import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Union, overload


class RangeList:
    @staticmethod
    def parse_time(s: str) -> int:
        """hh:mm:ss / str -> int"""
        try:
            return int(s)
        except:
            try:
                h, m, s = s.split(":")
                return int(h) * 3600 + int(m) * 60 + int(s)
            except:
                raise ValueError(f"Invalid time format: {s}. Expected string like 'hh:mm:ss' or convertible to int.")
    @overload
    def __init__(self): ...
    @overload
    def __init__(self, data: "Optional[ET.Element]"): ...
    @overload
    def __init__(self, data: "List[Tuple[int,int]]"): ...
    @overload
    def __init__(
        self, data: "List[Tuple[int,int]]", loop_times: int, loop_period: int
    ): ...

    def __init__(
        self,
        data: "Union[List[Tuple[int,int]], ET.Element, None]" = None,
        loop_times: int = 1,
        loop_period: Optional[int] = None,
    ):
        self.__always_true = False
        if isinstance(data, ET.Element):
            loop_period = int(data.attrib.get("loop_period", 0))
            loop_times = int(data.attrib.get("loop_times", 1))
            assert loop_times >= 1, "Invalid loop_times attribute: must be positive"
            data = [(
                self.parse_time(itm.attrib["btime"]),
                self.parse_time(itm.attrib["etime"]),
            ) for itm in data]
        elif data is None:
            data = []
            self.__always_true = True
        assert loop_times >= 1, "Invalid loop_times attribute: must be positive"
        self.__lp = loop_period
        self.__lt = loop_times
        if loop_times > 1 and len(data) >= 1:
            assert (
                loop_period is not None and
                loop_period > data[-1][1]
            ), f"Loop period {loop_period} must be greater than end time {data[-1][1]}."
            n = len(data)
            for j in range(1, loop_times):
                for i in range(n):
                    if data[i][0] >= data[i][1]:
                        raise ValueError(
                            f"Start time {data[i][0]} is later than end time {data[i][1]}."
                        )
                    data.append(
                        (data[i][0] + loop_period * j, data[i][1] + loop_period * j)
                    )
        self._d: "List[tuple[int,int]]" = data

    def toXML(self, tag: str = "range") -> str:
        return ET.tostring(self.toXMLNode(tag), encoding="unicode")

    def toXMLNode(self, tag: str = "range") -> ET.Element:
        attr: "Dict[str, str]" = {}
        if self.__lp:
            attr["loop_period"] = str(self.__lp)
        if self.__lt:
            attr["loop_times"] = str(self.__lt)
        elem = ET.Element(tag, attr)
        for d in self._d:
            if self.__lp and d[1] > self.__lp:
                break
            elem.append(ET.Element("item", {"btime": str(d[0]), "etime": str(d[1])}))
        return elem

    def __contains__(self, t: int):
        if self.__always_true: return True
        for l, r in self._d:
            if l <= t and t < r:
                return True
        return False

    def __len__(self) -> int:
        return self._d.__len__()

    def __getitem__(self, indices):
        return self._d.__getitem__(indices)

    def __str__(self):
        return str(self._d)

    def __iter__(self):
        return iter(self._d)


__all__ = ["RangeList"]