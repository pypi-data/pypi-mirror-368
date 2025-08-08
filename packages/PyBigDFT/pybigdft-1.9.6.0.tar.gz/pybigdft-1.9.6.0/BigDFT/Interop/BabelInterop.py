"""
This module contains some wrappers for using OpenBabel to perform
various operations on BigDFT molecules.

https://open-babel.readthedocs.io/en/latest/UseTheLibrary/Python.html
"""

# openbabel's forcefields can have different energy units.
_energy_conversion = {"kJ/mol": 0.00038, "kcal/mol": 0.0016}


def convert_system_to_babel(sys):
    """
    Convert a BigDFT system to an open babel molecule.

    Args:
      sys (BigDFT.Systems.System): the system to convert.

    Returns:
      (openbabel.OBMol): an open babel type molecule.
    """
    from BigDFT.IO import write_pdb
    from openbabel.openbabel import OBMol, OBConversion
    # py2 workaround
    from sys import version_info
    if version_info[0] < 3:
        from io import BytesIO as StringIO
    else:
        try:
            from io import StringIO
        except ImportError:
            from StringIO import StringIO

    # We convert by way of pdb file.
    conv = OBConversion()
    conv.SetInFormat("pdb")

    sval = StringIO()
    write_pdb(sys, sval)

    mol = OBMol()
    conv.ReadString(mol, sval.getvalue())

    return mol


def convert_babel_to_system(mol):
    """
    Convert a BigDFT fragment to an open babel molecule.

    Args:
      mol (openbabel.OBMol): the molecule to convert.

    Returns:
      (BigDFT.Systems.System): bigdft system.
    """
    from BigDFT.IO import read_mol2
    from openbabel.openbabel import OBConversion
    # py2 workaround
    from sys import version_info
    if version_info[0] < 3:
        from io import BytesIO as StringIO
    else:
        try:
            from io import StringIO
        except ImportError:
            from StringIO import StringIO

    conv = OBConversion()
    conv.SetOutFormat("mol2")

    sval = StringIO(conv.WriteString(mol))
    return read_mol2(sval)


def compute_babel_matching(sys, bsys, check_matching=True):
    """
    Similar to the cannonical `compute matching` of the system class, this 
    creates a lookup table mapping each atom in a system class to the index
    of the atom in a babel system.

    Args:
        sys (BigDFT.Systems.System): the bigdft system.
        bsys (openbabel.openbabel.OBMol): the openbabel version of the system.
        check_matching (bool): if set to True, this will raise an error
            if we can't match all of the atoms in the system.

    Returns:
        (dict): a mapping from a system to indices in the atom list. If
            an atom is not in the list, an index value of -1 is assigned.
    """
    from openbabel.openbabel import OBMolAtomIter
    from BigDFT.Atoms import Atom, number_to_symbol

    # Convert babel system to a list of atoms
    atm_list = []
    for bat in OBMolAtomIter(bsys):
        pos = [bat.GetX(), bat.GetY(), bat.GetZ()]
        atnum = bat.GetAtomicNum()
        at = Atom({number_to_symbol(atnum): pos,
                  "units": "angstroem"})
        atm_list.append(at)

    # Run compute matching.
    return sys.compute_matching(atm_list, check_matching)


def build_from_smiles(smi, form="smi"):
    """
    Build a system from its smiles representation.
    
    smi (str): the smiles string.
    form (str): the format of the smiles (either "smi" or "can")
    """
    from openbabel.openbabel import OBConversion, OBMol, OBBuilder

    # Check args
    if form.lower() not in ["can", "smi"]:
        raise ValueError("Form must be `can` or `smi`")
        
    # Basic conversion
    conv = OBConversion()
    conv.SetInFormat(form)
    mol = OBMol()
    conv.ReadString(mol, smi)

    # Build 3D Rep
    mol.AddHydrogens()
    builder = OBBuilder()
    builder.Build(mol)
    
    return convert_babel_to_system(mol)


def compute_smiles(sys, form="smi"):
    """
    Computes the SMILES representation of a given system.

    Args:
      sys (BigDFT.System.Systems): the system to compute the
        representation of.

    Return:
      (str): the smiles representation of this molecule.
    """
    from openbabel.openbabel import OBConversion

    # Check args
    if form.lower() not in ["can", "smi"]:
        raise ValueError("Form must be `can` or `smi`")

    # Convert
    conv = OBConversion()
    mol = convert_system_to_babel(sys)
    conv.SetOutFormat(form)

    # Strip formatting
    retstr = conv.WriteString(mol)
    retstr = retstr.replace("\n", "")
    retstr = retstr.replace("\t", "")

    return retstr


