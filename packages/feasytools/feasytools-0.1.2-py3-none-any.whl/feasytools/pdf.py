import random, bisect
from abc import abstractmethod
from enum import IntEnum
from typing import Dict, Optional, Union, TypeVar, Generic
from xml.etree import ElementTree as ET


class PDModel(IntEnum):
    Uniform = 0
    Normal = 1
    Triangular = 2
    Exponential = 3
    LogNormal = 4
    Beta = 5
    Gamma = 6
    Weibull = 7
    LogLogistic = 8


class PDFunc:
    '''Probability Distribution Function'''
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def sample(self) -> Union[float, int]:
        raise NotImplementedError()

    def __call__(self):
        return self.sample()

    def __repr__(self):
        s = []
        for k, v in self.__dict__.items():
            s.append(f"{k}={v}")
        return f"{self.__class__.__name__}({', '.join(s)})"
    

class PDUniform(PDFunc):
    def __init__(self, low: float = 0, high: float = 1, deviation: float = 0):
        self.low = low
        self.high = high
        self.deviation = deviation

    def sample(self):
        return random.uniform(self.low, self.high) + self.deviation


class PDNormal(PDFunc):
    def __init__(self, mean: float = 0, std: float = 1, deviation: float = 0):
        self.mean = mean
        self.std = std
        self.deviation = deviation

    def sample(self):
        return random.normalvariate(self.mean, self.std) + self.deviation


class PDTriangular(PDFunc):
    def __init__(self, low: float = 0, high: float = 1, mode: float = 0.5, deviation: float = 0):
        self.low = low
        self.high = high
        self.mode = mode
        self.deviation = deviation

    def sample(self):
        return random.triangular(self.low, self.high, self.mode) + self.deviation


class PDExponential(PDFunc):
    def __init__(self, lambd: float = 1, deviation: float = 0):
        self.lambd = lambd
        self.deviation = deviation

    def sample(self):
        return random.expovariate(self.lambd) + self.deviation


class PDLogNormal(PDFunc):
    def __init__(self, mean: float = 0, std: float = 1, deviation: float = 0):
        self.mean = mean
        self.std = std
        self.deviation = deviation

    def sample(self):
        return random.lognormvariate(self.mean, self.std) + self.deviation


class PDBeta(PDFunc):
    def __init__(self, alpha: float = 1, beta: float = 1, deviation: float = 0):
        self.alpha = alpha
        self.beta = beta
        self.deviation = deviation

    def sample(self):
        return random.betavariate(self.alpha, self.beta) + self.deviation


class PDGamma(PDFunc):
    def __init__(self, alpha: float = 1, beta: float = 1, deviation: float = 0):
        self.alpha = alpha
        self.beta = beta
        self.deviation = deviation

    def sample(self):
        return random.gammavariate(self.alpha, self.beta) + self.deviation


class PDWeibull(PDFunc):
    def __init__(self, alpha: float = 1, beta: float = 1, deviation: float = 0):
        self.alpha = alpha
        self.beta = beta
        self.deviation = deviation

    def sample(self):
        return random.weibullvariate(self.alpha, self.beta) + self.deviation


class PDLogLogistic(PDFunc):
    def __init__(self, mean: float = 0, std: float = 1, deviation: float = 0):
        self.mean = mean
        self.std = std
        self.deviation = deviation

    def sample(self):
        return random.lognormvariate(self.mean, self.std) + self.deviation


def _float(value: Optional[str]) -> float:
    if value is None:
        raise ValueError("Value cannot be None.")
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Cannot convert {value} to float.")

TV_PDF = TypeVar("TV_PDF", float, int)

class PDDiscrete(PDFunc, Generic[TV_PDF]):
    def __init__(self, values: "list[TV_PDF]", weights: "list[float]", deviation: float = 0):
        self.values = values
        tot_w = sum(weights)
        if tot_w == 0: 
            raise ZeroDivisionError("Sum of weights is zero.")
        self.weights = [w/tot_w for w in weights]
        self.deviation = deviation

    def sample(self) -> TV_PDF:
        return random.choices(self.values, self.weights)[0] + self.deviation # type: ignore

    @staticmethod
    def fromXMLNode(node: ET.Element):
        '''Read a XML node with children of items'''
        values = []
        weights = []
        for n in node:
            assert (
                n.tag == "item"
            ), f"Tags' name must be lower case 'item', not '{n.tag}'."
            values.append(_float(n.get("value")))
            weights.append(_float(n.get("weight")))
        return PDDiscrete(values, weights)
    
    @staticmethod
    def fromCSVFile(file_path: str, has_header: bool = False, type_func = float):
        '''Read a CSV file with two columns: value, weight'''
        values = []
        weights = []
        with open(file_path, "r") as f:
            if has_header:
                f.readline()
            for line in f:
                value, weight = line.strip().split(",")
                values.append(type_func(value))
                weights.append(float(weight))
        return PDDiscrete(values, weights)
    
    @staticmethod
    def fromCSVFileI(file_path: str, has_header: bool = False) -> 'PDDiscrete[int]':
        '''Read a CSV file with two columns: value, weight'''
        return PDDiscrete.fromCSVFile(file_path, has_header, int)
    
    @staticmethod
    def fromCSVFileF(file_path: str, has_header: bool = False) -> 'PDDiscrete[float]':
        '''Read a CSV file with two columns: value, weight'''
        return PDDiscrete.fromCSVFile(file_path, has_header, float)
    

