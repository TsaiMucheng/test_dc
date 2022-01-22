# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 11:06:41 2021

@author: Tsai, Mu-Cheng
"""

import time
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import selenium.common.exceptions as emuexceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from ._tool import *

"""
asynchronous crawler
"""        
class emuWebdriver():
    def __init__(self, driver, wait_time = 10):
        self.driver = driver
        self.wait_time = wait_time
        
    """
    reference: class name, tag name, or element name
    elementname: locate element name
    """
    def frame_switch(self, reference, elementname, rank = 1) -> bool:
        waitinstance = ui.WebDriverWait(self.driver, self.wait_time)
        switch_successful = waitinstance.until(
            EC.frame_to_be_available_and_switch_to_it(
                self.driver.find_elements(reflector(By, reference), elementname)[rank]
            )
        )
        return switch_successful
    
    def element_located(self, reference, elementname):
        waitinstance = ui.WebDriverWait(self.driver, self.wait_time)
        element = waitinstance.until(
            EC.presence_of_element_located(
                (reflector(By, reference), elementname)
            )
        )
        print("Located \'{0}\' successfully...".format(elementname))
        return element
    
    def element_located(self, reference, elementname):
        waitinstance = ui.WebDriverWait(self.driver, self.wait_time)
        element = waitinstance.until(
            EC.presence_of_element_located(
                (reflector(By, reference), elementname)
            )
        )
        print("Located \'{0}\' successfully...".format(elementname))
        return element
        
    def click_changed(self, element_xpath, wait_xpath, sleep_time=0):
        waitinstance = ui.WebDriverWait(self.driver, self.wait_time)
        old_element = self.driver.find_element_by_xpath(wait_xpath)
        old_text = old_element.text
        self.driver.find_element_by_xpath(element_xpath).click()
        waitinstance.until(self.element_changed(wait_xpath, old_text, 20))
        time.sleep(sleep_time)
        
    def element_changed(self, element_xpath, old_element_text, timeout_seconds = 10, pause_interval = 1):
        t0 = time.time()
        while time.time() - t0 < timeout_seconds:
            try:
                element = self.driver.find_element_by_xpath(element_xpath)
                if element.text != old_element_text:
                    return True
            except emuexceptions.StaleElementReferenceException:
                return True
            except emuexceptions.NoSuchElementException:
                pass
            time.sleep(pause_interval)
        return False