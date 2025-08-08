"""
An input file basically wraps a dictionary since it will ultimately
become a namelist. There are two concerns we have to take care of:

- namelists are not case sensitive
- valid parameter checking.

This class handles both of these issues. First, all keys are automatically
translated to case-inensitive. Second, all actual parameters are checked
using the facilities provided in `BigDFT.Interop.NTChem.Namelists`.

In addition to these facilities, this class also contains helper routines
for setting up standard calculations.
"""
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping


class Inputfile(MutableMapping):
    """
    The input file wrapper class.
    """
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def asdict(self):
        return {x: y.asdict() for x, y in self.store.items()}

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        from BigDFT.Interop.NTChem import Namelists as nl

        kt = self.__keytransform__(key)

        # First check that the key is valid
        if kt not in [x.lower() for x in nl.namelists]:
            raise KeyError("Illegal namelist name: " + key)

        # Now check the value
        if not isinstance(value, nl.NMLBase):
            # Try promoting the dictionary.
            for c in dir(nl):
                if self.__keytransform__(c) == kt:
                    self.store[kt] = getattr(nl, c)(**value)
                    return
            raise ValueError("Illegal namelist object.")

        self.store[kt] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key.lower()

    def _default(self, key):
        if key not in self:
            self[key] = {}

    def set_basic_rhf(self):
        """
        Create a basic input file which does a rhf calculation.
        """
        self._default("control")
        self._default("basinp")
        self._default("int1")
        self._default("int2")
        self._default("scf")
        self["scf"].coultype = "analy"
        self["scf"].exchtype = "analy"

    def set_basic_dft(self, *, xtype=None, ctype=None, xctype=None):
        """
        Create a basic input file which does a dft calculation using the
        provided functional.

        Args:
          xtype (str): the name of the correlation functional to use.
          ctype (str): the name of the exchange functional to use.
          xctype (str): the name of the DFT functional to use.
        """
        self.set_basic_rhf()
        self._default("dft")
        self["scf"].dft = True

        if xctype is not None and (xtype is not None or ctype is not None):
            raise TypeError("Specify only the xctype, or the c and x type.")

        if xctype is not None:
            self["dft"].xctype = xctype
        if xtype is not None:
            self["dft"].xtype = xtype
        if ctype is not None:
            self["dft"].ctype = ctype

    def set_custom_dft(self, xfun_xfac, cfun_cfac, hffac=0.0):
        """
        Set DFT functionals, including hybrid one.

        Args:
          xfun_xfac (Dict[str, float]): exchange functionals and their ratios
          cfun_cfac (Dict[str, float]): correlation functionals and their
            ratios
          hffac (float): ratio of exact HF exchange

        >>> f = Inputfile()
        >>> # set B3LYP
        >>> f.set_custom_dft(
        ...     {'B88GGA': 0.72, 'Slater': 0.80},
        ...     {'LYP': 0.81, 'VWN5': 0.19},
        ...     0.20)
        """

        self.set_basic_rhf()
        self._default("dft")
        self["scf"].dft = True
        self["dft"].xfun = list(xfun_xfac.keys())
        self["dft"].cfun = list(cfun_cfac.keys())
        self["dft"].xfac = list(xfun_xfac.values())
        self["dft"].cfac = list(cfun_cfac.values())
        self["dft"].hffac = hffac

    def set_dft_prune_grid(self, nrad, nang):
        """
        Set the DFT grid to the prune type.

        Note that the default for ntchem is Gaussian's super fine grid
        (99,590). The q-chem manual recommends (50,194) for LDA/GGA though,
        so this might also be acceptable.

        Args:
          nrad (int): number of radial spheres.
          nang (int): number of angular grid points.
        """
        self._default("dftnum")
        self["dftnum"].gridtype = "prune"
        self["dftnum"].nrad = nrad
        self["dftnum"].nang = nang

    def set_linear_scaling(self):
        """
        Set some suitable parameters for performing linear scaling
        calculations.
        """
        self._default("ntpoly")
        self["ntpoly"].pdmtype = "trs4"
        self["ntpoly"].thresholdpdm = 1e-7
        self["ntpoly"].convergencethresholdpdm = 1e-4
        self["ntpoly"].orthtype = "ord5"
        self["ntpoly"].thresholdorth = 1e-8
        self["ntpoly"].convergencethresholdorth = 1e-5

        self._default("int2")
        self["int2"].prelinkjthreshold = 1e-8
        self["int2"].prelinkkthreshold = 1e-4
        self["int2"].thrpre = 1e-10

        self.set_scf_convergence(1e-4, 1e-3)

    def set_atomic_guess_profile(self):
        """
        Set some suitable parameters for performing calculations of single
        atoms.
        """
        self.set_scf_guess("diagonal")
        self["scf"].maxdamp = 50
        self["scf"].mixdamp = False
        self._default("ntpoly")
        self["ntpoly"].pdmtype = "eig"

    def set_matrix_format(self, format):
        """
        Set the format of the matrices being written to and read from file.
        """
        self._default("ntpoly")
        if format == "binary":
            self["ntpoly"].binarymatrix = True
        else:
            self["ntpoly"].binarymatrix = False

    def set_name(self, name):
        """
        Set the calculation name.
        """
        self._default("control")
        self["control"].name = name

    def set_scf_convergence(self, density, energy):
        """
        Set parameters for the convergence of an scf calculation.
        """
        self._default("scf")
        self["scf"].thrden = density
        self["scf"].threne = energy

    def set_scf_maxiter(self, maxiter):
        """
        Set the maximum number of scf iterations.
        """
        self._default("scf")
        self["scf"].maxiter = maxiter

    def set_scf_guess(self, guess):
        """
        Set the guess for an scf calculation.
        """
        self._default("scf")
        self["scf"].guess = guess

        if guess == "sap":
            self._default("sap")
        elif guess == "huckel":
            self["scf"].guess = "readfock"
            self._default("huckel")

    def set_gradient(self):
        """
        Activates a calculation of the gradient.
        """
        self._default("scfgrad")

    def set_project(self):
        """
        Activate basis set projection.
        """
        self._default("projdens")


def _example():
    import f90nml

    # Create a basic input file.
    ifile = Inputfile()

    # Check setters.
    ifile.set_basic_rhf()
    ifile.set_scf_guess("sap")

    # Check access keys. It is case insensitive.
    print(ifile["int1"])
    print(ifile["SAP"])
    print(ifile["SAP"].asdict())

    # We can access individual members as well.
    print(ifile["int1"].thrint)
    ifile["int1"].thrint *= 1e-1
    print(ifile["int1"].thrint)

    # Check that we can write to file.
    scratch_file = "test.nml"
    with open(scratch_file, "w") as ofile:
        f90nml.write(ifile.asdict(), ofile, sort=True)

    # We can also build something from a file.
    with open(scratch_file, "r") as rfile:
        ifile2 = Inputfile(**f90nml.read(rfile))

    print(ifile2["scf"])


if __name__ == "__main__":
    _example()
