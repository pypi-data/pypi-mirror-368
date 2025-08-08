"""
This module contains some wrappers for using Genesis to perform calculations.

https://www.r-ccs.riken.jp/labs/cbrt/

Input files are defined using the toml format as a dictionary.
"""
from BigDFT.Calculators import Runner


def dump_genesis(data, ofile):
    """
    A helper to dump the simple TOML format of genesis.

    Args:
        data (dict): dictionary of dicts, one layer deep.
        ofile: open stream object.
    """
    for header, sub in data.items():
        ofile.write(f'[{header}]\n')
        for k, v in sub.items():
            ofile.write(f'{k} = {v}\n')
        ofile.write("\n")


class GenesisCalculator(Runner):
    """
    A calculator which can drive simulations using the Genesis program.

    This calculator will look in the environment for the following variables:
    * OMP_NUM_THREADS : number of threads to use
    * GENESIS_MPIRUN : the mpi command you want to launch genesis with
    * GENESIS_ROOT : the directoy that contains the genesis executables.
    """
    import os

    def __init__(self, exe="atdyn", omp=os.environ.get('OMP_NUM_THREADS', '1'),
                 mpi_run=os.environ.get('GENESIS_MPIRUN', ''),
                 dry_run=False, skip=False, verbose=True):
        """
        Args:
            exe (str): either atdyn or spdyn depending on the executable you
            want to use.
        """
        # Use the initialization from the Runner class (so all options inside
        # __global_options)
        Runner.__init__(self, omp=str(omp), dry_run=dry_run, skip=skip,
                        mpi_run=mpi_run, verbose=verbose)

        # Check exe args
        if exe not in ["atdyn", "spdyn"]:
            raise ValueError("exe mustr be atdyn or spdyn")
        self.exe = exe

        # Print out initialization information
        omp = self._global_options['omp']
        print(f'Initialize a Calculator with OMP_NUM_THREADS={omp} ' +
              f'and command {self.exe}')

    def pre_processing(self):
        """
        Process local run dictionary to create the input directory and copy
        over the needed files.

        Returns:
            (dict): dictionary containing the command to be passed to
            `process_run`
        """
        from shutil import copyfile, SameFileError
        from os.path import join
        from copy import deepcopy

        # Handle the files
        self._ensure_run_directory()
        name = self.run_options.get("name", "genesis")
        psf = self.run_options["psf"]
        pdb = self.run_options["pdb"]

        try:
            copyfile(psf, join(self.run_dir, name + ".psf"))
        except SameFileError:
            pass
        try:
            copyfile(pdb, join(self.run_dir, name + ".pdb"))
        except SameFileError:
            pass

        # Update the input with the psf and pdb names
        params = deepcopy(self.run_options.get("inp", {"INPUT": {}}))
        params["INPUT"]["psffile"] = name + ".psf"
        params["INPUT"]["pdbfile"] = name + ".pdb"

        # Write an input file
        with open(join(self.run_dir, f"{name}.toml"), "w") as ofile:
            dump_genesis(params, ofile)

        return {'command': self._get_command()}

    def _ensure_run_directory(self):
        """
        Handle the run directory.
        """
        from futile.Utils import ensure_dir

        run_dir = self.run_options.get('run_dir', '.')
        if ensure_dir(run_dir) and self.run_options['verbose']:
            print("Create the sub-directory '%s'" % run_dir)

        self.run_dir = run_dir

    def _get_command(self):
        """
        Build the command we are going to run including all options.
        """
        from os.path import join
        from os import environ

        # Check if it is a dry run or skip
        if self.run_options['dry_run']:
            return 'echo "dry run"'
        if self._check_skip():
            return 'echo "skip"'

        # Put it all together
        cmd = "cd " + self.run_dir + "; "
        if "mpi_run" in self.run_options:
            cmd += self.run_options["mpi_run"] + ' '
        if "GENESIS_ROOT" in environ:
            cmd += join(environ["GENESIS_ROOT"], self.exe)
        else:
            cmd += self.exe

        name = self.run_options.get("name", "genesis")
        logname = self._get_logname(False)
        cmd += f" {name}.toml > {logname}"

        return cmd

    def process_run(self, command):
        """
        Run the genesis executable.

        Returns:
            (dict): logname (full path)
        """
        from os import environ, system
        # Set the number of omp threads only if the variable is not present
        # in the environment
        if 'OMP_NUM_THREADS' not in environ:
            environ['OMP_NUM_THREADS'] = self.run_options['omp']

        if self.run_options['verbose']:
            if self.run_dir != '.':
                print('Run directory', self.run_dir)
            print('Executing command: ', command)

        # Run the command
        system(command)

        return {'logname': self._get_logname(True)}

    def post_processing(self, logname, command):
        """
        Post processing the calculation.

        Returns:
            (BigDFT.Interop.GenesisInterop.GenesisLogfile): a representation
            of the logfile.
        """
        try:
            return GenesisLogfile(logfile=self._get_logname(True))
        except IOError:
            raise ValueError(f"The logfile {logname} does not exist.")

    def _get_logname(self, full):
        """
        Get the name of the logfile.

        Args:
            full (bool): True with include the run_dir.
        """
        from os.path import join
        name = self.run_options.get("name", "genesis") + ".log"
        if full:
            run_dir = self.run_options.get('run_dir', '.')
            return join(run_dir, name)
        else:
            return name

    def _check_skip(self):
        """
        Check if we actually have to do the calculation.
        """
        from os.path import exists

        if not self.run_options["skip"]:
            return False

        # Does the file exist?
        fpath = self._get_logname(True)
        if not exists(fpath):
            return False

        # Did we finish the calculation?
        with open(fpath) as ifile:
            for line in ifile:
                if "Output_Time>" in line:
                    return True
        return False


