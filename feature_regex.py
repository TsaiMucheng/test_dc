# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 16:54:37 2021

@author: Tsai, Mu-Cheng
"""

import numpy as np
import pandas as pd
from ._tool import *
from .statistics import *
from .business import *
from .geoset import *

# Model
class filterModel:
    def __init__(self):
        self.Match = None
        self.UnMatch = None
        
"""
Calculate index by _call function
"""
class indexCalculation:
    def __init__(self, leader: str, _call: object, features: list(), index = None, *args, **kwargs):
        __index = 'index'
        index = None or index
        self.leader = leader
        self.call = _call
        self.features = features
        self.callvar = dymModel(*args, **kwargs)
        if index != None:
            setattr(self, __index, index)
        
        #if not callable(self.call):
        #    raise TypeError('{0} object is not callable!'.format(self.call.__name__))

"""
To find which feature to handle in cell of the Dataframe  
with regular pattern.  

default pattern: [a-zA-Z\u4e00-\u9fa5]  

While match to pattern:  
return df_filter(*).Match -> list()  
       df_filter(*).UnMatch -> list()  
"""
class df_filter(filterModel):
    def __init__(self, df_table: pd.DataFrame, 
                 pattern = None , 
                 notNa = True, 
                 col_assign = []):
        super().__init__()
        pattern = default2gived(pattern, '[a-zA-Z\u4e00-\u9fa5]')
        col_assign = [] or col_assign
        cols = list(df_table.columns)
        
        # cols assign checks
        if (len(col_assign) > 0) and False in [c in cols for c in col_assign]:
            outcols = ', '.join(inter_list(cols, col_assign))
            raise ValueError('[{0}] is not in columns of the dataframe!'.format(outcols))
        
        df_assign = df_table[col_assign].copy() if (len(col_assign) > 0) else df_table       
        self.truth = {k: np.nan for k, v in df_assign.items()}    
        
        # condition 1: cell match to pattern in string type
        mask = lambda col: df_assign[[col]].apply(
            lambda x: x.apply(str).str.contains(
                pattern,
                regex = True
            )
        ).any(axis=1)
        
        # condition 2: cell not be nan
        nafiltter = lambda col: df_assign[col].notna()
        
        # excute series
        condition = lambda col: (mask(col) & nafiltter(col)) if notNa else mask(col)
        lenscheck = lambda col: df_assign[condition(col)][[col]].shape[0] > 0
        updateitems = {
            key: lenscheck(key) for key in self.truth.keys()
        }
        
        self.truth.update(updateitems)
        self.Match = [k for k, v in self.truth.items() if v ]
        self.UnMatch = [k for k, v in self.truth.items() if not v ]
    
    """
    Default:    
    key_list: input list()  
    loadlist: self.UnMatch      
    return filterModel()
    """
    def element_inter_list(self, key_list: list(), loadlist: list() = []) -> filterModel():
        loadlist = default2gived(loadlist, self.UnMatch, [])
        _filterModel = filterModel()
        _filterModel.Match = inter_element(loadlist, key_list)
        _filterModel.UnMatch = [ c for c in loadlist if c not in _filterModel.Match]        
        return _filterModel

"""
Sample.

rawdata: data
observation: reference which group by
index_collection: [indexCalculation1, indexCalculation2, indexCalculation3, ...]

