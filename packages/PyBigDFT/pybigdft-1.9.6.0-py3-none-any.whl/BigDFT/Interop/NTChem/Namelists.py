"""Namelists with types and default values for NTChem.
"""
from typing import Any, Callable, Dict, Iterable, List
import argparse
import dataclasses
import logging
import f90nml
import sys

logging.basicConfig(level=logging.INFO)


def _convert(x: Any) -> Any:
    if isinstance(x, str):
        return x.lower()
    else:
        return x


def _check_positivity(obj: Any, attr: str):
    val = getattr(obj, attr)
    if val <= 0:
        raise ValueError(f"{obj.__class__.__name__}: {attr} = {val} ≤ 0")


def _check_membership(
    obj: Any,
    attr: str,
    allowed_values: Iterable,
    *,
    converter: Callable[[Any], Any] = lambda x: _convert(x),
):
    val = getattr(obj, attr)
    if converter(val) not in map(converter, allowed_values):
        raise ValueError(
            f"{obj.__class__.__name__}: {attr} = {val!r} "
            f"not in {allowed_values}"
        )


def _check_membership_tuple(
    obj: Any,
    attrs: Iterable[str],
    allowed_tuples: Iterable[Iterable],
    *,
    converter: Callable[[Any], Any] = lambda x: _convert(x),
):
    val = [converter(getattr(obj, a)) for a in attrs]
    allowed_tuples = [[converter(v) for v in vs] for vs in allowed_tuples]
    if val not in allowed_tuples:
        raise ValueError(
            f"{obj.__class__.__name__}: {attrs} = {val!r} "
            f"not in {allowed_tuples}"
        )


def _check_subset(
    obj: Any,
    attr: str,
    univ: Iterable,
    *,
    converter: Callable[[Any], Any] = lambda x: _convert(x),
    predicate: Callable[[Any], bool] = lambda x: True,
):
    val = getattr(obj, attr)
    s = {converter(v) for v in val if predicate(v)}
    if not s.issubset({converter(e) for e in univ}):
        raise ValueError(f"DFT: {attr} = {s} is not subset of {univ}")


class NMLBase:
    def asdict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class BasInp(NMLBase):
    """Performs basic processing of the basis functions used in a calculation.

    Attributes:
        gtotype (str): Flag of Gaussian-type orbitals.

            - ``"Cartesian"``: use Cartesian Gaussian-type orbitals.
            - ``"Spherical"``: use Spherical Gaussian-type orbitals.
        iprint (int): Level of verbosity.

            - ``0``: medium
            - ``1``: verbose
            - ``2``: more verbose
        normf (bool): Whether to normalize basis functions.
        normp (bool): Whether to normalize primitive gaussians.
        shuffle (bool): Whether to shuffle the atoms for load balancing.
        shuffleseed (int): The seed for the random number generator when doing
            shuffling.
        units (str): Unit for atom coordinates in input file.

             - ``"Ang"``: use angstrom
             - ``"AU"``: use atomic unit
             - ``"Bohr"``: use Bohr (= ``"AU"``)
    """

    gtotype: str = "Spherical"
    iprint: int = 0
    normf: bool = True
    normp: bool = True
    shuffle: bool = False
    shuffleseed: int = 1
    units: str = "ang"

    def __post_init__(self):
        _check_membership(self, "gtotype", ["Cartesian", "Spherical"])
        _check_membership(self, "units", ["ang", "au", "bohr"])


@dataclasses.dataclass
class Control(NMLBase):
    """Basic job parameters.

    Attributes:
        name (str): Job prefix.
    """

    name: str = "ntchem"

    def __post_init__(self):
        if any(s in self.name for s in "\t\n !\"$&'()*;<>?[\\]{|}"):
            raise ValueError(f"Control: name = {self.name!r}")


@dataclasses.dataclass
class DAC(NMLBase):
    """Performs a divide and conquer eigenvalue solve.

    Attributes:
        iprint (int): Level of verbosity.

            - ``0``: medium
            - ``1``: verbose
            - ``2``: more verbose
        norbs (int): number of orbitals to compute
    """

    iprint: int = 0
    norbs: int = 0


