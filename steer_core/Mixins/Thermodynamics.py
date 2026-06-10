# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Thermodynamics mixin providing generic phase equilibrium calculations.

This mixin provides reusable thermodynamic functions that can be
composed with material classes.
"""

import math
from steer_core.Constants.Universal import R_GAS


class ThermodynamicsMixin:
    """Mixin providing generic thermodynamic calculation methods."""
    
    @staticmethod
    def calculate_antoine_pressure(T: float, A: float, B: float, C: float) -> float:
        """
        Calculate vapor pressure using Antoine equation.
        
        Equation: log10(P) = A - B / (T + C)
        
        Args:
            T: Temperature (units depend on Antoine coefficients, typically °C or K)
            A, B, C: Antoine coefficients for the substance
            
        Returns:
            Vapor pressure (units depend on Antoine coefficients, typically mmHg or bar)
        """
        return 10 ** (A - B / (T + C))
    
    @staticmethod
    def calculate_antoine_temperature(P: float, A: float, B: float, C: float) -> float:
        """
        Calculate temperature from vapor pressure using inverse Antoine equation.
        
        Args:
            P: Vapor pressure (same units as Antoine coefficients)
            A, B, C: Antoine coefficients for the substance
            
        Returns:
            Temperature (same units as Antoine coefficients)
        """
        log_P = math.log10(P)
        return B / (A - log_P) - C
    
    @staticmethod
    def calculate_ideal_gas_density(P_Pa: float, T_K: float, MW_kg_mol: float) -> float:
        """
        Calculate ideal gas density using ideal gas law.
        
        Args:
            P_Pa: Pressure in Pascals
            T_K: Temperature in Kelvin
            MW_kg_mol: Molecular weight in kg/mol
            
        Returns:
            Density in kg/m³
        """

        return P_Pa * MW_kg_mol / (R_GAS * T_K)