def compute_fingerprint(sys, fps="fp2"):
    """
    Computes the fingerprint for a particular fragment.

    Args:
      sys (BigDFT.Systems.System): the fragment to compute the
        representation of.
      fps (str): the type of finger print to compute.

    Return:
      (openbabel.OBFingerprint): a fingerprint for this fragment.
    """
    from openbabel.openbabel import OBFingerprint, vectorUnsignedInt
    
    printer = OBFingerprint.FindType(fps)
    fp = vectorUnsignedInt()
    printer.GetFingerprint(convert_system_to_babel(sys), fp)
    
    return fp


def generate_connectivity(sys):
    """
    Generate the connectivity matrix for a system.

    Args:
        sys (BigDFT.Systems.System): the system to generate for.
    """
    from BigDFT.Systems import copy_bonding_information
    
    bsys = convert_system_to_babel(sys)
    consys = convert_babel_to_system(bsys)
    
    copy_bonding_information(consys, sys)


def get_partial_charges(sys, charge_model="gasteiger"):
    """
    Assign partial charges to a system using OpenBabel's charge
    models.

    Args:
        sys (BigDFT.Systems.System): the system to update.
    """
    from openbabel.openbabel import OBChargeModel
    
    # Convert to babel
    bsys = convert_system_to_babel(sys)
    matching = compute_babel_matching(sys, bsys)
    
    # Compute the charges
    cm = OBChargeModel.FindType(charge_model)
    cm.ComputeCharges(bsys)
    charges = cm.GetPartialCharges()
    
    # Assign back
    for fragid, frag in sys.items():
        for i, at in enumerate(frag):
            idx = matching[fragid][i]
            at["q0"] = [charges[idx]]


def system_energy(sys, forcefield="MMFF94", verbose=False):
    """
    Compute the energy of a system using an openbabel forcefield.

    Args:
      sys (BigDFT.Systems.System): the system to compute.
      forcefield (str): the type of forcefield to use.
      verbose (bool): whether to have openbabel run in verbose mode.

    Returns:
      (float): the energy value computed in Hartree.
    """
    from openbabel.openbabel import OBForceField, OBFF_LOGLVL_LOW

    # Setup the forcefield
    ff = OBForceField.FindForceField(forcefield)
    mol = convert_system_to_babel(sys)
    ff.Setup(mol)

    if verbose:
        ff.SetLogToStdOut()
        ff.SetLogLevel(OBFF_LOGLVL_LOW)

    # Call the energy routine.
    return ff.Energy() * _energy_conversion[ff.GetUnit()]


def optimize_system(sys, forcefield="MMFF94", method="SteepestDescent",
                    steps=1000, econv=1e-6, verbose=False):
    """
    Optimize the geometry of a given fragment.

    Args:
      sys (BigDFT.Systems.System): the fragment to optimize.
      forcefield (str): the type of forcefield to use.
      method (str): optimization method.
      steps (int): maximum steps to take.
      econv (float): convergence criteria
      verbose (bool): if True, the openbabel output will be printed.

    Returns:
      (BigDFT.Systems.System): a new fragment with the optimized positions.
    """
    from openbabel.openbabel import OBForceField, OBFF_LOGLVL_LOW
    from openbabel.openbabel import OBMolAtomIter
    from copy import deepcopy

    # Convert to babel
    bsys = convert_system_to_babel(sys)
    matching = compute_babel_matching(sys, bsys)

    # Setup the forcefield
    ff = OBForceField.FindForceField(forcefield)
    ff.Setup(bsys)
    if verbose:
        ff.SetLogToStdOut()
        ff.SetLogLevel(OBFF_LOGLVL_LOW)

    # Call the optimization routine.
    if method == "SteepestDescent":
        ff.SteepestDescent(steps, econv)
    elif method == "ConjugateGradients":
        ff.ConjugateGradients(steps, econv)
    else:
        raise ValueError("Invalid minimization method.")

    # Extract out the the positions.
    ff.GetCoordinates(bsys)
    
    # Copy those new positions
    positions = []
    for bat in OBMolAtomIter(bsys):
        pos = [bat.GetX(), bat.GetY(), bat.GetZ()]
        positions.append(pos)
        
    newsys = deepcopy(sys)
    for fragid, frag in newsys.items():
        for i, at in enumerate(frag):
            idx = matching[fragid][i]
            at.set_position(positions[idx], units="angstroem")

    return newsys