@dataclasses.dataclass
class DFT(NMLBase):
    """Set the parameters for the exchange and correlation potential.

    Attributes:
        cfac (list): Mixing factors of correlation functionals.
        cfun (list): Specify DFT correlation functionals. This entry would be
            overwritten if :attr:`xctype` is valid. In addition to those for
            :attr:`ctype`, the followings are available:

            - ``"M06"``: [`Zhao 2008 TCA 120 215`_]
            - ``"M062X"``, ``"M06_2X"``: [`Zhao 2008 TCA 120 215`_]
            - ``"M06HF"``, ``"M06_HF"``: [`Zhao 2006 JPCA 110 5121`_,
              `Zhao 2006 JPCA 110 13126`_]
            - ``"M06L"``, ``"M06_L"``: [`Zhao 2006 JCP 125 194101`_]
            - ``"tauHCTH"``: [`Boese 2002 JCP 116 9559`_]
            - ``"tauHCTHhyb"``: [`Boese 2002 JCP 116 9559`_]
            - ``"VS98"``: [`VanVoorhis 1998 JCP 109 400`_]
        ctype (str): Specify DFT correlation functional. This entry is ignored
            if :attr:`xctype` is valid or :attr:`cfun` is not empty.

            - ``"LYP"``: [`Lee 1988 PRB 37 785`_], (GGA)
            - ``"OP"``: [`Tsuneda 1999 JCP 110 10664`_,
              `Tsuneda 1999 JCP 111 5656`_], (GGA).
              This functional must be used with ``"B88"`` or ``"LCB88"``
              exchange functionals
            - ``"P86"``: [`Perdew 1992 PRB 45 13244`_], (GGA)
            - ``"PBE"``: [`Perdew 1996 PRL 77 3865`_], (GGA)
            - ``"PW91"``: [`Perdew 1992 PRB 46 6671`_], (GGA)
            - ``"PW92"``: [`Perdew 1986 PRB 33 8822`_], (LDA)
            - ``"PZ81"``: [`Perdew 1981 PRB 23 5048`_], (LDA)
            - ``"VWN1RPA"``: [`Vosko 1980 CJP 58 1200`_], (LDA)
            - ``"VWN5"``: [`Vosko 1980 CJP 58 1200`_], (LDA)
            - ``"VWN5RPA"``: [`Vosko 1980 CJP 58 1200`_], (LDA)
        dftfun (bool): Flag to select the DFT library.

            - ``T`` : use exchange correlation functionals in dftfun_lib
            - ``F`` : use exchange correlation functionals in dft_lib
        gaufac (list): Mixing factors of gau type functional.
        gaumu (list): Exponents for gau type functional.
        hffac (float): Scaling factor of Hartree–Fock exchange.
        procslices (int): The number of process slices to use for DFT
            calculations.
        rsfac (list): Scaling factors of Long-range Hartree–Fock exchange.
            This keyword applies only when the exchange functional is
            range-separated type functional.
        rsmu (list): Parameters for the long range correction scheme. This
            keyword applies only when the exchange functional is
            range-separated type functional.
        xctype (str): Select standalone DFT exchange correlation functional.
            If valid, :attr:`xtype`, :attr:`xfun`, :attr:`ctype`, and
            :attr:`cfun` would be ignored.

            - ``"B3LYP"``: [`Becke 1993 JCP 98 5648`_], (GGA), (Hybrid)
            - ``"B97"``: [`Becke 1997 JCP 107 8554`_], (GGA), (Hybrid)
            - ``"B971"``, ``"B97_1"``: [`Hamprecht 1998 JCP 109 6264`_],
              (GGA), (Hybrid)
            - ``"B972"``, ``"B97_2"``: [`Willoson 2001 JCP 115 9233`_],
              (GGA), (Hybrid)
            - ``"B97D"``, ``"B97_D"``: [`Grimme 2006 JCC 27 1787`_], (GGA)
            - ``"BNL07"``: [`Livshits 2007 PCCP 9 2932`_], (GGA), (LC)
              (:attr:`dftfun` should be true)
            - ``"CAMB3LYP"``: [`Yanai 2004 CPL 393 51`_], (GGA), (LC), (Hybrid)
              (:attr:`dftfun` should be true)
            - ``"EDF1"``: [`Adamson 1998 CPL 284 6`_]
            - ``"HCTH"``: [`Hamprecht 1998 JCP 109 6264`_], (GGA)
            - ``"HCTH120"``: [`Boese 2000 JCP 112 1670`_], (GGA)
            - ``"HCTH147"``: [`Boese 2000 JCP 112 1670`_], (GGA)
            - ``"HCTH407"``: [`Boese 2001 JCP 114 5497`_], (GGA)
            - ``"LCPBE"``: [`Iikura 2001 JCP 115 3540`_]
            - ``"LCwPBE"``: [`Vydrov 2006 JCP 125 234109`_]
            - ``"M06"``: [`Zhao 2008 TCA 120 215`_], (meta-GGA), (Hybrid)
              (:attr:`dftfun` should be true)
            - ``"M062X"``, ``"M06_2X"``: [`Zhao 2008 TCA 120 215`_],
              (meta-GGA), (Hybrid) (:attr:`dftfun` should be true)
            - ``"M06HF"``, ``"M06_HF"``: [`Zhao 2006 JPCA 110 5121`_,
              `Zhao 2006 JPCA 110 13126`_], (meta-GGA), (Hybrid)
              (:attr:`dftfun` should be true)
            - ``"M06L"``, ``"M06_L"``: [`Zhao 2006 JCP 125 194101`_],
              (meta-GGA) (:attr:`dftfun` should be true)
            - ``"PW91"``: [`Perdew 1992 PRB 46 6671`_]
            - ``"tauHCTH"``: [`Boese 2002 JCP 116 9559`_]
            - ``"tauHCTHhyb"``: [`Boese 2002 JCP 116 9559`_]
            - ``"VS98"``: [`VanVoorhis 1998 JCP 109 400`_], (meta-GGA)
              (:attr:`dftfun` should be true)
            - ``"wB97"``: [`Chai 2008 JCP 128 084106`_], (GGA), (LC)
              (:attr:`dftfun` should be true)
            - ``"wB97X"``, ``"wB97_X"``: [`Chai 2008 JCP 128 084106`_], (GGA),
              (LC), (Hybrid) (:attr:`dftfun` should be true)
            - ``"wB97XD"``, ``"wB97_XD"``: [`Chai 2008 PCCP 10 6615`_], (GGA),
              (LC), (Hybrid) (:attr:`dftfun` should be true)
        xfac (list): Mixing factors of exchange functionals.
        xfun (list): Specify DFT exchange functionals. This entry would be
            overwritten if :attr:`xctype` is valid. In addition to those for
            :attr:`xtype`, the followings are available:

            - ``"B88GGA"``, ``"BeckeGGA"``:
            - ``"GauPBEh"``:
            - ``"M06"``: [`Zhao 2008 TCA 120 215`_]
            - ``"M062X"``, ``"M06_2X"``: [`Zhao 2008 TCA 120 215`_]
            - ``"M06HF"``, ``"M06_HF"``: [`Zhao 2006 JPCA 110 5121`_,
              `Zhao 2006 JPCA 110 13126`_]
            - ``"M06L"``, ``"M06_L"``: [`Zhao 2006 JCP 125 194101`_]
            - ``"VS98"``: [`VanVoorhis 1998 JCP 109 400`_]

        xtype (str): Specify DFT exchange functional. This entry is ignored if
            :attr:`xctype` is valid or :attr:`xfun` is not empty.

            - ``"B3"``:
            - ``"B88"``,  ``"Becke"``: [`Becke 1988 PRA 38 3098`_], (GGA)
            - ``"FT97B"``: [`Filatov 1997 MP 91 847`_]
            - ``"LCB88"``: [`Iikura 2001 JCP 115 3540`_], (GGA), (LC)
            - ``"LCLDA"``,  ``"LCSlater"``: [`Iikura 2001 JCP 115 3540`_],
              (LDA), (LC)
            - ``"LCPBE"``: [`Iikura 2001 JCP 115 3540`_], (GGA), (LC)
            - ``"LCwPBE"``: [`Vydrov 2006 JCP 125 234109`_]
            - ``"LDA"``, ``"Slater"``: [`Slater 1972 PRB 5 844`_], (LDA)
            - ``"mPW91"``: [`Adamo 1998 JCP 108 664`_]
            - ``"PBE"``: [`Perdew 1996 PRL 77 3865`_], (GGA)
            - ``"PW91"``: [`Perdew 1992 PRB 46 6671`_], (GGA)
    """

    cfac: List[float] = dataclasses.field(default_factory=list)
    cfun: List[str] = dataclasses.field(default_factory=list)
    ctype: str = ""
    dftfun: bool = True
    gaufac: List[float] = dataclasses.field(default_factory=list)
    gaumu: List[float] = dataclasses.field(default_factory=list)
    hffac: float = 0.0
    procslices: int = 0
    rsfac: List[float] = dataclasses.field(default_factory=list)
    rsmu: List[float] = dataclasses.field(default_factory=list)
    xctype: str = ""
    xfac: List[float] = dataclasses.field(default_factory=list)
    xfun: List[str] = dataclasses.field(default_factory=list)
    xtype: str = ""

    def __post_init__(self):
        def check_len(at_funcs: str, at_fctrs: str):
            funcs = getattr(self, at_funcs)
            fctrs = getattr(self, at_fctrs)
            err = (
                f"DFT: {at_funcs} = {funcs} mismatches with "
                f"{at_fctrs} = {fctrs}"
            )
            if funcs:
                if not fctrs:
                    fctrs = [1.0 for _ in funcs]
                    setattr(self, at_fctrs, fctrs)
                    logging.info(
                        f"DFT: {at_fctrs} is set to {fctrs} for "
                        f"{at_funcs} of {funcs}"
                    )
                elif len(funcs) != len(fctrs):
                    raise ValueError(err)
            elif fctrs:
                raise ValueError(err)

        check_len("cfun", "cfac")
        check_len("xfun", "xfac")

        known_xcs = [
            "B3LYP",
            "B97",
            "B971",
            "B972",
            "B97_1",
            "B97_2",
            "B97_D",
            "B97D",
            "BNL07",
            "CAMB3LYP",
            "EDF1",
            "HCTH",
            "HCTH120",
            "HCTH147",
            "HCTH407",
            "LCPBE",
            "LCwPBE",
            "M06",
            "M062X",
            "M06_2X",
            "M06_HF",
            "M06_L",
            "M06HF",
            "M06L",
            "PW91",
            "tauHCTH",
            "tauHCTHhyb",
            "VS98",
            "wB97",
            "wB97_X",
            "wB97_XD",
            "wB97X",
            "wB97XD",
        ]
        known_xs = [
            "B3",
            "B88",
            "B88GGA",
            "Becke",
            "BeckeGGA",
            "FT97B",
            "GauPBEh",
            "LCB88",
            "LCLDA",
            "LCPBE",
            "LCSlater",
            "LCwPBE",
            "LDA",
            "M06",
            "M062X",
            "M06_2X",
            "M06_HF",
            "M06_L",
            "M06HF",
            "M06L",
            "mPW91",
            "PBE",
            "PW91",
            "Slater",
            "VS98",
        ]
        known_cs = [
            "LYP",
            "M06",
            "M062X",
            "M06_2X",
            "M06_HF",
            "M06_L",
            "M06HF",
            "M06L",
            "OP",
            "P86",
            "PBE",
            "PW91",
            "PW92",
            "PZ81",
            "tauHCTH",
            "tauHCTHhyb",
            "VS98",
            "VWN1RPA",
            "VWN5",
            "VWN5RPA",
        ]

        if self.xctype:
            _check_membership(self, "xctype", known_xcs)
        if self.xtype:
            _check_membership(self, "xtype", known_xs)
        if self.ctype:
            _check_membership(self, "ctype", known_cs)
        _check_subset(self, "xfun", known_xs, predicate=lambda x: x)
        _check_subset(self, "cfun", known_cs, predicate=lambda x: x)

    def asdict(self):
        # Check compatability of functionals
        exchs = {
            k: getattr(self, k)
            for k in ["xctype", "xtype", "xfun"]
            if getattr(self, k)
        }
        corrs = {
            k: getattr(self, k)
            for k in ["xctype", "ctype", "cfun"]
            if getattr(self, k)
        }

        if not exchs:
            raise ValueError("DFT: exchange functional is not set")
        elif len(exchs) != 1:
            raise ValueError(f"DFT: exchange functionals conflict: {exchs}")
        if not corrs:
            raise ValueError("DFT: correlation functional is not set")
        elif len(corrs) != 1:
            raise ValueError(f"DFT: correlation functionals conflict: {corrs}")

        # Remove empty list entries.
        retval = super().asdict()
        retval = {k: v for k, v in retval.items() if not
                  (isinstance(v, list) and len(v) == 0)}

        return retval


