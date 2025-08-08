"""
A module that downloads a basis set from the Basis Set Exchange
website and converts it to the NTChem format. This basis set object can
be passed to a system calculator as is. You can also convert the basis
set to string if you wish to manually write an input file.

This module uses the REST API of basis set exchange:
https://www.basissetexchange.org/

so retrieving a basis set has a certain amount of latency. For high throughput
calculations, we recommend caching the basis set locally and reusing it.

Attributes:
  symlookup (dict): A mapping from symbol names to number of electrons.
"""

# Names for the different angular momentum values.
_moname = ["S", "P", "D", "F", "H", "I", "J", "K"]

# Base URL for the basis set exchange
_bsse = "https://www.basissetexchange.org/"

symlookup = {"H": 1, "He": 2,
             "Li": 3, "Be": 4,
             "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
             "Na": 11, "Mg": 12,
             "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18,
             "K": 19, "Ca": 20,
             "Sc": 21, "Ti": 22, "Cr": 24, "Mn": 25, "Fe": 26,
             "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30,
             "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36,
             "Rb": 37, "Sr": 38,
             "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44,
             "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48,
             "In": 49, "Sn": 50, "Sb": 51, "Te": 52, "I": 53, "Xe": 54,
             "Pb": 82}
for k in list(symlookup):
    symlookup["Bq" + k] = symlookup[k]


class BasisSet:
    """
    This class wraps up an NTChem basis set.

    Retrieves the desired gaussian basis from the basis set exchange.

    Args:
      name (str): the name of the basis set you want.
      atoms (dict): a dictionary mapping atomic symbols to atomic numbers
        for the atoms you want.
      ecp (bool): if True, this will also retrieve the ecp basis values.
    """
    def __init__(self, name, atoms, ecp=False):
        self._name = name
        self.atoms = atoms
        self.ecp = ecp
        self.r = _get_json_basis(name.replace("*", "_st_"), atoms)

        if "gto_cartesian" in self.r["function_types"]:
            self.gtotype = "Cartesian"
        elif "gto_spherical" in self.r["function_types"]:
            self.gtotype = "Spherical"
        else:
            self.gtotype = None  # For s,p only

    @property
    def name(self):
        star = self._name.replace("*", "s")
        return "".join([x if x.isalnum() else "_" for x in star])

    def get_input_string(self, atoms=None, project=False):
        """
        Get the input string required by NTChem.

        Args:
          atoms (dict): a dictionary mapping atomic symbols to atomic numbers
            for the atoms you want. This has to be a subset of the atoms you
            gave when constructing this object.
          project (bool): if you want to write in the format for the
            projected basis.

        Returns:
          (str): the NTChem representation of the basis.
        """
        # Optional Parameters
        if atoms is None:
            atoms = self.atoms

        # Convert to NTChem
        retval = _convert_json_basis(self.r, atoms, project)
        if self.ecp:
            retval += _convert_ecp_json_basis(self.r, atoms)

        return retval


def get_symlookup(sys):
    """
    Get a dictionary which maps the atoms in a system to their atomic
    numbers.

    This is useful for setting up the basis.

    Args:
      (BigDFT.Systems.System): the system to generate for.

    Returns:
      (dict): a dictionary mapping each atomic symbol in the system to its
        atomic number.
    """
    symlist = set([x.sym for frag in sys.values() for x in frag])
    return {x: symlookup[x] for x in symlist}


def _get_json_basis(name, atoms):
    """
    Retrieves the desired gaussian basis from the basis set exchange in the
    json format.
    https://www.basissetexchange.org/

    Args:
      name (str): the name of the basis set you want.
      atoms (dict): a dictionary mapping atomic symbols to atomic numbers for
        the atoms you want.

    Returns:
      (str): the json representation of the basis.
    """
    import requests

    # First check that this basis is available
    r = requests.get(_bsse + '/api/metadata')
    if name.lower() not in r.json().keys():
        raise ValueError("Basis set not available.")

    # Now download the basis set for the desired atoms
    elstr = "/?elements=" + ','.join([str(x) for x in atoms.values()])
    basstr = _bsse + '/api/basis/'+name.lower()+'/format/json'

    return requests.get(basstr+elstr).json()


