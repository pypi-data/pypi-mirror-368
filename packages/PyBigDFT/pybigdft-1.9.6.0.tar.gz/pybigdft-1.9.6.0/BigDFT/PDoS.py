"""
This module offers a suite of tools for calculating and analyzing the projected
density of states (PDoS) in molecular systems. It provides functionality to
extract projection information from cubic and linear scaling PDoS calculations,
and compute weights associated with each projection.

Examples:
The module includes two example functions (_example_cubic and _example_linear)
to demonstrate usage with cubic and linear scaling PDoS calculations,
respectively.
"""

# Constants
PROJECTION_THRESHOLD = 0.3


def cubic_projection_info(log):
    """
    Extracts projection information from a cubic scaling Projected Density of
    States (PDoS) calculation, as performed in a BigDFT run.

    This function processes the output log file from a cubic scaling BigDFT
    calculation to map each atom in the system to its projections, such
    as 's', 'px', 'py', 'pz', etc. The function is designed to work with the
    specific structure of BigDFT log files, particularly extracting information
    from the 'Mulliken Charge Population Analysis' section.

    Args:
        log (BigDFT.Logfiles.Logfile): A BigDFT log file object, containing
            the results of a cubic scaling calculation with the pdos option on.

    Returns:
        dict of dict of list: A nested dictionary where the
        first key is the atomic symbol, and the second key is the projection
        type. The value is a list of indices, each corresponding to a
        projection of that type for the atom.
        For example: {'C': {'s': [0], 'px': [1], 'py': [2], 'pz': [3]}}.
    """
    from BigDFT.Systems import system_from_log
    from collections import defaultdict

    sys = system_from_log(log, fragmentation="full")
    proj_list = defaultdict(lambda: defaultdict(list))
    charge_analy = log.log["Mulliken Charge Population Analysis"]

    i = 0
    for at, proj in zip(sys.get_atoms(), charge_analy):
        for p in proj:
            if p == "Center Quantities":
                continue
            proj_list[at.sym][p].append(i)
            i += 1
    return _defaultdict_to_dict(proj_list)


def cubic_projection_weights(log, proj_info, log_dir="."):
    """
    Calculates the weights associated with each projection from a cubic scaling
    Projected Density of States (PDoS) calculation.

    This function interprets the PDoS data stored in a BigDFT log file to
    compute the weights of different atomic projections (e.g., 's', 'px', 'py',
    'pz') for each  orbital. It utilizes the projection information obtained
    from `cubic_projection_info` and the PDoS data file ('pdos.dat').

    Args:
        log (BigDFT.Logfiles.Logfile): The BigDFT log file object from a cubic
            scaling PDoS calculation.
        proj_info (dict): A dictionary mapping atomic symbols to projection
            types and indices, as returned by `cubic_projection_info`.
            log_dir (str, optional): The directory where the BigDFT log file is
            located. Defaults to the current directory (".").

    Returns:
        list of dict: A list where each element corresponds to an
        orbital. Each element is a dict, mapping atomic types to another dict,
        which in turn maps projections to their weights. For example, if you
        want the weight of the first orbital for the 's' projection of Carbon,
        it would be accessed as weights[0]['C']['s'].
    """
    from os.path import join
    from collections import defaultdict

    weights = []

    # Map back from index to symbol / projector type
    reverse_lookup = {}
    for k, v in proj_info.items():
        for p, idx in v.items():
            for i in idx:
                reverse_lookup[i] = (k, p)

    with open(join(log_dir, log.data_directory, "pdos.dat")) as ifile:
        for line in ifile:
            vals = [float(x) for x in line.split()]
            wdict = defaultdict(lambda: defaultdict(float))
            i = 0
            for j, w in enumerate(vals):
                if j not in reverse_lookup:  # Sometimes padding
                    continue
                sym, p = reverse_lookup[j]
                wdict[sym][p] += w
            weights.append(wdict)
    return _defaultdict_to_dict(weights)


def compute_weight(evec, sks_evec, orb_idx, proj_idx):
    """
    Computes the weight of a specific projection for a given orbital in the
    projected density of states (PDoS) calculation, typically used in the
    linear scaling mode.

    This function calculates the contribution of a specified set of projections
    (identified by their indices) to a particular orbital, based on the
    eigenvectors of the system. The function allows for optional inclusion of
    the overlap matrix (s) and the density matrix (k) if you're doing
    Mulliken analysis or projecting out virtuals, respectively.

    Args:
        evec (numpy.array): Array of eigenvectors, where each column represents
            an eigenvector of the system.
        evec (numpy.array): Overlap * Density * Overlap * evec. Overlap
            allows you to do a Mulliken projection, and Density can be used
            to filter in energy. If you're doing Lowdin, just use the
            density. If you don't need to filter in energy, the identity
            matrix can be used for the density.
        orb_idx (int): Index of the orbital for which the weight is being
            computed.
        proj_idx (list of int): List of indices corresponding to the
            projections included in the weight calculation.

    Returns:
        (float): the calculated weight.
    """
    from numpy import trace

    # Project
    seig_l = evec[:, orb_idx:orb_idx+1]
    seig_r = sks_evec[:, orb_idx:orb_idx+1]
    return trace(seig_l[proj_idx, :].T @ (seig_r)[proj_idx, :]).item()