@dataclasses.dataclass
class DFTD3(NMLBase):
    """Compute the van der Waals correction to the energy and forces.

    Attributes:
        anal (bool): Whether to perform a detailed analysis of pair
            contributions.
        echo (bool): Whether to print out detailed information.
        energy (bool): Whether to perform DFT-D energy calculation.
        func (str): Select DFT exchange correlation functional.

            - ``"B1B95"``:
            - ``"B2-PLYP"``:
            - ``"B2GP-PLYP"``:
            - ``"B3LYP"``:
            - ``"B3LYP/6-31Gd"``:
            - ``"B3PW91"``:
            - ``"B97D"``:
            - ``"BH-LYP"``:
            - ``"BLYP"``:
            - ``"BMK"``:
            - ``"BOP"``:
            - ``"BP86"``:
            - ``"BPBE"``:
            - ``"CAM-B3LYP"``:
            - ``"DFTB3"``:
            - ``"DSD-BLYP"``:
            - ``"DSD-BLYP-FC"``:
            - ``"HCTH120"``:
            - ``"HF"``:
            - ``"HF/MINIS"``:
            - ``"HF/MIXED"``:
            - ``"HF/SV"``:
            - ``"HF3C"``:
            - ``"HF3CV"``:
            - ``"HSE06"``:
            - ``"HSEsol"``:
            - ``"LC-wPBE"``:
            - ``"M05"``:
            - ``"M052X"``:
            - ``"M06"``:
            - ``"M062X"``:
            - ``"M06HF"``:
            - ``"M06L"``:
            - ``"MPW1B95"``:
            - ``"MPW2-PLYP"``:
            - ``"MPWB1K"``:
            - ``"MPWLYP"``:
            - ``"O-LYP"``:
            - ``"O-PBE"``:
            - ``"OPBE"``:
            - ``"OTPSS"``:
            - ``"PBE"``:
            - ``"PBE0"``:
            - ``"PBE38"``:
            - ``"PBEh-3c"``:
            - ``"PBEsol"``:
            - ``"PTPSS"``:
            - ``"PW1PW"``:
            - ``"PW6B95"``:
            - ``"PWB6K"``:
            - ``"PWGGA"``:
            - ``"PWPB95"``:
            - ``"REVPBE"``:
            - ``"REVPBE0"``:
            - ``"REVPBE38"``:
            - ``"REVSSB"``:
            - ``"RPBE"``:
            - ``"RPW86-PBE"``:
            - ``"SLATER-DIRAC-EXCHANGE"``:
            - ``"SSB"``:
            - ``"TPSS"``:
            - ``"TPSS0"``:
            - ``"TPSSH"``:
            - ``"wB97XD"``:
        grad (bool): Whether to perform DFT-D gradient calculation.
        version (int): Version of DFTD3 damping.

            - ``2``: DFT-D2
            - ``3``: DFT-D3
            - ``4``: DFT-D3 (Becke–Johnson)
    """

    anal: bool = True
    echo: bool = True
    energy: bool = True
    func: str = ""
    grad: bool = False
    version: int = 4

    def __post_init__(self):
        _check_membership(self, "version", [2, 3, 4])

    def asdict(self):
        if not self.func:
            raise ValueError("DFTD3: func is not set")
        return super().asdict()