class GenesisLogfile():
    """
    This class stores the results of a Genesis calculation which might be later
    post-processed.

    Attributes:
        sys (BigDFT.Systems.System): the initial system simulated.
        run_dir (str): relative path to the directory this was run in.
        info (dict): a dictionary of lists with time steps, temperature,
            energy, etc.
        output (str): the name of the output coordinate file.
    """
    def __init__(self, logfile):
        from os.path import dirname, join
        name = logfile.replace(".log", "")
        self._name = name
        self.run_dir = dirname(logfile)
        self.sys = self._process_geom(name + ".pdb")
        self.info = self._process_info(name + ".log")
        try:
            self.output = join(self.run_dir,
                               self._get_output_file(name + ".log"))
        except TypeError:
            self.output = None

    def _process_geom(self, fname):
        from BigDFT.IO import read_pdb
        with open(fname) as ifile:
            return read_pdb(ifile, include_chain=True, charmm_format=True)

    def _process_info(self, fname):
        data = {}
        with open(fname) as ifile:
            line = next(ifile)
            while "INFO:" not in line:
                line = next(ifile)
            keys = line.split()[1:]
            data = {k: [] for k in keys}
            for line in ifile:
                if "INFO:" in line:
                    for k, v in zip(keys, line.split()[1:]):
                        data[k].append(float(v))
        return data

    def _get_output_file(self, fname):
        """
        Look for output file name in the log.
        """
        with open(fname) as ifile:
            try:
                for line in ifile:
                    if "dcdfile" in line:
                        return line.split("=")[-1].strip()
            except StopIteration:
                return None

    def get_trajectory(self):
        """
        Extract the trajectory in BigDFT system format.

        Returns:
            (list): a list of BigDFT.Systems.System types.
        """
        from MDAnalysis.coordinates.DCD import DCDReader
        from copy import deepcopy

        traj = []
        reader = DCDReader(self.output)
        for frame in reader:
            traj.append(deepcopy(self.sys))
            for at, p in zip(traj[-1].get_atoms(), frame.positions):
                at.set_position(p, units="angstroem")
        return traj


def _example():
    """Example of using Genesis interoperability"""
    params = {}
    params["INPUT"] = {}
    params["INPUT"]["topfile"] = "top_all36_prot.rtf"
    params["INPUT"]["parfile"] = "par_all36m_prot.prm"

    params["ENERGY"] = {}
    params["ENERGY"]["forcefield"] = "CHARMM"
    params["ENERGY"]["electrostatic"] = "CUTOFF"
    params["ENERGY"]["switchdist"] = 48.0
    params["ENERGY"]["cutoffdist"] = 49.0
    params["ENERGY"]["pairlistdist"] = 50.0

    params["DYNAMICS"] = {}
    params["DYNAMICS"]["integrator"] = "VVER"
    params["DYNAMICS"]["nsteps"] = 500
    params["DYNAMICS"]["timestep"] = 0.002
    params["DYNAMICS"]["eneout_period"] = 10

    params["CONSTRAINTS"] = {}
    params["CONSTRAINTS"]["rigid_bond"] = "YES"

    params["ENSEMBLE"] = {}
    params["ENSEMBLE"]["ensemble"] = "NVT"
    params["ENSEMBLE"]["tpcontrol"] = "BUSSI"
    params["ENSEMBLE"]["temperature"] = 298.15

    params["BOUNDARY"] = {}
    params["BOUNDARY"]["type"] = "NOBC"

    calc = GenesisCalculator()
    log = calc.run(inp=params, psf="6lu7.psf", pdb="6lu7.pdb")

    print(log.info["TOTAL_ENE"])


if __name__ == "__main__":
    _example()
