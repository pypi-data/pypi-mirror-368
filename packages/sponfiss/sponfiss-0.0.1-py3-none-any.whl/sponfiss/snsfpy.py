import numpy as np


periodic_table = {
    1: "H",   2: "He",  3: "Li",  4: "Be",  5: "B",   6: "C",   7: "N",   8: "O",   9: "F",   10: "Ne",
    11: "Na", 12: "Mg", 13: "Al", 14: "Si", 15: "P",  16: "S",  17: "Cl", 18: "Ar", 19: "K",  20: "Ca",
    21: "Sc", 22: "Ti", 23: "V",  24: "Cr", 25: "Mn", 26: "Fe", 27: "Co", 28: "Ni", 29: "Cu", 30: "Zn",
    31: "Ga", 32: "Ge", 33: "As", 34: "Se", 35: "Br", 36: "Kr", 37: "Rb", 38: "Sr", 39: "Y",  40: "Zr",
    41: "Nb", 42: "Mo", 43: "Tc", 44: "Ru", 45: "Rh", 46: "Pd", 47: "Ag", 48: "Cd", 49: "In", 50: "Sn",
    51: "Sb", 52: "Te", 53: "I",  54: "Xe", 55: "Cs", 56: "Ba", 57: "La", 58: "Ce", 59: "Pr", 60: "Nd",
    61: "Pm", 62: "Sm", 63: "Eu", 64: "Gd", 65: "Tb", 66: "Dy", 67: "Ho", 68: "Er", 69: "Tm", 70: "Yb",
    71: "Lu", 72: "Hf", 73: "Ta", 74: "W",  75: "Re", 76: "Os", 77: "Ir", 78: "Pt", 79: "Au", 80: "Hg",
    81: "Tl", 82: "Pb", 83: "Bi", 84: "Po", 85: "At", 86: "Rn", 87: "Fr", 88: "Ra", 89: "Ac", 90: "Th",
    91: "Pa", 92: "U",  93: "Np", 94: "Pu", 95: "Am", 96: "Cm", 97: "Bk", 98: "Cf", 99: "Es", 100: "Fm",
    101: "Md",102: "No",103: "Lr",104: "Rf",105: "Db",106: "Sg",107: "Bh",108: "Hs",109: "Mt",110: "Ds",
    111: "Rg",112: "Cn",113: "Nh",114: "Fl",115: "Mc",116: "Lv",117: "Ts",118: "Og"}


def zaid_to_symbol(zaid):

    """
    Convert a ZAID code into an isotope symbol.

    Parameters:
        zaid (int or str): Numeric ZAID (Z*1000 + A),
            where Z = atomic number and A = mass number.

    Returns:
        str: Element symbol followed by A, e.g. "U235".
    """
    zaid = int(zaid)
    Z = zaid // 1000   # atomic number
    A = zaid % 1000        # mass number
    symbol = periodic_table.get(Z, f"Z{Z}")
    return f"{symbol}{A}"


def decayConst(hl,unit='s'):

    """
    Compute decay constant λ from half-life.

    Parameters:
        hl (float): Half-life value in the specified unit.
        unit (str): Unit of hl:
            's' for seconds, (Default if not specified)
            'm' for minutes,
            'h' for hours,
            'd' for days,
            'y' for years.

    Returns:
        float: Decay constant λ in s⁻¹.
    """
    if unit=='h':
        t = 60*60
    elif unit=='m':
        t = 60
    elif unit =='s':
        t = 1
    elif unit=='d':
        t = 24*60*60
    elif unit =='y':
        t = 24*60*60*365.25
    else: 
        raise ValueError("Use 'h','m','s','d','y'")
        
    lam = np.log(2)/(hl*t)
    return lam