@dataclasses.dataclass
class DFTNum(NMLBase):
    """Controls the parameters for the numerical grid used for integrating
    the exchange and correlation potential.

    Attributes:
        celltype (str): Atomic partition function.

            - ``"Becke"``: Becke's scheme
            - ``"SSF"``: scheme of Stratmann, Scuseria, and Frisch
        cuttol (float):
        geotol (float):
        gpwtol (float):
        grdtol (float):
        gridincore (bool):
        gridtype (str): Type of grid.

            - ``"Adaptive"``: adaptive grid of Krack and Koster
            - ``"Lebedev"``: Lebedev's grid

              :attr:`nang` must be one of 1, 6, 14, 26, 38, 50, 74, 86, 110,
              146, 170, 194, 230, 266, 302, 350, 434, 590, 770, 974, and 1202
            - ``"Prune"``: prune scheme based on Lebedev's grid

              (:attr:`nrad`, :attr:`nang`) must be one of (35, 110), (50, 194),
              (75, 194), (75, 302), and (99, 590)
        iprint (int): Level of verbosity.

            - ``0``: medium
            - ``1``: verbose
            - ``2``: more verbose
        nang (int): Number of angular integration points in Lebedev or
            prune grid. See :attr:`gridtype` for valid values.
        nrad (int): number of radial integration points in Lebedev or
            prune grid. See :attr:`gridtype` for valid values.
        quadrad (str): Quadrature type for radial part.

            - ``"EulMac"``: Euler–MacLaurin quadrature
            - ``"GauChe"``: Gauss–Chebyshev quadrature
        radtol (float):
        rhotol (float):
    """

    celltype: str = "SSF"
    cuttol: float = 1e-12
    geotol: float = 1e-6
    gpwtol: float = 1e-10
    grdtol: float = 1e-5
    gridincore: bool = False
    gridtype: str = "prune"
    iprint: int = 0
    nang: int = 590
    nrad: int = 99
    quadrad: str = "EulMac"
    radtol: float = 1e-12
    rhotol: float = 1e-12

    def __post_init__(self):
        _check_membership(self, "celltype", ["Becke", "SSF"])
        _check_membership(self, "gridtype", ["Adaptive", "Lebedev", "Prune"])
        _check_membership(self, "quadrad", ["EulMac", "GauChe"])

        for attr in ["nang", "nrad"]:
            _check_positivity(self, attr)

        if self.gridtype.lower() == "lebedev":
            try:
                _check_membership(
                    self,
                    "nang",
                    [
                        1,
                        6,
                        14,
                        26,
                        38,
                        50,
                        74,
                        86,
                        110,
                        146,
                        170,
                        194,
                        230,
                        266,
                        302,
                        350,
                        434,
                        590,
                        770,
                        974,
                        1202,
                    ],
                )
            except ValueError:
                logging.error(
                    f"DFTNum: gridtype = {self.gridtype!r}, invalid nang"
                )
                raise

        elif self.gridtype.lower() == "prune":
            try:
                _check_membership_tuple(
                    self,
                    ["nrad", "nang"],
                    [[35, 110], [50, 194], [75, 194], [75, 302], [99, 590]],
                )
            except ValueError:
                logging.error(
                    f"DFTNum: gridtype = {self.gridtype!r}, "
                    "invalid nrad and nang"
                )
                raise


@dataclasses.dataclass
class ECP(NMLBase):
    """Options for generating effective core potentials..

    Attributes:
        iprint (int): The level of verbosity when printing.
    """

    iprint: int = 0


@dataclasses.dataclass
class Huckel(NMLBase):
    """Generate a huckel guess.

    Attributes:
        iprint (int): Level of verbosity.

            - ``0``: medium
            - ``1``: verbose
            - ``2``: more verbose
        units (str): the unit of the ionization potentials

             - ``"eV"``: use electron volts
             - ``"AU"``: use atomic unit
    """

    iprint: int = 0
    units: str = "eV"

    def __post_init__(self):
        _check_membership(self, "units", ["au", "eV"])


@dataclasses.dataclass
class Int1(NMLBase):
    """Options for one electron integrals.

    Attributes:
        extrapolated (bool): Whether to extrapolate the density matrix using
            the new overlap matrix.
        iprint (int): The level of verbosity when printing.
        nddo (bool): Whether to invoke neglect of diatomic differential
            overlap, NDDO, approximation to molecular Hamiltonian.
        only1c (bool): Whether to discard multicenter ERI.
        procslices (int): The number of process slices to use.
        thrint (float): Threshold for ignoring ERI in constructing Fock matrix;
            the same threshold is applied to preexponent factor.
        thrprim (float): Threshold value of integration targeting primitive
            Gaussian.
        uhf (bool): Whether to perform spin-unrestricted HF/KS-DFT
            calculations.
    """

    extrapolated: bool = False
    iprint: int = 0
    nddo: bool = False
    only1c: bool = False
    procslices: int = 0
    thrint: float = 1.0e-15
    thrprim: float = 1.0e-20
    uhf: bool = False


@dataclasses.dataclass
class Int1D(NMLBase):
    """Options for one electron gradient integrals.

    Attributes:
        iprint (int): The level of verbosity when printing.
        thrint (float): Threshold for ignoring ERI in constructing Fock matrix;
            the same threshold is applied to preexponent factor.
        thrprim (float): Threshold value of integration targeting primitive
            Gaussian.
    """

    iprint: int = 0
    thrint: float = 1.0e-15
    thrprim: float = 1.0e-20


