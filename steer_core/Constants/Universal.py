"""
Universal physical constants.

This module contains fundamental physical constants used across
engineering calculations. All values use SI units.
"""


# =============================================================================
# MATHEMATICAL CONSTANTS
# =============================================================================

PI = 3.14159265358979323846


# =============================================================================
# UNIVERSAL PHYSICAL CONSTANTS
# =============================================================================

R_GAS = 8.314  # J/(mol·K) Universal gas constant

GRAVITY = 9.81  # m/s² - Standard acceleration due to gravity


# =============================================================================
# STANDARD CONDITIONS
# =============================================================================

STANDARD_PRESSURE = 101325.0  # Pa (1 atm)
STANDARD_TEMPERATURE = 273.15  # K


# =============================================================================
# CONVERSION FACTORS FOR SPECIAL UNITS
# =============================================================================

MMHG_PER_PA = 0.00750062  # mmHg per Pascal
PA_PER_BAR = 1e5  # Pascal per bar
GPU_TO_SI = 3.35e-10  # mol/(m²·s·Pa) per GPU (gas permeation unit)

# =============================================================================
# MOLAR MASSES
# =============================================================================
M_G_PER_MOL_NO2 = 46.0055
M_G_PER_MOL_SO2 = 64.0638
MW_G_PER_MOL_CO2 = 44.0095
