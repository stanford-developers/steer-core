"""
Constants module for steer-core.

This module provides centralized access to:
- Universal physical constants (R_GAS, PI, GRAVITY, etc.)
- Unit conversion constants and functions
- Thermodynamic properties for gases and fluids

Example usage:
    from steer_core.Constants import R_GAS, CO2, celsius_to_kelvin
    from steer_core.Constants import HOURS_PER_YEAR, MW_TO_KW
"""

# Universal physical constants
from steer_core.Constants.Universal import (
    PI,
    R_GAS,
    R_GAS_J_MOL_K,
    R_GAS_KJ_KMOL_K,
    GRAVITY,
    STANDARD_PRESSURE,
    STANDARD_TEMPERATURE,
    MMHG_PER_PA,
    PA_PER_BAR,
    GPU_TO_SI,
)

# Unit conversion constants
from steer_core.Constants.Units import (
    # Length/Mass
    KG_TO_G, G_TO_KG,
    M_TO_CM, CM_TO_M, M_TO_MM, MM_TO_M, M_TO_UM, UM_TO_M,
    KG_TO_T, T_TO_KG, T_TO_MT, MT_TO_T,
    # Time
    S_TO_H, H_TO_S, S_TO_MIN, MIN_TO_S, S_TO_Y, Y_TO_S,
    SECONDS_PER_MINUTE, MINUTES_PER_HOUR, SECONDS_PER_HOUR,
    HOURS_PER_DAY, DAYS_PER_YEAR, HOURS_PER_YEAR,
    SECONDS_PER_YEAR, SECONDS_PER_DAY,
    # Power
    W_TO_KW, KW_TO_W, KW_TO_MW, MW_TO_KW,
    KW_PER_HP, HP_PER_KW,
    # Energy
    J_TO_WH, MWH_TO_GJ, GJ_TO_MWH, KJ_TO_GJ, GJ_TO_KJ, J_TO_KJ, KJ_TO_J,
    GJ_TO_MGJ, MGJ_TO_GJ,
    KW_TO_MJ_PER_HOUR, KW_PER_KG_TO_MJ_PER_KG,
    # Pressure
    BAR_TO_PA, PA_TO_BAR, KPA_TO_PA, PA_TO_KPA,
    # Temperature
    KELVIN_OFFSET,
    # Volume
    L_TO_M3, M3_TO_L,
    # Currency
    USD_TO_KUSD, KUSD_TO_USD, USD_TO_MUSD, MUSD_TO_USD,
    # Angle
    DEG_TO_RAD, RAD_TO_DEG,
    # Percentage
    PERCENT_TO_FRACTION, FRACTION_TO_PERCENT,
)

# Unit conversion functions
from steer_core.Constants.Units import (
    # Power
    mw_to_kw, kw_to_mw, w_to_kw, kw_to_w, w_to_mw,
    hp_to_kw, kw_to_hp,
    # Energy
    gj_to_mwh, mwh_to_gj, gj_per_tonne_to_mwh_per_tonne,
    j_to_kj, kj_to_j,
    kg_kmol_to_kg_mol, kg_mol_to_kg_kmol,
    # Pressure
    bar_to_pa, pa_to_bar, atm_to_bar, bar_to_atm, psi_to_bar,
    # Temperature
    celsius_to_kelvin, kelvin_to_celsius,
    # Volume
    m3_to_l, l_to_m3, m3_to_gal,
    # Area
    m2_to_ft2, ft2_to_m2,
    # Flow rate
    m3_s_to_gpm, gpm_to_m3_s,
    # Currency
    usd_to_kusd, kusd_to_usd, usd_to_musd, musd_to_usd,
)

# Thermodynamic property classes
from steer_core.Constants.ThermodynamicProperties import (
    CO2,
    N2,
    FlueGas,
    Water, H2O,  # H2O is alias for Water
    Steam,
    NaturalGas,
    MEA,
)

# Thermodynamic functions
from steer_core.Constants.ThermodynamicProperties import (
    antoine_pressure_mmhg,
    antoine_temperature_celsius,
    water_vapor_pressure_pa,
    mea_equilibrium_pressure_pa,
    mea_equilibrium_loading,
    mea_bubble_point_temperature,
)


# Aliases for backward compatibility
GAS_CONSTANT = R_GAS


__all__ = [
    # Universal constants
    "PI", "R_GAS", "R_GAS_J_MOL_K", "R_GAS_KJ_KMOL_K", "GAS_CONSTANT",
    "GRAVITY", "STANDARD_PRESSURE", "STANDARD_TEMPERATURE",
    "MMHG_PER_PA", "PA_PER_BAR", "GPU_TO_SI",
    # Unit conversion constants
    "KG_TO_G", "G_TO_KG", "M_TO_CM", "CM_TO_M", "KG_TO_T", "T_TO_KG", "T_TO_MT", "MT_TO_T",
    "S_TO_H", "H_TO_S", "SECONDS_PER_HOUR", "HOURS_PER_YEAR", "SECONDS_PER_YEAR",
    "W_TO_KW", "KW_TO_W", "KW_TO_MW", "MW_TO_KW",
    "MWH_TO_GJ", "GJ_TO_MWH", "KJ_TO_GJ", "GJ_TO_KJ", "GJ_TO_MGJ", "MGJ_TO_GJ",
    "BAR_TO_PA", "PA_TO_BAR", "KELVIN_OFFSET",
    "L_TO_M3", "M3_TO_L",
    "USD_TO_KUSD", "KUSD_TO_USD", "USD_TO_MUSD", "MUSD_TO_USD",
    # Unit conversion functions
    "mw_to_kw", "kw_to_mw", "w_to_kw", "kw_to_w", "w_to_mw",
    "gj_to_mwh", "mwh_to_gj", "j_to_kj", "kj_to_j",
    "bar_to_pa", "pa_to_bar",
    "celsius_to_kelvin", "kelvin_to_celsius",
    "m3_to_l", "l_to_m3",
    # Thermodynamic classes
    "CO2", "N2", "FlueGas", "Water", "H2O", "Steam", "NaturalGas", "MEA",
    # Thermodynamic functions
    "antoine_pressure_mmhg", "antoine_temperature_celsius",
    "water_vapor_pressure_pa", "mea_equilibrium_pressure_pa",
    "mea_equilibrium_loading", "mea_bubble_point_temperature",
]
