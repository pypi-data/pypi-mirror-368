def get_molecule(name):
    """
    Get a system class representation of a molecule from the built in database.

    Args:
        name (str): the name of the molecule. You can find a list in
        bigdft-suite/PyBigDFT/Database/XYZs
    """
    import os
    from os.path import dirname, join, abspath
    from BigDFT.IO import read_xyz

    # Get the database path.
    dirXYZ = join(dirname(__file__), 'XYZs')
    filename = abspath(join(dirXYZ, name+'.xyz'))

    # Read and return
    try:
        with open(filename) as ifile:
            return read_xyz(ifile)
    except IOError:
        raise ValueError("Molecule not available")
