"""
Unit conversion constants and functions.

This module provides consistent unit handling across the codebase.
All conversions are defined as constants or pure functions.

IMPORTANT: Always use these functions/constants for unit conversions.
           Never use raw multipliers like /1000 or *1000 directly.
"""

import math

# =============================================================================
# LENGTH AND MASS UNITS
# =============================================================================
KG_TO_G = 1e3
KG_TO_T = 1e-3
T_TO_KG = 1e3
G_TO_KG = 1e-3
T_TO_MT = 1e-6      # tonnes to megatonnes
MT_TO_T = 1e6       # megatonnes to tonnes
# Cascaded mass conversions
G_TO_T = G_TO_KG * KG_TO_T  # 1e-6
T_TO_G = T_TO_KG * KG_TO_G  # 1e6

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
LB_TO_KG = 0.453592
KG_TO_LB = 1 / 0.453592
T_TO_SHORT_TON = 1.10231
SHORT_TON_TO_T = 1 / 1.10231
LB_TO_SHORT_TON = 1 / 2000
SHORT_TON_TO_LB = 2000
LB_TO_T = 1 / 2000 * 1/1.10231


# =============================================================================
# TIME UNITS
# =============================================================================
S_TO_H = 1.0 / 3600.0
H_TO_S = 3600.0
MIN_TO_H = 1.0 / 60.0
H_TO_MIN = 60.0
S_TO_MIN = 1.0 / 60.0
MIN_TO_S = 60.0
S_TO_Y = 1.0 / (3600.0 * 24.0 * 365)
Y_TO_S = 3600.0 * 24.0 * 365  

D_TO_H = 24.0
Y_TO_D = 365 
Y_TO_H = Y_TO_D * D_TO_H  # 8760 - Cascaded
H_TO_Y = 1.0 / Y_TO_H     # From origin/dev
D_TO_S = D_TO_H * H_TO_S  # Cascaded

# Legacy aliases for compatibility
SECONDS_PER_MINUTE = MIN_TO_S
MINUTES_PER_HOUR = H_TO_MIN
SECONDS_PER_HOUR = H_TO_S
HOURS_PER_DAY = D_TO_H
DAYS_PER_YEAR = Y_TO_D
HOURS_PER_YEAR = Y_TO_H
SECONDS_PER_YEAR = Y_TO_S
SECONDS_PER_DAY = D_TO_S

# =============================================================================
# POWER & ENERGY UNITS
# =============================================================================
W_TO_KW = 1e-3
KW_TO_W = 1e3
KW_TO_MW = 1e-3
MW_TO_KW = 1e3
# Cascaded power conversions
W_TO_MW = W_TO_KW * KW_TO_MW  # 1e-6
MW_TO_W = MW_TO_KW * KW_TO_W  # 1e6

KW_PER_HP = 0.7457
HP_PER_KW = 1.0 / KW_PER_HP

J_TO_WH = 1.0 / 3600.0
MWH_TO_GJ = 3.6
GJ_TO_MWH = 1.0 / MWH_TO_GJ

KJ_TO_GJ = 1e-6
GJ_TO_KJ = 1e6
GJ_TO_MGJ = 1e-6
MGJ_TO_GJ = 1e6

J_TO_KJ = 1e-3
KJ_TO_J = 1e3
J_TO_GJ = J_TO_KJ * KJ_TO_GJ
GJ_TO_J = GJ_TO_KJ * KJ_TO_J

# =============================================================================
# PRESSURE UNITS
# =============================================================================
BAR_TO_PA = 1e5
PA_TO_BAR = 1e-5
KPA_TO_PA = 1e3
PA_TO_KPA = 1e-3
# Cascaded pressure conversions
BAR_TO_KPA = BAR_TO_PA * PA_TO_KPA  # 1e2
KPA_TO_BAR = KPA_TO_PA * PA_TO_BAR  # 1e-2

# =============================================================================
# TEMPERATURE UNITS
# =============================================================================
K_TO_C = -273.15
C_TO_K = 273.15

# =============================================================================
# VISCOSITY UNITS
# =============================================================================
PA_S_TO_CP = 1e3      # Pascal-seconds to Centipoise
CP_TO_PA_S = 1e-3     # Centipoise to Pascal-seconds

# =============================================================================
# CURRENCY & MISC
# =============================================================================
USD_TO_KUSD = 1e-3
KUSD_TO_USD = 1e3
USD_TO_MUSD = 1e-6
MUSD_TO_USD = 1e6
# Cascaded currency conversions
MUSD_TO_KUSD = MUSD_TO_USD * USD_TO_KUSD  # 1e3
KUSD_TO_MUSD = KUSD_TO_USD * USD_TO_MUSD  # 1e-3

DEG_TO_RAD = 0.017453292519943295
RAD_TO_DEG = 57.29577951308232

PERCENT_TO_FRACTION = 1e-2
FRACTION_TO_PERCENT = 1e2
FRACTION_TO_PPM = 1e6
PPM_TO_FRACTION = 1e-6

# =============================================================================
# VOLUME UNITS
# =============================================================================
L_TO_M3 = DM_TO_M**3  # Derived from length (1e-3)
M3_TO_L = 1.0 / L_TO_M3
GAL_TO_L = 3.78541
L_TO_GAL = 1 / 3.78541
MMGAL_TO_GAL = 1e-6
GAL_TO_MMGAL = 1e6
