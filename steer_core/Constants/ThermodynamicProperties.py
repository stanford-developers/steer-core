"""
Thermodynamic properties for gases and fluids.

This module contains thermodynamic property classes for common gases and fluids
used in process engineering calculations. All values use SI units.

Classes:
    CO2: Carbon dioxide properties
    N2: Nitrogen properties
    FlueGas: Flue gas / air mixture properties
    Water: Water properties
    Steam: Steam properties at various pressures
    NaturalGas: Natural gas properties for combustion calculations
    MEA: Monoethanolamine solvent properties
"""

import math
from typing import Callable


# =============================================================================
# CO2 PROPERTIES
# =============================================================================

class CO2:
    """Carbon dioxide thermodynamic properties.
    
    All molecular weights in kg/mol (SI) with kg/kmol aliases.
    """
    
    # Molecular weight
    MW_KG_KMOL = 44.01  # kg/kmol (same as g/mol)
    MW_KG_MOL = 0.04401  # kg/mol (SI for molar calculations)
    MW_CO2 = 0.04401  # kg/mol (alias for compatibility)
    
    # Antoine equation coefficients for sublimation curve
    # log10(P_mmHg) = A - B / (T_celsius + C)
    # Valid range: approximately -120°C to -60°C
    ANTOINE_A = 9.81
    ANTOINE_B = 1347.79
    ANTOINE_C = 273.0
    
    # Phase change enthalpies
    H_SUBLIMATION_KJ_KG = 571.0  # kJ/kg, solid → gas
    H_FUSION_KJ_KG = 196.0  # kJ/kg, solid → liquid
    
    # Heat capacities
    CP_SOLID_KJ_KG_K = 0.95  # kJ/(kg·K), solid phase
    CP_LIQUID_KJ_KG_K = 2.5  # kJ/(kg·K), liquid phase
    
    # Triple point
    T_TRIPLE_C = -56.6  # °C
    P_TRIPLE_PA = 5.18e5  # Pa
    
    # Typical pipeline pressure
    P_PIPELINE_PA = 150e5  # Pa (150 bar)
    
    # Liquid density
    RHO_LIQUID_KG_M3 = 1100  # kg/m³


# =============================================================================
# NITROGEN PROPERTIES
# =============================================================================

class N2:
    """Nitrogen properties."""
    
    MW_KG_KMOL = 28.01  # kg/kmol
    MW_KG_MOL = 0.02801  # kg/mol
    MW_N2 = 0.02801  # kg/mol (alias for compatibility)


# =============================================================================
# FLUE GAS / AIR PROPERTIES
# =============================================================================

class FlueGas:
    """Flue gas and air properties.
    
    These are typical values for combustion flue gas.
    Exact values depend on fuel composition.
    """
    
    # Average molecular weight (varies with composition)
    MW_AVG_KG_KMOL = 29.0  # kg/kmol, approximate for air-like mixture
    MW_FLUE_GAS = 0.029  # kg/mol (alias for compatibility)
    MW_AIR = 0.02897  # kg/mol (dry air average, alias for compatibility)
    
    # Heat capacity (average for flue gas mixture)
    CP_KJ_KG_K = 1.05  # kJ/(kg·K)
    
    # Density at ambient conditions (~25°C, 1 atm)
    RHO_AMBIENT_KG_M3 = 1.2  # kg/m³
    
    # Ratio of specific heats (Cp/Cv), for air-like mixtures
    GAMMA = 1.4


# =============================================================================
# WATER PROPERTIES
# =============================================================================

class Water:
    """Water thermodynamic properties."""
    
    MW_KG_KMOL = 18.015  # kg/kmol
    MW_KG_MOL = 0.018015  # kg/mol (SI)
    MW_H2O = 0.01802  # kg/mol (alias for compatibility)
    
    # Latent heat of vaporization
    LAMBDA_VAPORIZATION_KJ_KG = 2200.0  # kJ/kg at ~120°C (stripper conditions)
    LAMBDA_H2O_KJ_KG = 2260.0  # kJ/kg at 100°C (latent heat of vaporization)
    
    # Heat capacity
    CP_WATER_KJ_KG_K = 4.18  # kJ/(kg·K) - Specific heat capacity of water
    
    # Density
    DENSITY_KG_M3 = 1000.0  # kg/m³
    RHO_LIQUID_KG_M3 = 1000.0  # kg/m³ (alias)


# Alias for Water
H2O = Water


# =============================================================================
# STEAM PROPERTIES
# =============================================================================