def _convert_json_basis(json, atoms, project):
    """
    Given a json representation of a basis set, this converts it to the
    NTChem format.

    Args:
      json (dict): the json representation of the basis from Basis Set
        Exchange.
      atoms (dict): a dictionary mapping atomic symbols to atomic numbers for
        the atoms in this basis.
      project (bool): whether to write in the format for the projected
        basis or not.

    Returns:
      (str): a basis set string for NTChem.
    """
    if project:
        outstr = " Basis_ProjMO\n"
    else:
        outstr = " Basis\n"
    for sym, num in atoms.items():
        outstr += sym + " 0\n"

        for shell in json["elements"][str(num)]["electron_shells"]:
            exponents = shell["exponents"]
            coefficients_list = shell["coefficients"]
            momentums_list = shell["angular_momentum"]

            diff = len(coefficients_list) - len(momentums_list)
            if diff > 0:
                momentums_list += [momentums_list[-1] for x in range(diff)]

            for coefficients, momentum in zip(coefficients_list,
                                              momentums_list):
                # Prune Zero Coefficients
                pairs = [(e, c) for e, c in zip(exponents, coefficients)
                         if abs(float(c)) > 1e-15]

                am = _moname[int(momentum)]
                outstr += am + " " + str(len(pairs)) + " 1.00\n"
                for e, c in pairs:
                    outstr += str(e) + " " + str(c) + "\n"

        outstr += "****\n"

    outstr += " End\n"

    return outstr


def _convert_ecp_json_basis(json, atoms):
    """
    Given a json representation of an ecp basis set, this converts it to the
    NTChem format.

    Args:
      json (dict): the json representation of the basis from Basis Set
        Exchange.
      atoms (dict): a dictionary mapping atomic symbols to atomic numbers for
        the atoms in this basis.

    Returns:
      (str): a basis set string for NTChem.
    """
    outstr = "\n ECP\n"
    for sym, num in atoms.items():
        atdir = json["elements"][str(num)]
        if "ecp_potentials" not in atdir:
            continue

        outstr += sym + " 0\n"
        nel = atdir["ecp_electrons"]
        maxmom = max(x["angular_momentum"] for x in atdir["ecp_potentials"])[0]
        outstr += str(maxmom) + " " + str(nel) + "\n"

        for shell in atdir["ecp_potentials"]:
            r_exponents = shell["r_exponents"]
            gaussian_exponents = shell["gaussian_exponents"]
            coefficients_list = shell["coefficients"]
            momentums_list = shell["angular_momentum"]

            diff = len(coefficients_list) - len(momentums_list)
            if diff > 0:
                momentums_list += [momentums_list[-1] for x in range(diff)]

            for coefficients, momentum in zip(coefficients_list,
                                              momentums_list):
                if momentum == maxmom:
                    outstr += _moname[momentum].lower()
                    outstr += " potential\n"
                else:
                    outstr += _moname[momentum].lower()
                    outstr += "-" + _moname[maxmom].lower()
                    outstr += " potential\n"

                outstr += "  " + str(len(coefficients)) + " \n"
                for r, e, c in zip(r_exponents, gaussian_exponents,
                                   coefficients):
                    outstr += str(r) + " " + str(e) + " " + str(c) + "\n"

        outstr += "****\n"
    outstr += " End\n"

    return outstr


def _example():
    # Be sure to specify the same name as listed on the website.
    basis_name = "6-31G"

    # This dictionary parameter is necessary because we need to know how
    # to convert from atomic number to atomic symbol.
    atoms = {"H": 1, "Cl": 17}
    basis = BasisSet(basis_name, atoms)

    print(basis.get_input_string())

    # Sometimes we only want to print a subset.
    sub_at = {"Cl": 17}
    print(basis.get_input_string(sub_at))

    # Example with ECP
    basis_name = "def2-SVP"
    atoms = {"H": 1, "Cl": 17, "Bi": 83}
    basis = BasisSet(basis_name, atoms, ecp=True)

    print(basis.get_input_string())


if __name__ == "__main__":
    _example()