class Material: 
    """
    
    Represents a material with nuclide composition for spontaneous-fission calculations.

    Attributes:
        name (str): Identifier for the material.
        density (float): Density in g/cm³.
        volume (float|None): Volume in cm³; if None, sponfiss() returns rate per cm³.
        composition (dict): Mapping nuclide -> fraction (either atom-frac or number density).
        nuclides (dict): Library of half-life [s], branching ratio [%], molar mass [g/mol].
    
    """


    def __init__(self, name=None, density=None, volume=None):
        self.name = name
        self.density = density
        self.composition = {}
        self.volume = volume
        
        
        
        ''' 
                The following dictionairy is the data set of available nuclides in the library 
                half_life - is the halflife in seconds [s] of the nuclide
                BR - is the branching ratio of the nuclide in percent[%] (99% is in this case 99 not 0.99)
                molar_mass - is the Molar mass in g/mol
                All data taken from iaea.org (https://www-nds.iaea.org/relnsd/vcharthtml/VChartHTML.html)
        '''


        self.nuclides = {
        "Th232": { "half_life": 441796963644288000, "BR": 1.1e-9, "molar_mass": 232.038055},
        "U232":  { "half_life": 2174272200, "BR": 2.7e-12, "molar_mass": 232.037156},
        "U233":  { "half_life": 5023547045895, "BR": 6e-11, "molar_mass": 233.039635},
        "U234":  { "half_life": 7747225326762, "BR": 1.64e-11, "molar_mass": 234.040952},
        "U235":  { "half_life": 22216075886112768, "BR": 7e-9, "molar_mass": 235.0439299},
        "U236":  { "half_life": 739063206324945, "BR": 9.4e-8, "molar_mass": 236.045568},
        "U238":  { "half_life": 140996345254477056, "BR": 5.45e-5, "molar_mass": 238.0507882},
        "Np237": { "half_life": 67658049289525, "BR": 2e-10, "molar_mass": 237.0481734},
        "Pu236": { "half_life": 90189694, "BR": 1.9e-7, "molar_mass": 236.046058},
        "Pu238": { "half_life": 2767542408, "BR": 1.9e-7, "molar_mass": 238.0495599},
        "Pu239": { "half_life": 760837485247 , "BR": 3.1e-10, "molar_mass": 239.0521634},
        "Pu240": { "half_life": 207044991319, "BR": 5.7e-6, "molar_mass": 240.0538135},
        "Pu241": { "half_life": 452179192, "BR": 2.4e-14, "molar_mass": 241.0568515},
        "Pu242": { "half_life": 11770733388523, "BR": 5.53e-4, "molar_mass": 242.0587426},
        "Am241": { "half_life": 13651526177, "BR": 3.6e-10, "molar_mass": 241.0568293},
        "Cm242": { "half_life": 14072832, "BR": 6.2e-6, "molar_mass": 242.058835},
        "Cm244": { "half_life": 571495929, "BR": 1.37e-4, "molar_mass": 244.0627526},
        "Cm246": { "half_life": 148506893636 , "BR": 0.02615, "molar_mass": 246.0672237},
        "Cm248": { "half_life": 10981810239158, "BR": 8.39, "molar_mass": 248.0723499},
        "Bk249": { "half_life": 28270080, "BR": 47e-9, "molar_mass": 249.0749807},
        "Cf246": { "half_life": 128520, "BR": 2.3e-4, "molar_mass": 246.068804},
        "Cf250": { "half_life": 412764592, "BR": 0.077, "molar_mass": 250.076406},
        "Cf252": { "half_life": 83531183, "BR": 3.102, "molar_mass": 252.081626},
        "Cf254": { "half_life": 5227200, "BR": 99.62, "molar_mass": 254.087323},
        "Fm257": { "half_life": 8683200, "BR": 99.790, "molar_mass": 257.095105},
        "No252": { "half_life": 2.46, "BR": 33.0, "molar_mass": 252.08897}}


    def addtodata(self, nuclide, halflife=None, BR=None, molar_mass=None): 

        """
        Add or overwrite nuclide data.
        Parameters:
            nuclide (str): Nuclide symbol, e.g. "U235".
            halflife (float|None): Half-life in seconds.
            BR (float|None): Branching ratio in percent [%].
            molar_mass (float|None): Molar mass in g/mol.
        """
        self.nuclides[nuclide] =  {}
        self.nuclides[nuclide]["half_life"] = halflife
        self.nuclides[nuclide]["BR"] = BR
        self.nuclides[nuclide]["molar_mass"] = molar_mass
    
    def removedata(self, nuclide):

        """
        Remove a nuclide from the library.

        Parameters:
            nuclide (str): Symbol to remove.
        """
        
        if nuclide in self.nuclides:
            del self.nuclides[nuclide]
        else:
            raise KeyError(f"Nuclide '{nuclide}' not found in the data.")
        

    def addnuclei(self,nuclei, frac, Format='nuclide'):

        """
        Define material composition.

        Parameters:
            nuclei (str|int): Nuclide symbol (e.g. "U235") or ZAID code if Format='ZAID'.
            frac (float): Either atomic fraction (if using AtomFrac) or number density [atoms/cm³].
            Format (str): "nuclide" or "ZAID".
        """
        if Format == 'ZAID':
            nuc = zaid_to_symbol(nuclei)
        elif Format == 'nuclide':
            nuc = nuclei
        else:
            raise ValueError("Invalid format. Acceptable formats are 'ZAID' or 'nuclide'.")
        self.composition[nuc] = frac


    def set_density(self, density): 
        """
        Set material density.

        Parameters:
            density (float): Density in g/cm³.
        """
        self.density = density
    def set_volume(self, volume):
        """
        Set material volume.

        Parameters:
            volume (float): volume in cm³.
        """
        self.volume = volume

    def sponfiss(self, unit='AtomFrac'):
        """
        Calculate spontaneous-fission rate.

        Parameters:
            unit (str):
                'AtomFrac' to interpret self.composition values as atom fractions,
                'NumDens' to interpret them as number densities [atoms/cm³].

        Returns:
            float: If volume is None, rate in fissions/s/cm³.
                   Otherwise, total rate in fissions/s.
        """

        if unit not in ['AtomFrac', 'NumDens']:
            raise ValueError("Invalid unit Acceptable formats are 'AtomFrac' or 'NumDens'.")
        N_A  = 6.02214076e23
        spontfiss = 0
        for key, frac in self.composition.items():
            if unit == 'NumDens':
                var1 = frac
            elif unit == 'AtomFrac':
                var1 = (self.density * N_A * frac) / self.nuclides[key]["molar_mass"]    
            
            if self.nuclides[key]["BR"] is None or self.nuclides[key]["half_life"] is None:
                continue
            else:
                lam = decayConst(self.nuclides[key]["half_life"])
                spontfiss += (lam * self.nuclides[key]["BR"] * var1) / 1000
        if self.volume == None:
            return spontfiss #Else returns the rate in units of fissions/s/cm3
        else: #if volume is set, calculate spontaneous fission rate in units of fissions/s
            return spontfiss * self.volume