class Steam:
    """Steam thermodynamic properties at various pressures.
    
    Reference: Steam tables (IAPWS-IF97)
    """
    
    # Latent heat of vaporization at different pressures
    # Used for reboiler steam calculations
    LAMBDA_LP_KJ_KG = 2200.0    # kJ/kg at ~2-3 bar (LP steam, ~120-135°C)
    LAMBDA_MP_KJ_KG = 2015.0    # kJ/kg at ~10 bar (MP steam, ~180°C)
    LAMBDA_6BAR_KJ_KG = 2086.0  # kJ/kg at 6 bar saturated (~159°C)
    
    # For energy cost calculations (converting GJ thermal to tonnes steam)
    LAMBDA_LP_GJ_TONNE = 2.2    # GJ/tonne for LP steam (2.2 GJ = 2200 kJ/kg × 1000 kg)
    LAMBDA_6BAR_GJ_TONNE = 2.086  # GJ/tonne at 6 bar


# =============================================================================
# NATURAL GAS PROPERTIES
# =============================================================================

class NaturalGas:
    """Natural gas properties for boiler calculations.
    
    Values are for typical pipeline-quality natural gas (mainly methane).
    """
    
    # Lower Heating Value (net calorific value)
    LHV_MJ_KG = 47.0       # MJ/kg - typical for natural gas
    LHV_GJ_TONNE = 47.0    # GJ/tonne
    LHV_MJ_NM3 = 36.0      # MJ/Nm³ - volumetric basis
    
    # Higher Heating Value (gross calorific value)  
    HHV_MJ_KG = 52.2       # MJ/kg
    HHV_GJ_TONNE = 52.2    # GJ/tonne
    
    # For $/MMBTU to $/GJ conversion
    GJ_PER_MMBTU = 1.055   # 1 MMBTU = 1.055 GJ


# =============================================================================
# MEA SOLVENT PROPERTIES
# =============================================================================

class MEA:
    """Monoethanolamine solvent properties.
    
    Properties for aqueous MEA solution (typically 30 wt%).
    
    References:
        - Weiland et al. (1998): Density and viscosity correlations
        - Amundsen et al. (2009): Physical properties of MEA solutions
    """
    
    MW_KG_KMOL = 61.08  # kg/kmol, pure MEA
    MW_KG_MOL = 0.06108  # kg/mol (SI)
    MW_MEA = 0.06108  # kg/mol (alias for compatibility)
    
    # Heat capacity of 30 wt% MEA solution (temperature-averaged)
    CP_SOLUTION_KJ_KG_K = 3.8  # kJ/(kg·K)
    CP_MEA_30_KJ_KG_K = 3.8  # kJ/(kg·K) (alias for compatibility)
    
    # Density of 30 wt% MEA solution
    RHO_COLD_KG_M3 = 1020  # kg/m³, at absorber conditions (~45°C)
    RHO_HOT_KG_M3 = 950  # kg/m³, at stripper conditions (~120°C)
    RHO_MEA_30_KG_M3 = 1020.0  # kg/m³ at 40°C (alias for compatibility)
    RHO_MEA_30_HOT_KG_M3 = 950.0  # kg/m³ at ~120°C (alias for compatibility)
    
    # Viscosity of 30 wt% MEA solution (Pa·s)
    # Reference: Weiland et al. (1998)
    MU_45C_PA_S = 0.003    # Pa·s at 45°C (absorber conditions)
    MU_120C_PA_S = 0.001   # Pa·s at 120°C (stripper conditions)
    MU_COLD_PA_S = 0.003   # Pa·s at absorber (alias)
    MU_HOT_PA_S = 0.001    # Pa·s at stripper (alias)
    
    # Heat of absorption for CO2 (Kim & Svendsen)
    HEAT_OF_ABSORPTION_J_MOL = 84000.0  # J/mol CO2
    
    @staticmethod
    def viscosity_pa_s(T_celsius: float) -> float:
        """
        Calculate 30 wt% MEA solution viscosity as function of temperature.
        
        Simplified Arrhenius-type correlation fitted to Weiland et al. (1998) data.
        Valid range: 25-130°C
        
        Args:
            T_celsius: Temperature in Celsius
            
        Returns:
            Dynamic viscosity in Pa·s
        """
        # Arrhenius parameters (fitted to MEA 30 wt% data)
        # μ = A × exp(B/T_K)
        A = 2.0e-6  # Pa·s
        B = 2500.0  # K
        T_K = T_celsius + 273.15
        return A * math.exp(B / T_K)
    
    @staticmethod
    def density_kg_m3(T_celsius: float) -> float:
        """
        Calculate 30 wt% MEA solution density as function of temperature.
        
        Linear interpolation based on Weiland et al. (1998) data.
        Valid range: 25-130°C
        
        Args:
            T_celsius: Temperature in Celsius
            
        Returns:
            Density in kg/m³
        """
        # Linear fit: ρ = ρ_ref - α × (T - T_ref)
        rho_ref = 1030.0  # kg/m³ at 25°C
        T_ref = 25.0  # °C
        alpha = 0.7  # kg/m³/°C thermal expansion coefficient
        return rho_ref - alpha * (T_celsius - T_ref)


