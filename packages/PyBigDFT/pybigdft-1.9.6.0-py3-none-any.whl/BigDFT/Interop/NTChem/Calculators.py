"""
A class that is able to drive calculations. Calculations are driven by
system calls from within python. If you wish to run the calculation on
a different machine, you can also use the dry_run feature which simply
creates the necessary input scripts.
"""


class SystemCalculator():
    """
    A class that can drive calculations with NTChem.

    Args:
      omp (int): the number of openmp threads. Default is taken from the
        environment.
      mpi_run (str): the mpirun command to use. The default is taken from
        the environment variable "NTCHEM_MPIRUN".
      skip (bool): if this is sets to True, calculations are skipped if the
        total energy is present.
    """
    def __init__(self, omp=None, mpi_run=None, skip=False, verbose=True):
        from os import environ

        self.calculations = {}

        if not omp:
            self.omp = environ.get("OMP_NUM_THREADS", "1")
        else:
            self.omp = omp

        if not mpi_run:
            self.mpi_run = environ.get("NTCHEM_MPIRUN", "")
        else:
            self.mpi_run = mpi_run

        self.skip = skip
        self.root = environ.get("NTCHEM_ROOT", "")
        self.verbose = verbose

    def check_results(self):
        """
        Check if all of the calculations have completed.

        Returns:
            (bool): True if all the calculation have completed.
        """
        success = True
        for job in self.calculations.values():
            if job.log is None:
                job.get_logfile()
            if job.log is None:
                success = False
        return success

    def _get_exe_sequence(self, params):
        """
        Analyzes a set of parameters to determine the necessary calculations.
        """
        exeset = ["basinp", "int1", "mdint1", "ecp", "projdens", "huckel",
                  "sap", "scf", "scfgrad", "dac"]
        return [x for x in exeset if x in params.keys()]

    def _check_multiplicity(self, sys, params):
        """
        Check that the multiplicity/use of RHF or UHF is correct for this
        system.
        """
        from BigDFT.Interop.NTChem.BasisSets import symlookup
        from copy import deepcopy
        subparams = deepcopy(params)

        # First, check if someone manually set the occupation numbers.
        if not (subparams["scf"].nocca == 0 and subparams["scf"].noccb == 0):
            total_electrons = subparams["scf"].nocca
            total_electrons += subparams["scf"].noccb
        else:  # Compute the total number of electrons.
            total_electrons = 0
            for frag in sys.values():
                for at in frag:
                    total_electrons += symlookup[at.sym]

        # Check if the charge has been set.
        total_electrons -= subparams["scf"].icharg

        # Check RHF/UHF
        if total_electrons % 2 == 1:
            subparams["scf"].scftype = "uhf"

        # Check Mult
        if total_electrons % 2 == 0:
            subparams["scf"].mult = 1
        else:
            subparams["scf"].mult = 2

        return subparams

    def run(self, sys, params, basis_set, name="ntchem", run_dir=".",
            dry_run=False, basis_set_proj=None, huckel=None):
        """
        Perform the actual calculation.

        Args:
            sys (BigDFT.Systems.System): the system to compute.
            params: an input file to calculate with.
            basis_set (BigDFT.Interop.NTChem.BasisSets.BasisSet): the
              basis set for this calculation.
            name (str): an identifier for this calculation.
            run_dir (str): the directory in which to run the calculation.
            dry_run (bool): if set to True, we just write the input file and
              skip the actual calculation.
            basis_set_proj (BigDFT.Interop.NTChem.BasisSets.BasisSet):
              if we are doing projection, the basis to project from.
            huckel (BigDFT.Interop.NTChem.Huckels.Huckel): ionization
              potential info for a Huckel guess.

        Returns:
            (BigDFT.Interop.NTChem.Logfiles.Logfile): a logfile with the
            results.
        """
        from os import system, environ
        from os.path import join
        from shutil import copyfile

        # Handle the overriding of the name and multiplicity.
        subparams = self._override_parameters(sys, params, name)
        name = subparams["control"].name

        # Check that the run directory exists
        self._check_rundirectory(run_dir, subparams["control"].name)
        run_dir = join(run_dir, name)
        fname = join(run_dir, name)

        # Determine the sequence of calculations.
        exe_sequence = self._get_exe_sequence(params)

        # Get the subset of atoms needed for the basis.
        sym_sub = self._get_subset(sys)

        # Determine the units.
        units = params["basinp"].units
        if units == "ang":
            units = "angstroem"

        # Build a calculation object
        self.calculations[name] = CalculationInfo(name, run_dir, exe_sequence)

        # Try an early exit.
        if self._check_skip(join(run_dir, name), exe_sequence):
            if self.verbose:
                print("Requirements found. Skipping calculation.")
            self.calculations[name].get_logfile()
            return self.calculations[name].log

        # Write Input File
        self._write_input_file(fname, subparams, sys, units, basis_set,
                               basis_set_proj, sym_sub, huckel=huckel)

        # Check dry run early return
        if dry_run:
            return None

        # Actual Run
        environ["OMP_NUM_THREADS"] = self.omp
        copyfile(fname + ".Inp", join(run_dir, "INPUT"))
        for exe in exe_sequence:
            runline = self._get_runline(run_dir, exe, name)
            if self.verbose:
                print(runline)
            system(runline)

        self.calculations[name].get_logfile()
        return self.calculations[name].log

    def _check_skip(self, path, exe_sequence):
        from os.path import exists
        if not self.skip:
            return False

        # Check that all the result files we want are there.
        requirements = {"scf": ".TotEne", "scfgrad": ".Grad"}
        for exe, ext in requirements.items():
            if exe in exe_sequence and not exists(path + ext):
                return False

        # We won't skip any calculation that doesn't do SCF
        if all([x not in exe_sequence for x in requirements]):
            return False

        return True

    def _write_input_file(self, fname, subparams, sys, units, basis_set,
                          basis_set_proj, sym_sub, huckel):
        import f90nml
        from warnings import warn

        # Consistency of input and basis
        if "basinp" in subparams:
            if basis_set.gtotype is not None and \
                    basis_set.gtotype.lower() != \
                    subparams["basinp"].gtotype.lower():
                warn("Basis is " + basis_set.gtotype + ", but input is "
                     + subparams["basinp"].gtotype)

        # Write
        with open(fname + ".Inp", "w") as ofile:
            f90nml.write(subparams.asdict(), ofile, sort=True)
            ofile.write(" GEOM\n")
            for frag in sys.values():
                for at in frag:
                    pos = " ".join([str(x) for x in
                                    at.get_position(units)])
                    if at.is_ghost:
                        sym = "Bq" + at.sym
                    else:
                        sym = at.sym
                    ofile.write(sym + " " + pos + "\n")
            ofile.write(" END\n")
            ofile.write(basis_set.get_input_string(atoms=sym_sub))
            if basis_set_proj is not None:
                ofile.write(basis_set_proj.get_input_string(atoms=sym_sub,
                                                            project=True))
            if huckel is not None:
                ofile.write(huckel.get_input_string())

    def _get_subset(self, sys):
        from BigDFT.Interop.NTChem.BasisSets import symlookup
        symlist = []
        for frag in sys.values():
            for at in frag:
                if at.is_ghost:
                    symlist.append("Bq" + at.sym)
                else:
                    symlist.append(at.sym)
        symlist = list(set(symlist))
        return {x: symlookup[x] for x in symlist}

    def _check_rundirectory(self, run_dir, name):
        """
        Make sure the run directory exists.
        """
        from os import makedirs
        from os.path import exists, join

        if run_dir != "" and not exists(run_dir):
            makedirs(run_dir)
        if not exists(join(run_dir, name)):
            makedirs(join(run_dir, name))

    def _override_parameters(self, sys, params, name=None):
        from copy import deepcopy

        # Override the name
        subparams = deepcopy(params)
        subparams.set_name(name)

        # Check the multiplicity
        if "scf" in subparams:
            subparams = self._check_multiplicity(sys, subparams)

        return subparams

    def _get_runline(self, run_dir, exe, name):
        """
        This will generate the exact command we will call to run an
        executable. This will also handle the rediction to the logfile, which
        can depend on the system platform.
        """
        from os.path import join

        logname = name + "." + exe + ".log"

        runline = "cd " + run_dir + " ; " + self.mpi_run
        if _is_fugaku():
            runline += (" -stdout-proc " + logname +
                        " -stderr-proc " + logname + ".err")

        runline += " " + join(self.root, exe + ".exe")

        if not _is_fugaku():
            runline += " | tee " + logname

        return runline