@dataclasses.dataclass
class Int2(NMLBase):
    """Options for two electron integrals.

    Attributes:
        inttype (str): Specify the method to evaluate electron repulsion
            integrals (ERI).
        nddo (bool): Whether to invoke neglect of diatomic differential
            overlap, NDDO, approximation to molecular Hamiltonian
        only1c (bool): Whether to discard multicenter ERI.
        only2c (bool): Whether to discard three-and four-center ERI.
        prelinkjthreshold (float): Threshold for prescreening coulomb matrix
            entries.
        prelinkkthreshold (float): Threshold for prescreening exchange matrix
            entries.
        procslices (int): The number of process slices to use.
        pscreen (bool): Whether to invoke Schwarz integral prescreening in
            direct SCF.
        sptype (str): Specify the method to evaluate ERI involving only s and p
            functions
        thrint (float): Threshold for ignoring ERI in constructing Fock matrix;
            the same threshold is applied to preexponent factor.
        thrpre (float): Threshold in Schwarz integral prescreening; this
            parameter has no effect when :attr:`pscreen` is false.
        thrprim (float): Threshold value of integration targeting primitive
            Gaussian.
    """

    inttype: str = "smash"
    nddo: bool = False
    only1c: bool = False
    only2c: bool = False
    prelinkjthreshold: float = 0.0
    prelinkkthreshold: float = 0.0
    procslices: int = 0
    pscreen: bool = True
    sptype: str = "smash"
    thrint: float = 1.0e-15
    thrpre: float = 1.0e-12
    thrprim: float = 1.0e-20

    def __post_init__(self):
        _check_membership(self, "inttype", ["libint", "smash"])
        _check_membership(self, "sptype", ["libint", "smash"])


@dataclasses.dataclass
class Int2D(NMLBase):
    """Options for two electron integrals.

    Attributes:
        dencut (float): Threshold for ignoring ERI derivatives in integral
            prescreening; this parameter has no effect when :attr:`denscreen`
            is false.
        denscreen (bool): Whether to invoke ERI derivatives prescreening using
            two-particle density matrix elements.
        procslices (int): The number of process slices to use.
        thrint (float): Threshold for ignoring ERI in constructing Fock matrix;
            the same threshold is applied to preexponent factor.
        thrprim (float): Threshold value of integration targeting primitive
            Gaussian.
    """

    dencut: float = 1e-13
    denscreen: bool = True
    procslices: int = 0
    thrint: float = 1.0e-15
    thrprim: float = 1.0e-20


@dataclasses.dataclass
class MDInt1(NMLBase):
    """Compute one electron integrals (custom). This can be used with
    Spin-Orbit calculations.

    Attributes:
        calchg (bool): Whether to calculate Coulomb attraction integrals from
            point charges.
        caldip (bool): Whether to calculate dipole moment integral; the origin
            of dipole moment integrals is assumed to be a coordinate origin.
        finite (bool): Whether to consider finite nuclear effect.
        iprint (int):
        nddo (bool): Whether to employ the neglect of diatomic differential
            overlap (NDDO) method.
        only1c (bool): Whether to discard multicenter integrals for nuclear
            attraction.
        only2c (bool):
        procslices (int): The number of process slices to use.
        qrel1c (bool): Whether to discard multicenter integrals for
            relativistic nuclear attraction.
        qrelham (str): One-electron relativistic Hamiltonian.

            - ``"DK1"``: use first-order Douglas–Kroll (DK) method
            - ``"DK2"``: use second-order Douglas–Kroll (DK) method
            - ``"DK3"``: use third-order Douglas–Kroll (DK) method
            - ``"FPRA"``: use free-particle regular approximation
            - ``"IORA"``: use infinite-order regular approximation
            - ``"NREL"``: nonrelativistic
            - ``"RESC"``: use relativistic elimination of small components
            - ``"ZORA"``: use zeroth-order regular approximation
        thrint (float): Threshold value of integration.
        thrprim (float): Threshold value of integration targeting primitive
            Gaussian.
        thrqrel (float): Threshold for linear dependency of relativistic
            Hamiltonian calculation
    """

    calchg: bool = False
    caldip: bool = False
    finite: bool = False
    iprint: int = 0
    nddo: bool = False
    only1c: bool = False
    only2c: bool = False
    procslices: int = 0
    qrel1c: bool = False
    qrelham: str = "NRel"
    thrint: float = 1e-15
    thrprim: float = 1e-20
    thrqrel: float = 1e-9

    def __post_init__(self):
        _check_membership(
            self,
            "qrelham",
            ["DK1", "DK2", "DK3", "FPRA", "IORA", "NRel", "RESC", "ZORA"],
        )


@dataclasses.dataclass
class NTPoly(NMLBase):
    """Options for using NTPoly.

    Attributes:
        binarymatrix (bool): Whether to write binary matrices or text.
        convergencethresholdpdm (float): The threshold for convergence of
            density matrix purification.
        doloadbalancingpdm (bool): Whether to do load balancing or not when
            performing purification.
        maxiterationspdm (int): The maximum number of purification
            iterations.
        pdmtype (str): The purification algorithm to use.

            - ``"EIG"``
            - ``"HPCP"``
            - ``"TC2"``
            - ``"TRS4"``
        thresholdpdm (float): The zero threshold for flushing small values.
        convergencethresholdorth (float): The threshold for convergence of
            orthogonalization.
        doloadbalancingorth (bool): Whether to do load balancing or not when
            performing orthogonalization.
        maxiterationsorth (int): The maximum number of orthogonalization
            iterations.
        orthtype (str): The orthgonalization algorithm to use.

            - ``"ORD5"``
            - ``"ORD2"``
        thresholdorth (float): The zero threshold for flushing small values.
    """

    binarymatrix: bool = False

    convergencethresholdpdm: float = 1e-10
    doloadbalancingpdm: bool = True
    maxiterationspdm: int = 100
    pdmtype: str = "TRS4"
    thresholdpdm: float = 0

    convergencethresholdorth: float = 1e-10
    doloadbalancingorth: bool = True
    maxiterationsorth: int = 100
    orthtype: str = "ORD5"
    thresholdorth: float = 0

    def __post_init__(self):
        _check_membership(
            self, "pdmtype", ["EIG", "HPCP", "TC2", "TRS4"],
        )
        _check_membership(
            self, "orthtype", ["ORD5", "ORD2", "EIG"],
        )


