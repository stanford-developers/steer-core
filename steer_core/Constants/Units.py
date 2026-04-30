# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

# =============================================================================
# MASS UNITS
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

# =============================================================================
# MOLAR UNITS
# =============================================================================
KMOL_TO_MOL = 1e3
MOL_TO_KMOL = 1e-3

# =============================================================================
# LENGTH UNITS
# =============================================================================
M_TO_CM = 1e2
CM_TO_M = 1e-2
M_TO_MM = 1e3
MM_TO_M = 1e-3
M_TO_DM = 1e1
DM_TO_M = 1e-1
MG_TO_KG = 1e-6
KG_TO_MG = 1e6
M_TO_UM = 1e6
MM_TO_UM = 1e3
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
# Cascaded imperial-to-metric mass conversions
LB_TO_T = LB_TO_KG * KG_TO_T

# =============================================================================
# CURRENT UNITS
# =============================================================================
A_TO_mA = 1e3
mA_TO_A = 1e-3

# =============================================================================
# TIME UNITS
# =============================================================================
S_TO_H = 1 / 3600
H_TO_S = 3600
S_TO_MIN = 1 / 60
MIN_TO_S = 60
H_TO_MIN = 60
MIN_TO_H = 1 / 60
S_TO_Y = 1 / (3600 * 24 * 365)
Y_TO_S = 3600 * 24 * 365
H_TO_Y = 1 / 8760
Y_TO_H = 8760
S_TO_D = 1 / (3600 * 24)
D_TO_S = 3600 * 24
H_TO_D = 1 / 24
D_TO_H = 24
H_TO_W = 1 / (24 * 7)
D_TO_W = 1 / 7
W_TO_D = 7
Y_TO_M = 12
D_TO_H = 24
W_TO_D = 7
M_TO_Y = 1 / 12

# Millisecond conversions (used for Plotly datetime axis bin sizing)
S_TO_MS = 1e3
H_TO_MS = H_TO_S * S_TO_MS                   # 3_600_000
D_TO_MS = D_TO_S * S_TO_MS                   # 86_400_000

# Average-based time conversions
AVG_D_TO_MONTH = 12 / 365.25
AVG_D_TO_Y = 1 / 365.25
Y_TO_AVG_D = 365.25
AVG_W_TO_Y = 1 / (365.25 / 7)
AVG_H_TO_Y = 1 / (365.25 * 24)

# =============================================================================
# ENERGY UNITS
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

BTU_TO_J = 1055.05585262
J_TO_BTU = 1 / 1055.05585262
BTU_TO_MMBTU = 1e-6
MMBTU_TO_BTU = 1e6


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
MMHG_TO_PA = 133.322                 # mmHg to Pascal
PA_TO_MMHG = 1.0 / MMHG_TO_PA       # Pascal to mmHg
GPU_TO_SI = 3.35e-10                 # mol/(m²·s·Pa) per GPU (gas permeation unit)

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

UNIT_TO_MILLION = 1e-6
MILLION_TO_UNIT = 1e6

# =============================================================================
# VOLUME UNITS
# =============================================================================
L_TO_M3 = DM_TO_M**3  # Derived from length (1e-3)
M3_TO_L = 1.0 / L_TO_M3
GAL_TO_L = 3.78541
L_TO_GAL = 1 / 3.78541
MMGAL_TO_GAL = 1e-6
GAL_TO_MMGAL = 1e6

# Composite energy conversions
ENERGY_CONVERSION_FACTOR = S_TO_H                               # J/s → Wh
VOLUMETRIC_ENERGY_CONVERSION = S_TO_H / M_TO_DM**3              # J/m³ → Wh/L
NORMALISED_COST_CONVERSION = 1 / (ENERGY_CONVERSION_FACTOR * W_TO_KW)  # → $/kWh





