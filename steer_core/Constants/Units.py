"""
Unit conversion constants and functions.

This module provides consistent unit handling across the codebase.
All conversions are defined as constants or pure functions.

IMPORTANT: Always use these functions/constants for unit conversions.
           Never use raw multipliers like /1000 or *1000 directly.

Categories:
    - Length/Mass
    - Time
    - Power/Energy
    - Pressure
    - Temperature
    - Volume
    - Currency
"""

import math
from typing import Union


# =============================================================================
# LENGTH AND MASS UNITS
# =============================================================================

# Length units
KG_TO_G = 1e3
KG_TO_T = 1e-3
T_TO_KG = 1e3
G_TO_KG = 1e-3
T_TO_MT = 1e-6      # tonnes to megatonnes (million tonnes)
MT_TO_T = 1e6       # megatonnes to tonnes

KMOL_TO_MOL = 1e3  
MOL_TO_KMOL = 1e-3
M_TO_CM = 1e2
CM_TO_M = 1e-2
M_TO_MM = 1e3
MM_TO_M = 1e-3
M_TO_DM = 1e1
DM_TO_M = 1e-1
MG_TO_KG = 1e-6
KG_TO_MG = 1e6
M_TO_UM = 1e6
UM_TO_M = 1e-6
MM_TO_CM = 1e-1
CM_TO_MM = 1e1
UM_TO_MM = 1e-3
mG_TO_G = 1e-3
G_TO_mG = 1e3
CM_TO_UM = 1e4
UM_TO_CM = 1e-4



# Current units
A_TO_mA = 1e3
mA_TO_A = 1e-3


# =============================================================================
# TIME UNITS
# =============================================================================

S_TO_H = 1 / 3600
H_TO_S = 3600
S_TO_MIN = 1 / 60
MIN_TO_S = 60
S_TO_Y = 1 / (3600 * 24 * 365)
Y_TO_S = 3600 * 24 * 365

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
SECONDS_PER_HOUR = 3600
HOURS_PER_DAY = 24
DAYS_PER_YEAR = 365
HOURS_PER_YEAR = 8760
SECONDS_PER_YEAR = SECONDS_PER_HOUR * HOURS_PER_YEAR
SECONDS_PER_DAY = SECONDS_PER_HOUR * HOURS_PER_DAY


# =============================================================================
# POWER UNITS
# =============================================================================

W_TO_KW = 1e-3
KW_TO_W = 1e3
KW_TO_MW = 1e-3
MW_TO_KW = 1e3


def mw_to_kw(power_mw: float) -> float:
    """Convert megawatts to kilowatts."""
    return power_mw * MW_TO_KW


def kw_to_mw(power_kw: float) -> float:
    """Convert kilowatts to megawatts."""
    return power_kw * KW_TO_MW


def w_to_kw(power_w: float) -> float:
    """Convert watts to kilowatts."""
    return power_w * W_TO_KW


def kw_to_w(power_kw: float) -> float:
    """Convert kilowatts to watts."""
    return power_kw * KW_TO_W


def w_to_mw(power_w: float) -> float:
    """Convert watts to megawatts."""
    return power_w * W_TO_KW * KW_TO_MW


# Horsepower conversions
KW_PER_HP = 0.7457
HP_PER_KW = 1.0 / KW_PER_HP


def hp_to_kw(power_hp: float) -> float:
    """Convert horsepower to kilowatts."""
    return power_hp * KW_PER_HP


def kw_to_hp(power_kw: float) -> float:
    """Convert kilowatts to horsepower."""
    return power_kw * HP_PER_KW


# =============================================================================
# ENERGY UNITS
# =============================================================================

J_TO_WH = 1 / 3600

# Energy conversion factors (MW·h to GJ)
MWH_TO_GJ = 3.6  # 1 MW·h = 3600 MJ = 3.6 GJ
GJ_TO_MWH = 1.0 / MWH_TO_GJ  # 1 GJ = 1/3.6 MW·h

# Energy conversion factors (kJ to GJ)
KJ_TO_GJ = 1e-6  # 1 kJ = 0.000001 GJ
GJ_TO_KJ = 1e6   # 1 GJ = 1,000,000 kJ
GJ_TO_MGJ = 1e-6  # GJ to million GJ (megagigajoules)
MGJ_TO_GJ = 1e6   # million GJ to GJ

# Energy conversion factors (J to kJ)
J_TO_KJ = 1e-3      # 1 J = 0.001 kJ
KJ_TO_J = 1e3       # 1 kJ = 1000 J

# Power-energy factors
KW_TO_MJ_PER_HOUR = 3.6  # kW·h to MJ conversion: 1 kW·h = 3600 kJ = 3.6 MJ
KW_PER_KG_TO_MJ_PER_KG = 3.6  # kW/kg = kJ/(kg·s) = 3600 kJ/(kg·h) = 3.6 MJ/kg


def gj_to_mwh(energy_gj: float) -> float:
    """Convert gigajoules to megawatt-hours."""
    return energy_gj * GJ_TO_MWH


