"""
A module that is used to setup Huckel ionization potentials.
"""


class HuckelPotential:
    def __init__(self):
        self.atoms = {}

    def add_atom(self, sym, potentials):
        """
        Add the potentials for a given atom.

        Args:
            sym (str): atomic symbol.
            potentials (list): a list of pairs of angular momentum and value.
        """
        self.atoms[sym] = potentials

    def get_input_string(self):
        """
        Generate the input string for an NTChem Input File.

        Returns:
            (str): the input string.
        """
        istr = " IOP\n"
        for at, pot in self.atoms.items():
            istr += at + "\n"
            for ang, val in pot:
                istr += ang + " " + str(val) + "\n"
            istr += "****\n"
        istr += " END\n"

        return istr


def _example():
    from BigDFT.Database.Molecules import get_molecule
    from BigDFT.Interop.NTChem.BasisSets import BasisSet, get_symlookup
    from BigDFT.Interop.NTChem.Inputfiles import Inputfile
    from BigDFT.Interop.NTChem.Calculators import SystemCalculator
    from BigDFT.Interop.NTChem.Huckel import HuckelPotential

    # System
    sys = get_molecule("H2O")
    basis = BasisSet("6-31G", atoms=get_symlookup(sys))

    # Huckel Potential
    iop = HuckelPotential()
    iop.add_atom("H", [("S", -13.6), ("S", -13.6)])
    iop.add_atom("O", [("S", -560), # Split Valence so only one here
                       ("S", -32.3), ("S", -32.3),
                       ("P", -14.8), ("P", -14.8)])

    # Input File
    inp = Inputfile()
    inp.set_basic_rhf()
    inp.set_scf_guess("huckel")

    # Run
    calc = SystemCalculator()
    log = calc.run(sys, inp, basis, huckel=iop, run_dir="scr")


if __name__ == "__main__":
    _example()