@dataclasses.dataclass
class ProjDens(NMLBase):
    """Options for density matrix projection from one basis to another.

    Attributes:
        iprint (int): The level of verbosity when printing.
        sorbit (bool): Whether to use density matrix which includes spin-orbit
            interaction.
        thrint (float): Threshold for ignoring ERI in constructing Fock matrix;
            the same threshold is applied to preexponent factor.
        thrprim (float): Threshold value of integration targeting primitive
            Gaussian.
        uhf (bool): Whether to perform spin-unrestricted calculations.
    """

    iprint: int = 0
    sorbit: bool = False
    thrint: float = 1.0e-15
    thrprim: float = 1.0e-20
    uhf: bool = False


@dataclasses.dataclass
class SAP(NMLBase):
    """Options for the superposition of atomic potentials calculation.

    Attributes:
        iprint (int): The level of verbosity when printing.
        pottype (bool): The type of potential.

            - ``"CAPX"``
            - ``"CHAX"``
            - ``"LDAX"``
            - ``"srCAPX"``
            - ``"srCHAX"``
            - ``"srLDAX"``
        procslices (int): The number of process slices to use.
    """

    iprint: int = 0
    pottype: str = "srCHAX"
    procslices: int = 0

    def __post_init__(self):
        _check_membership(
            self,
            "pottype",
            ["CAPX", "CHAX", "LDAX", "srCAPX", "srCHAX", "srLDAX"],
        )


@dataclasses.dataclass
class SAPNum(NMLBase):
    """Controls the parameters for the numerical grid used for integrating
    the super position of atomic potentials guess.

    Attributes:
        celltype (str): Atomic partition function.

            - ``"Becke"``: Becke's scheme
            - ``"SSF"``: scheme of Stratmann, Scuseria, and Frisch
        cuttol (float):
        geotol (float):
        gpwtol (float):
        grdtol (float):
        gridincore (bool):
        gridtype (str): Type of grid.

            - ``"Adaptive"``: adaptive grid of Krack and Koster
            - ``"Lebedev"``: Lebedev's grid

                :attr:`nang` must be one of 1, 6, 14, 26, 38, 50, 74, 86, 110,
                146, 170, 194, 230, 266, 302, 350, 434, 590, 770, 974, and 1202
            - ``"Prune"``: prune scheme based on Lebedev's grid

                (:attr:`nrad`, :attr:`nang`) must be one of (35, 110),
                (50, 194), (75, 194), (75, 302), and (99, 590)
        nang (int): Number of angular integration points in Lebedev or
            prune grid. See :attr:`gridtype` for valid values.
        nrad (int): Number of radial integration points in Lebedev or
            prune grid. See :attr:`gridtype` for valid values.
        quadrad (str): Quadrature type for radial part.

            - ``"EulMac"``: Euler–MacLaurin quadrature
            - ``"GauChe"``: Gauss–Chebyshev quadrature
        radtol (float):
        rhotol (float):
    """

    celltype: str = "SSF"
    cuttol: float = 1e-12
    geotol: float = 1e-6
    gpwtol: float = 1e-10
    grdtol: float = 1e-5
    gridincore: bool = False
    gridtype: str = "prune"
    nang: int = 110
    nrad: int = 35
    quadrad: str = "EulMac"
    radtol: float = 1e-12
    rhotol: float = 1e-12

    def __post_init__(self):
        _check_membership(self, "celltype", ["Becke", "SSF"])
        _check_membership(self, "gridtype", ["Adaptive", "Lebedev", "Prune"])
        _check_membership(self, "quadrad", ["EulMac", "GauChe"])

        for attr in ["nang", "nrad"]:
            _check_positivity(self, attr)

        if self.gridtype.lower() == "lebedev":
            try:
                _check_membership(
                    self,
                    "nang",
                    [
                        1,
                        6,
                        14,
                        26,
                        38,
                        50,
                        74,
                        86,
                        110,
                        146,
                        170,
                        194,
                        230,
                        266,
                        302,
                        350,
                        434,
                        590,
                        770,
                        974,
                        1202,
                    ],
                )
            except ValueError:
                logging.error(
                    f"SAPNum: gridtype = {self.gridtype!r}, invalid nang"
                )
                raise

        elif self.gridtype.lower() == "prune":
            try:
                _check_membership_tuple(
                    self,
                    ["nrad", "nang"],
                    [[35, 110], [50, 194], [75, 194], [75, 302], [99, 590]],
                )
            except ValueError:
                logging.error(
                    f"SAPNum: gridtype = {self.gridtype!r}, "
                    "invalid nrad and nang"
                )
                raise


