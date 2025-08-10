# ArgChecker: A simple tool for parsing command line arguments with type checking and error handling
import sys
from typing import Any, Callable, Dict, Iterable, Optional, Union, overload


class KeyNotSpecifiedError(KeyError):
    def __init__(self, key: str):
        super().__init__(f"'{key}' must be specified.")
        self.key = key


class ArgumentWithoutKeyError(ValueError):
    def __init__(self, val: str):
        super().__init__(f"'{val}' is an argument without key.")
        self.val = val


class ArgChecker:
    ErrorHandler: "Optional[Callable[[Exception],None]]" = None

    @staticmethod
    def __err(err_type: type, data: str):
        if ArgChecker.ErrorHandler is not None:
            ArgChecker.ErrorHandler(err_type(data))
        # If the error handler is not set or does not terminate the program, raise the error directly
        raise err_type(data)

    @staticmethod
    def __cast(v: str) -> "Union[None,bool,int,float,str]":
        if v == "True":
            return True
        if v == "False":
            return False
        if v == "None":
            return None
        try:
            return int(v)
        except:
            pass
        try:
            return float(v)
        except:
            return v.strip('"')

    @staticmethod
    def get_dict(
        params: "Union[str, Iterable[str]]" = sys.argv[1:],
        force_parametric: "list[str]" = [],
    ) -> "Dict[str,Union[str,Any]]":
        """Return the input parameters as a dict"""
        if isinstance(params, str):
            cur_item = ""
            inquote = 0
            new_params: "list[str]" = []
            for c in params:
                if c == " " and inquote == 0:
                    if cur_item != "":
                        new_params.append(cur_item)
                        cur_item = ""
                else:
                    if c == '"' and inquote == 0:
                        inquote = 2
                    elif c == '"' and inquote == 2:
                        inquote = 0
                    elif c == "'" and inquote == 0:
                        inquote = 1
                    elif c == "'" and inquote == 1:
                        inquote = 0
                    else:
                        cur_item += c
            if inquote != 0:
                ArgChecker.__err(ValueError, "Unmatched quote")
            if cur_item != "":
                new_params.append(cur_item)
            params = new_params

        cur_key = None
        force_param = False
        ret: "Dict[str, Any]" = {}
        for v in params:
            if v.startswith("-") and not force_param:
                if cur_key != None:
                    ret[cur_key] = True
                cur_key = v.lstrip("-")
                eq_pos = cur_key.find("=")
                if eq_pos != -1:
                    # If the key contains '=', split it into key and value
                    cur_key, val = cur_key[:eq_pos], cur_key[eq_pos + 1:]
                    ret[cur_key] = ArgChecker.__cast(val)
                    cur_key = None
                else:
                    if cur_key in force_parametric:
                        force_param = True
                    else:
                        force_param = False
            elif cur_key != None:
                ret[cur_key] = ArgChecker.__cast(v)
                cur_key = None
                force_param = False
            else:
                # Argument without key
                ArgChecker.__err(ArgumentWithoutKeyError, v)
        if cur_key != None:
            ret[cur_key] = True
        return ret

    @overload
    def __init__(self, *, force_parametric: "list[str]" = []) -> None: ...

    @overload
    def __init__(self, pars: str, force_parametric: "list[str]" = []) -> None: ...

    @overload
    def __init__(
        self, pars: "Dict[str, Any]", force_parametric: "list[str]" = []
    ) -> None: ...

    def __init__(
        self,
        pars: "Union[None,str,Dict[str,Any]]" = None,
        force_parametric: "list[str]" = [],
    ):
        if pars is None:
            self.__args = ArgChecker.get_dict(force_parametric=force_parametric)
        elif isinstance(pars, str):
            self.__args = ArgChecker.get_dict(pars, force_parametric=force_parametric)
        elif isinstance(pars, dict):
            self.__args = pars
        else:
            raise TypeError(type(pars))

    def pop_bool(self, key: str) -> bool:
        '''
        Pop a boolean value from the argument list. If the key exists, return True; otherwise, return False.
        '''
        if self.__args.pop(key, False):
            return True
        return False
    
    def get_bool(self, key: str) -> bool:
        '''
        Get a boolean value from the argument list.If the key exists, return True; otherwise, return False.
        '''
        val = self.__args.get(key, False)
        if val is None:
            ArgChecker.__err(KeyNotSpecifiedError, key)
        return bool(val)

    def pop_int(self, key: str, default: "Optional[int]" = None) -> int:
        '''
        Pop an integer value from the argument list. If the key does not exist, return the default value.
        If the default value is None, raise an error.
        '''
        val = self.__args.pop(key, default)
        if val is None:
            ArgChecker.__err(KeyNotSpecifiedError, key)
        return int(val)
    
    def get_int(self, key: str, default: "Optional[int]" = None) -> int:
        '''
        Get an integer value from the argument list. If the key does not exist, return the default value.
        If the default value is None, raise an error.
        '''
        val = self.__args.get(key, default)
        if val is None:
            ArgChecker.__err(KeyNotSpecifiedError, key)
        return int(val)
    
    def pop_int_or_none(self, key: str, default: "Optional[int]" = None) -> "Optional[int]":
        '''
        Pop an integer value from the argument list. If the key does not exist, return the default value.
        '''
        val = self.__args.pop(key, default)
        if val is None:
            return None
        return int(val)

    def get_int_or_none(self, key: str, default: "Optional[int]" = None) -> "Optional[int]":
        '''
        Get an integer value from the argument list. If the key does not exist, return the default value.
        '''
        val = self.__args.get(key, default)
        if val is None:
            return None
        return int(val)
    
    def pop_str(self, key: str, default: "Optional[str]" = None) -> str:
        '''
        Pop a string value from the argument list. If the key does not exist, return the default value.
        If the default value is None, raise an error.
        '''
        val = self.__args.pop(key, default)
        if val is None:
            ArgChecker.__err(KeyNotSpecifiedError, key)
        return str(val).strip('"')
    
    def get_str(self, key: str, default: "Optional[str]" = None) -> str:
        '''
        Get a string value from the argument list. If the key does not exist, return the default value.
        If the default value is None, raise an error.
        '''
        val = self.__args.get(key, default)
        if val is None:
            ArgChecker.__err(KeyNotSpecifiedError, key)
        return str(val).strip('"')
    
    def pop_str_or_none(self, key: str, default: "Optional[str]" = None) -> "Optional[str]":
        '''
        Pop a string value from the argument list. If the key does not exist, return the default value.
        '''
        val = self.__args.pop(key, default)
        if val is None:
            return None
        return str(val).strip('"')

    def get_str_or_none(self, key: str, default: "Optional[str]" = None) -> "Optional[str]":
        '''
        Get a string value from the argument list. If the key does not exist, return the default value.
        '''
        val = self.__args.get(key, default)
        if val is None:
            return None
        return str(val).strip('"')
    
    def pop_float(self, key: str, default: "Optional[float]" = None) -> float:
        '''
        Pop a float value from the argument list. If the key does not exist, return the default value.
        If the default value is None, raise an error.
        '''
        val = self.__args.pop(key, default)
        if val is None:
            ArgChecker.__err(KeyNotSpecifiedError, key)
        return float(val)
    
    def get_float(self, key: str, default: "Optional[float]" = None) -> float:
        '''
        Get a float value from the argument list. If the key does not exist, return the default value.
        If the default value is None, raise an error.
        '''
        val = self.__args.get(key, default)
        if val is None:
            ArgChecker.__err(KeyNotSpecifiedError, key)
        return float(val)
    
    def pop_float_or_none(self, key: str, default: "Optional[float]" = None) -> "Optional[float]":
        '''
        Pop a float value from the argument list. If the key does not exist, return the default value.
        '''
        val = self.__args.pop(key, default)
        if val is None:
            return None
        return float(val)

    def get_float_or_none(self, key: str, default: "Optional[float]" = None) -> "Optional[float]":
        '''
        Get a float value from the argument list. If the key does not exist, return the default value.
        '''
        val = self.__args.get(key, default)
        if val is None:
            return None
        return float(val)
    
    def empty(self) -> bool:
        '''
        Return whether the argument list is empty.
        '''
        return len(self.__args) == 0

    def to_dict(self) -> dict:
        '''
        Return the argument list as a dictionary (Shallow copy).
        '''
        return self.__args.copy()
    
    def __contains__(self, key: str) -> bool:
        return key in self.__args
    
    def keys(self):
        return self.__args.keys()

    def values(self):
        return self.__args.values()

    def items(self):
        return self.__args.items()

    def __len__(self) -> int:
        return len(self.__args)

    def __getitem__(self, key: str):
        return self.__args[key]

    def __repr__(self):
        return "ArgChecker<" + repr(self.__args) + ">"

    def __str__(self):
        return str(self.__args)


__all__ = [
    "ArgChecker", "KeyNotSpecifiedError", "ArgumentWithoutKeyError",
]