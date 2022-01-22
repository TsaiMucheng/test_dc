# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 15:04:09 2022

@author: Tsai, Mu-Cheng
"""
import chromedriver_autoinstaller
import time
import numpy as np
from ._tool import *
from .crawler import *
from selenium import webdriver
import requests
from bs4 import BeautifulSoup

class coordinate:
    def __init__(self, chromepth:str = None, wdpth:str = None):
        
        self.url = "http://www.map.com.tw/"
        wdpth = None or wdpth
        chromepth = None or chromepth         
        options = webdriver.ChromeOptions()
        
        # hide mode
        options.add_argument("headless")
        if wdpth == None:
            wdpth = str(chromedriver_autoinstaller.install())
        
        if chromepth != None:
            options.binary_location = str(chromepth) 
        
        self.chromepth = chromepth
        self.wdpth = wdpth
        self.options = options
        
    def Wgs84(self, df, *args, **kwargs) -> np.dtype:
        df = None or df
        _coordinate = np.nan
        try:
            feature = featureCatch(df)
            _mode = df[feature].mode().values[0]
            #print('use {0} to excute...'.format(_mode))
            _coordinate = self._call_wgs84(_mode, *args, **kwargs)
            print('coordinate is: {0}'.format(_coordinate))
        except Exception as ex:
            print(ex)
        return _coordinate
        
    """
    Translate address to wgs84-system
        addr: address
        _interval: waiting time(minutes)
    """
    def _call_wgs84(self, addr:str, _interval:float = 0):
        """
        chrome_options: replace by options
        """
        _interval = 0 or _interval
        browser = webdriver.Chrome(executable_path=self.wdpth, options=self.options)
        browser.get(self.url)
        try:
            search = browser.find_element_by_id("searchWord")
            search.clear()
            search.send_keys(addr)
            
            # wait
            _wait_time = 6
            wait = emuWebdriver(browser, _wait_time)
            locate_btn = browser.find_element_by_xpath("/html/body/form/div[10]/div[2]/img[2]")
            locate_btn.click()            
            
            if _interval != 0:
                time.sleep(_interval)
            _frame_switch = wait.frame_switch("TAG_NAME", "iframe")
            if not _frame_switch:
                raise Exception('Time out after {0} seconds...'.format(_wait_time))
            browser.switch_to.default_content()
            framelist = browser.find_elements_by_tag_name("iframe")
            if len(framelist) < 1:
                print('framelist: {0}'.format(framelist))
            iframe = framelist[1]
            browser.switch_to.frame(iframe)
            
            # wait located finishing
            if _interval != 0:
                time.sleep(_interval)
            coor_btnpth = "/html/body/form/div[4]/table/tbody/tr[3]/td/table/tbody/tr/td[2]"
            coor_btn = wait.element_located("XPATH", coor_btnpth)
            #coor_btn = browser.find_element_by_xpath(coor_btnpth)
            coor_btn.click()
            
            # wait located finishing
            if _interval != 0:
                time.sleep(_interval)
            coorpth = "/html/body/form/div[5]/table/tbody/tr[2]/td"
            coor = wait.element_located("XPATH", coorpth)
            
            #coor = browser.find_element_by_xpath("/html/body/form/div[5]/table/tbody/tr[2]/td")
            coor = coor.text.strip().split(" ")
            lat = coor[-1].split("：")[-1]
            log = coor[0].split("：")[-1]
            _coordinate = (lat, log)
            #print('coordinate is: {0}'.format(_coordinate))
        except Exception as ex:
            print(ex)
            _coordinate = (np.nan, np.nan)
        #print('(lat, log): ({0}, {1})'.format(lat, log))
        finally:
            browser.quit()
        return _coordinate