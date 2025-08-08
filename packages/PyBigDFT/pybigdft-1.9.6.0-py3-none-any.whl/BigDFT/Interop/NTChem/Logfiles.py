"""
Stores the results of an ntchem calculation.
"""


_angular_lookup = {"S": 0, "P": 1, "D": 2, "F": 3, "G": 4,
                   "H": 5, "I": 6, "K": 7, "L": 8}


class BasisFunction():
    """
    A class that wraps up the basis functions in a given shell.
    """
    def __init__(self, gtotype):
        self.momentum = None
        self.coef = []
        self.exp = []
        self.gtotype = gtotype

    def num_basis(self):
        """
        For this shell, how many basis functions are present.

        Returns:
            (int): number of functions.
        """
        nltuv = [1]
        for i in range(1, 8):
            if self.gtotype == "SPHERICAL":
                nltuv.append(i + i + 1)
            else:
                nltuv.append(int(((i+1)*(i+2))/2))
        return nltuv[_angular_lookup[self.momentum]]


class Logfile():
    """
    A class that wraps up the results of a calculation.

    Attributes:
        name (str): the name of the calculation.
        total_energy (float): the energy computed.
        iteration (list): the energy at each step of the SCF cycle.
        converged (bool): whether or not the calculation converged.
        densalp (str): the name of the density matrix file.
        densbet (str): the name of the density matrix file (UHF).
        fockalp (str): the name of the fock matrix file.
        fockbet (str): the name of the fock matrix file (UHF).
        overlap (str): the name of the overlap matrix file.
        isq (str): the name of the inverse square root matrix file.
        kxs (str): the name of the mulliken projected density matrix file.
        sinhv (str): the name of the mulliken projected fock matrix.
        korth (str): the name of the lowdin projected density matrix file.
        horth (str): the name of the lowdin projected fock matrix.
        gradients (list): the gradients computed on each atom.
    """
    def __init__(self, name, grad=False):
        self.name = name
        self._total_energy(name + ".TotEne")
        self._scf_info(name + ".SCF_Info")
        self._basis_info(name + ".Basis")
        self._convergence(name + ".scf.log")

        self.densalp = name + ".DensAlp.mtx"
        self.densbet = name + ".DensBet.mtx"
        self.fockalp = name + ".FockAlp.mtx"
        self.fockbet = name + ".FockBet.mtx"
        self.overlap = name + ".Overlap.mtx"
        self.isq = name + ".ISQ.mtx"

        self.orbenealp = name + ".OrbEneAlp.mtx"
        self.orbenebet = name + ".OrbEneBet.mtx"
        self.moalp = name + ".MOAlp.mtx"
        self.mobet = name + ".MOBet.mtx"

        self.kxs = name + ".KXS.mtx"
        self.sinvh = name + ".SINVH.mtx"
        self.korth = name + ".KOrth.mtx"
        self.horth = name + ".HOrth.mtx"
        if grad:
            self.gradients = self._get_gradient(name + ".Grad")

    def get_timings(self, name, walltime=True):
        """
        Various timings are available in a logfile. You can extract a list of
        timing with a given name using this routine.

        Args:
            name (str): the name of the timer.
            walltime (bool): if True, extracts the walltime. If false,
              extracts the cpu time.

        Returns:
            (list): the time required.
        """
        prefix = name.split("_")[0].lower()
        if prefix == "dft":
            prefix = "scf"
        file = self.name + "." + prefix + ".log"

        if walltime:
            search = "WALL time"
        else:
            search = "CPU time"

        result = []
        with open(file) as ifile:
            for line in ifile:
                if name in line and search in line:
                    result.append(float(line.split()[4]))

        return result

    def _basis_info(self, file):
        """
        Read in information about the basis.
        """
        self.basis = []
        with open(file) as ifile:
            gtotype = next(ifile).strip()
            self.normp = bool(next(ifile))
            self.normf = bool(next(ifile))
            self.natoms = int(next(ifile))

            for at in range(0, self.natoms):
                entry = {}
                line = next(ifile).split()
                entry["sym"] = line[0]
                entry["pos"] = [float(x) for x in line[1:]]
                entry["functions"] = []
                nbasis = int(next(ifile))
                for i in range(0, nbasis):
                    fun = BasisFunction(gtotype)
                    line = next(ifile).split()
                    fun.momentum = line[0]
                    ncoef = int(line[1])
                    for j in range(0, ncoef):
                        line = [float(x) for x in next(ifile).split()]
                        fun.exp.append(line[0])
                        fun.coef.append(line[1])
                    entry["functions"].append(fun)
                self.basis.append(entry)
        self.idxlist = self._index_list()

    def _get_gradient(self, file):
        result = []
        with open(file) as ifile:
            for line in ifile:
                result.append([float(x) for x in line.split()])
        return result

    def _index_list(self):
        idxlist = []
        idx = 0
        for b in self.basis:
            entry = []
            for fun in b["functions"]:
                entry += list(range(idx, idx+fun.num_basis()))
                idx += fun.num_basis()
            idxlist.append(entry)
        return idxlist

    def _scf_info(self, file):
        """
        Get the info from the SCF_Info file.
        """
        with open(file) as ifile:
            line1 = next(ifile).split()
            line2 = next(ifile).split()
        self.nbf = int(line1[0])
        self.nmo = int(line1[1])
        self.nocca = int(line1[2])
        self.noccb = int(line1[3])
        self.uhf = line1[4] == "T"
        self.rohf = line1[5] == "T"

        self.dft = line2[0] == "T"
        self.skip1e = line2[1] == "T"
        self.skip2e = line2[2] == "T"
        self.coultype = line2[3]
        self.exchtype = line2[4]

    def _convergence(self, file):
        """
        Extract the information which is printed directly in the log.
        """
        self.iteration = []
        self.converged = False
        with open(file) as ifile:
            for line in ifile:
                if "ITERATION" in line:
                    self.iteration.append(float(line.split()[2]))
                if "SCF converged !!" in line:
                    self.converged = True

    def _total_energy(self, file):
        """
        Read in the total energy.
        """
        with open(file) as ifile:
            self.total_energy = float(next(ifile))

    @property
    def energy(self):
        """
        Maintain compatability with PyBigDFT.
        """
        return self.total_energy

def _example():
    from BigDFT.Database.Molecules import get_molecule
    from BigDFT.Interop.NTChem.BasisSets import BasisSet, get_symlookup
    from BigDFT.Interop.NTChem.Inputfiles import Inputfile
    from BigDFT.Interop.NTChem.Calculators import SystemCalculator

    # Calculate
    sys = get_molecule("H2O")
    basis = BasisSet("6-31G", atoms=get_symlookup(sys))
    inp = Inputfile()
    inp.set_basic_rhf()
    inp.set_scf_guess("gwh")
    calc = SystemCalculator()
    log = calc.run(sys, inp, basis, run_dir="scr")

    # Calculation Results
    print(log.energy)
    print(log.converged)
    print(log.iteration)

    # Basis Info
    print(log.basis)
    print(log.idxlist)

    # SCF Information
    print(log.natoms)
    print(log.nbf)

    # Timer
    print(log.get_timings("SCF_Driv", walltime=True))
    print(log.get_timings("SCF_Driv", walltime=False))


if __name__ == "__main__":
    _example()