# =============================================================================
# THERMODYNAMIC FUNCTIONS
# =============================================================================

def antoine_pressure_mmhg(T_celsius: float) -> float:
    """
    Calculate CO2 sublimation pressure using Antoine equation.
    
    Args:
        T_celsius: Temperature in Celsius
        
    Returns:
        Pressure in mmHg
    """
    return 10 ** (CO2.ANTOINE_A - CO2.ANTOINE_B / (T_celsius + CO2.ANTOINE_C))


def antoine_temperature_celsius(P_mmhg: float) -> float:
    """
    Calculate CO2 sublimation temperature from pressure.
    
    Args:
        P_mmhg: Pressure in mmHg
        
    Returns:
        Temperature in Celsius
    """
    log_P = math.log10(P_mmhg)
    return CO2.ANTOINE_B / (CO2.ANTOINE_A - log_P) - CO2.ANTOINE_C


def water_vapor_pressure_pa(T_K: float) -> float:
    """
    Calculate water vapor pressure using Antoine equation.
    
    Args:
        T_K: Temperature in Kelvin
        
    Returns:
        Pressure in Pa
    """
    # NIST Antoine parameters for water
    A, B, C = 5.19621, 1730.63, -39.724
    log10_P_bar = A - B / (T_K + C)
    P_bar = 10**log10_P_bar
    return P_bar * 1e5  # Convert bar to Pa


def mea_equilibrium_pressure_pa(loading: float, T_K: float) -> float:
    """
    Calculate equilibrium partial pressure of CO2 over MEA solution.
    
    Correlation fitted to Hilliard (2008) for 30 wt% MEA data.
    ln(P_CO2 [Pa]) = A + B/T + C*alpha
    
    Valid range: 40-120°C, α=0.1-0.55
    
    Args:
        loading: CO2 loading (mol CO2 / mol MEA)
        T_K: Temperature (Kelvin)
        
    Returns:
        P_star_CO2 (Pa)
    """
    # Keep loading in physical bounds
    alpha = max(0.001, min(0.60, loading))
    
    # Calibrated coefficients (fitted to Hilliard 2008 data)
    A = 24.48
    B = -6882.0
    C = 12.97
    
    ln_p_pa = A + B/T_K + C*alpha
    return math.exp(ln_p_pa)


def mea_equilibrium_loading(P_CO2_Pa: float, T_K: float) -> float:
    """
    Inverse VLE: Calculate equilibrium loading given P_CO2 and T.
    
    Solves ln(P) = A + B/T + C*alpha for alpha.
    
    Args:
        P_CO2_Pa: CO2 partial pressure (Pa)
        T_K: Temperature (Kelvin)
        
    Returns:
        Equilibrium loading (mol CO2 / mol MEA)
    """
    A = 24.48
    B = -6882.0
    C = 12.97
    
    target_ln_p = math.log(max(1.0, P_CO2_Pa))
    
    # Rearrange: alpha = (ln_P - A - B/T) / C
    numerator = target_ln_p - A - B/T_K
    alpha = numerator / C
    
    # Clamp to physical limits
    return max(0.01, min(0.60, alpha))


def mea_bubble_point_temperature(loading: float, P_total_Pa: float) -> float:
    """
    Calculate bubble point temperature for MEA solution.
    
    At bubble point: P_total = P*_CO2 + P*_H2O
    
    Args:
        loading: CO2 loading (mol CO2 / mol MEA)
        P_total_Pa: Total pressure (Pa)
        
    Returns:
        Bubble point temperature (Kelvin)
    """
    # Initial guess: 120°C (typical stripper temperature)
    T_guess_K = 273.15 + 120.0
    
    # Iterate to find bubble point
    for _ in range(20):  # Max 20 iterations
        P_co2_star = mea_equilibrium_pressure_pa(loading, T_guess_K)
        P_h2o_star = water_vapor_pressure_pa(T_guess_K)
        P_total_calc = P_co2_star + P_h2o_star
        
        # Check convergence
        error = abs(P_total_calc - P_total_Pa) / P_total_Pa
        if error < 0.01:  # 1% tolerance
            return T_guess_K
        
        # Adjust temperature
        if P_total_calc > P_total_Pa:
            T_guess_K -= 2.0
        else:
            T_guess_K += 2.0
        
        # Clamp to reasonable range
        T_guess_K = max(273.15 + 80.0, min(273.15 + 140.0, T_guess_K))
    
    return T_guess_K