class CDDiscrete(Generic[TV_PDF]):
    '''Cumulative Distribution Function'''
    def __init__(self, pdf: Union[PDDiscrete, str], pdf_file_has_header: bool = False, type_func = float):
        '''
            pdf: PDDiscrete or file path of a PDDiscrete
            pdf_file_has_header: bool, whether the file has header
            type_func: function, the function to convert value from string to the type of values in PDDiscrete, float or int
        '''
        if isinstance(pdf, str):
            pdf = PDDiscrete.fromCSVFile(pdf, pdf_file_has_header, type_func=type_func)
        self.values:"list[TV_PDF]" = pdf.values
        self.cum_weights = pdf.weights
        for i in range(1, len(self.cum_weights)):
            self.cum_weights[i] += self.cum_weights[i-1]
        self.cum_weights[-1] = 1
    
    def sample(self) -> TV_PDF:
        r = random.random()
        return self.values[bisect.bisect_right(self.cum_weights, r)]
        # No Error because cum_weights[-1] = 1, so r < cum_weights[-1]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.values}, {self.cum_weights})"
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.values}, {self.cum_weights})"


def GetPDFuncFromXMLNode(node: ET.Element):
    model = node.get("model")
    if model == "Discrete":
        return PDDiscrete.fromXMLNode(node)
    args = []
    if model == "Normal":
        args.append(_float(node.get("mean")))
        args.append(_float(node.get("std")))
    elif model == "Uniform":
        args.append(_float(node.get("low")))
        args.append(_float(node.get("high")))
    elif model == "Triangular":
        args.append(_float(node.get("low")))
        args.append(_float(node.get("high")))
        args.append(_float(node.get("mode")))
    elif model == "Exponential":
        args.append(_float(node.get("lambda")))
    elif model == "LogNormal":
        args.append(_float(node.get("std")))
        args.append(_float(node.get("mean")))
    elif model == "Beta":
        args.append(_float(node.get("alpha")))
        args.append(_float(node.get("beta")))
    elif model == "Gamma":
        args.append(_float(node.get("alpha")))
        args.append(_float(node.get("beta")))
    elif model == "Weibull":
        args.append(_float(node.get("alpha")))
        args.append(_float(node.get("beta")))
    elif model == "LogLogistic":
        args.append(_float(node.get("mean")))
        args.append(_float(node.get("std")))
    else:
        raise ValueError(f"Unknown probability distribution model {model}")
    return CreatePDFunc(model, *args)


def CreatePDFunc(model: "Union[str, PDModel]", *args, **kwargs):
    if model == PDModel.Uniform or model == "Uniform":
        return PDUniform(*args, **kwargs)
    elif model == PDModel.Normal or model == "Normal":
        return PDNormal(*args, **kwargs)
    elif model == PDModel.Triangular or model == "Triangular":
        return PDTriangular(*args, **kwargs)
    elif model == PDModel.Exponential or model == "Exponential":
        return PDExponential(*args, **kwargs)
    elif model == PDModel.LogNormal or model == "LogNormal":
        return PDLogNormal(*args, **kwargs)
    elif model == PDModel.Beta or model == "Beta":
        return PDBeta(*args, **kwargs)
    elif model == PDModel.Gamma or model == "Gamma":
        return PDGamma(*args, **kwargs)
    elif model == PDModel.Weibull or model == "Weibull":
        return PDWeibull(*args, **kwargs)
    elif model == PDModel.LogLogistic or model == "LogLogistic":
        return PDLogLogistic(*args, **kwargs)
    elif model == "Discrete":
        return PDDiscrete(*args, **kwargs)
    else:
        raise ValueError(f"Unknown probability distribution model {model}")

def CreatePDDiscretesFromCSVbyRow(path:str, has_index_col:bool = True) -> "Dict[Union[str,int], PDDiscrete]":
    '''
    Read a CSV file, whose header row indicates values, and the following columns are the probability weights.
        path: str, the file path
        has_index_col: bool, whether the first column is index column. It means the values and weights start from the second column.
    '''
    pdfs = {}
    with open(path, "r") as f:
        header = f.readline().strip().split(",")
        ncol = len(header)
        values = [float(header[i]) for i in range(1 if has_index_col else 0, ncol)]
        for i, line in enumerate(f):
            line = line.strip().split(",")
            assert len(line) == ncol, f"Line {line} has different length from header {header}"
            weights = [float(line[i]) for i in range(1 if has_index_col else 0, ncol)]
            if has_index_col:
                tag = line[0]
                try:
                    tag = int(tag)
                except:
                    pass
            else:
                tag = i
            pdfs[tag] = PDDiscrete(values, weights)
    return pdfs

__all__ = ["PDModel", "PDFunc", "PDUniform", "PDNormal", "PDTriangular", "PDExponential", 
    "PDLogNormal", "PDGamma", "PDWeibull", "PDLogLogistic", "PDDiscrete", "CDDiscrete", 
    "GetPDFuncFromXMLNode", "CreatePDFunc", "CreatePDDiscretesFromCSVbyRow"]