@dataclasses.dataclass
class SCF(NMLBase):
    """Compute the energy of a system (standard).

    Attributes:
        chkpnt (int): How often to write out a check point.
        coultype (str): Computational type for two-electron Coulomb integrals.

            - ``"Analy"``: analytical integrals
            - ``"GFC"``: Gaussian.finite elements Coulomb (GFC) approximation
              (Serial only)
            - ``"None"``: no Coulomb calculation
            - ``"PS"``: pseudospectral approximation
            - ``"RI"``: resolution of the identity (RI) approximation
        dft (bool): Flag to carry out a DFT/UDFT calculation.

            - ``T``: DFT/UDFT calculation
            - ``F``: Hartree–Fock SCF/UHF calculation
        diagtype (str):
        diffden (bool): Whether to use the density difference technique to
            accelerate the SCF convergence.
        diistype (str): DIIS type.

            - ``"C1DIIS"``: original C1-DIIS
            - ``"C2DIIS"``: C2-DIIS of Sellers
            - ``"Anderson"``: pure anderson mixing of the density
            - ``"Potential"``: mixing of the potential.
        direct (bool): Whether the direct or disk-base SCF is used.
        exchtype (str): Computational type for HF exchange integrals.

            - ``"Analy"``: analytical integrals
            - ``"None"``: no exchange calculation
            - ``"PS"``: pseudospectral approximation
            - ``"RI"``: resolution of the identity (RI) approximation (NYI)
        extrapolate (bool): whether to extrapolate the input gues matrix.
        facdamp (float): Damping factor used in the damping method.
        facdisp (float):
        findiag (bool): Whether to diagonalize the Fock/KS matrix after the SCF
            calculation.
        finshift (bool): In a shift calculation, whether to turn off the shift
            at the end and proceed until reconvergence.
        guess (str): Guess of initial orbitals.

            - ``"Diagonal"``
            - ``"HCore"``
            - ``"GWH"``
            - ``"ReadDens"``
            - ``"ReadFock"``
            - ``"SAP"``
            - ``"ChkPnt"``
        hcoremask (bool): use the HCore density matrix as a filter.
        icharg (int): Total charge of the system.
        iprint (int): level of verbosity.
        maxdamp (int): Maximum number of iterations in the damping step in the
            SCF calculation.
        maxdiis (int): Maximum number of the DIIS error vectors.
        maxediis (int): Maximum number of EDIIS error vectors.
        maxiter (int): Maximum number of iterations.
        mixdamp (bool): Whether to combine the damping scheme with the DIIS
            method.
        mult (int): Spin multiplicity of the system
        nocca (int): Number of electrons for alpha orbitals.
            If ``0``, automatically determine the number of electrons for the
            neutral molecule.
        noccb (int): Number of electrons for beta orbitals.
            If ``0``, automatically determine the number of electrons for the
            neutral molecule.
        onbasdiis (bool): Whether to use orthogonalized of atomic basis
            functions.
        procslices (int): The number of process slices to use.
        pulayperiod (int): activate the periodic pulay diis algorithm, with
            a given period.
        readisq (bool): if true, checks for the inverse square root file on
            disk before computing.
        scftype (str): Type of SCF wavefunction.

            - ``""``: ``"RHF"``/``"UHF"`` for even/odd electrons, respectively
            - ``"RHF"``: restricted HF/DFT
            - ``"UHF"``: unrestricted HF/DFT
            - ``"CUHF"``: constrained (pseudo-canonical) HF/DFT
            - ``"ROHF"``: restricted open HF/DFT
        skip1e (bool): Whether to skip the calculation of one-electron
            kinetic-energy and potential terms
        skip2e (bool): Whether to skip the calculation of two-electron terms.
        thrden (float): Convergence criterion for the density matrix.
        threne (float): Convergence criterion for the total SCF energy.
        throffmdamp (float): threshold to turn off damping.
        throffediis (float): threshold to turn off EDIIS
        vshift (float): Energy shift for virtual orbitals.
        writeanal (logical): whether to write the analyis matrices.
    """

    chkpnt: int = 0
    coultype: str = "Analy"
    dft: bool = False
    diagtype: str = ""
    diffden: bool = True
    diistype: str = "C1DIIS"
    direct: bool = True
    exchtype: str = "Analy"
    extrapolate: bool = False
    facdamp: float = 0.4
    facdisp: float = 0.0
    findiag: bool = False
    finshift: bool = True
    guess: str = "ReadDens"
    hcoremask: bool = False
    icharg: int = 0
    iprint: int = 0
    maxdamp: int = 2
    maxdiis: int = 6
    maxediis: int = 0
    maxiter: int = 200
    mixdamp: bool = True
    mult: int = 1
    nocca: int = 0
    noccb: int = 0
    onbasdiis: bool = False
    procslices: int = 0
    pulayperiod: int = 0
    readisq: bool = False
    scftype: str = ""
    skip1e: bool = False
    skip2e: bool = False
    sts: float = 0.0
    thrden: float = 1e-5
    threne: float = 1e-6
    throffediis: float = 1e-5
    throffmdamp: float = 1e-2
    vshift: float = 0.1
    writeanal: bool = False

    def __post_init__(self):
        _check_membership(
            self, "coultype", ["Analy", "GFC", "None", "PS", "RI"]
        )
        _check_membership(self, "diistype", ["C1DIIS", "C2DIIS", "Anderson",
                                             "Potential"])
        _check_membership(self, "exchtype", ["Analy", "None", "PS", "RI"])
        _check_membership(
            self, "guess", ["ChkPnt", "Diagonal", "HCore", "GWH", "ReadDens",
                            "ReadFock", "SAP"]
        )
        _check_membership(self, "scftype", ["", "CUHF", "RHF", "ROHF", "UHF"])


@dataclasses.dataclass
class SCFGrad(NMLBase):
    """Compute the gradient of the energy of a system (standard).

    Attributes:
        couldtype (str): Flag for Coulomb integration.

            - ``""``: use the same method as the previous SCF calculation
            - ``"Analy"``: use analytical method for Coulomb-type integration
            - ``"RI"``: use resolution-of-identity (RI) approximation
        exchdtype (str): Flag for exchange integration.

            - ``""``: use the same method as the previous SCF calculation
            - ``"Analy"``: use analytical method for exchange-type integration
        grad (bool): Whether to calculate energy gradient.
        iprint (int):
        procslices (int): The number of process slices to use.
        readdenew (bool):
    """

    couldtype: str = ""
    exchdtype: str = ""
    grad: bool = True
    iprint: int = 0
    procslices: int = 0
    readdenew: bool = False


@dataclasses.dataclass
class SOInt1(NMLBase):
    """Options for one electron integrals.

    Attributes:
        clight (float): Speed of light (atomic unit).
        finite (bool): Whether to consider finite nuclear effect.
        iprint (int): The level of verbosity when printing.
        mpecp (bool):
        only1c (bool): Whether to discard multicenter ERI.
        procslices (int): The number of process slices to use.
        qrelham (str): Flag for spin-orbit calculations.

            - ``"BP"``: use Breit–Pauli approximation
            - ``"DK1"``: use first-order Douglas–Kroll (DK) method
            - ``"IORA"``: use infinite-order regular approximation
            - ``"NREL"``: alias to ``"BP"``
            - ``"ZORA"``: use zeroth-order regular approximation
        snso (bool): Flag for screened-nuclear spin-orbit (SNSO)
            approximation for two-electron spin-orbit contribution.
        thrint (float): Threshold for ignoring ERI in constructing Fock matrix;
            the same threshold is applied to preexponent factor.
        thrprim (float): Threshold value of integration targeting primitive
            Gaussian.
        thrqrel (float): Threshold for linear dependency of relativistic
            Hamiltonian calculation.
    """

    clight: float = 137.0359895
    finite: bool = False
    iprint: int = 0
    mpecp: bool = False
    only1c: bool = False
    procslices: int = 0
    qrelham: str = "NREL"
    snso: bool = True
    thrint: float = 1.0e-15
    thrprim: float = 1.0e-20
    thrqrel: float = 1.0e-9

    def __post_init__(self):
        _check_membership(
            self, "qrelham", ["BP", "DK1", "IORA", "NREL", "ZORA"]
        )