def mwh_to_gj(energy_mwh: float) -> float:
    """Convert megawatt-hours to gigajoules."""
    return energy_mwh * MWH_TO_GJ


def gj_per_tonne_to_mwh_per_tonne(specific_energy: float) -> float:
    """Convert GJ/tonne to MWh/tonne."""
    return specific_energy / 3.6


def j_to_kj(energy_j: float) -> float:
    """Convert joules to kilojoules."""
    return energy_j * J_TO_KJ


def kj_to_j(energy_kj: float) -> float:
    """Convert kilojoules to joules."""
    return energy_kj * KJ_TO_J


def kg_kmol_to_kg_mol(mw_kg_kmol: float) -> float:
    """Convert molecular weight from kg/kmol to kg/mol."""
    return mw_kg_kmol * MOL_TO_KMOL


def kg_mol_to_kg_kmol(mw_kg_mol: float) -> float:
    """Convert molecular weight from kg/mol to kg/kmol."""
    return mw_kg_mol * KMOL_TO_MOL


# =============================================================================
# PRESSURE UNITS
# =============================================================================

BAR_TO_PA = 1e5       # bar to Pa conversion factor
PA_TO_BAR = 1e-5      # Pa to bar conversion factor
KPA_TO_PA = 1e3      # kPa to Pa conversion factor
PA_TO_KPA = 1e-3     # Pa to kPa conversion factor


def bar_to_pa(pressure_bar: float) -> float:
    """Convert bar to Pascal."""
    return pressure_bar * BAR_TO_PA


def pa_to_bar(pressure_pa: float) -> float:
    """Convert Pascal to bar."""
    return pressure_pa * PA_TO_BAR


def atm_to_bar(pressure_atm: float) -> float:
    """Convert atmospheres to bar."""
    return pressure_atm * 1.01325


def bar_to_atm(pressure_bar: float) -> float:
    """Convert bar to atmospheres."""
    return pressure_bar / 1.01325


def psi_to_bar(pressure_psi: float) -> float:
    """Convert psi to bar."""
    return pressure_psi * 0.0689476


# =============================================================================
# TEMPERATURE UNITS
# =============================================================================

KELVIN_OFFSET = 273.15  # Celsius to Kelvin offset


def celsius_to_kelvin(temp_c: float) -> float:
    """Convert Celsius to Kelvin."""
    return temp_c + KELVIN_OFFSET


def kelvin_to_celsius(temp_k: float) -> float:
    """Convert Kelvin to Celsius."""
    return temp_k - KELVIN_OFFSET


# =============================================================================
# VOLUME UNITS
# =============================================================================

L_TO_M3 = 1e-3
M3_TO_L = 1e3


def m3_to_l(volume_m3: float) -> float:
    """Convert cubic meters to liters."""
    return volume_m3 * M3_TO_L


def l_to_m3(volume_l: float) -> float:
    """Convert liters to cubic meters."""
    return volume_l * L_TO_M3


def m3_to_gal(volume_m3: float) -> float:
    """Convert cubic meters to US gallons."""
    return volume_m3 * 264.172


# =============================================================================
# AREA UNITS
# =============================================================================

def m2_to_ft2(area_m2: float) -> float:
    """Convert square meters to square feet."""
    return area_m2 * 10.7639


def ft2_to_m2(area_ft2: float) -> float:
    """Convert square feet to square meters."""
    return area_ft2 / 10.7639


# =============================================================================
# FLOW RATE UNITS
# =============================================================================

def m3_s_to_gpm(flow_m3_s: float) -> float:
    """Convert m³/s to gallons per minute."""
    return flow_m3_s * 15850.3


def gpm_to_m3_s(flow_gpm: float) -> float:
    """Convert gallons per minute to m³/s."""
    return flow_gpm / 15850.3


# =============================================================================
# CURRENCY UNITS
# =============================================================================

USD_TO_KUSD = 1e-3          # $ to k$ (thousands)
KUSD_TO_USD = 1e3         # k$ to $
USD_TO_MUSD = 1e-6           # $ to M$ (millions)
MUSD_TO_USD = 1e6            # M$ to $


def usd_to_kusd(cost_usd: float) -> float:
    """Convert dollars to thousands of dollars."""
    return cost_usd * USD_TO_KUSD


def kusd_to_usd(cost_kusd: float) -> float:
    """Convert thousands of dollars to dollars."""
    return cost_kusd * KUSD_TO_USD


def usd_to_musd(cost_usd: float) -> float:
    """Convert dollars to millions of dollars."""
    return cost_usd * USD_TO_MUSD


def musd_to_usd(cost_musd: float) -> float:
    """Convert millions of dollars to dollars."""
    return cost_musd * MUSD_TO_USD


# =============================================================================
# ANGLE UNITS
# =============================================================================

DEG_TO_RAD = 0.017453292519943295
RAD_TO_DEG = 57.29577951308232


# =============================================================================
# PERCENTAGE UNITS
# =============================================================================

PERCENT_TO_FRACTION = 1e-2
FRACTION_TO_PERCENT = 1e2
