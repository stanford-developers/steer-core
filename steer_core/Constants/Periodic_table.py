# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

atomic_numbers_to_symbols = {
    1: "H", 2: "He", 3: "Li", 4: "Be", 5: "B", 6: "C", 7: "N", 8: "O", 9: "F", 10: "Ne",
    11: "Na", 12: "Mg", 13: "Al", 14: "Si", 15: "P", 16: "S", 17: "Cl", 18: "Ar", 19: "K", 20: "Ca",
    21: "Sc", 22: "Ti", 23: "V", 24: "Cr", 25: "Mn", 26: "Fe", 27: "Co", 28: "Ni", 29: "Cu", 30: "Zn",
    31: "Ga", 32: "Ge", 33: "As", 34: "Se", 35: "Br", 36: "Kr", 37: "Rb", 38: "Sr", 39: "Y", 40: "Zr",
    41: "Nb", 42: "Mo", 43: "Tc", 44: "Ru", 45: "Rh", 46: "Pd", 47: "Ag", 48: "Cd", 49: "In", 50: "Sn",
    51: "Sb", 52: "Te", 53: "I", 54: "Xe", 55: "Cs", 56: "Ba",
    57: "La", 58: "Ce", 59: "Pr", 60: "Nd", 61: "Pm", 62: "Sm", 63: "Eu", 64: "Gd", 65: "Tb", 66: "Dy",
    67: "Ho", 68: "Er", 69: "Tm", 70: "Yb", 71: "Lu",
    72: "Hf", 73: "Ta", 74: "W", 75: "Re", 76: "Os", 77: "Ir", 78: "Pt", 79: "Au", 80: "Hg",
    81: "Tl", 82: "Pb", 83: "Bi", 84: "Po", 85: "At", 86: "Rn", 87: "Fr", 88: "Ra",
    89: "Ac", 90: "Th", 91: "Pa", 92: "U", 93: "Np", 94: "Pu",
    95: "Am", 96: "Cm", 97: "Bk", 98: "Cf", 99: "Es", 100: "Fm", 101: "Md", 102: "No", 103: "Lr",
    104: "Rf", 105: "Db", 106: "Sg", 107: "Bh", 108: "Hs", 109: "Mt", 110: "Ds", 111: "Rg", 112: "Cn", 113: "Nh",
    114: "Fl", 115: "Mc", 116: "Lv",
    117: "Ts", 118: "Og"
}

atomic_numbers_to_names = {
    1: "Hydrogen", 2: "Helium", 3: "Lithium", 4: "Beryllium", 5: "Boron", 6: "Carbon", 7: "Nitrogen", 8: "Oxygen",
    9: "Fluorine", 10: "Neon", 11: "Sodium", 12: "Magnesium", 13: "Aluminum", 14: "Silicon", 15: "Phosphorus", 16: "Sulfur", 17: "Chlorine", 18: "Argon", 19: "Potassium", 20: "Calcium",
    21: "Scandium", 22: "Titanium", 23: "Vanadium", 24: "Chromium", 25: "Manganese", 26: "Iron", 27: "Cobalt", 28: "Nickel", 29: "Copper", 30: "Zinc",
    31: "Gallium", 32: "Germanium", 33: "Arsenic", 34: "Selenium", 35: "Bromine", 36: "Krypton", 37: "Rubidium", 38: "Strontium", 39: "Yttrium", 40: "Zirconium",
    41: "Niobium", 42: "Molybdenum", 43: "Technetium", 44: "Ruthenium", 45: "Rhodium", 46: "Palladium", 47: "Silver", 48: "Cadmium", 49: "Indium", 50: "Tin",
    51: "Antimony", 52: "Tellurium", 53: "Iodine", 54: "Xenon", 55: "Cesium", 56: "Barium",
    57: "Lanthanum", 58: "Cerium", 59: "Praseodymium", 60: "Neodymium", 61: "Promethium", 62: "Samarium", 63: "Europium", 64: "Gadolinium", 65: "Terbium", 66: "Dysprosium", 67: "Holmium", 68: "Erbium", 69: "Thulium", 70: "Ytterbium",
    71: "Lutetium", 72: "Hafnium", 73: "Tantalum", 74: "Tungsten", 75: "Rhenium", 76: "Osmium", 77: "Iridium", 78: "Platinum", 79: "Gold", 80: "Mercury",
    81: "Thallium", 82: "Lead", 83: "Bismuth", 84: "Polonium", 85: "Astatine", 86: "Radon", 87: "Francium", 88: "Radium",
    89: "Actinium", 90: "Thorium", 91: "Protactinium", 92: "Uranium", 93: "Neptunium", 94: "Plutonium",
    95: "Americium", 96: "Curium", 97: "Berkelium", 98: "Californium", 99: "Einsteinium", 100: "Fermium", 101: "Mendelevium", 102: "Nobelium", 103: "Lawrencium",
    104: "Rutherfordium", 105: "Dubnium", 106: "Seaborgium", 107: "Bohrium", 108: "Hassium", 109: "Meitnerium", 110: "Darmstadtium", 111: "Roentgenium", 112: "Copernicium", 113: "Nihonium",
    114: "Flerovium", 115: "Moscovium", 116: "Livermorium",
    117: "Tennessine", 118: "Oganesson"
}

atomic_numbers_to_masses = {
    1: 1.008, 2: 4.003, 3: 6.940, 4: 9.012, 5: 10.810, 6: 12.011, 7: 14.007, 8: 15.999, 9: 18.998, 10: 20.180, 11: 22.990, 12: 24.305, 13: 26.982, 14: 28.085, 15: 30.974, 16: 32.060, 17: 35.450, 18: 39.948,
    19: 39.098, 20: 40.078, 21: 44.956, 22: 47.867, 23: 50.942, 24: 51.996, 25: 54.938, 26: 55.845, 27: 58.933, 28: 58.693, 29: 63.546, 30: 65.380,
    31: 69.723, 32: 72.630, 33: 74.922, 34: 78.971, 35: 79.904, 36: 83.798, 37: 85.468, 38: 87.620, 39: 88.906, 40: 91.224, 41: 92.906, 42: 95.950, 43: 98.000, 44: 101.070, 45: 102.906, 46: 106.420, 47: 107.868, 48: 112.414, 49: 114.818,
    50: 118.710, 51: 121.760, 52: 127.600, 53: 126.904, 54: 131.293, 55: 132.905, 56: 137.327, 57: 138.905, 58: 140.116, 59: 140.908, 60: 144.242, 61: 145.000, 62: 150.360, 63: 151.964, 64: 157.250, 65: 158.925, 66: 162.500, 67: 164.930, 68: 167.259,
    69: 168.934, 70: 173.040, 71: 174.967, 72: 178.490, 73: 180.948, 74: 183.840, 75: 186.207, 76: 190.230, 77: 192.217, 78: 195.084, 79: 196.967, 80: 200.592, 81: 204.380, 82: 207.200, 83: 208.980, 84: 209.000, 85: 210.000, 86: 222.000, 87: 223.000, 88: 226.000,
    89: 227.000, 90: 232.038, 91: 231.036, 92: 238.029, 93: 237.000, 94: 244.000, 95: 243.000, 96: 247.000, 97: 247.000, 98: 251.000, 99: 252.000, 100: 257.000, 101: 258.000, 102: 259.000, 103: 262.000, 104: 267.000, 105: 270.000, 106: 271.000, 107: 270.000, 108: 277.000, 109: 276.000, 110: 281.000, 111: 282.000, 112: 285.000, 113: 286.000, 114: 289.000,
    115: 288.000, 116: 293.000, 117: 294.000, 118: 294.000
}


