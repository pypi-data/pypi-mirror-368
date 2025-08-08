"""
This module contains some wrappers for using OpenBabel to perform
various operations with RDKit.

https://www.rdkit.org/docs/api-docs.html
"""


def convert_system_to_rdkit(sys):
    """
    Convert a BigDFT system to rdkit molecule.

    Args:
      sys (BigDFT.Systems.System): the system to convert.

    Returns:
      (rdkit.Chem.rdchem.Mol): an rdkit type molecule.
    """
    from BigDFT.IO import write_mol2
    from io import StringIO
    from rdkit import Chem

    ostr = StringIO()
    write_mol2(sys, ostr)

    rdmol = Chem.MolFromMol2Block(ostr.getvalue())

    return rdmol


def compute_rdkit_matching(sys, rdsys, check_matching=True):
    """
    Similar to the cannonical `compute matching` of the system class, this
    creates a lookup table mapping each atom in a system class to the index
    of the atom in a rdkit system.

    Args:
        sys (BigDFT.Systems.System): the bigdft system.
        bsys (rdkit.Chem.rdchem.Mol): the rdkit version of the system.
        check_matching (bool): if set to True, this will raise an error
            if we can't match all of the atoms in the system.

    Returns:
        (dict): a mapping from a system to indices in the atom list. If
            an atom is not in the list, an index value of -1 is assigned.
    """
    from BigDFT.Atoms import Atom

    # Convert rdkit system to a list of atoms
    atm_list = []
    conf = rdsys.GetConformer()
    for at in rdsys.GetAtoms():
        sym = at.GetSymbol()
        idx = at.GetIdx()
        pos = [float(x) for x in list(conf.GetAtomPosition(idx))]
        newat = Atom({sym: pos, "units": "angstroem"})
        atm_list.append(newat)

    # Run compute matching.
    return sys.compute_matching(atm_list, check_matching)


def rdkit_visualize(sys, colordict=None, format="SVG"):
    """
    Visualize a molecule and its fragments using RDKit.

    Args:
        sys (BigDFT.Systems.System): the system to visualize.
        colordict (dict): a dictionary mapping fragments to colors.
        format (str): either SVG or Cairo.

    Returns:
        (str): the image to display. If it's SVG use SVG(result), Cairo
        Image(result).
    """
    from rdkit.Chem import rdDepictor, Draw

    rdsys = convert_system_to_rdkit(sys)
    matching = compute_rdkit_matching(sys, rdsys, check_matching=False)

    # Setup the atom colors
    if colordict is not None:
        atcolor = {}
        for fragid, frag in sys.items():
            for j, at in enumerate(frag):
                if at.sym == "H":
                    continue
                idx = matching[fragid][j]
                atcolor[idx] = tuple(colordict[fragid])
        dargs = {"highlightAtoms": range(rdsys.GetNumAtoms()),
                 "highlightAtomColors": atcolor, "highlightBonds": None}
    else:
        dargs = {}

    # Do the drawing.
    if format == "Cairo":
        d2d = Draw.MolDraw2DCairo(-1, -1)
    elif format == "SVG":
        d2d = Draw.MolDraw2DSVG(-1, -1)
    else:
        raise ValueError("Wrong format for drawing")

    rdDepictor.Compute2DCoords(rdsys)
    d2d.DrawMolecule(rdsys, **dargs)
    d2d.FinishDrawing()

    return d2d.GetDrawingText()
