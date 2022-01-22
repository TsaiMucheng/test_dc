# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 11:06:41 2021

@author: Tsai, Mu-Cheng
"""

import numpy as np
import pandas as pd

import shutil
import os
import pathlib

# na filtter
isNan = lambda x : x!=x

# list intersection
inter_list = lambda _list, _filter: list(filter(lambda x: x in _list, _filter))

cross_list = lambda _list, _filter: list(filter(lambda x: x not in _filter, _list))

# element intersection
inter_element = lambda loadlist, key_list: list(c for c in loadlist if len(inter_list(c, key_list)) > 0)

cross_element = lambda loadlist, key_list: list(c for c in loadlist if len(inter_list(c, key_list)) == 0)

textspliter = lambda sentence, spliter: sentence.split(spliter)

class dymModel:
    def __init__(self, *args, **kwargs):
        if len(args) != 0:
            setattr(self, 'args' , list(ag for ag in args))
        if len(kwargs) != 0:
            for kw, kv in kwargs.items():
                setattr(self, kw , kv)
                
    def getargs(self):
        args = []
        tsmpdict ={k:v for k,v in self.__dict__.items()}
        if 'args' in tsmpdict:
            args = tsmpdict['args']
        return args
        
    def getkwargs(self):
        kwargs = {}
        tsmpdict ={k:v for k,v in self.__dict__.items()}
        if 'args' in tsmpdict:
            tsmpdict.pop('args')
        kwargs = tsmpdict
        return kwargs

"""
reflection
"""
def reflector(moudle: object, attr: str, _errmsg = None, *args, **kwargs) -> object:
    _errmsg = None or _errmsg
    if not hasattr(moudle, attr):
        _errmsg = '{0} is not a valid attribute!'.format(attr) if _errmsg is None else _errmsg
        raise ValueError(_errmsg)
        
    attr_func = getattr(moudle, attr)
        
    if len(kwargs) != 0 or len(args) != 0:
        return attr_func(*args, **kwargs)
    return attr_func

"""
if _1st was gived
return _2rd,
else return varable self
"""
def default2gived(var, _2rd, _1st = None):    
    var = _1st or var
    var = _2rd if var == _1st else var
    return var

"""
return the variable name

Sample.

var_name(variables = variables)
return "variables"
"""
def var_name(**variables):
    return [x for x in variables]
    
"""
var to string
"""
# Force to string
def to_str(var) -> str:
    if type(var) is list:
        return str(var)[1:-1] # list
    if type(var) is np.ndarray:
        try:
            return str(list(var[0]))[1:-1] # numpy 1D array
        except TypeError:
            return str(list(var))[1:-1] # numpy sequence
    return str(var) # everything else

def To64(path):
    import base64
    f=open(path,'rb')
    ls_f=base64.b64encode(f.read())
    f.close()
    return ls_f

"""
source: str or pathlib.WindowsPath
folder: Parent Folder Name
file: file name
"""
def moveParentFolder(source, folder: str, file: str):
    nwd = str(pathlib.Path(source).parent)
    spth = os.path.join(source, file)
    dest = os.path.join(nwd, folder , file)
    return shutil.move(spth, dest)

def featureCatch(df: pd.DataFrame):
    df = None or df
    cols = [c for c in df.columns]
    feature = cols[0]
    if len(cols) > 2: # one is features, the other one is groupy key
        raise Exception('{0} is not the one feature of the data,\n(Maybe 0 or more than 1!)'.format(feature))
    return feature