def linear_projection_info(log, thresh=PROJECTION_THRESHOLD):
    """
    Analyze and categorize projection types for each atom in the system based
    on electrostatic multipole information from a given log file.

    This function processes the electrostatic multipoles associated with atoms
    in a system and classifies each support function (such as 's', 'px', 'py',
    'pz', 'dxy', etc.) based on their multipole expansion.

    Args:
        log (BigDFT.Logfiles.Logfile): The log file object from a BigDFT run.
        thresh (float): the threshold used for determining the character
          of a multipole.

    Returns:
        dict of dict of list: A nested dictionary where the first key is the
        atomic symbol, the second key is the projection type, and the value is
        a list of indices associated with that projection type for the given
        atom.
        Example: {'H': {'s': [0]}, 'O': {'px': [1], 'py': [2], 'pz': [3]'}}

    Raises:
        ValueError: If the projection type cannot be determined for an atom
        based on the heuristic criteria.
    """
    def guess_proj_type(atm, thresh):
        if abs(abs(atm["q1"][0]) - 1) < thresh:
            ptype = 'py'
        elif abs(abs(atm["q1"][1]) - 1) < thresh:
            ptype = 'pz'
        elif abs(abs(atm["q1"][2]) - 1) < thresh:
            ptype = 'px'
        elif abs(abs(atm["q0"][0]) - 1) < thresh:
            ptype = 's'
        elif abs(abs(atm["q2"][0]) - 1) < thresh:
            ptype = 'dxy'
        elif abs(abs(atm["q2"][1]) - 1) < thresh:
            ptype = 'dyz'
        elif abs(abs(atm["q2"][2]) - 1) < thresh:
            ptype = 'dz^2'
        elif abs(abs(atm["q2"][3]) - 1) < thresh:
            ptype = 'dxz'
        elif abs(abs(atm["q2"][4]) - 1) < thresh:
            ptype = 'dx^2-y^2'
        else:
            raise ValueError("Can't figure out " + str(atm))
        return ptype
    from warnings import warn
    from collections import defaultdict

    proj_info = defaultdict(lambda: defaultdict(list))

    # Use the multipole information for the compute matching
    mp = log.electrostatic_multipoles
    for pole in mp["values"]:
        pole["units"] = mp["units"]

    # Get the Multipole Descriptions
    gsfm = log.log["Gross support functions moments"]
    mp_info = gsfm["Multipole coefficients"]["values"]
    for i, atm in enumerate(mp_info):
        sym = atm["sym"].split("-")[0]
        ptype = guess_proj_type(atm, thresh)
        if atm["type"] != "unknown":
            ltype = atm["type"].replace("_", "")
            if ltype != ptype:
                warn("Uncertainty about support function character" + str(atm))
            ptype = ltype
        proj_info[sym][ptype].append(i)
    return _defaultdict_to_dict(proj_info)


def linear_projection_weights(evec, proj_info, s, k):
    """
    Computes the weights associated with a set of projections for each
    eigenvalue in a linear scaling Projected Density of States (PDoS)
    calculation.

    This function uses the eigenvectors and eigenvalues of a system, along with
    projection information (such as atomic symbols and projection types), to
    calculate the contribution of these projections to each eigenvalue.

    The function allows for inclusion of the overlap matrix (s) and the
    density matrix (k) if you're doing Mulliken analysis or projecting out
    virtuals, respectively. If you're doing Lowdin, pass the Lowdin
    orthogonalized eigenvectors and the identity matrix for s. You're doing
    Mulliken, and don't want to project out virtuals, pass the overlap matrix
    as K.

    Args:
        evec (numpy.array): Array of eigenvectors, where each column represents
            an eigenvector of the system.
        proj_info (dict): Dictionary mapping atom symbols to projections, and
            projections to indices, as obtained from `linear_projection_info`.
        s (numpy.array): Overlap matrix, used in the calculation of the weights
        k (numpy.array): Density matrix, used in the calculation of the weights

    Returns:
        list of dict: A list where each element corresponds to an
        eigenvalue. Each element is a dict, mapping atomic types to another
        dict, which in turn maps projections to their computed weights. For
        example, weights[0]['C']['s'] would access the weight of 's' projection
        for Carbon for the first eigenvalue.
    """
    from collections import defaultdict

    sks = s @ k @ s
    sks_evec = sks @ evec
    weights = []
    for i in range(evec.shape[1]):
        wdict = defaultdict(lambda: defaultdict(float))
        for atm, proj in proj_info.items():
            for p in proj:
                wdict[atm][p] += compute_weight(evec, sks_evec, i,
                                                proj_info[atm][p])
        weights.append(wdict)
    return _defaultdict_to_dict(weights)


