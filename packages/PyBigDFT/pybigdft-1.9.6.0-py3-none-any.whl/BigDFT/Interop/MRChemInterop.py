"""
This module contains some wrappers for using MRChem to perform calculations.

https://mrchem.readthedocs.io/en/latest/index.html

Input files are defined using the json format as a dictionary.

https://mrchem.readthedocs.io/en/latest/users/program_json.html
"""
from BigDFT.Calculators import Runner
from futile.Utils import write as safe_print


class MRChemLogfile(dict):
    """
    This class stores the detailed output from MRChem.

    Attributes:
        energy (float): the energy of the system
    """
    def __init__(self, logname):
        self._process_values(logname)

    @property
    def energy(self):
        """
        The total energy of the system.
        """
        return self["output"]["properties"]["scf_energy"]["E_tot"]

    def _process_values(self, logname):
        from json import load, JSONDecodeError
        with open(logname) as ifile:
            data = load(ifile)
            
        for k, v in data.items():
            self[k] = v

        # Check that it was successful
        if "output" not in self:
            raise ValueError("Calculation data not there")


class MRChemCalculator(Runner):
    """
    A calculator that drives MRChem calculations through the command line.

    This calculator will look in the environment for the following variables:
    * OMP_NUM_THREADS : number of threads to use
    * MRCHEM_MPIRUN : the mpi command you want to launch mrchem with
    * MRCHEM_ROOT : the directoy that contains the mrchem executable.
    """
    import os

    def __init__(self, omp=os.environ.get('OMP_NUM_THREADS', '1'),
                 mpi_run=os.environ.get('MRCHEM_MPIRUN', ''),
                 dry_run=False, skip=False, verbose=True):
        from os.path import join

        # Use the initialization from the Runner class (so all options inside
        # __global_options)
        Runner.__init__(self, omp=str(omp), dry_run=dry_run, skip=skip,
                        mpi_run=mpi_run, verbose=verbose)

        self.command = self._global_options['mpi_run'] + " mrchem"

        if verbose:
            safe_print(
                'Initialize a Calculator with OMP_NUM_THREADS=%s '
                'and command %s' %
                (self._global_options['omp'], self.command))
            
    def pre_processing(self):
        """
        Process local run dictionary to create the input directory and identify
        the command to be passed

        Returns:
            :py:class:`dict`: dictionary containing the command to be passed to
            :meth:`process_run`
        """
        from json import dump
        from os.path import join

        self._ensure_run_directory()
        sys = self.run_options["sys"]
        inp = self.run_options.get("input", {})

        if "Molecule" not in inp:
            inp["Molecule"] = {}
        inp["Molecule"]["coords"] = self._get_coords(sys)

        name = self.run_options.get("name", "mrchem") + ".inp"
        with open(join(self.run_dir, name), "w") as ofile:
            dump(inp, ofile)

        return {'command': self._get_command()}

    def process_run(self, command):
        """
        Run the MRChem executable.
        """
        from os import environ, system
        from os.path import join

        # Set the number of omp threads only if the variable is not present
        # in the environment
        if 'OMP_NUM_THREADS' not in environ:
            environ['OMP_NUM_THREADS'] = self.run_options['omp']

        if self.run_options['verbose']:
            if self.run_dir != '.':
                safe_print('Run directory', self.run_dir)
            safe_print('Executing command: ', command)

        # Run the command
        system(command)

        return {'logname': join(self.run_dir, self._get_logname())}

    def post_processing(self, logname, command):
        """
        Post processing the calculation.

        Returns:
            (BigDFT.Interop.MRChemLogfile): a representation of the
            detailed output.
        """
        from json import JSONDecodeError
        from os.path import join

        try:
            logname = join(self.run_dir, self._get_logname())
            return MRChemLogfile(logname)
        except JSONDecodeError:
            raise ValueError("Invalid logfile ", logname)

    def _get_coords(self, sys):
        ostr = ""
        for frag in sys.values():
            for at in frag:
                ostr += at.sym + " "
                ostr += " ".join([str(x) for x in at.get_position()])
                ostr += "\n"

        return ostr

    def _get_logname(self):
        return self.run_options.get("name", "mrchem") + ".json"

    def _get_command(self):
        from os import environ
        from os.path import join

        if self._check_skip():
            return '''echo "skip"'''

        iname = self.run_options.get("name", "mrchem") + ".inp"
        oname = self.run_options.get("name", "mrchem") + ".json"

        cmd = "cd " + self.run_dir + "; "
        if "MRCHEM_ROOT" in environ:
            cmd += join(environ["MRCHEM_ROOT"], "mrchem")
        else:
            cmd += "mrchem"
        cmd += " --json " + iname + " "
        if "mpi_run" in self.run_options:
            cmd += '--launcher="' + self.run_options["mpi_run"] + '" '
        if "MRCHEM_ROOT" in environ:
            cmd += "--executable=" + join(environ["MRCHEM_ROOT"], "mrchem.x")
        cmd += " > " + oname

        return cmd

    def _check_skip(self):
        from json import JSONDecodeError
        from os.path import join

        if not self.run_options["skip"]:
            return False
        try:
            logname = join(self.run_dir, self._get_logname())
            return MRChemLogfile(logname)
        except FileNotFoundError:  # No output file
            return False
        except JSONDecodeError:  # Input probably malformed and failed
            return False
        except ValueError:  # Only the input was read, calculation not done.
            return False
        return False

    def _ensure_run_directory(self):
        from futile.Utils import ensure_dir
        run_dir = self.run_options.get('run_dir', '.')
        # Create the run_dir if not exist
        if ensure_dir(run_dir) and self.run_options['verbose']:
            safe_print("Create the sub-directory '%s'" % run_dir)

        self.run_dir = run_dir

def _example():
    """Example of using MRChem interoperability"""
    from BigDFT.IO import XYZReader
    from BigDFT.Systems import System
    from BigDFT.Fragments import Fragment
    from os.path import join
    from os import getcwd
    from copy import deepcopy

    # Create a system.
    reader = XYZReader("He")
    fsys = System()
    fsys["FRA:1"] = Fragment(xyzfile=reader)
    fsys["FRA:2"] = deepcopy(fsys["FRA:1"])
    fsys["FRA:2"].translate([-4, 0, 0])

    # Create an input file
    inp = {}
    inp["WaveFunction"] = {"method": "PBE"}
    inp["world_prec"] = 1.0e-2

    # Create a Calculator and Run
    calc = MRChemCalculator(mpi_run="mpirun -np 1")
    log = calc.run(sys=fsys, input=inp, name="HE2", run_dir="scratch")

    # The full set of data from the json output are available
    log["output"]

if __name__ == "__main__":
    _example()