def molecular_dynamics(sys, steps, temperature, forcefield="MMFF94",
                       timestep=0.001, verbose=False):
    """
    Run molecular dynamics on a given fragment..

    Args:
      sys (BigDFT.Systemtems.System): the system to run.
      steps (int): the number of MD steps to take.
      temperature (float): temperature in K.
      forcefield (str): the type of forcefield to use.
      timestep (float): time step in picoseconds.
      constraints (list): for each atom, list whether it if frozen or not.
      verbose (bool): if True, the openbabel output will be printed.

    Returns:
      (BigDFT.Systems.System): a new system with the optimized positions.
    """
    from openbabel.openbabel import OBForceField, OBFF_LOGLVL_LOW
    from openbabel.openbabel import OBMolAtomIter
    from copy import deepcopy

    # Convert to babel
    bsys = convert_system_to_babel(sys)
    matching = compute_babel_matching(sys, bsys)

    # Setup the calculation
    ff = OBForceField.FindForceField(forcefield)
    bsys = convert_system_to_babel(sys)
    ff.Setup(bsys)
    if verbose:
        ff.SetLogToStdOut()
        ff.SetLogLevel(OBFF_LOGLVL_LOW)

    # Run
    ff.MolecularDynamicsTakeNSteps(steps, temperature, timestep)

    # Extract out the the positions.
    ff.GetCoordinates(bsys)

    # Copy those new positions
    positions = []
    for bat in OBMolAtomIter(bsys):
        pos = [bat.GetX(), bat.GetY(), bat.GetZ()]
        positions.append(pos)
        
    newsys = deepcopy(sys)
    for fragid, frag in newsys.items():
        for i, at in enumerate(frag):
            idx = matching[fragid][i]
            at.set_position(positions[idx], units="angstroem")

    return newsys


def compute_system_forces(sys, forcefield="MMFF94", verbose=False):
    """
    Assign the forces of a system using an openbabel forcefield.

    Args:
      sys (BigDFT.Systems.System): the system to compute.
      forcefield (str): the type of forcefield to use.
      verbose (bool): whether to have openbabel run in verbose mode.

    Returns:
      (float): the energy of the system.
    """
    from openbabel.openbabel import OBForceField, OBFF_LOGLVL_LOW
    from BigDFT.Atoms import AU_to_A
    from openbabel.openbabel import OBMolAtomIter

    # Convert to babel
    bsys = convert_system_to_babel(sys)
    matching = compute_babel_matching(sys, bsys)
    
    # Setup the forcefield
    ff = OBForceField.FindForceField(forcefield)
    ff.Setup(bsys)
    if verbose:
        ff.SetLogToStdOut()
        ff.SetLogLevel(OBFF_LOGLVL_LOW)

    # Compute the forces.
    energy_out = ff.Energy() * _energy_conversion[ff.GetUnit()]
    gradients = []
    for bat in OBMolAtomIter(bsys):
        grad = ff.GetGradient(bat)
        convgrad = [grad.GetX(), grad.GetY(), grad.GetZ()]
        convgrad = [x * _energy_conversion[ff.GetUnit()]/AU_to_A
                    for x in convgrad]
        gradients.append(convgrad)

    # Assign
    for fragid, frag in sys.items():
        for i, at in enumerate(frag):
            idx = matching[fragid][i]
            at.set_force(gradients[idx])

    return energy_out


def _setup_constraints(forcefield, constraints):
    """
    This helper routine takes a list of constraints and updates
    as forcefield with those values.
    """
    constr = forcefield.GetConstraints()
    for i in range(0, len(constraints)):
        if constraints[i] is None:
            continue
        elif constraints[i] == "fxyz" or constraints[i] == "f":
            constr.AddAtomConstraint(i+1)
        elif constraints[i] == "fx":
            constr.AddAtomXConstraint(i+1)
        elif constraints[i] == "fy":
            constr.AddAtomYConstraint(i+1)
        elif constraints[i] == "fz":
            constr.AddAtomZConstraint(i+1)
    forcefield.SetConstraints(constr)


def add_hydrogens(sys):
    """Add hydrogens to a BigDFT System.

    This routine may be useful to complete a ligand which is not provided
    with hydrogen atoms, for instance coming from PDB database.

    Args:
        sys (Systems.System): the original system without hydrogens.

    Returns:
        Systems.System: the system with hydrogen included.
            Hydrogens should preserve the residue identification in the case
            of a pdb. This should be controlled to avoid mistakes in the
            choice of tautomers.

    """
    from os import remove, system
    from BigDFT.IO import write_pdb, read_pdb
    from futile.Utils import unique_filename
    oname1 = unique_filename(prefix='sys_') + '.pdb'
    oname2 = unique_filename(prefix='sys_') + '.pdb'
    with open(oname1, "w") as ofile:
            write_pdb(sys, ofile)
    system("obabel -ipdb " + oname1 + " -opdb -h >> " + oname2)
    sysh = read_pdb(open(oname2))
    remove(oname1)
    remove(oname2)
    return sysh


