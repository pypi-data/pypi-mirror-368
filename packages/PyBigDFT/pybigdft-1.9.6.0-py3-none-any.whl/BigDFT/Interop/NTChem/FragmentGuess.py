"""
Helper routines for computing a guess based on some superposition of fragments.
"""


def stack_matrices(sys, subsystems, logfiles, mattype="density"):
    """
    Combine the matrices of various subsystems into one big matrix
    for the full system.

    Args:
        sys (BigDFT.Systems.System): the full system containing all fragments.
        subsystems (dict): a dictionary of subsystem, one for each fragment.
        logfiles (dict): a dictionary of logfiles, one for each fragment.
        mattype (str): which matrix to stack (density, overlap).

    Returns:
        (scipy.sparse.csr_matrix): the full matrix.
    """
    from scipy.sparse import bmat, csr_matrix
    from scipy.io import mmread
    from os.path import exists

    # Precompute the order of the fragments
    ordering = {}
    for i, fragid in enumerate(sys):
        ordering[fragid] = i

    # Build an empty 2d array for inserting matrices to stack.
    stackarray = []
    for i in range(0, len(sys)):
        sub = []
        for j in range(0, len(sys)):
            sub.append(None)
        stackarray.append(sub)

    # Loop over fragments, getting the matrix, and inserting it into the
    # stack array.
    for fragid1 in sys:
        # Get the indices
        frag_indices = get_frag_indices(subsystems[fragid1],
                                        logfiles[fragid1])
        indices1 = frag_indices[fragid1]

        # Read the matrix from file
        if mattype == "density":
            mat = mmread(logfiles[fragid1].densalp)
            if (exists(logfiles[fragid1].densbet)):
                mat = 0.5*mat + 0.5*mmread(logfiles[fragid1].densbet)
        elif mattype == "overlap":
            mat = mmread(logfiles[fragid1].overlap)
        else:
            raise ValueError("Invalid matrix type.")

        submat = csr_matrix(mat)[indices1, :]
        for fragid2 in sys:
            if fragid2 not in frag_indices:
                continue
            indices2 = frag_indices[fragid2]
            block = submat[:, indices2]

            stackarray[ordering[fragid1]][ordering[fragid2]] = block

    retmat = bmat(stackarray)

    # Symmetrize
    retmat = 0.5*retmat + 0.5*retmat.T

    return retmat


def get_frag_indices(sys, log):
    """
    Get a dictionary associating matrix indices with the fragments of a
    system.

    Args:
        sys (BigDFT.Systems.System): the system computed.
        log (BigDFT.Interop.NTChem.Logfiles.Logfile): the logfile to get
          information from.

    Returns:
        (dict): a mapping from fragments to indices.
    """
    from BigDFT.Atoms import Atom
    atlist = []
    for at in log.basis:
        atlist.append(Atom({at["sym"]: at["pos"]}))
    matching = sys.compute_matching(atlist)

    frag_indices = {}
    for fragid in sys:
        frag_indices[fragid] = []
        for idx in matching[fragid]:
            frag_indices[fragid] += log.idxlist[idx]

    return frag_indices


def combine_guess(sys, mapping, renamed, name, run_dir):
    """
    Combine a superposition of fragment guesses according to the mapping.
    After this routine is called, the density matrix is written to file.

    Args:
        sys (BigDFT.Systems.System): the full system containing all fragments.
        mapping (dict): a dictionary of fragment ids to a list of fragments
          in order to specify the templates.
        renamed (dict): a dictionary mapping fragment ids to the name
          used for the calculation.
        name (str): the name of the calculation you will use the guess matrix
          for.
        run_dir (str): the directory where the calculation was / will be run.
    """
    from BigDFT.Interop.NTChem.Logfiles import Logfile
    from BigDFT.Systems import System
    from copy import deepcopy
    from os.path import join

    sublogs = {}
    subsystems = {}
    for template, targets in mapping.items():
        log = Logfile(join(run_dir, renamed[template], renamed[template]))
        for target in targets:
            frag = sys[target]
            sublogs[target] = deepcopy(log)
            if len(frag) != len(sublogs[target].basis):
                raise ValueError("Fragments don't match")
            for i in range(len(frag)):
                sublogs[target].basis[i]["pos"] = frag[i].get_position("bohr")
            subsystems[target] = System()
            subsystems[target][target] = frag

    mat = stack_matrices(sys, subsystems, sublogs)
    _put_matrix(mat, run_dir, name, ".DensAlp.mtx")


def combined_embedded_guess(sys, subsystems, renamed, name, run_dir):
    """
    Combine a superposition of fragments computed in an embedding environment.
    After this routine is called, the density matrix is written to file.

    Note that in this case you don't provide a mapping, but the subsystems
    you created (fragment and environment).

    Args:
        sys (BigDFT.Systems.System): the full system containing all fragments.
        subsystems (dict): a dictionary mapping fragments to System types
          with the fragment and its embedding environment.
        renamed (dict): a dictionary mapping fragment ids to the name
          used for the calculation.
        name (str): the name of the calculation you will use the guess matrix
          for.
        run_dir (str): the directory where the calculation was / will be run.
    """
    from BigDFT.Interop.NTChem.Logfiles import Logfile
    from os.path import join

    sublogs = {}
    for fid in sys:
        sublogs[fid] = Logfile(join(run_dir, renamed[fid], renamed[fid]))

    mat = stack_matrices(sys, subsystems, sublogs)
    _put_matrix(mat, run_dir, name, ".DensAlp.mtx")


def _put_matrix(mat, run_dir, name, ext):
    from scipy.io import mmwrite
    from os.path import join, exists
    from os import mkdir
    if not exists(join(run_dir, name)):
        mkdir(join(run_dir, name))
    mmwrite(join(run_dir, name, name + ext), mat)