pandas.Series.mean/ pandas.Series.mode/ ...
"""
class id_annotation:
    def __init__(self, rawdata: pd.DataFrame, 
                 observation: str, 
                 index_collection: list()):
        self.colerr_exec = lambda col : '[{0}] is not in columns of the dataframe!'.format(col)
        self.iderr_exec = lambda _id, moudle_name : '[{0}] is not a valid index in {1}!'.format(_id, moudle_name)
        self.__calerr_exec = lambda _cal, moudle_name : '[{0}] is not a valid function in {1}!'.format(_cal, moudle_name)
        
        ### Error proofing mechanism
        # Check if rawdata have the special column
        if observation not in rawdata.columns:
            raise ValueError(self.colerr_exec(observation))
            
        # observation data name
        self.observation = observation
        
        # observation data collection
        self.observars = list(rawdata[[observation]].drop_duplicates().dropna()[observation])
        
        for _indexCal in index_collection:
            # Check if _indexCal method is indexCalculation type
            if not isinstance(type(_indexCal), type(indexCalculation)):
                raise TypeError(self.iderr_exec(_indexCal.__name__, indexCalculation.__name__))
            # Check if rawdata have the features
            if len(inter_list(_indexCal.features, rawdata.columns)) == 0:
                raise ValueError(self.colerr_exec(', '.join(_indexCal.features)))
        self.index_collection = index_collection
        
        # group instance collection
        self.gpdata = rawdata.copy().groupby(self.observation)
        
        self.report = pd.DataFrame.empty
    
    """
    Exception handle:
        have no observation to group by
    Prevent case - observation not in features
    """
    def col_exec(self, cols: list()) -> list():
        collist = cols.copy()
        if self.observation not in collist: 
            collist.append(self.observation)
        return collist
        
    """
    Source test
    Execute all index for assign features with ass_features
    """
    def agg_exec(self, obser_df: pd.DataFrame, 
                   _indexCal: indexCalculation) -> pd.DataFrame:
        __index = 'index'
        # obser_df.reset_index(inplace=True) 
        ass_features = self.col_exec(_indexCal.features)
        _index_df = obser_df[ass_features]
        
        #_index_df.reset_index(drop=True, inplace=True)
        
        index = getattr(_indexCal, __index)
        
        # Basic index function with pandas or numpy
        if not hasattr(_indexCal, __index):
            _errmsg = '{0} is not a valid attribute in {1}!'.format(__index, _indexCal.__name__)
            raise ValueError(_errmsg)
            
        _aggExec = aggExec(
            _index_df.copy(), 
            self.observation
        )
        
        index_df = _aggExec.describe(
            _indexCal.call, 
            index,                         
            *_indexCal.callvar.getargs(), 
            **_indexCal.callvar.getkwargs()
        )
        #index_df.reset_index(inplace=True) 
        _columns = {c: (c+'_'+index) for c in ass_features}
        index_df.rename(columns = _columns, inplace = True)
        return index_df
    
    def series_exec(self, obser_df: pd.DataFrame, 
                   _indexCal: indexCalculation) -> pd.DataFrame:
        __index = 'index'
        # obser_df.reset_index(inplace=True) 
        ass_features = self.col_exec(_indexCal.features)
        _index_df = obser_df[ass_features]
        index = getattr(_indexCal, __index)
        
        # Basic index function with pandas or numpy
        if not hasattr(_indexCal, __index):
            _errmsg = '{0} is not a valid attribute in {1}!'.format(__index, _indexCal.__name__)
            raise ValueError(_errmsg)
        
        _seriesExec = seriesExec(
            _index_df.copy(), 
            self.observation
        )
        
        index_df = _seriesExec.apply(
            _indexCal.call,
            index,
            *_indexCal.callvar.getargs(), 
            **_indexCal.callvar.getkwargs()
        )
        #index_df.reset_index(inplace=True) 
        _columns = {c: (c+'_'+index) for c in ass_features}
        index_df.rename(columns = _columns, inplace = True)
        
        return index_df

    """
    Execute index features dataframe
    in index_collection-items, 
    and combine all dataframe 
    with the same observation.
    return Each observation dataframe
    """
    def obser_row(self, observar: str) -> pd.DataFrame:
        obser_row_df = pd.DataFrame.empty
        
        # set all index dataframe as empty
        for i, _indexCal in enumerate(self.index_collection):
            # _indexCal.call.__name__ + 
            locals()[(_indexCal.index + '_df' + str(i))] = pd.DataFrame.empty
        
        df_lst = list()
        
        # get group from group instance collection
        obser_df = self.gpdata.get_group(observar)
        
        """
        obser_df have multiple rows to excute the indexs 
        for each feature. 
        
        Indexs refer to index_collection.keys()
        
        Column-collection is selected from index_collection.values()
        
        Represent to one row
        """
        for i, _indexCal in enumerate(self.index_collection):
            try:
                _function = '{0}_exec'.format(_indexCal.leader)
                # _indexCal.call.__name__ + 
                locals()[(_indexCal.index + '_df' + str(i))] = reflector( 
                    self, 
                    _function, 
                    None, 
                    obser_df = obser_df, 
                    _indexCal = _indexCal
                )
                df_lst.append(locals()[(_indexCal.index + '_df' + str(i))])                
            except Exception as ex:
                print(ex)
        # combine to one row
        try:
            obser_row_df = pd.concat(df_lst, axis = 1)
        except Exception as ex:
            print(ex)
        # obser_row_df.reset_index(inplace=True)
        return obser_row_df
    
    """
    raw_fileName: file name of the output file(*.csv)
    num: how many rows would you like to excute
    encoding: encode
    output: if you would like to output as *.csv
    """
    def static_all(self, raw_fileName: str = None, num: int = 0, encoding: str = 'utf_8_sig', output: bool = True):
        raw_fileName = None or raw_fileName
        results = pd.DataFrame.empty        
        num = 0 or num
        
        for i, observar in enumerate(self.observars):          
            obserDf = self.obser_row(observar)
            if i == 0:
                results = obserDf.copy()
            else:
                # combine to multiple rows for each observation data
                try:
                    results = pd.concat([results, obserDf], axis = 0, verify_integrity = True)
                except Exception as ex:
                    print(ex)
                    _obj = dymModel(
                        main_DataFrame = results,
                        concat_DataFrame = obserDf,
                        rank = i,
                        axis = 0
                    )
                    return _obj
            if num != 0 and i == (num - 1):
                break
            
        #results.reset_index(inplace=True)
        
        if output:
            _raw_fn_top = '{0}_Gpby_{1}_{2}.csv'.format(raw_fileName, self.observation, num)
            _raw_fn = '{0}_Gpby_{1}.csv'.format(raw_fileName, self.observation)
            _raw_fileName = _raw_fn if num == 0 else _raw_fn_top
            results.to_csv(_raw_fileName, index = True, encoding = encoding)
            
        self.report = results
        return results

    def AppendFeature(self, ref: pd.DataFrame):
        reffeats = list(c for c in ref.columns)
        xlst = cross_list(self.observars, reffeats)
        msg = ','.join(xlst)
        print('Appending features...{0}'.format(msg))
        if not self.observation in ref.columns:            
            raise Exception('Reference Dataframe have no column {0}'.format(self.observation))
        if len(xlst) == 0:            
            raise Exception('Reference Dataframe have no new column to append!')
            
        
        
        
        