@dataclasses.dataclass
class SOPolar(NMLBase):
    """

    Attributes:
        citype (str):
        iprint (int):
        iprintfock (int):
        maxiter (int):
        maxsub (int):
        method (str):
        nactcorea (int):
        nactcoreb (int):
        nblock (int):
        nfrzoa (int):
        nfrzob (int):
        nfrzva (int):
        nfrzvb (int):
        noncol (bool):
        nstates (int):
        omega (complex):
        procslices (int): The number of process slices to use.
        thrconv (float):
    """

    citype: str = "CIS"
    iprint: int = 0
    iprintfock: int = 0
    maxiter: int = 200
    maxsub: int = 600
    method: str = "DISK"
    nactcorea: int = 0
    nactcoreb: int = 0
    nblock: int = 0
    nfrzoa: int = 0
    nfrzob: int = 0
    nfrzva: int = 0
    nfrzvb: int = 0
    noncol: bool = False
    nstates: int = 3
    omega: complex = complex(0, 0)
    procslices: int = 0
    thrconv: float = 1e-5


@dataclasses.dataclass
class SOSCF(NMLBase):
    """Compute the energy of a system including Spin-Orbit effects.

    Attributes:
        coultype (str): Computational type for two-electron Coulomb integrals.

            - ``"Analy"``: analytical integrals
            - ``"GFC"``: Gaussian-finite elements Coulomb (GFC) approximation
              (Serial only)
            - ``"None"``: no Coulomb calculation
            - ``"PS"``: pseudospectral approximation
            - ``"RI"``: resolution of the identity (RI) approximation
        dft (bool): Flag to carry out a DFT/UDFT calculation.

            - ``T`` : DFT/UDFT calculation
            - ``F`` : Hartree–Fock SCF/UHF calculation
        diagtype (str):
        diffden (bool): Flag to use the density difference technique to
            accelerate the SCF convergence.
        diistype (str): DIIS Type.

            - ``"C1DIIS"``: original C1-DIIS
            - ``"C2DIIS"``: C2-DIIS of Sellers
        direct (bool): Whether the direct or disk-base SCF is used.
        exchtype (str): Computational type for HF exchange integrals.

            - ``"Analy"``: analytical integrals
            - ``"None"``: no exchange calculation
            - ``"PS"``: pseudospectral approximation
            - ``"RI"``: resolution of the identity (RI) approximation (NYI)
        facdisp (float):
        guess (str): Guess of initial orbitals.

            - ``"HCore"``
            - ``"ReadDens"``
        icharg (int): Total charge of the system.
        iprint (int):
        magfld (float): Magnetic field strength.
        maxdiis (int): Maximum number of the DIIS error vectors.
        maxiter (int): Maximum number of iterations.
        mult (int): Spin multiplicity of the system.
        ncdft (bool):
        nocca (int): Number of electrons for alpha orbitals.
            If ``0``, automatically determine the number of electrons for the
            neutral molecule.
        noccb (int): Number of electrons for beta orbitals.
            If ``0``, automatically determine the number of electrons for the
            neutral molecule.
        onbasdiis (bool):
        pdmtype (str):
            - ``"TC2"``
            - ``"TRS4"``
        procslices (int): The number of process slices to use.
        scftype (str):
        skip1e (bool): Whether to skip the calculation of one-electron
            kinetic-energy and potential terms
        skip2e (bool): Whether to skip the calculation of two-electron terms
        sofld (float):
        souhf (bool):
        spcdir (int): ``1`` (*x*), ``2`` (*y*), ``3`` (*z*).
            If ``0`` (default), set to the same as :attr:`spndir`.
        spndir (int): ``1`` (*x*), ``2`` (*y*), ``3`` (*z*).
        thrden (float): Convergence criterion for the density matrix.
        threne (float): Convergence criterion for the total SCF energy.
        vshift (float): Energy shift for virtual orbitals.
    """

    coultype: str = "Analy"
    dft: bool = False
    diagtype: str = "PDMSCF"
    diffden: bool = True
    diistype: str = "C1DIIS"
    direct: bool = True
    exchtype: str = "Analy"
    facdisp: float = 0.0
    guess: str = "ReadDens"
    icharg: int = 0
    iprint: int = 0
    magfld: float = 0.0
    maxdiis: int = 6
    maxiter: int = 200
    mult: int = 1
    ncdft: bool = False
    nocca: int = 0
    noccb: int = 0
    onbasdiis: bool = False
    pdmtype: str = "TC1"
    procslices: int = 0
    scftype: str = "GUHF"
    skip1e: bool = False
    skip2e: bool = False
    sofld: float = 0.0
    souhf: bool = False
    spcdir: int = 0
    spndir: int = 3
    thrden: float = 1.0e-5
    threne: float = 1.0e-6
    vshift: float = 0.1

    def __post_init__(self):
        _check_membership(
            self, "coultype", ["Analy", "GFC", "None", "PS", "RI"]
        )
        _check_membership(self, "diistype", ["C1DIIS", "C2DIIS"])
        _check_membership(self, "exchtype", ["Analy", "None", "PS", "RI"])
        _check_membership(self, "guess", ["HCore", "ReadDens"])
        _check_membership(self, "pdmtype", ["TC1", "TRS4"])
        _check_membership(self, "scftype", ["GUHF", "KRHF"])
        _check_membership(self, "spcdir", range(4))
        _check_membership(self, "spndir", range(1, 4))


@dataclasses.dataclass
class TDDFT(NMLBase):
    """Options for TDDFT calculations.

    Todo: when Kamiya-san finishes TDDFT, document this class.
    """

    pass


namelists = [
    "BasInp",
    "Control",
    "DAC",
    "DFT",
    "DFTD3",
    "DFTNum",
    "ECP",
    "Huckel",
    "Int1",
    "Int1D",
    "Int2",
    "Int2D",
    "MDInt1",
    "NTPoly",
    "ProjDens",
    "SAP",
    "SAPNum",
    "SCF",
    "SCFGrad",
    "SOInt1",
    "SOPolar",
    "SOSCF",
    "TDDFT",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("w"),
        default="-",
        help="output file for namelists, defaulted to stdout",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="list supported namelists and exit",
    )
    parser.add_argument(
        "namelist",
        nargs="*",
        default=namelists,
        help="namelists to output, defaulted to all the supported ones",
    )

    args = parser.parse_args()

    if args.list:
        print(*namelists)
        return

    lowered_namelists = {nl.lower(): globals()[nl] for nl in namelists}
    try:
        d = {
            nl: lowered_namelists[nl.lower()]().asdict()
            for nl in args.namelist
        }
    except KeyError as e:
        logging.error(f"Unsupported namelist: {e.args}")
        sys.exit(1)
    else:
        f90nml.write(d, args.output, sort=True)


if __name__ == "__main__":
    main()
