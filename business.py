# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 11:06:41 2021

@author: Tsai, Mu-Cheng
"""

import pandas as pd
import numpy as np
from ._tool import *
    
"""
normal index for business
"""
class business:

    def labelProportion(df:pd.DataFrame, label:str, _items:list(), _tittle:str = "Percentage", precision:int = 2) -> float:
        """
        proportional index
        df: data
        label: feature
        _items: conditions is in label
        _tittle: name of the index
        precision: precision
        """
        # filter - isin label-items
        items_filter = df[label].map(lambda x: _labelcheck(x, _items))
        # get limit-df without label-items
        limit_df = df[~items_filter]
        # get limit-rate
        limit_rate = _rate(limit_df.shape[0], df.shape[0])
        limit_rate = np.around(100 * limit_rate, precision)
        print("{0}: {1}%".format(_tittle, limit_rate))
        return limit_rate
        
    def Frequency(df = None) -> np.dtype:
        """
        Repurchase cycle function
        """
        df = None or df
        frequency = np.nan
        try:
            feature = featureCatch(df)
            frequency = len(df[feature].unique())
        except Exception as ex:
            print(ex)
        return frequency

    def Recencydate(df = None) -> np.dtype:
        """
        Repurchase Recency function
        """
        df = None or df
        recencyday = np.nan
        try:
            feature = featureCatch(df)
            recencyday = pd.to_datetime(df[feature]).max()
        except Exception as ex:
            print(ex)
        return recencyday
    
    def Recency(df = None, to_date: str = 'today') -> np.dtype:
        """
        Days between date and today 
        """
        df = None or df
        recencyday = np.nan
        timediff = np.nan
        try:
            feature = featureCatch(df)
            recencyday = pd.to_datetime(df[feature]).max()
            nowday = pd.to_datetime(to_date)
            timediff = int((nowday - recencyday).days)
        except Exception as ex:
            print(ex)
        return timediff
    

    def Term(df = None) -> np.dtype:
        """
        Days between date and today 
        """
        df = None or df
        diffs = []
        term = np.nan
        try:
            feature = featureCatch(df)
            timediff = df[[feature]].sort_values(feature)
            startday = pd.to_datetime(timediff[feature].iloc[0])
            for orderdate in timediff.iloc[1: , :][feature]:
                lastday = pd.to_datetime(orderdate)
                diff = (lastday - startday).days
                if diff != 0:# 同天表視為同次購買，不計入
                    diffs.append(diff) 
                startday = lastday
            dftmp = pd.DataFrame(diffs)
            term =  int(dftmp.mean().values[0])
        except Exception as ex:
            #print(ex)
            term = 0
        return term