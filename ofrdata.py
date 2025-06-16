# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 13:24:55 2025

@author: peo0005
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class OFR_Data():
    def __init__(self,path):
        #import data into dataframe
        self.path = path       
        self.df = pd.read_csv(path, delimiter = "\t")
        
        #turn date into pandas timestamp
        self.df['dat'] = pd.to_datetime(self.df['dat'])
        
        
        #flags for what has been calculated yet
        self.calculated_UV = False
        self.calculated_H2Omr = False
        self.calculate_OHR_ext = False
        self.calculated_OHexp = False
        
        
        
        
        #NOT REAL CODE; update equations with real code
    def calc_UV(self,wl):
        photon_energy = wl * 1       
        self.df['UV'] = self.df['UV']/photon_energy
        
        #flag that UV flux has been calculated
        self.calculated_UV = True
        
        
        
        
        
        
        #NOT REAL CODE; update equation with real code
    def calc_h2o_mr(self):
        self.df['h2o_mr'] = self.df['RH'] * self.df['Temp']
        
        #flag that h2o mixing ratio has been calculated
        self.calculated_H2Omr = True
        
        
        
        
        
        
        #NOT REAL CODE; update equations with real code
    def calc_OHR_ext(self,voc):
        
        if voc == 'toluene':
            rate_constant = 1
        elif voc == 'alpha-pinene':
            rate_constant = 2
        else:
            print("unknown VOC, cannot calculate OHR_ext")
            return
        
        self.df['calc_OHR_ext'] = rate_constant
        
        #flag that OHR_ext has been calculateed
        self.calculated_OHR_ext = True
        
        
        
        
        
        
        
        #NOT REAL CODE; update equation with real code
    def calc_oh_exp(self):
        
        #Check to make sure that each needed parameter has been calculated.
        if self.calculated_UV == False:
            print("Can't calculate OH exposure, haven't calculated UV flux yet.")
            return
        
        if self.calculated_H2Omr == False:
            print("Can't calculate OH exposure; haven't calculated H2O mixing ratio yet.")
            return
        
        if self.calculated_OHR_ext == False:
            print("Can't calculate OH exposure; haven't calculated OHR_ext yet.")
            return
            
        
        
        self.df['calc_OHexp'] = self.df['h2o_mr'] * self.df['UV']
        
        #flag that OHexposure has been calculated
        self.calculated_OHexp = True
    

        
    