def _is_fugaku():
    from platform import machine
    return machine() == "aarch64"


class CalculationInfo:
    """
    Stores information about a given calculation.
    """
    def __init__(self, name, path, exe_sequence):
        self.name = name
        self.path = path
        self.do_grad = _do_grad(exe_sequence)
        self.exe_sequence = exe_sequence
        self.log = None

    def get_logfile(self):
        from BigDFT.Interop.NTChem.Logfiles import Logfile
        from os.path import join
        try:
            self.log = Logfile(join(self.path, self.name),
                               grad=self.do_grad)
        except IOError:  # File isn't there.
            self.log = None
        except StopIteration:  # File is incomplete.
            self.log = None


def _do_grad(exe_sequence):
    return ("scfgrad" in exe_sequence)


def _example():
    from BigDFT.Database.Molecules import get_molecule
    from BigDFT.Interop.NTChem.BasisSets import BasisSet, get_symlookup
    from BigDFT.Interop.NTChem.Inputfiles import Inputfile
    from BigDFT.Interop.NTChem.Calculators import SystemCalculator

    # Create the system to calculate.
    sys = get_molecule("H2O")

    # Get the basis set.
    basis = BasisSet("6-31G", atoms=get_symlookup(sys))

    # Create an input file
    inp = Inputfile()
    inp.set_basic_rhf()

    # Actual run
    calc = SystemCalculator()
    log = calc.run(sys, inp, basis, run_dir="scr")

    print(log.energy)


if __name__ == "__main__":
    _example()
