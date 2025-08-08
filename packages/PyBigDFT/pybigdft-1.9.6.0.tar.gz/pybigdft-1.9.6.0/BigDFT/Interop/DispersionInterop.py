"""
Provides an interface to DFTD3/DFTD4.

https://github.com/dftd3/simple-dftd3
https://github.com/dftd4/dftd4
"""


def bigdft_to_dftd(sys, version="dftd3"):
    """
    Converts a BigDFT system to the `simple-dftd3` format.
    
    Args:
        sys (BigDFT.Systems.System): the system to compute.
        version (str): either `dftd3` or `dftd4`.
        
    Returns:
        (dftd3.interface.DispersionModel): a dispersion model for use.
    """
    from numpy import array

    # Switch on version
    if version == "dftd3":
        from dftd3.interface import DispersionModel
    elif version == "dftd4":
        from dftd4.interface import DispersionModel
    else:
        raise ValueError("version must be dftd3 or dftd4")

    positions = []
    numbers = []
    for frag in sys.values():
        for at in frag:
            positions.append(at.get_position("bohr"))
            numbers.append(at.atomic_number)

    return DispersionModel(array(numbers), array(positions))


def get_damping_parameters(xc, damping, version="dftd3"):
    """
    Generate the damping parameters.

    Args:
        xc (str): XC functional
        damping (str): for DFTD3 `ZeroDampingParam`, `RationalDampingParam`,
            `ModifiedRationalDampingParam`, `ModifiedZeroDampingParam`,
            `OptimizedPowerDampingParam`; for DFTD4 `DampingParam`
        version (str): either `dftd3` or `dftd4`.

    Returns:
        (dftd3.interface.DampingParam): damping parameter object.
    """
    # Switch on version
    if version == "dftd3":
        from dftd3 import interface
    elif version == "dftd4":
        from dftd4 import interface
    else:
        raise ValueError("version must be dftd3 or dftd4")

    d = getattr(interface, damping)

    return d(method=xc)


def pairwise_fragment_interactions(sys, xc, damping, version="dftd3"):
    """
    Compute the dispersion interaction energy between all pairs of fragments.

    Args:
        sys (BigDFT.Systems.System): the system to compute.
        xc (str): XC functional
        damping (str): for DFTD3 `ZeroDampingParam`, `RationalDampingParam`,
            `ModifiedRationalDampingParam`, `ModifiedZeroDampingParam`,
            `OptimizedPowerDampingParam`; for DFTD4 `DampingParam`
        version (str): either `dftd3` or `dftd4`.

    Returns:
        (dict): dictionary of dictionaries with pairwise interactions.
    """
    # Compute
    model = bigdft_to_dftd(sys, version=version)
    param = get_damping_parameters(xc=xc, damping=damping, version=version)
    pairs = model.get_pairwise_dispersion(param)

    # Translate to fragments
    lookup = []
    for fragid, frag in sys.items():
        for at in frag:
            lookup.append(fragid)

    result = {x: {y: 0.0 for y in sys} for x in sys}
    for i, vals in enumerate(pairs["additive pairwise energy"]):
        fid1 = lookup[i]
        for j, v in enumerate(vals):
            fid2 = lookup[j]
            result[fid1][fid2] += v

    return result


def _example():
    """Test the dispersion approach"""
    from BigDFT.IO import XYZReader
    from BigDFT.Systems import System
    from BigDFT.Fragments import Fragment
    from copy import deepcopy

    # BigDFT Molecule
    reader = XYZReader("Ar")
    sys = System()
    sys["FRA:1"] = Fragment(xyzfile=reader)
    sys["FRA:2"] = deepcopy(sys["FRA:1"])
    sys["FRA:2"].translate([-2, 0, 0])

    # Convert to DispersionModel
    model3 = bigdft_to_dftd(sys, version="dftd3")
    model4 = bigdft_to_dftd(sys, version="dftd4")

    # Lookup the parameters
    param3 = get_damping_parameters(xc="pbe", 
                                    damping="RationalDampingParam",
                                    version="dftd3")
    param4 = get_damping_parameters(xc="pbe", 
                                    damping="DampingParam",
                                    version="dftd4")
    # Get the energy
    dispersion_energy = model3.get_dispersion(param3, grad=False)["energy"]
    print("DFTD3", dispersion_energy)
    if abs(dispersion_energy - (-0.0008628959813317974)) > 1e-8:
        raise Exception("Test Failed")

    dispersion_energy = model4.get_dispersion(param4, grad=False)["energy"]
    print("DFTD4", dispersion_energy)
    if abs(dispersion_energy - (-0.0008417917644302559)) > 1e-8:
        raise Exception("Test Failed")

    # Pairwise interactions
    pe = pairwise_fragment_interactions(sys, xc="blyp",
                                        damping="OptimizedPowerDampingParam",
                                        version="dftd3")
    print(pe)
    if abs(pe["FRA:1"]["FRA:2"] - (-0.00016771172526004852)) > 1e-8:
        raise Exception("Test Failed")