def atomic_partial_charges(system=None, pdbfile=None, forcefield='mmff94'):
    """Generate a system which stores the atomic partial charges in the atoms.

    Args:
        sys (Systems.System): the system to analyze.
        pdbfile (str): path of the file to analyze.
        forcefield (str): force field to define the partial charges with.

    Returns:
        Systems.System: system with the partial charges provided.
    """
    from os import system as ss, remove
    from futile.Utils import unique_filename
    from BigDFT.IO import write_pdb, read_mol2, read_pdb
    oname = unique_filename(prefix='sys_') + '.mol2'
    if pdbfile is not None:
        fn = pdbfile
        oname1 = None
    elif system is not None:
        oname1 = unique_filename(prefix='sys_') + '.pdb'
        with open(oname1, "w") as ofile:
            write_pdb(system=system, ofile=ofile)
        fn = oname1
    ss("obabel -ipdb  " + fn +
       " --partialcharge " + forcefield + " -omol2 > " + oname)
    with open(fn) as ifile:
        sys = read_pdb(ifile, include_chain=True)
    with open(oname) as ifile:
        molsys = read_mol2(ifile)
    remove(oname)
    if oname1 is not None:
        remove(oname1)
    # the newly read mol2 system has the atom charges stored in q0.
    q0atoms = [at for at in molsys.get_atoms()]
    lookup = sys.compute_matching(q0atoms)
    for frag in sys:
        for iat, at in enumerate(sys[frag]):
            idx = lookup[frag][iat]
            charge = [q0atoms[idx].q0]
            at.store['q0'] = charge
    return sys


def split_system_by_rotamers(sys):
    """
    This module will split a system into fragments based on the Rotamers.

    Args:
        sys (BigDFT.Systems.System): the system to split

    Returns:
        (BigDFT.Systems.System): the split up system.
    """
    from openbabel.openbabel import OBRotorList
    from networkx import Graph, connected_components
    from copy import deepcopy
    from BigDFT.Systems import System
    from BigDFT.Fragments import Fragment

    # Convert to openbabel type
    bsys = convert_system_to_babel(sys)

    # Generate the list of cuts
    rlist = OBRotorList()
    rlist.Setup(bsys)
    it = rlist.BeginRotors()
    cuts = []
    while True:
        try:
            rotor = rlist.NextRotor(it)
            atms = list(rotor.GetDihedralAtoms())
            cuts.append((atms[1], atms[2]))
        except AttributeError:
            break

    # Translate the cuts
    matching = compute_babel_matching(sys, bsys)
    reverse_matching = []
    for fragid, frag in matching.items():
        for i, at in enumerate(frag):
            reverse_matching.append((fragid, i))
    scuts = []
    for c in cuts:
        scuts.append((reverse_matching[c[0]-1], reverse_matching[c[1]-1]))

    # Modify the connectivity matrix
    cutsys = deepcopy(sys)
    for c1, c2 in scuts:
        cutsys.conmat[c1[0]][c1[1]].pop(c2)
        cutsys.conmat[c2[0]][c2[1]].pop(c1)

    # Convert to networkx
    g = Graph()
    k = 0
    lookup = {}
    for fragid, frag in cutsys.items():
        for i, at in enumerate(frag):
            g.add_node(k, fragid=fragid, idx=i)
            lookup[(fragid, i)] = k
            k += 1

    for fragid, frag in cutsys.conmat.items():
        for i, at in enumerate(frag):
            for con in at:
                idx1 = lookup[(fragid, i)]
                idx2 = lookup[con]
                g.add_edge(idx1, idx2)

    # Split
    new_sys = System()
    for i, comp in enumerate(connected_components(g)):
        key = "FRA:"+str(i)
        new_sys[key] = Fragment()
        for idx in comp:
            fragid = g.nodes[idx]["fragid"]
            fidx = g.nodes[idx]["idx"]
            new_sys[key].append(cutsys[fragid][fidx])

    return new_sys


def _example():
    """Example of using OpenBabel interoperability"""
    from BigDFT.Systems import System
    from BigDFT.Fragments import Fragment
    from BigDFT.IO import XYZReader

    # Read in a system.
    sys = System()
    sys["FRA:1"] = Fragment()
    with XYZReader("CH4") as ifile:
        for at in ifile:
            sys["FRA:1"] += Fragment([at])

    # We can compute the smiles representation.
    print(compute_smiles(sys))

    # The energy.
    print(system_energy(sys, forcefield="UFF"))

    # Extract the forces.
    compute_system_forces(sys, forcefield="UFF")
    for frag in sys.values():
        for at in frag:
            print(at.get_force())

    # Optimize the geometry.
    sys2 = optimize_system(sys, forcefield="UFF")
    print(system_energy(sys2, forcefield="UFF"))


if __name__ == "__main__":
    _example()
