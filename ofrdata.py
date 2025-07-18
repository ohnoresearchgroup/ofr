# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 13:24:55 2025

@author: peo0005
"""

import pandas as pd
import numpy as np

class OFR_Data():
    def __init__(self, path):
        #import dataframe
        self.path = path
        self.df = pd.read_csv(path, delimiter = "\t")
        
        #convert to datetime
        #self.df['dat'] = pd.to_datetime(self.df['dat'])
        
        #flags for what has been calculated yet
        self.calculated_UV = False
        self.calculated_H2Omr = False
        self.calculated_OHR_ext = False
        self.calculated_OHexp = False

    def calc_UV(self):
        """Convert UV (μW/cm²) to photon flux (photons/cm²/s) at 254 nm"""
        h = 6.626e-34  # J·s
        c = 3.0e8      # m/s
        wl_m = 254e-9  # m
        photon_energy = h * c / wl_m  # J/photon
        power_W_cm2 = self.df['Irradiance'] * 1e-6  # μW/cm² → W/cm²
        self.df['UV_photons'] = power_W_cm2 / photon_energy  # photons/cm²/s
        
        #flag as UV converted
        self.calculated_UV = True
        print("Converted UV to photons/cm^2/s.")

    def calc_h2o_mr(self, pressure_hPa=1013.25):
        """
        Calculate water vapor mixing ratio (unitless) as per Peng et al. (2015)
        """
        T = self.df['Temp']  # °C
        RH = self.df['RH']   # %
        
        # 1. Saturation vapor pressure (hPa), Bolton equation
        e_s = 6.112 * np.exp((17.67 * T) / (T + 243.5))
        # 2. Actual vapor pressure (hPa)
        e = (RH / 100.0) * e_s
        
        # 3. mixing ratio (unitless)
        w = 0.622 * e / (pressure_hPa - e)
        
        self.df['h2o_mr'] = w
        
        #flag as unitless mixing ratio calculated       
        self.calculated_H2Omr = True

        print("Calculated water vapor mixing ratio.")

    def estimate_voc_concentration(self, syringe_rate_μL_hr=2):
        """
        Estimate voc concentration in molecules/cm³ from syringe injection,
        using a fixed OFR flow of 8 L/min.
        """
        NA = 6.022e23  # Avogadro's number
        syringe_rate_mL_s = syringe_rate_μL_hr / 3600 / 1000  # μL/hr → mL/s
        fixed_flow_L_min = 8  # L/min (fixed)
        flow_rate_cm3_s = fixed_flow_L_min * 1000 / 60  # L/min → cm³/s

        # Properties for alpha-pinene
        density = 0.858  # g/mL
        MW = 136.24      # g/mol

        # Properties for toluene
        #density = 0.865  # g/mL
        #MW = 92.14      # g/mol
        
        mass_per_s = syringe_rate_mL_s * density  # g/s
        mol_per_s = mass_per_s / MW               # mol/s
        mol_cm3 = mol_per_s / flow_rate_cm3_s     # mol/cm³
        self.voc_conc = mol_cm3 * NA                   # molecules/cm³
        
        print(f"Estimated alpha-pinene concentration: {self.voc_conc:.2e} molecules/cm³")


    def calc_OHR_ext(self):
        """Assign constant OH reactivity for alpha-pinene""" #modify for other precursors
        rate_constant = 5.0e-11  # cm³/molecule/s for alpha-pinene (update if needed)
        est_conc = self.voc_conc
        if est_conc is None:
            return
        ohr_ext = rate_constant * est_conc
        self.df['calc_OHR_ext'] = ohr_ext
        self.calculated_OHR_ext = True
        print(f"Calculated OHRext: {ohr_ext:.2e} s⁻¹")

    def calc_oh_exp(self,O3in_ppm=14.5):
        
        """Calculate actual OH exposure (molecules·cm⁻³·s)"""
        if not self.calculated_UV or not self.calculated_H2Omr or not self.calculated_OHR_ext:
            print("Please calculate UV, H2O mixing ratio, and OHR_ext first.")
            return

        # 14.5 ppm @ 10 V ozone lamp

        # Convert O3 (ppm) to molecules/cm³ at 298 K
        T_K = self.df['Temp'] + 273.15  # K
        O3in_molec_cm3 = O3in_ppm * 2.46e13 * (298 / T_K)
        self.df['O3in'] = O3in_molec_cm3

        H2O = self.df['h2o_mr'].replace(0, np.nan)  # Now unitless
        UV = self.df['UV_photons'].replace(0, np.nan)
        OHR_ext = self.df['calc_OHR_ext'].replace(0, np.nan)

        # Avoid log of zero or negative
        H2O[H2O <= 0] = np.nan
        UV[UV <= 0] = np.nan
        OHR_ext[OHR_ext <= 0] = np.nan

        logH2O = np.log10(H2O)
        logUV = np.log10(UV)
        logO3_OHR = np.log10(O3in_molec_cm3 / OHR_ext)

        # Peng et al. (2015) OH parameterization equation from equation 12 after correction
        term1 = 15.514
        term2 = 0.79292 * logH2O
        term3 = 0.023076 * (logH2O ** 2)
        term4 = -1.0238 * logUV
        term5 = 0.060786 * (logUV ** 2)
        term6 = -np.log10(1 + np.exp((-0.42602 - logO3_OHR) / 0.39479))

        logOHexp = term1 + term2 + term3 + term4 + term5 + term6
        OHexp = 10 ** logOHexp
        self.df['OHexp_molec_cm3_s'] = OHexp
        self.calculated_OHexp = True
