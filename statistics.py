# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 11:28:37 2021

@author: Tsai, Mu-Cheng
"""
import numpy as np
import pandas as pd
from ._tool import *

"""
Call series method
"""
class seriesExec:
    def __init__(self, data: pd.DataFrame, observation = None):
        # print('Describe Method: pandas.Series, numpy, ... etc.')
        
        self.data = data
        self.observation = None or observation
        
        self.gpdata = self.data.groupby(self.data[self.observation])
        
        cols = list(c for c in self.data.columns)
        self._features = cross_list(cols, self.observation)
        self.__iderr_exec = lambda _id, moudle_name : '[{0}] is not a valid index in {1}!'.format(_id, moudle_name)
    
    def apply(self, method: object, index: str, *args, **kwargs):
        instance = reflector(
            moudle = method, 
            attr = index 
        )
        index_df = None
        series = self.gpdata.apply(instance , *args, **kwargs)
        #print('series: {0}'.format(series))
        index_df = pd.DataFrame(series)
        #print('series: {0}'.format(index_df))
        _columns = {i: (c+'_'+index) for i, c in enumerate(self._features)}
        index_df.rename(columns = _columns, inplace = True)
        
        #index_df.reset_index(inplace=True)
        return index_df

"""
Call pandas method
"""
class aggExec:
    def __init__(self, data: pd.DataFrame, observation = None):
        # print('Describe Method: pandas.Series, numpy, ... etc.')
        
        self.data = data
        self.observation = None or observation
        
        self.gpdata = self.data.groupby(self.observation)
        
        self.__iderr_exec = lambda _id, moudle_name : '[{0}] is not a valid index in {1}!'.format(_id, moudle_name)
        
    def describe(self, method: object, index: str, *args, **kwargs) -> pd.DataFrame:
        _index = index.lower()
        errmsg = self.__iderr_exec(_index, method.__name__)        
        index_func = reflector(moudle = method, attr = _index, _errmsg = errmsg, *args, **kwargs)
        index_df = self.gpdata.agg(index_func)
        #print(index_df)
        # _columns = {c: (c+'_'+index) for c in index_df.columns}
        # index_df.rename(columns = _columns, inplace = True)
        return index_df
        
    def pdSeries(self, index: str)->pd.DataFrame:
        index_df = self.describe(index, pd.Series)
        return index_df
    
    def npignan(self, index: str)->pd.DataFrame:        
        index_df = self.describe(index, np)
        return index_df

class sumSquares:
    def __init__(self, df:pd.DataFrame, features:list(), name = 'sumSquares'):
        self.df = df
        self.features = features
        self._name = name
        self._featuresLst = []
        self._sumSquares = []
        self._ssdf = pd.DataFrame
        
    def featuresLst(self)->list():
        result = []
        df = self.df
        features = self.features
        for i in range(0, df.shape[0]):
            l = list(c for c in df[features].iloc[i,:])
            result.append(l)
        self._featuresLst = result
        return result
    
    def sumSquare(self, features):
        return np.sum(np.square(features))    
    
    def DataFrame(self) -> pd.DataFrame:
        df = self.df
        features = self.features
        _featuresLst = self.featuresLst()
        ssf = lambda x : np.sum(np.square(list(c for c in x)))
        df[self._name] = df[features].apply((lambda x: ssf(x)), axis = 1)
        self._ssdf = df
        return self._ssdf
    
    def Series(self) -> pd.Series:
        _featuresLst = self.featuresLst()
        _sumSquares = list(map(self.sumSquare, _featuresLst))
        self._sumSquares = _sumSquares
        return pd.Series(_sumSquares)

"""
condition that more than (mean +- stds * 3)
"""
def stds(group: pd.Series, coefficient: int):
    stds = np.abs(group - group.mean()) > coefficient * group.std()
    return stds
    
"""
replace stds * coefficient as np.nan

Example.
    series that more than (mean +- stds * 3)
    are error replaced as np.nan
"""
def errorshooting(group: pd.Series, coefficient: int) -> pd.Series:
    group[np.abs(group - group.mean()) > coefficient * group.std()] = np.nan
    return group