def compute_fragment_weights(sys, log, evec, s, k):
    """
    Computes the weights associated with fragments in a system for each
    eigenvalue for a Fragment Projected Density of States (PDoS) calculation.

    Args:
        sys (BigDFT.Systems.System): The system object as defined in BigDFT,
            representing the fragments of the system.
        log (BigDFT.Logfiles.Logfile): The log file object from a BigDFT run
            computed in the linear scaling mode.
        evec (numpy.array): Array of eigenvectors, where each column represents
            an eigenvector of the system.
        s (numpy.array): Overlap matrix, used in the calculation of the weights
        k (numpy.array): Density matrix, used in the calculation of the weights

    Returns:
        list of dict: A list where each element corresponds to an
        eigenvalue. Each element is a dict, mapping fragment identifiers to
        their computed weights. For example, weights[0]['HOH:1'] accesses the
        weight of fragment 'HOH:1' for the first eigenvalue.
    """
    from BigDFT.PostProcessing import BigDFTool
    tool = BigDFTool()
    fidx = tool.get_frag_indices(sys, log)
    weights = linear_projection_weights(evec, {"frag": fidx}, s=s, k=k)

    # Eliminate intermediate dictionary
    for i, v in enumerate(weights):
        weights[i] = v["frag"]
    return _defaultdict_to_dict(weights)


def compute_SFs_weights(evec, metadata, mapping):
    """
    Computes the support functions weights from the mapped indices

    Args:
        evec (numpy.array): Array of eigenvectors
        metadata (BigDFT.Spillage.MatrixMetadata): The information
        on the matrices indexing
        mapping (dict): The instruction to fold the eigenvectors

    Returns:
        list of dict: A list where each element corresponds to an
        eigenvalue. Each element is a dict, mapping SFs to their
        computed weights.
    """
    from numpy import array, sum

    id_mat = [i.get('indices') for i in metadata.atoms]
    id_sym = [i.get('sym') for i in metadata.atoms]
    weights = [{k: [] for k, v in mapping.items()} for _ in range(len(evec))]
    evec2 = evec**2
    for k, v in mapping.items():
        id_k = array([id_mat[i] for i, ai in enumerate(id_sym) if ai == k])
        wg_k = array([sum(evec2[id_k[:, vi].flatten(), :], 0) for vi in v])
        [weights[i].update({k: [float(w_ii)for w_ii in w_i]})
         for i, w_i in enumerate(wg_k.T)]
    return weights


def _defaultdict_to_dict(d):
    """
    Recursively converts a nested defaultdict or a list of defaultdicts to a
    nested dict or a list of dicts, respectively.

    Args:
        d (defaultdict, dict, list): A defaultdict, a standard dict, or a list.
            The defaultdict may be nested and the list may contain defaultdicts
            or nested defaultdicts.

    Returns:
        dict or list: A standard dict or a list of dicts with all nested
        defaultdicts converted into dicts. If the input is a standard dict or
        a list containing standard dicts, it returns the input as-is.
    """
    from collections import defaultdict
    if isinstance(d, defaultdict):
        return {k: _defaultdict_to_dict(v) for k, v in d.items()}
    elif isinstance(d, dict):
        return {k: _defaultdict_to_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [_defaultdict_to_dict(v) for v in d]
    return d


def _example_cubic():
    # System
    from BigDFT.Database.Molecules import get_molecule
    sys = get_molecule("H2O")

    # Input file
    from BigDFT.Inputfiles import Inputfile
    inp = Inputfile()
    inp.set_hgrid(0.4)
    inp.set_xc("PBE")
    inp.calculate_pdos()

    # Calculate
    from BigDFT.Calculators import SystemCalculator
    code = SystemCalculator(skip=True, verbose=False)
    log = code.run(sys=sys, input=inp, name="pdos-C")

    # Get weights
    proj_list = cubic_projection_info(log)
    weights = cubic_projection_weights(log, proj_list)

    print(weights[0]["O"]["s"])
    print(weights[1]["H"]["s"])


def _example_linear():
    # System
    from BigDFT.Database.Molecules import get_molecule
    sys = get_molecule("H2O")

    # Input file
    from BigDFT.Inputfiles import Inputfile
    inp = Inputfile()
    inp.set_hgrid(0.4)
    inp.set_xc("PBE")
    inp["import"] = "linear"
    inp["lin_general"] = {"support_function_multipoles": True}

    from BigDFT.Calculators import SystemCalculator
    code = SystemCalculator(skip=True, verbose=False)
    log = code.run(sys=sys, input=inp, name="pdos-L")

    # Read the matrices
    from BigDFT.PostProcessing import BigDFTool
    tool = BigDFTool()
    h = tool.get_matrix_h(log)
    s = tool.get_matrix_s(log)
    k = tool.get_matrix_k(log)

    # Diagonalize
    from scipy.linalg import eigh
    evals, evec = eigh(h.todense(), b=s.todense())

    # Get the weights
    proj_info = linear_projection_info(log)
    weights = linear_projection_weights(evec, proj_info, s=s, k=0.5 * k)
    print(weights[0]["O"]["s"])
    print(weights[1]["H"]["s"])


if __name__ == "__main__":
    _example_linear()
    _example_cubic()
