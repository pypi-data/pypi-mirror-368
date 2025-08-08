"""A module to define typical operations that can be done on biological systems

"""
from BigDFT.Systems import System


# conversion names on nonstandard residues for BioPython
_extra_conversions = {'HSD': 'HIS', 'HID': 'HIS'}


def load(archive, serialization_version=None, options={}):
    """
    Create a Biosystem from a serialization archive.
    It extracts the archive files in a temporary directory
    and loads the related information. Also it deletes the directory
    once the load is finished.

    Args:
       archive(path): the path of the serialization archive
       serialization_version (str): version of the archive.
           Latest if not specified.

    Returns:
       BioSystem: Instance of the class, loaded from the archive
    """
    from futile.Utils import unpack_tarball
    from shutil import rmtree
    from os.path import join, isfile
    import json
    tmpdir, files = unpack_tarball(archive, tmpdir_prefix='tmp_BioQM_archive_')
    # load the data
    sys = BioSystem(join(tmpdir, 'posinp.pdb'), **options)
    sys.set_archive_name(archive)
    jsonfile = join(tmpdir, 'log.json')
    yamlfile = join(tmpdir, 'log.yaml')
    logfile = jsonfile if isfile(jsonfile) else yamlfile
    sys.set_qm_run(logfile)
    for version, attrs in BioSystemSerialization.cached_attributes.items():
        if serialization_version is not None:
            desired = serialization_version
        else:
            desired = BioSystemSerialization.version
        if not _version_is_compatible(desired, version):
            continue
        for attr in attrs:
            f = open(join(tmpdir, attr+'.json'), 'r')
            value = json.load(f)
            setattr(sys, '_'+attr, value)
            f.close()
    # remove the directory
    rmtree(tmpdir)

    return sys


def _version_is_compatible(desired_version, present_version):
    desired = list(map(int, desired_version.split('.')))
    obtained = list(map(int, present_version.split('.')))
    not_ok = obtained[0] != desired[0]
    if not not_ok:
        not_ok = any([ll < m for ll, m in zip(desired[1:], obtained[1:])])
    return not not_ok


def serialize_biosystem(archive, posinp, logfile, version=None, **kwargs):
    """
    Serialize the biosystem associated to the provided files

    Args:
       archive (path): name of the archive to be employed for dumping
       posinp (path): pdbfile of the structure
       logfile (path): logfile of the structure
       version(str): version of the serialization
       ** kwargs: Arguments to be passed to BioSystem instantiation
    """
    system = BioSystem(posinp, **kwargs)
    system.set_qm_run(logfile)
    if version is not None and _version_is_compatible('2.0', version):
        system.refragment(0.05)  # to create the atomic purities
    serialization = BioSystemSerialization(system, version=version)
    serialization.dump(archive)


class BioSystemSerialization():
    """
    Serialization of the BioSystem class that would prevent the need to
    copy the entire matrices of the QM calculations

    Args:
        biosys (BioSystem): a instance of the Biosystem class
        version (str): the version of the desired serialization.
           If absent, the default is considered.
    """

    version = '1.1'  #: version of the serialization
    cached_attributes = {'1.0': {'purities': 'purities',
                                 'fragindices': 'frag_indices',
                                 'pairwise_BO': 'bond_orders',
                                 'cached_refragment': '_cached_refragment'},
                         '1.1': {'interactions': 'interactions'},
                         '1.2': {'fragment_quantities':
                                 '_fragment_quantities'},
                         '2.0': {'atomic_purities': '_atomic_purities',
                                 'atomic_BO': 'atomic_bond_orders',
                                 'atomic_interactions': 'atomic_interactions',
                                 'cached_refragment': '_cached_refragment'}}

    def __init__(self, biosys, version=None):
        from os.path import isfile
        from BigDFT.Logfiles import Logfile
        import tarfile
        if hasattr(biosys, 'archive'):
            tardude = tarfile.open(biosys.archive)
            members = [m.name for m in tardude.getmembers()]
            tardude.close()
            self.files = {f: {'archive': biosys.archive, 'file': f}
                          for f in ['posinp.pdb', 'log.yaml',
                                    'log.json', 'time.yaml']
                          if f in members}
        else:
            logfile = biosys.logfile_path
            if logfile.endswith('.json'):
                jsonfile = logfile
                yamlfile = logfile.replace('.json', '.yaml')
            else:
                yamlfile = logfile
                jsonfile = yamlfile.replace('.yaml', '.json')
            assert isfile(yamlfile), 'YAML Logfile: "'+yamlfile+'" not present'
            if not hasattr(biosys, 'logfile'):
                log = Logfile(yamlfile)  # this may become very costly
            else:
                log = biosys.logfile
            if not isfile(jsonfile):
                log.to_json(jsonfile)
            self.files = {'posinp.pdb': biosys.structure_file_path,
                          'log.yaml': yamlfile,
                          'log.json': jsonfile}
            # timeyaml = basename(yamlfile).replace('log-', 'time-')
            ld = log if len(log) == 0 else log[0]
            # timefile = join(ld.datadir, timeyaml)
            # if isfile(timefile):
            #     self.files['time.yaml'] = timefile
            if ld.timefile is not None:
                self.files['time.yaml'] = ld.timefile

        self.true_version = version if version is not None else self.version

        for version, attributes in self.cached_attributes.items():
            if not _version_is_compatible(self.true_version, version):
                continue
            for attr, trueattr in attributes.items():
                setattr(self, attr, getattr(biosys, trueattr))

    def dump(self, archive):
        """
        Create an archive with the entire set of information of the
        Serialization. Such a tarfile should be such that the same
        analysis of the BioSystem is possible
        """
        from futile.Utils import create_tarball, serialize_objects
        from futile.Utils import tarfile_is_coherent
        # import json
        from BigDFT import Systems

        def if_system(sys):
            return sys.get_posinp()

        dictionaries = {}
        for version, attrs in self.cached_attributes.items():
            if not _version_is_compatible(self.true_version, version):
                continue
            dictionaries.update({att+'.json': getattr(self, att)
                                 for att in attrs})

        system_encoding = {'cls': Systems.System, 'func': if_system}

        objects = serialize_objects(
                    dictionaries, extra_encoder_functions=[system_encoding])

        create_tarball(archive, self.files, objects)
        tarfile_is_coherent(archive)


class Sequence():
    """
    Initialize and define a sequence, may be amminoacidic or nitrogenous.

    Args:
       seq(Bio.Seq.Sequence) : the starting sequence
    """

    def __init__(self, seq):
        self.sequence = seq

    def __add__(self, other):
        return Sequence(self.sequence + other.sequence)

    def __radd__(self, other):
        return self if other == 0 else self.__add__(other)

    def display(self, colors=None, labels=None, axs=None, boxcount=None,
                remove_letters=[]):
        """
        Display the sequence in a easy-to-read form

        Args:
            boxcount(int): the number of boxes per row
            remove_letters (list): list of letter positions that will be
                removed
        """
        from BigDFT.Visualization import contrasting_text_color as ctc
        from matplotlib.colors import to_hex

        def formatfun(x):
            return ("{: ^"+str(llen)+"}").format(x)
        # Handle optional axis
        if axs is None:
            import matplotlib.pyplot as plt
            fig, axs = plt.subplots()
        axs.axis('off')
        # bbox = axs.get_window_extent()

        # Handle the sizes based on the presence of labels
        if labels:
            yoffset = 24
            boxcount = 30 if boxcount is None else boxcount
            llen = max([len(x) for x in labels if x is not None])
            xoffset = 3*llen + 5
        else:
            xoffset = 7
            yoffset = 14
            boxcount = 40 if boxcount is None else boxcount

        # Handle the matplotlib options
        matargs = {"size": 18, "va": "center", "ha": "center",
                   "multialignment": "left"}
        matargs["fontdict"] = {"family": "monospace", "weight": "normal"}

        xcoord = 0
        ycoord = 100
        removed = False
        for i, letter in enumerate(str(self.sequence)):
            xct = 0.01 * xcoord
            yct = 0.01 * ycoord
            if i in remove_letters:
                if not removed:
                    matargs['bbox'] = {"linewidth": 0, 'fill': False}
                    axs.text(xct, yct, "-", **matargs)
                    # Update coordinates
                    xcoord += xoffset
                    removed = True
                continue
            removed = False
            label = None if labels is None or labels[i] is None else labels[i]
            fc = "k" if colors is None or colors[i] is None else colors[i]

            if isinstance(fc, tuple):
                lc = fc[1]
                fc = fc[0]
            else:
                lc = fc

            # contrasting colors if needed
            clc = ctc(to_hex(lc)) if lc != 'none' else 'k'
            cfc = ctc(to_hex(fc)) if fc != 'none' else 'k'

            if label:
                matargs["bbox"] = {"fc": lc, "linewidth": 0}
                axs.text(xct, yct + 0.05, formatfun(""),  **matargs)

                matargs["bbox"] = {"fill": False, "linewidth": 1,
                                   "edgecolor": 'k'}
                matargs['fontdict']['color'] = clc
                axs.text(xct, yct, formatfun(label) + "\n" + formatfun(""),
                         **matargs)

                matargs["bbox"] = {"fc": fc, "linewidth": 0}
                axs.text(xct, yct - 0.05, formatfun(""),  **matargs)

                matargs["bbox"] = {"fill": False, "linewidth": 1,
                                   "edgecolor": 'k'}
                matargs['fontdict']['color'] = cfc
                axs.text(xct, yct, formatfun("") + "\n" + formatfun(letter),
                         **matargs)

                # matargs["bbox"] = {"fill": False, "linewidth": 1,
                #                    "edgecolor": "k"}
                # axs.text(xct, yct, formatfun(label)+"\n"+formatfun(letter),
                #          **matargs)
            else:
                matargs["bbox"] = {"fc": fc, "linewidth": 1,
                                   "edgecolor": 'k'}
                matargs['fontdict']['color'] = ctc(to_hex(fc))
                axs.text(xct, yct, letter, **matargs)

            # Update coordinates
            xcoord += xoffset
            if xcoord > boxcount * xoffset:
                xcoord = 0
                ycoord -= yoffset
        return axs


def name_letter(resname):
    """Return the residue letter associated with the name.

    Arguments:
        resname (str): Three letter name of the residue. Can be nonstandard.

    Returns:
        str: Letter of the Residue. Returns 'X' if not found/valid.

    Example:

        >>> name_letter('HIS')
        'H'

        >>> name_letter('BCP')
        'X''
    """
    from Bio.PDB import Polypeptide as P

    name = _extra_conversions.get(resname, resname)

    if P.is_aa(name):
        three_to_one = P.protein_letters_3to1_extended
    elif P.is_nucleic(name):
        three_to_one = P.nucleic_letters_3to1_extended
    else:
        three_to_one = {name: 'X'}

    return three_to_one[name]


def order_chains(fragments):
    # from Bio.PDB.Polypeptide import three_to_index, index_to_one
    chains = {}
    for f in fragments:
        ch, res, num = construct_frag_tuple(f)
        resnum = ':'.join([res, str(num)])
        lett = name_letter(res)
        # try:
        #     lett = index_to_one(three_to_index(res))
        # except KeyError:
        #     lett = 'X'
        chains.setdefault(ch, {})[resnum] = lett
    return chains


def residue_to_chains(chdict, residues):
    chlett = {}
    for ires, res in enumerate(residues):
        ch, resname, num = construct_res_tuple(res)
        resnum = ':'.join([resname, str(num)])
        lett = chdict[ch].pop(resnum)
        if lett != 'X':
            chlett.setdefault(ch, {})[num] = (lett, ires)
    assert all(len(ch) == 0 for ch in chdict.values())
    return chlett


def chains_to_sequences(chlett):
    from Bio.Seq import Seq
    try:
        from Bio.Alphabet import ProteinAlphabet
        noalph = False
    except ImportError:
        noalph = True
    seqs = []
    chains_to_residues = []
    for ch in sorted(chlett.keys()):
        chain = chlett[ch]
        numbers = sorted(chain.keys())
        # strseq = ''.join([chain[i+1][0] for i in range(len(chain))])
        strseq = ''.join([chain[i][0] for i in numbers])
        if noalph:
            seq = Sequence(Seq(strseq))
        else:
            seq = Sequence(Seq(strseq, alphabet=ProteinAlphabet))
        seqs.append(seq)
        chains_to_residues.append([chain[i][1] for i in numbers])
    return seqs, chains_to_residues


def pdb_sequences(filename):
    """
    Sequences of the chains of the proteins, in the order of the residue_list

    Args:
       filename (str): protein file, in pdb format

    Returns:
       list: strings of the protein sequence in the FASTA sequence order
    """
    import Bio.SeqIO as S
    return [Sequence(rec.seq) for rec in S.parse(filename, format='pdb-atom')]


def read_structure(filename, name='protein'):
    """
    Extract a biological structure from a PDB file. Use the package Bio.PDB

    Args:
       filename (str): path to the file of the structure
       name (str): the name of the structure

    Returns:
       (Bio.PDB.Structure) A structure instance
    """
    import Bio.PDB as pdb
    parser = pdb.PDBParser()
    return parser.get_structure(name, filename)


def number_of_significative_digits(scl, ref):
    """
    Identify the number of significative digits that are preserved in both
    the values.
    """
    import math
    # first check the sign
    if (scl >= 0) != (ref >= 0):
        return 0
    rel_diff = abs(float(scl) / ref - 1.0)
    digits = math.log(rel_diff) / math.log(10)
    return 1 - int(digits)


def compare_vectors(v1, v2):
    """Compare the minimum significative digits of two vectors."""
    dg = 100000
    for x1, x2 in zip(v1, v2):
        dg = min(dg, number_of_significative_digits(x1, x2))
    return dg


def residue_list(structure, system, strict=True):
    """
    Identify the residues of the sequence in the fragment of the system

    Args:
       structure (structure): A structure read from the PDB parser of Bio.PDB
       system (BigDFT.Systems.System): a system coming from BigDFT package
       strict (bool): define if the identification has to be performend via
          centroids control or just by the residue name

    Returns:
       tuple: tuple of list the fragments of the `system` in the order of the
           residues of the structure. Some of the fragments may be missing as
           they may have been merged of not associated to elements of the
           sequence. The second list is the list of the ordered residues.
    """
    from BigDFT.Atoms import AU_to_A
    import numpy as np
    reslist = []
    centroids_dict = {frag: np.array(system[frag].centroid) * AU_to_A
                      for frag in system}
    original_residues = []
    for residue in structure.get_residues():
        restuple = construct_res_tuple(residue)
        centroid = sum([a.coord for a in residue.get_atoms()]) / len(residue)
        found = False
        for frag in centroids_dict:
            fragtuple = construct_frag_tuple(frag)
            if not strict:
                found = restuple == fragtuple
            else:
                found = np.linalg.norm(
                    centroids_dict[frag] - np.array(centroid)) < 1.e-4
                if not found:
                    found = compare_vectors(centroids_dict[frag],
                                            np.array(centroid)) >= 6

            if found:
                reslist.append(frag)
                centroids_dict.pop(frag)
                break
        if not found:
            reslist.append(None)
        original_residues.append(residue)
    return reslist, original_residues


def sequences_to_residues(reslist, chains, valid_chains):
    """
    Identify for each element of the chains which are the residues that may be
    associated to them.

    Args:
       reslist(list): the list of all the residues of the system
       chains (list): a list containing the sequences of the system

    Returns:
       list: a list of length of the chains indicating the lookup array for the
           sequence
    """
    # lookup = [[None for k in c.sequence] for c in chains]
    # chain_letters = []
    # for ires, res in enumerate(reslist):
    #     chain_id = res.full_id[2]
    #     if chain_id not in chain_letters:
    #         chain_letters.append(chain_id)
    #     ch = chain_letters.index(chain_id)
    #     pos = res.full_id[3][1] - 1
    #     if ch < len(lookup) and ch >= 0 and
    #          pos < len(lookup[ch]) and pos >= 0:
    #          lookup[ch][pos] = ires

    ch_keys = list(valid_chains.keys())
    assert len(chains) == len(ch_keys), 'Calculated vs. parsed unmatching.'
    for seq, ch in zip(chains, ch_keys):
        word = ''.join([lt for lt in str(seq.sequence) if lt != 'X'])
        reword = ''.join(valid_chains[ch][res][0]
                         for res in sorted(valid_chains[ch].keys()))
        assert word == reword, 'Sequences on chain ' + ch + ' unmatching.'

    lookup_dict = {}
    for ires, res in enumerate(reslist):
        chain_id = res.full_id[2]
        if chain_id not in ch_keys:
            continue
        pos = res.full_id[3][1]
        jres = valid_chains[chain_id][pos][1]
        assert ires == jres, 'residue list and valid_chains are not coherent'
        lookup_dict.setdefault(chain_id, {}).setdefault(pos, ires)

    lookup = [[lookup_dict[ch][pos]
               for pos in sorted(lookup_dict[ch].keys())]
              for ch in ch_keys]
    return lookup


class Graph():
    """
    A Graph representation of a System or a subportion of it.

    Identify the connectivity of the system given a threshold, possibly
    restricted to a subset of fragments
    Args:
       cutoff (float) : the threshold of the cumulative fragment bond order
        that is applied to define the connectivity
       restrict_to (list): list of the fragment id to which calculate
        the connectivity
    """

    def __init__(self, fragkeys, bond_orders, frag_labels, cutoff=0.01,
                 restrict_to=None):
        import numpy as np
        self.bo_cutoff = cutoff
        self.connectivity_matrix = graph_bond(
            fragkeys, cutoff, bond_orders, restrict_to=restrict_to)

        self.nw, self.target_nodes, self.target_edges = get_BO_network(
                                                    self.connectivity_matrix.T)

        self.labels = {i: l for i, l in enumerate(frag_labels)
                       if i in self.target_nodes}

        if restrict_to is not None:
            self.restrict_nodes = [fragkeys.index(f) for f in restrict_to]
        else:
            self.restrict_nodes = None

        frags = fragkeys

        self.edge_weights = []
        self.max_weight = 0.0
        for i, j in self.target_edges:
            fi = frags[i]
            fj = frags[j]
            boij = bond_orders[fi][fj]
            boji = bond_orders[fj][fi]
            if i != j:
                wgt = 0.5*(boij+boji)
                self.max_weight = max(self.max_weight, wgt)
            else:
                wgt = np.nan
            self.edge_weights.append(wgt)

        self.edge_weights = np.abs(np.array(self.edge_weights))

    def display(self, colors=None, axs=None, edge_labels=None,
                node_shapes=None, edge_colors=None,
                node_edge_colors=None,
                colorbar_mappable=None, colorbar_label='',
                **kwargs):
        """
        Draw the graph in the Kamada Kawai representation.
        Employ colors if present.

        Args:
           colors (list): the list of the colors that have to be employed for
              all the graph nodes. The list has the size of the full keys list.
              Only target nodes are employed.
           colorbar_mappable (matplotlib.colors.ScalarMappable): mappable to be
              employed to draw a colorbar associated to the node colors.
           colorbar_label(str): label to be associated to the colorbar
           edge_colors (list): the list of the colors that have to be employed
              for each of the edges of the node
           axs (matplotlib.axis): the axis to draw on (optional)
           edge_labels (dict): a dictionary from tuples of node labels to
             a given label.
           node_shapes (list): list indicating the shapes of the nodes,
               in order of full keys. Only target nodes are used for the shape.
           node_edge_colors (list): the list of the colors that have to be
              employed for all the graph node borders. Same specs than the
              colors argument.
           kwargs (dict): any other argument you wish to pass to networkx.
               Those arguments are arranged in keys, among which
               ``common``, ``nodes``, ``edges``, ``labels``, ``edge_labels``.
               Each values of the keys correspond to the arguments which
               should be passed to the corresponding ``draw_networkx_<>``
               method.

        """
        def update_arg(key, args, kwargs, **default_kwargs):
            new_arg = dict(**default_kwargs)
            new_arg.update(args)
            extra = kwargs.get(key)
            if extra is not None:
                new_arg.update(extra)
            return new_arg

        import networkx as nx
        from BigDFT.Visualization import contrasting_text_color

        # Handle optional axis
        if axs is None:
            import matplotlib.pyplot as plt
            fig, axs = plt.subplots(1, 1, figsize=(18, 12))

        # Handle kwargs
        args = {"alpha": 0.95, "ax": axs}
        args = update_arg('common', args, kwargs)
        # args.update(kwargs.get('common'))

        # nodeargs
        node_args = update_arg('nodes', args, kwargs,
                               node_size=800, linewidths=4)

        # edgeargs
        edge_args = update_arg('edges', args, kwargs)

        # labelargs
        label_args = update_arg('labels', args, kwargs,
                                font_size=10, font_family='serif',
                                font_weight='bold')

        # edge_labelargs
        edge_label_args = update_arg('edge_labels', args, kwargs,
                                     font_size=10, font_family='serif',
                                     font_weight='bold')

        layout = nx.kamada_kawai_layout(self.nw)

        shapegroups = {}
        non_default_shape = []
        if node_shapes is not None:
            for i, sh in enumerate(node_shapes):
                if sh is None or i not in self.target_nodes:
                    continue
                shapegroups.setdefault(sh, []).append(i)
                non_default_shape.append(i)
        else:
            shapegroups['s'] = self.restrict_nodes
            non_default_shape += [n for n in self.restrict_nodes]
        default_shape = shapegroups.setdefault('o', [])
        for n in self.target_nodes:
            if n not in non_default_shape and n not in default_shape:
                default_shape.append(n)

        for shape, nodes in shapegroups.items():
            node_color = 'r' if colors is None else [
                colors[i] for i in nodes]
            edgecolors = None if node_edge_colors is None else [
                 node_edge_colors[i] for i in nodes]
            nx.draw_networkx_nodes(self.nw, layout, node_shape=shape,
                                   node_color=node_color, nodelist=nodes,
                                   edgecolors=edgecolors, **node_args)

        nx.draw_networkx_edges(self.nw, layout,
                               edgelist=self.target_edges,
                               edge_color=edge_colors,
                               width=_edge_width_function(self.edge_weights),
                               **edge_args)

        colorgroups = {}
        for node in self.target_nodes:
            if colors is not None:
                color = contrasting_text_color(colors[node])
            else:
                color = 'k'
            colorgroups.setdefault(color, {}).setdefault(node,
                                                         self.labels[node])
        for col, colorgroup in colorgroups.items():
            nx.draw_networkx_labels(self.nw, layout, labels=colorgroup,
                                    font_color=col, **label_args)

        if edge_labels is not None:
            nx.draw_networkx_edge_labels(self.nw, layout,
                                         edge_labels=edge_labels,
                                         **edge_label_args)
        # Add legend for edge widths
        axs.legend(handles=_edge_width_legend(self.bo_cutoff, self.max_weight))
        if colorbar_mappable is not None:
            axs.get_figure().colorbar(colorbar_mappable, ax=axs,
                                      label=colorbar_label,
                                      pad=0.01, shrink=0.5)
        return axs


def FragmentTuple(chain, residue, id):
    from collections import namedtuple
    cls = namedtuple('FragmentTuple', 'chain residue id')
    return cls(chain=chain.strip(), residue=residue.strip(), id=int(id))


def construct_frag_tuple(frag):
    """
    Build the fragment tuple given the fragment name.

    Args:
        frag (str): the fragment name

    Returns:
        namedtuple: the (chain, residue, id) tuple name
    """
    ch, resnum = frag.split('-')
    res, num = resnum.split(':')
    return FragmentTuple(chain=ch, residue=res, id=int(num))


def construct_res_tuple(res):
    """
    Build the BigDFT fragment tuple given the residue of the structure

    Args:
       res(Residue): A residue Class on the Biopython package

    Returns:
       namedtuple: the (chain, residue, id) tuple name
    """
    chain = res.full_id[2]
    if len(chain.lstrip(' ')) == 0:
        chain = 'A'
    resname = res.resname
    position = res.full_id[3][1]
    return FragmentTuple(chain=chain, residue=resname, id=position)


def frag_tuple_name(fragtuple):
    return ':'.join(('-'.join((fragtuple.chain, fragtuple.residue)),
                    str(fragtuple.id)))


def residue_name(res):
    """
    Name of the residue in the fragment specification of PyBigDFT

    Args:
       res(Residue): A residue Class on the Biopython package
    Returns:
       str: name of the fragment
    """
    # chain, resname, position = construct_res_tuple(res)
    # return ':'.join(('-'.join((chain, resname)), str(position)))
    return frag_tuple_name(construct_res_tuple(res))


def biosystem_fragmentation(sys, structure):
    """
    Refragment the system names according to the residues name of the
    structure from the biopython module.

    Args:
       sys (System): and instance of the BioSystem class, fragmented in a
       traditional way
       structure (Bio.Structure): a structure coming from the BioPython module

    Returns:
       System: a system with a fragmentation that is dependent of the
          chain of the molecules
    """
    from BigDFT.Fragments import Fragment
    from BigDFT.Systems import System
    from warnings import warn
    # from Atom import Atom
    # newsys = [at for at in sys.get_posinp()['positions']]
    # units = sys.get_posinp()['units']
    from BigDFT.Atoms import AU_to_A
    # from Fragments import system_from_dict_positions
    mproat = [{at.element: list(at.coord/AU_to_A), 'atom': at,
               'frag': residue_name(at.get_parent()), 'units': 'bohr',
               'chain':
               at.full_id[2] if len(at.full_id[2].lstrip(' ')) > 0 else 'A'}
              for at in structure.get_atoms()]
    try:
        lookup = sys.compute_matching(atlist=mproat)
    except ValueError as e:
        lookup = sys.compute_matching(atlist=mproat, check_matching=False)
        warn('Some atoms were not matched' + str(e))
    newsys = System()
    for frag in sys:
        for at, jat in zip(sys[frag], lookup[frag]):
            # reat = mproat[jat]['atom']
            # newname = residue_name(reat.get_parent())
            newname = mproat[jat]['frag']
            if frag not in newname:
                newname = '-'.join([mproat[jat]['chain'], frag])
            # if newname not in newsys:
            #     newsys[newname] = Fragment()
            newsys.setdefault(newname, Fragment()).append(at)
    return newsys


def sequences_to_fragments(chains_to_residues, frag_to_residues):
    """Defines the lookup array of the sequences to the fragments.

    Args:
       chains_to_residues(list): lookup of the chains to the list of recognized
             residues.
       frag_to_residues (list): name of the associated fragments in the order
             of residues list.

    Returns:
       list: array of the name of the fragments in the same representation of
           chain_to_residues
    """
    from copy import deepcopy
    lookup = deepcopy(chains_to_residues)
    for c in lookup:
        for i, ires in enumerate(c):
            if ires is None:
                continue
            frag = frag_to_residues[ires]
            c[i] = frag
    return lookup


def fragment_name_conversion(fragments):
    """Dictionary of fragments for conversion.

    This function is useful to define a dictionary to be used to reform
    the fragment of a system such that the resulting PDB
    can be more easily read as a BioSystem.
    Such function can be used in conjunction with
    `py:func:Systems.reform_superunits` and
    `py:func:Systems.to_file` in order to define a better pdb for
    Bioystem instantiation.

    Arguments:
        fragments (list): list of the original fragments

    Returns:
        dict: keys are the original fragments, values are the
           renamed ones.

    Example:
        >>> mapping = fragment_name_conversions(sys)
        >>> newsys = sys.reform_superunits(mapping=mapping)
        >>> newsys.to_file('newfile.pdb')

    """

    from string import ascii_uppercase as alphabet
    from futile.Utils import split_contiguous
    dt = {}
    for frag in fragments:
        ch, res, num = construct_frag_tuple(frag)
        newres = _extra_conversions.get(res, res)
        letter = name_letter(newres)
        dt.setdefault(ch, {}).setdefault(num, (frag, newres, letter))

    # now reorder.
    hetchains = sorted([ch for ch in dt if all(v[2] == 'X'
                        for v in dt[ch].values())])
    neworder = sorted([ch for ch in dt if ch not in hetchains]) + hetchains
    mapping = {}
    ialpha = 0
    for ch in neworder:
        chain = dt[ch]
        subchs = split_contiguous(sorted(chain))
        for sch in subchs:
            cha = alphabet[ialpha]
            for num in sch:
                frag, newres, letter = chain[num]
                key = frag_tuple_name(FragmentTuple(cha, newres, num))
                mapping[frag] = key
            ialpha += 1
    return mapping


def _aggregate_values(fragments, data, view, op=sum):
    newdata = [d for d in data]
    for multiple_frag in view.values():
        datasum = op(data[fragments.index(f)] for f in multiple_frag)
        for f in multiple_frag:
            newdata[fragments.index(f)] = datasum
    return newdata


class BioSystem(System):
    """
    Initialize a System for a Biological analysis.
    Retrieve, from the initial file, the basic fragments, the system sequence,
    their mutual interactions and the informations about the purity and the
    observables

    Args:
       filename (str): a pdb file with fragment information inside
       use_native_fragmentation (bool): When true, the fragmentation is
           inferred from the definition in the pdbfile instead than from
           the Bio.Structure instance. Useful when dealing with non-biological
           objects, or with malformed biofragments.
       sys (System): an initial system, useful for a custom refragmentation.
            If present, overrides the association written in the pdbfile.
            It is user's responsibility to ensure coherency of the total
            number of atoms.
       sequence_from_fragments (bool): method to determine the sequences.
            If True, the sequence are determined by the fragment names.
            It is user's responsibility to provide a inputfile that has a
            set of residues compatible with the fragmentation.
       disable_warnings (bool): disable the BioPython warnings if true
       structure (Bio.Structure): a system structure that is meant to replace
            the one generated by the file parser. Useful for corrupted pdb
            files. To be used with `sequence from_fragments`
       atomic_granularity (bool): When True, employ atoms as the main units
           to define the interaction quantities. When False, fragments are
           employed. Useful for very large systems where atomic matrices
           may not be necessary, or too demanding.
       **kwargs: other arguments to be passed to `py:func:~BigDFT.IO.read_pdb`
    """
    def __init__(self, filename, sys=None, structure=None,
                 sequence_from_fragments=False, disable_warnings=False,
                 use_native_fragmentation=False, atomic_granularity=True,
                 **kwargs):
        from BigDFT.IO import read_pdb
        from os import path
        import warnings
        # disable warnings if asked for
        if disable_warnings:
            from Bio import BiopythonWarning
            warnings.simplefilter('ignore', BiopythonWarning)
        # path of the file
        self.structure_file_path = path.abspath(filename)
        if structure is None:
            # read structure from the Bio.PDB format
            # (can replace custom read_pdb)
            self.structure = read_structure(filename)
        else:
            self.structure = structure

        if use_native_fragmentation:
            # read pdb from the custom routine
            with open(filename) as ifile:
                newsys = read_pdb(ifile, include_chain=True, **kwargs)
        elif sys is None:
            # read pdb from the custom routine
            with open(filename) as ifile:
                sys = read_pdb(ifile, **kwargs)
            # reorganize the fragmentation
            newsys = biosystem_fragmentation(sys, self.structure)
        else:
            newsys = sys

        System.__init__(self, **newsys.dict())

        permissive = sequence_from_fragments or use_native_fragmentation

        self._residue_identification(permissive)

        self._sequence_identification(permissive)

        # once the system is identified proceed with the association
        self._fragment_identification()

        self.atomic_granularity = atomic_granularity

    def _residue_identification(self, sequence_from_fragments):
        # match the system's fragment into the amminoacids of he structure
        self.frag_to_residues, self.residues = residue_list(
                                        self.structure, self,
                                        strict=not sequence_from_fragments)

    def _sequence_identification(self, sequence_from_fragments):
        chdict = order_chains(self.keys())
        chlett = residue_to_chains(chdict, self.residues)
        # identify sequences
        if sequence_from_fragments:
            self.chains, self.chains_to_residues = chains_to_sequences(chlett)
        else:
            self.chains = pdb_sequences(self.structure_file_path)  # filename)
            # convert the element of the sequences to residues (if possible)
            self.chains_to_residues = sequences_to_residues(
                self.residues, self.chains, chlett)
        # associate to each of the chain elements the corresponding fragment
        # names
        self.sequences_to_fragments = sequences_to_fragments(
                              self.chains_to_residues,
                              self.frag_to_residues)

    def _fragment_identification(self):
        # store the fragment keys in a given order
        self.fragment_names = list(self.keys())
        # obtain the list of the letters of each fragment (if possible)
        self.fragment_letters = fragment_letters(
                        self.fragment_names,
                        [seq.sequence for seq in self.chains],
                        self.frag_to_residues,  self.chains_to_residues)
        # identify the fragments that are unmatched either in the residues or
        # in the sequence
        self.unmatched_fragments = [frag for frag, lett in zip(
            self.fragment_names, self.fragment_letters) if lett == 'X' or
            lett == 'None' or lett is None]
        # : quantities of the fragments
        self._fragment_quantities = {}

    @classmethod
    def from_sys(cls, system, attributes={}, **kwargs):
        """
        Create a BioSystem instance from a previously existing system.

        Args:
            system (System): the system instance.
            attributes (dict): attributes of the Biosystem that will be
                set from the user.
            **kwargs: other arguments that have to be passed to the
             BioSystem instantiation.

        Returns:
            BioSystem: a BioSystem instance
        """
        from futile.Utils import unique_filename
        from BigDFT import IO
        from os import remove
        attrs = ['_df'] + list(attributes)
        tmpfile = unique_filename(prefix='fix_') + '.pdb'
        ofile = open(tmpfile, 'w')
        IO.write_pdb(ofile=ofile, system=system)
        ofile.close()
        loaded = cls(tmpfile, **kwargs)
        remove(tmpfile)
        for attr in attrs:
            if hasattr(system, attr):
                setattr(loaded, attr, getattr(system, attr))
            if attr in attributes:
                setattr(loaded, attr, attributes[attr])
        return loaded

    @classmethod
    def from_logfile(cls, logfile, **kwargs):
        """
        Create a BioSystem instance from the information in a logfile.

        Args:
            logfile (str): path of the logfile.
            **kwargs: other arguments that have to be passed to the
             BioSystem instantiation.

        Returns:
            BioSystem: a System population instance
        """
        from BigDFT import Systems, Logfiles
        log = Logfiles.Logfile(logfile)
        sys = Systems.system_from_log(log)
        loaded = cls.from_sys(sys, **kwargs)
        loaded.set_qm_run(logfile)
        return loaded

    @classmethod
    def from_archive(cls, archive, **kwargs):
        """
        Create a BioSystem instance from the information in a serialized
        archive.

        Args:
            archive (str): path of the serialized biosystem.
            **kwargs: other arguments that have to be passed to the
             BioSystem load function.

        Returns:
            BioSystem: a System instance
        """
        from futile.Utils import kw_pop
        kw, version = kw_pop('serialization_version', '1.1', **kwargs)
        loaded = load(archive, serialization_version=version,
                      options=kw)
        return loaded

    def set_archive_name(self, archive):
        """Original archive name.

        Set the name of the original archive from which this biosystem comes
        from.

        Args:
             archive (str): archive name
        """
        from os import path
        self.archive = path.abspath(archive)

    def set_qm_run(self, log):
        """
        Associate the system to a QM run that has been performed by BigDFT.
        Such run assumes that the positions of the system atoms are consistent
        with the PDB

        Args:
           log (str): A path to the Logfile of the BigDFT run
        """
        import numpy as np
        from os import path
        from BigDFT.Logfiles import Logfile
        from BigDFT.Systems import system_from_log
        # path of the logfile
        self.logfile_path = path.abspath(log)
        self.logfile = Logfile(log)
        self.set_logfile_info(self.logfile)
        self.fragment_charges = np.array(
            [self[frag].q0[0] for frag in self.fragment_names])
        self.fragment_dipoles = np.array([self[frag].d1()
                                          for frag in self.fragment_names])
        self.fragment_dipole_norms = np.array(
            [np.linalg.norm(d1) for d1 in self.fragment_dipoles])
        if self.atomic_granularity:
            atomic_system = system_from_log(self.logfile,
                                            fragmentation='atomic')
            rename_mapping = {'ATOM:'+str(i): str(i)
                              for i in range(len(atomic_system))}
            self.atomic_system = atomic_system.rename_fragments(rename_mapping)
            lookup = self.compute_matching(
                [x[0] for x in self.atomic_system.values()])
            self.atomic_lookup = {x: [str(z) for z in y] for x, y in
                                  lookup.items()}
        self._cached_refragment = {}

    def refragment(self, cutoff=0.05, view=None, groups=[]):
        """
        Identify the system's fragmentation and represent it in terms of the
        systems' residues.
        Employs the user defined cutoff to find the correct fragmentation

        Args:
            cutoff (float): cutoff employed for the refragmentation.
            view (dict): the view to be imposed as a starting
                fragmentation in the system.
            groups (list): list of groups of the fragments view that
                will be employed as an initial guess for the fragmentation.
        """
        from BigDFT import Systems

        data = self._cached_refragment.get(str(cutoff))
        if data is not None:
            if isinstance(data, (list, tuple)):  # backward compatibility
                if not isinstance(data[0], Systems.System):
                    pos = data[0]['positions']
                    unt = data[0]['units']
                    data[0] = Systems.system_from_dict_positions(pos,
                                                                 units=unt)
                remapping = {frag: frag.split('+') for frag in data[0]}
            else:
                remapping = data
            return remapping

        auto_fragment_kw = dict(cutoff=cutoff, verbose=True,
                                criteria="bondorder")

        review = {} if view is None else view.copy()
        for gr in groups:
            if view is None:
                nw = {f: [f] for f in gr}
            else:
                nw = {}
                for f in gr:
                    for frag, fraglist in view.items():
                        if f in fraglist:
                            nw[frag] = fraglist
                            if frag in review:
                                review.pop(frag)
                            break

            review.update(self.auto_fragment(self.bigdft_tool, self.purities,
                                             self.bond_orders, nw,
                                             **auto_fragment_kw))

        if view is None and len(review) == 0:
            review = view
        else:
            review = clean_view(review, self)

        remapping = self.auto_fragment(self.bigdft_tool, self.purities,
                                       self.bond_orders, review,
                                       **auto_fragment_kw)

        # fw = Systems.FragmentView(self.purities, self.bond_orders,
        #                          charges={k: f.nel for k, f in self.items()})
        # if view is None:
        #     new_view = fw
        #     sys = Systems.System(self)
        # else:
        #     new_view = fw.refragment(view)
        #     sys = self.reform_superunits(view)
        # remapping = self.bigdft_tool.auto_fragment(sys, new_view, cutoff,
        #                                            verbose=True,
        #                                            criteria="bondorder")
        # # the mapping has to be reworked in terms of a view
        # # to prevent renaming of the original fragments
        # if view is not None:
        #     remap = {}
        #     for frag, lst in remapping.items():
        #         if frag in view and lst == view[frag]:
        #             remap[frag] = lst
        #             continue
        #         remap[frag] = []
        #         for orig_frag in view:
        #             if all(f in frag.split('+')
        #                    for f in orig_frag.split('+')):
        #                 remap[frag] += view[orig_frag]
        #     remapping = remap
        self._cached_refragment[str(cutoff)] = remapping
        return remapping

    def chessboards(self, cutoffs, initial_view=None, initial_groups=[]):
        """
        Define a coherent group of fragmentations that are provided
        from the loosest to tightest cutoffs.
        The views of the fragmentations are defined such as the tighest
        cutoffs always contain regrouping of fragments from the loosest

        Args:
            cutoffs (list): list of floating point numbers of the desired
                cutoffs values.
            initial_view (dict): mapping of the initial fragmentation that will
                be imposed starting from the loosest cutoff.
            initial_groups (list): groups of the initial view which will
                be first considered for fragmentation.
        Returns:
            dict: dictionary of the view. the values of the dictionary are
                length-1 lists such that subsequent views (for instance found
                when instantiating a population) can be appended
        """
        coff = sorted(cutoffs, reverse=True)
        cb = {}
        current_view = None if initial_view is None else initial_view.copy()
        current_groups = initial_groups
        self._cached_refragment = {}  # remove the caching for refragmenting
        for c in coff:
            current_view = self.refragment(c, view=current_view,
                                           groups=current_groups)
            # preserve the group association as most as possible
            new_groups = []
            for gr in current_groups:
                new_gr = []
                for frag, fragl in current_view.items():
                    if all(f in fragl for f in gr):
                        new_gr.append(frag)
                if len(new_gr) > 0:
                    new_groups.append(new_gr)
            current_groups = new_groups
            cb[c] = [current_view]
        return cb

    @property
    def fragment_ids(self):
        if not hasattr(self, '_fragment_ids'):
            self._fragment_ids = {}
            for frag in self.fragment_names:
                ifrag = 0
                found = False
                for ch in self.sequences_to_fragments:
                    if frag in ch:
                        jfrag = ch.index(frag)
                        found = True
                        break
                    ifrag += len(ch)
                if not found:
                    jfrag = self.unmatched_fragments.index(frag)
                self._fragment_ids[frag] = jfrag + ifrag
        return self._fragment_ids

    def _fragment_labels(self, view=None):
        label = {}
        if view is None:
            view = {f: [f] for f in self.fragment_names}
        for lf in view.values():
            lb = min([self.fragment_ids[f] for f in lf])
            for f in lf:
                if self.fragment_ids[f] == lb:
                    relb = lb
                    for ch in self.chains_to_residues:
                        if relb < len(ch):
                            break
                        # if relb >= len(ch):
                        relb -= len(ch)
                    label[f] = str(relb + 1)
                else:
                    label[f] = '   '
        return label

    @property
    def purities(self):
        from BigDFT.PostProcessing import superunits_purities
        if not hasattr(self, '_atomic_purities') and \
           not hasattr(self, '_purities'):
            if self.atomic_granularity:
                self._atomic_purities = self.bigdft_tool.run_compute_purity(
                             self.atomic_system, self.logfile,
                             kxs=self.ks_matrix,
                             frag_indices=self.atomic_frag_indices)
            else:
                self._atomic_purities = None
                self._purities = self.bigdft_tool.run_compute_purity(
                                self, self.logfile,
                                kxs=self.ks_matrix,
                                frag_indices=self.frag_indices)
        if not hasattr(self, '_purities'):
            atomic_charges = {iat: at.nel for iat, at in
                              self.atomic_system.items()}
            fragment_charges = {frag: f.nel for frag, f in
                                self.items()}
            self._purities = superunits_purities(self.atomic_bond_orders,
                                                 self._atomic_purities,
                                                 atomic_charges,
                                                 self.atomic_lookup,
                                                 fragment_charges)
        return self._purities

    @property
    def fragment_purities(self):
        """
        Define the quality of the fragmentation that is provided in the system
        """
        from numpy import array as a
        return a([abs(self.purities[frag]) for frag in self.fragment_names])

    @property
    def ks_matrix(self):
        if not hasattr(self, '_kxs'):
            self._kxs = self.bigdft_tool.get_matrix_kxs(self.logfile)
        return self._kxs

    @property
    def sinvh_matrix(self):
        if not hasattr(self, '_sinvh'):
            self._sinvh = self.bigdft_tool.get_matrix_sinvh(self.logfile)
        return self._sinvh

    @property
    def atomic_frag_indices(self):
        if not hasattr(self, '_atomic_fragindices'):
            self._atomic_fragindices = self.bigdft_tool.get_frag_indices(
                self.atomic_system, self.logfile)
        return self._atomic_fragindices

    @property
    def frag_indices(self):
        if not hasattr(self, '_fragindices'):
            self._fragindices = self.bigdft_tool.get_frag_indices(
                self, self.logfile)
        return self._fragindices

    @property
    def bigdft_tool(self):
        from BigDFT.PostProcessing import BigDFTool
        if not hasattr(self, '_btool'):
            from os import environ as env
            if 'BIGDFT_MPIRUN' not in env:
                # to be customized
                env['BIGDFT_MPIRUN'] = 'OMP_NUM_THREADS=2 mpirun -np 2'
            self._btool = BigDFTool()
        return self._btool

    def d3(self):
        from ase.calculators.dftd3 import DFTD3
        from os import environ
        from os.path import join
        from futile.Utils import unique_filename
        if 'ASE_DFTD3_COMMAND' not in environ:
            environ["ASE_DFTD3_COMMAND"] = join(environ["BIGDFT_ROOT"],
                                                "dftd3")
        label = unique_filename(prefix='ased3_')
        return DFTD3(xc='pbe', grad=False, damping="bj", label=label)

    @property
    def atomic_bond_orders(self):
        if not hasattr(self, '_atomic_BO'):
            atoms = [str(i) for i in range(len(self.atomic_system))]
            self._atomic_BO = self.bigdft_tool.fragment_bond_order(
                       self.atomic_system, atoms, atoms,
                       self.logfile, kxs=self.ks_matrix,
                       frag_indices=self.atomic_frag_indices)
        return self._atomic_BO

    @property
    def bond_orders(self):
        from BigDFT.PostProcessing import superunits_quadratic_quantities
        if not hasattr(self, '_pairwise_BO'):
            if self.atomic_granularity:
                self._pairwise_BO = superunits_quadratic_quantities(
                                       self.atomic_bond_orders,
                                       self.atomic_lookup)
            else:
                self._pairwise_BO = self.bigdft_tool.fragment_bond_order(
                           self, self.fragment_names, self.fragment_names,
                           self.logfile, kxs=self.ks_matrix,
                           frag_indices=self.frag_indices)
        return self._pairwise_BO

    @property
    def atomic_interactions(self):
        if not hasattr(self, '_atomic_interactions'):
            atoms = [str(i) for i in range(len(self.atomic_system))]
            self._atomic_interactions = \
                self.bigdft_tool.fragment_interaction_energy(
                         self.atomic_system, atoms, atoms,
                         self.logfile, kxs=self.ks_matrix,
                         frag_indices=self.atomic_frag_indices,
                         sinvh=self.sinvh_matrix)
        return self._atomic_interactions

    @property
    def interactions(self):
        from BigDFT.PostProcessing import superunits_quadratic_quantities
        if not hasattr(self, '_atomic_interactions') and \
           not hasattr(self, '_interactions'):
            self._interactions = self.bigdft_tool.fragment_interaction_energy(
                 self, self.fragment_names, self.fragment_names,
                 self.logfile, kxs=self.ks_matrix,
                 frag_indices=self.frag_indices,
                 sinvh=self.sinvh_matrix)
        elif not hasattr(self, '_interactions'):
            self._interactions = superunits_quadratic_quantities(
                                 self.atomic_interactions,
                                 self.atomic_lookup)
        return self._interactions

    def set_fragment_quantities(self, name, data):
        """Set fragment quantities to the system.

        Include in the biosystem a set of fragment quantities that are
        associated to the fragments. Such quantities can then be retrieved
        by the `fragment_values` method.

        Args:
            name (str): the name of the quantities to invoke
            data (list, dict): if a list, the quantities in order of
                `fragment_names`, otherwise a dictionary containing the
                 per-fragment information
        """
        self._fragment_quantities[name] = {}
        if isinstance(data, dict):
            for frag in data:
                self._fragment_quantities[name][frag] = data[frag]
        else:
            for frag, dt in zip(self.fragment_names, data):
                self._fragment_quantities[name][frag] = dt

    def fragment_distances(self, target_fragments):
        """
        Calculate the distance between each of the fragment and
        a list of target fragments.

        Args:
            target_fragments (list): Id of the fragments to focus on

        Returns:
            array-like: list of the distances in the order of fragment_names
        """
        from numpy import array
        distances = self.distances_from_target(target_fragments)
        return array([distances[frag] for frag in self.fragment_names])

    def fragment_interaction_and_feedback(self, target, criteria,
                                          environment=None, view=None):
        """Provides interaction with a target and its feedback.

        This method calculates the fragment interactions between a target
        and completes the result with the feedback of such interaction that
        an environmental region provides on such target.
        Args:
           target (list): Id of the fragments to focus on
           criteria (str): may be 'hamiltonian', 'electrostatic',
               or 'bond_order'
           environment (list): environmental region, separated from the
               target. If absent, the complementary region of the target is
               considered.
           view (dict): fragmentation view of the system. If present, target
               should be defined in the view.

        Returns:
           array-like: list of the strengths of the interactions of the
                fragments wrt to the target fragments. The order of the list
                is provided in terms of the `fragment_names`.
                The values of target fragments are associated to the feedback
                interaction with the environment
        """
        from numpy import array, nan
        from BigDFT.Systems import flatten_from_view
        interactions, feedback = _interaction_and_feedback(self,
                                                           target, criteria,
                                                           environment, view)
        flattened_target = flatten_from_view(target, view)
        if environment is not None:
            flattened_environment = [frag for frag in
                                     flatten_from_view(environment, view)
                                     if frag not in flattened_target]
        else:
            flattened_environment = [frag for frag in self.fragment_names
                                     if frag not in flattened_target]
        return array([f if frag in flattened_target
                      else (i if frag in flattened_environment else nan)
                      for i, f, frag in zip(interactions, feedback,
                                            self.fragment_names)])

    def identify_contact_region(self, target, cutoff_bo=0.001,
                                cutoff_el=1.e10, view=None,
                                environment=None):
        """Identify the contact with a target.

        Single out the portion of the target fragments
        that interacts with the rest of the system.

        Args:
            target (list): fragments of the target region.
            cutoff_bo (float): the value of the Fragment Bond Order
                above which the fragments are considered to be
                interacting. Typical values range between 0.01 and 1.e-3.
            cutoff_el (float): cutoff for the electrostatic value (Ha).
                Fragments whose interaction is larger than such value are also
                included in the contact region.
            view (dict): the mapping of the superunits into fragments.
            environment (list): environmental region under which
                restrict the sum.
        Returns:
            tuple: the list of the contact region as well as the value of the
                bond order
        """
        def select_subregion(fragments, interactions, cutoff):
            from numpy import where, array
            return list(array(fragments)[where(
                abs(array(interactions)) > cutoff)[0]])

        combined_bonds = self.fragment_interaction_and_feedback(
            target, 'bond_order', view=view, environment=environment)
        first = select_subregion(self.fragment_names,
                                 combined_bonds, cutoff_bo)
        if cutoff_el < 1.e6:  # do it only if meaningful
            combined_electrostatic = self.fragment_interaction_and_feedback(
                target, 'electrostatic', view=view, environment=environment)
            second = select_subregion(self.fragment_names,
                                      combined_electrostatic, cutoff_el)
        else:
            second = []
        total = first + [s for s in second if s not in first]
        return total, combined_bonds

    def calculate_contact_regions(self, target, cutoff_bo=0.001,
                                  cutoff_el=1.e10, name='', view=None,
                                  environment=None):
        """Identify the contact with a target.

        Single out the portion of the target fragments
        that interacts with the rest of the system, and store it.

        Args:
            target (list): fragments of the target region.
            cutoff_bo (float): the value of the Fragment Bond Order
                above which the fragments are considered to be
                interacting. Typical values range between 0.01 and 1.e-3.
            cutoff_el (float): cutoff for the electrostatic value (kcal/mol).
                Fragments whose interaction is larger than such value are also
                included in the contact region.
            name (str): Name of the region to be stored in the fragment_values.
            view (dict): mapping of the superunits into fragments.
            environment (list): the contact region is only calculated taking
               into accout those fragments.
        """

        from ase.units import Hartree, kcal, mol
        from BigDFT.Systems import flatten_from_view
        factor = Hartree / (kcal/mol)
        contact, strengths = self.identify_contact_region(
            target, cutoff_bo, cutoff_el/factor, view=view,
            environment=environment)
        flattened_target = flatten_from_view(target, view)
        target_zone = [f for f in contact if f in flattened_target]
        environment_zone = [f for f in contact if f not in flattened_target]
        nm = name + '_' if len(name) > 0 else ''
        self.set_fragment_quantities(
            nm+'contact_regions', {f: 1.0 if f in target_zone else (
                                   -1.0 if f in environment_zone else 0.0)
                                   for f in self.fragment_names})
        self.set_fragment_quantities(nm+'contact_bond_orders', strengths)

    def extract_target_contact_and_counter_region(self, name='',
                                                  environment=None):
        """Extract the contact region in the target and counter-region.

        Args:
            name (str): name of the stored region to extract
            environment (list): fragment belonging to the environmental region.
                The entire complementary region will be considered if absent.
        """
        target_zone = []
        environment_zone = []
        nm = name + '_' if len(name) > 0 else ''
        for frag, val in zip(
                self.fragment_names,
                self.fragment_values(criteria=nm+'contact_regions')):
            if val == 1.0:
                target_zone.append(frag)
            elif val == -1.0:
                if environment is None or frag in environment:
                    environment_zone.append(frag)
        return target_zone, environment_zone

    def calculate_target_interactions(self, target, name='',
                                      include_dispersion=False, nthreads=1,
                                      environment=None, view=None):
        """Calculate the interaction terms with a target.

        This function stores the fragment quantities associated to the
        interaction term with a target.

        Args:
            target (list): list of the fragments of the target region
            name (str): Name of the region to be stored in the fragment values.
            include_dispersion (bool): if true, calculate also the dispersion
               interaction of the target with the environment.
               The dispersion is only calculated in the contact fragments.
               Therefore if this value it true it is assumeed that the
               contact regions have already been calculated and stored.
            nthreads (int): number of threads for the parallel evaluation
               of the dispersion
            environment (list): fragments which correspond to the environment
               region to be considered for the target. If absent,
               the complementary region will be considered.
            view (dict): mapping of the superunits into fragments
        """
        from ase.units import Hartree, kcal, mol
        factor = Hartree / (kcal/mol)
        nm = name + '_' if len(name) > 0 else ''
        interactions = {}
        for kind, nameint in [('hamiltonian', 'contact_interactions'),
                              ('electrostatic', 'electrostatic_interactions'),
                              ('hartree', 'hartree_interactions'),
                              ('ionic', 'ionic_interactions'),
                              ('longrange', 'long_range_interactions')]:
            interactions[kind] = factor*self.fragment_interaction_and_feedback(
                target, kind, environment, view)
            self.set_fragment_quantities(nm+nameint, interactions[kind])

        # to be reassessed
        total = interactions['hamiltonian'] + interactions['electrostatic']
        if include_dispersion:
            tgt, env = self.extract_target_contact_and_counter_region(
                name, environment)
            if len(tgt) > 0 and len(env) > 0:
                disps = self.dispersion_interactions(tgt, env,
                                                     nthreads=nthreads,
                                                     view=view)
            else:
                disps = {}
            dispersion = [factor*disps.get(f, 0.0)  # bug of ASE solved now
                          for f in self.fragment_names]
            self.set_fragment_quantities(nm+'dispersion_interactions',
                                         dispersion)
            total += dispersion

        self.set_fragment_quantities(nm+'total_interactions',
                                     total)

    def dispersion_interactions(self, region1, region2, nthreads=1, view=None):
        """Van der Waals interaction strengths.

        Extract the dictionary of the dispersion interactions
        Between two disjoint regions.

        Args:
            region1 (list): list of fragments of region 1
            region2 (list): list of fragments of region 2
            nthreads (int): number of omp threads to perform the calculation.
            view (dict): mapping of the superunits into fragments.
        """
        from futile.Utils import fill_dictionary_in_parallel

        def regroup_region(region, view):
            if view is None:
                return region
            review = []
            for frag in view:
                subfrag = [su for su in view[frag] if su in region]
                if len(subfrag) > 0:
                    review.append('+'.join(subfrag))
            return review

        def distribute_results(dd):
            redd = {}
            for frag, data in dd.items():
                for ref in frag.split('+'):
                    redd[ref] = data
            return redd

        er1 = self.d3PBE_energy(subsystem=region1)
        er2 = self.d3PBE_energy(subsystem=region2)
        allints = {}
        intsr1 = fill_dictionary_in_parallel(nthreads,
                                             regroup_region(region1, view),
                                             _three_point_dispersion,
                                             sys=self, extra=region2,
                                             Eextra=er2)
        allints.update(distribute_results(intsr1))
        intsr2 = fill_dictionary_in_parallel(nthreads,
                                             regroup_region(region2, view),
                                             _three_point_dispersion,
                                             sys=self, extra=region1,
                                             Eextra=er1)
        allints.update(distribute_results(intsr2))
        return allints

    def fragment_interaction_strengths(self, target_fragments,
                                       criteria='hamiltonian', view=None):
        """
        Interactions between the different fragments of the system,
        possibly specified on target regions.

        Args:
           target_fragments (list): Id of the fragments to focus on.
               If a view is provided it should be expressed in terms of the
               fragments of the view.
           criteria (str): may be 'hamiltonian', 'electrostatic',
               or 'bond_order'.
           view (dict): view of the fragmentation to be employed to evaluate
               the strength.

        Returns:
           array-like: list of the strengths of the interactions of the
                fragments wrt to the target fragments. If a view is provided
                the data of each fragment is replicated for each of the
                superunits belonging to the fragment.
        """
        from BigDFT.PostProcessing import superunits_quadratic_quantities
        from numpy import array, nan
        intsc = {'bond_order': 'bond_orders',
                 'hamiltonian': 'interactions',
                 'electrostatic': 'electrostatic_interactions',
                 'hartree': 'hartree_interactions',
                 'ionic': 'ionic_interactions',
                 'longrange': 'long_range_interactions'}
        pairwise_bo = getattr(self, intsc[criteria])
        if view is None:
            fragments = self.fragment_names
            ints = interaction_strengths(fragments, target_fragments,
                                         pairwise_bo)
        else:
            fragments = list(view)
            assert all(t in view for t in target_fragments),\
                'target must be in view'
            pairwise_bo = superunits_quadratic_quantities(pairwise_bo, view)
            ints_view = interaction_strengths(fragments, target_fragments,
                                              pairwise_bo)
            intsd = {i: nan for i in range(len(self.fragment_names))}
            for frag, data in zip(fragments, ints_view):
                for su in view[frag]:
                    isu = self.fragment_names.index(su)
                    intsd[isu] = data
            ints = array([intsd[isu] for isu in sorted(intsd)])
        return ints

    def d3PBE_energy(self, subsystem=None, erase_d3_files=True):
        """
        Full dispersion energy of the system, or of a subsystem.

        Args:
            subsystem (list): fragment to focus on. If absent, the
                entire system is considered.
            erase_d3_files (bool): If true remove the d3 files
                once the calculation is completed.

        Returns:
            float: the d3 PBE energy for the PBE functional, in Hartree.
        """
        from os import remove
        import resource  # D3 needs unlimited stack to work properly
        resource.setrlimit(resource.RLIMIT_STACK,
                           (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
        if subsystem is None:
            sys = self
        else:
            sys = self.subsystem(subsystem)

        d3calc = self.d3()
        energy = sys.ase_potential_energy(d3calc)
        if erase_d3_files:
            remove(d3calc.label+'.xyz')
            remove(d3calc.label+'.out')
        return energy

    def system_target_interaction_investigation(self, target, nthreads,
                                                environment=None,
                                                **kwargs):
        """Identify the different interactions of the system with a target.
        Args:
            target (list): the list of the fragments defining the target.
            nthreads (int): number of threads to calculate the vdW correction.
            environment (list): fragments which will be considered in the
                environmental region. If absent the complementary region of
                the target will be considered.
            **kwargs: arguments of `calculate_contact_regions`
        """
        self.calculate_contact_regions(target=target, environment=environment,
                                       **kwargs)
        self.calculate_target_interactions(target=target,
                                           include_dispersion=True,
                                           nthreads=nthreads,
                                           environment=environment,
                                           name=kwargs.get('name', ''),
                                           view=kwargs.get('view'))

    def display_sequences(self, axs=None, labeldict=None, boxcount=None,
                          with_fragment_labels=False, remove_letters=None,
                          **kwargs):
        """
        Display the full sequencies of the system.
        Employ the given field to define the color dict if available

        Args:
           field_vals(list) : values of the field to decide
               the colors of the keys
           labeldict (dict): an optional dictionary mapping fragment ids
               to strings that will be printed on each sequence square.
           colordict (dict) :  the dictionary of the keys,
               and the corresponding colors. Overrides field_vals if present
           axs (list): list of the axis in which to plot the sequences
           with_fragment_labels (bool): a boolean useful to represent the
               fragment numbers. Can be combined with a view to visualize the
               QM fragments. Provides a default labeldict.
           remove_letters (list): list of the letters to be removed from
               the display. In elements of the chains.
           **kwargs: arguments to be passed to display of the colordict
        Returns:
           list: list of the axis of the sequences
        """
        # import matplotlib.pyplot as plt
        colord = self.colordict(**kwargs)
        if with_fragment_labels and labeldict is None:
            labeldict = self._fragment_labels(kwargs.get('view'))

        if labeldict is not None and 'colordict' not in kwargs:
            colord = self._colordict_for_labelling(colord, **kwargs)

        # if fig is None:
        #     fig = plt.figure()
        ifig = 1
        # nrows = len(self.chains)
        reax = []
        for i, (seq, lookup) in enumerate(zip(self.chains,
                                              self.sequences_to_fragments)):
            colorletters = [colord.get(frag) for frag in lookup]
            if remove_letters is None:
                remove_chain_letters = []
            else:
                remove_chain_letters = remove_letters[i]
            if labeldict is not None:
                labelletters = [labeldict.get(frag) for frag in lookup]
            else:
                labelletters = None
            # ax = fig.add_subplot(nrows, 1, ifig)
            # ax =
            ax = None if axs is None else axs[i]
            reax.append(seq.display(colors=colorletters, labels=labelletters,
                                    axs=ax, boxcount=boxcount,
                                    remove_letters=remove_chain_letters))
            ifig += 1
        return reax

    def display_graph(self, restrict_to=None, bo_cutoff=0.01,
                      fragment_labels=None, fragment_shapes=None, ax=None,
                      colorbar_label='', edge_labels=None, bond_orders=None,
                      edge_colordict_kw=None, node_edge_colordict_kw=None,
                      display_kwargs={},
                      **kwargs):
        """Display a graph view of the system.

        With this routine the fragments of the system are represented
        as a Graph, connected by the Fragment Bond Order criteria.
        Graph nodes can be represented as with a color map that is provided
        in a similar way than the sequence display.

        Args:
           restrict_to (list): list of fragments to which the graph
                 has to be restricted.
           bo_cutoff (float): the limit for a non-negligible chemical link
           fragment_labels (list, dict): list (in fragment_names order) of the
               labels of the fragments or dictionary of the fragments which
               need relabelling.
           fragment_shapes (dict): per-fragment dictionary of the shapes to be
               employed in the graph drawing.
               Only non-default values are indicated. If absent,
               the nodes which belong to the `restrict_to` list will
               be represented  as squares, and the others as circles.
           edge_labels (dict): dictionary of dictionaries: labels to be
               written next to the edges, with keys indicating the fragment
               names.
           ax (matplotlib.pyplot.axes): matplotlib axis
           colorbar_label(str): label to be associated to the colorbar.
               If None, no colorbar is drawn.
           bond_orders (dict-like): dictionary of the bond orders.
               Supersedes the systems' bond order if present.
               Not compatible with a view.
           edge_colordict_kw (dict): dictionary of the keyword arguments
               of the edge colors. The same syntax of the `colordict` method
               is allowed, written in terms of the tuple of the fragments.
               An additional keyword argument, `colordict_special`, is also
               allowed. This one overrides the arguments provided by the
               colordict for the fragment tuples provided.
           node_edge_colordict_kw (dict): dictionary of the keyword arguments
               of the node border colors. The same syntax of the `colordict`
               method is allowed.
           display_kwargs (dict): dictionary of the keyword arguments to be
               passed to `Graph.display` method.
           **kwargs: colordict arguments.

        Returns:
            matplotlib.pyplot.axes: the axes of the displayed graph
        """
        from BigDFT.Systems import FragmentView
        from BigDFT.Visualization import get_colordict
        import networkx as nx

        view = kwargs.get('view')

        colord = self.colordict(**kwargs)
        if view is None:
            fragments = self.fragment_names
            if bond_orders is None:
                bond_orders = self.bond_orders
            colors = [colord[i] for i in self.fragment_names]
        else:
            fw = FragmentView(self.purities, self.bond_orders,
                              charges={k: f.nel for k, f in self.items()})
            new_view = fw.refragment(view)
            fragments = list(view.keys())
            bond_orders = new_view.bond_orders
            # the first fragment dictate color and shape
            colors = [colord[view[f][0]] for f in fragments]

        lbdict = self.labeldict(fmt=['ch', '\n', 'letter', 'num'],
                                view=view, joinchar='\n')

        labels = [lbdict[fl] for fl in fragments]
        if fragment_labels is not None:
            if isinstance(fragment_labels, dict):
                for ifrag, frag in enumerate(fragments):
                    if frag in fragment_labels:
                        labels[ifrag] = fragment_labels[frag]
            else:
                labels = fragment_labels

        G = Graph(fragments, bond_orders, labels,
                  restrict_to=restrict_to, cutoff=bo_cutoff)

        # remove self_edges
        if hasattr(G.nw, 'selfloop_edges'):
            G.nw.remove_edges_from(G.nw.selfloop_edges())
        else:
            G.nw.remove_edges_from(nx.selfloop_edges(G.nw))

        # remove unused nodes (useful for big graphs)
        useless_nodes = [n for n in list(G.nw.nodes())
                         if n not in set(G.target_nodes + G.restrict_nodes)]
        G.nw.remove_nodes_from(useless_nodes)

        if fragment_shapes is not None:
            shapes = []
            for n in range(len(fragments)):  # G.target_nodes:
                if view is None:
                    toget = fragments[n]
                else:
                    toget = view[fragments[n]][0]
                shapes.append(fragment_shapes.get(toget))
        else:
            shapes = None

        if edge_labels is not None:
            edge_labels_tgt = {}
            for i, j in G.target_edges:
                fi = fragments[i]
                fj = fragments[j]
                lb = edge_labels.get(fi, {}).get(fj)
                if lb is not None:
                    edge_labels_tgt[(i, j)] = lb
        else:
            edge_labels_tgt = None

        if edge_colordict_kw is not None:
            edge_cdict = edge_colordict_kw.get('colordict')
            if edge_cdict is None:
                edge_kwargs = {}
                field_vals_tmp = edge_colordict_kw.get('field_vals')
                edge_kwargs.update(edge_colordict_kw)
                if field_vals_tmp is None:
                    edge_kwargs['field_vals'] = G.edge_weights
                    edge_kwargs['keys'] = G.target_edges
                elif isinstance(field_vals_tmp, dict):
                    keys = []
                    field_vals = []
                    for i in field_vals_tmp:
                        for j in field_vals_tmp[i]:
                            keys.append((i, j))
                            field_vals.append(field_vals_tmp[i][j])
                    edge_kwargs['field_vals'] = field_vals
                    edge_kwargs['keys'] = keys
                if 'colordict_special' in edge_kwargs:
                    dd = edge_kwargs.pop('colordict_special')
                else:
                    dd = None
                edge_cdict = get_colordict(**edge_kwargs)
                if dd is not None:
                    for i, j in G.target_edges:
                        newcl = dd.get(fragments[i],
                                       {}).get(fragments[j],
                                               dd.get(fragments[j],
                                                      {}).get(fragments[i]))
                        if newcl is not None:
                            edge_cdict[(i, j)] = newcl
                edge_colors = [edge_cdict.get((i, j), 'k')
                               for i, j in G.target_edges]
            else:
                edge_colors = [edge_cdict.get(fragments[i],
                                              {}).get(fragments[j],
                                                      edge_cdict.get(
                                                      fragments[j],
                                                      {}).get(fragments[i],
                                                              'k'))
                               for i, j in G.target_edges]
        else:
            edge_colors = None

        if node_edge_colordict_kw is not None:
            necd = self.colordict(**node_edge_colordict_kw)
            if view is None:
                node_edge_colors = [necd[i] for i in self.fragment_names]
            else:
                # the first fragment dictate color and shape
                node_edge_colors = [necd[view[f][0]] for f in fragments]
        else:
            node_edge_colors = None

        if colorbar_label is not None:
            mappable = colord.get('__mappable__')
        else:
            mappable = None
        return G.display(colors=colors,
                         node_shapes=shapes,
                         colorbar_mappable=mappable,
                         colorbar_label=colorbar_label,
                         edge_labels=edge_labels_tgt,
                         edge_colors=edge_colors,
                         node_edge_colors=node_edge_colors,
                         axs=ax, **display_kwargs)

    def display(self, cartoon=False, by_types=False, **kwargs):
        """Display the Biosystem along the same lines of `py:func:colordict`.

        Arguments:

            cartoon(bool): define the cartoon representation.

            by_types(bool): when true, atoms are colorized by types.

            **kwargs: arguments of the `py:func:colordict` function.

        """

        System.display(self, colordict=self.colordict(**kwargs),
                       by_types=by_types, cartoon=cartoon)

    def _colordict_for_labelling(self, colord, **kwargs):
        from futile.Utils import kw_pop
        if 'color_by' not in kwargs and 'field_vals' not in kwargs:
            fragment_colors = colord
            cd = {name: ('white', fragment_colors.get(name, 'white'))
                  for name in colord}
        else:
            new_kw, tt = kw_pop('color_by', None, **kwargs)
            new_kw, tt = kw_pop('field_vals', None, **new_kw)
            new_kw, tt = kw_pop('colorcode', None, **new_kw)
            fragment_colors = self.colordict(**new_kw)
            cd = {name: (fc, fragment_colors.get(name, 'white'))
                  for name, fc in colord.items()}
        return cd

    def refragmentation_colordict(self, refrag_keys, **kwargs):
        """
        Define a colordict that associates the fragment which go together
        with the same color and put to white all the previously pure fragments.

        Args:
           refrag_keys (list): Keys of the refragmented system
           **kwargs: keyword arguments of the initial colordict

        Returns:
           dict: the dictionary of the colors (equal color means same fragment)
        """
        # colordict = self.colordict(**kwargs)
        rekeys = {}
        for frag in refrag_keys:
            # if isinstance(frag, tuple):
            if '+' in frag:
                allfrags = frag.split('+')
                # recolor = colordict[allfrags[0]]
                rekeys[allfrags[0]] = []
                for refrag in allfrags[1:]:
                    # colordict[refrag] = recolor
                    rekeys[allfrags[0]].append(refrag)
            # else:
            #     colordict[frag] = 'white'
        cc = self.colordict(keys=rekeys.keys())
        for leadfrag in rekeys:
            for refrag in rekeys[leadfrag]:
                cc[refrag] = cc[leadfrag]
        return cc

    def colordict(self, color_by=None, keys=None, field_vals=None,
                  colordict=None, colorcode=None, highlight=None,
                  view=None, vmin=None, vmax=None, highlight_color='red'):
        """
        Define the colordict to quantify the fragments
        according to the method.

        Args:
           keys (list): keys of the fragment names.
           color_by (str): can be 'charge', 'dipole', 'purity'.
           field_vals(list) : values of the field to decide
                 the colors of the keys.
           colordict (dict) :  the dictionary of the keys,
                 and the corresponding colors. Overrides field_vals if present
           colorcode (str): the string of the colorcode.
                It represents the colormap of matplotlib.
                Default is 'seismic' for diverging values
                (i.e. field_dict has negative data), otherwise 'Reds'.
            highlight (list) : color in red only the fragments which
                are indicated in the list.
            view (dict): the fragmentation of the system to aggregate
                the field_vals to.
            highlight_color (matplotlib.colors): color to be employed
                for highlighting.
        """
        from BigDFT import Visualization as V
        if keys is None:
            keys = self.fragment_names
        if colorcode is None:
            colorcode = self._colorcode(criteria=color_by)
        if field_vals is None:
            if color_by is not None:
                field_vals = self.fragment_values(criteria=color_by, view=view)
            elif view is not None and colordict is None:
                return self.refragmentation_colordict(view)
        elif view is not None:
            field_vals = _aggregate_values(keys, field_vals, view)
        if highlight is not None:
            colord = {frag: highlight_color if frag in highlight else 'white'
                      for frag in self}
        elif colordict is None:
            colord = V.get_colordict(keys=keys, field_vals=field_vals,
                                     colorcode=colorcode, vmin=vmin, vmax=vmax)
        else:
            colord = colordict
        return colord

    def fragment_label(self, frag, fmt, shift={}):
        """String that can be used for labelling a fragment.

        Args:
            shift (dict): dictionary of the shifts to be applied to each chain
                from the first residue ID, with keys corresponding to the ID of
                the chain to be shifted. Useful for sequence alignment.
            frag (str): the fragment name.
            fmt (list): list indicating the characters that concatenate the
                residue attributes. The list should indicate "ch", "res", and
                "num" as the chain, residue name and number, respectively.
                "letter" can also be provided in case this is available.

        Returns:
            str: the label string.
        """
        ch, res, num = construct_frag_tuple(frag)
        if frag in self:
            lett = self.fragment_letters[self.fragment_names.index(frag)]
        else:
            lett = None
        num += shift.get(ch, 0)
        d = {'ch': ch, 'res': res, 'num': num, 'letter': lett}
        fmtstr = [str(d.get(item, item)) for item in fmt]
        return ''.join(fmtstr)

    def labeldict(self, labels={}, shift={}, mappable=None, fmt=['num'],
                  view=None, joinchar='+'):
        """Label the fragments with a recognizable string.

        This function returns a dictionary to label the fragments
        of the system in a way that can be employed in plots or graphs.

        Args:
            shift (dict): dictionary of the shifts to be applied to each chain
                from the first residue ID, with keys corresponding to the ID of
                the chain to be shifted. Useful for sequence alignment.
            mappable (func): function that returns a string from a system's
                fragment name.
            labels (dict): dictionary of explicit labels to be given to
                each fragment. Overrides all the other options for the
                indicated fragments.
            view (dict): a System fragments' view. If present, fragment names
                are concatenated unless specified otherwise in `mappable` and
                `labels`.
            joinchar (str): character to be used to join labels in case of
                a view.
            fmt (list): list indicating the characters that concatenate the
                residue attributes. The list should indicate "ch", "res", and
                "num" as the chain, residue name and number, respectively.
                "letter" can also be provided in case this is available.

        Returns:
            dict: A dictionary of the considered fragments with
                the corresponding names as strings.
        """
        def override_label(frag):
            if frag in labels:
                return labels[frag]
            if mappable is not None:
                try:
                    res = mappable(frag)
                except Exception:
                    res = None
                if res is not None:
                    return res
            return None

        def local_label(frag):
            lb = override_label(frag)
            if lb is not None:
                return lb
            return self.fragment_label(frag, fmt=fmt, shift=shift)
            # ch, res, num = construct_frag_tuple(frag)
            # lett = self.fragment_letters[self.fragment_names.index(frag)]
            # num += shift.get(ch, 0)
            # d = {'ch': ch, 'res': res, 'num': num, 'letter': lett}
            # fmtstr = [str(d.get(item, item)) for item in fmt]
            # return ''.join(fmtstr)
        if view is None:
            lbls = {frag: local_label(frag) for frag in self.fragment_names}
        else:
            lbls = {}
            for frag in view:
                lbl = override_label(frag)
                if lbl is None:
                    lbl = joinchar.join([local_label(f) for f in view[frag]])
                lbls[frag] = lbl
        return lbls

    def _colorcode(self, criteria=None):
        """
        Retrieve the colorcode to be used for the numpy cmap
        This is a commodity function made to make more intentional
        some treatment.

        Args:
           criteria (str): can can be 'charge', 'dipole', 'purity'

        Returns:
           str: matplotlib cmap to be used
        """
        if criteria is None:
            return None
        if criteria == 'charge':
            colorcode = 'seismic'
        elif criteria == 'dipole':
            colorcode = 'Greens'
        elif criteria == 'purity':
            colorcode = 'Greys'
        else:
            colorcode = None
        return colorcode

    def fragment_values(self, criteria=None, view=None):
        """
        Retrieve the fragment values that are associated to a given criteria.
        This is a commodity function made to make more intentional some data.

        Args:
           criteria (str): can can be 'charge', 'dipole', 'purity'
           view (dict): the dictionary of the fragment view. If present,
               aggregate the values accordingly.

        Returns:
           list: in order of the fragment names.
        """
        from BigDFT.Systems import FragmentView
        from numpy.linalg import norm
        from numpy import array
        if criteria is None:
            return None
        field_vals = None
        if criteria in self._fragment_quantities:
            vals = array([self._fragment_quantities[criteria][frag]
                          for frag in self.fragment_names])
            if view is None:
                field_vals = vals
            else:
                field_vals = _aggregate_values(self.fragment_names,
                                               vals, view)
        elif criteria == 'charge':
            if view is None:
                field_vals = self.fragment_charges
            else:
                field_vals = _aggregate_values(self.fragment_names,
                                               self.fragment_charges, view)
        elif criteria == 'dipole':
            if view is None:
                field_vals = self.fragment_dipole_norms
            else:
                aggregated_dipoles = _aggregate_values(self.fragment_names,
                                                       self.fragment_dipoles,
                                                       view)
                field_vals = map(norm, aggregated_dipoles)
        elif criteria == 'purity':
            field_vals = self.fragment_purities
            if view is not None:
                fw = FragmentView(self.purities, self.bond_orders,
                                  {f: ff.nel for f, ff in self.items()})
                new_fw = fw.refragment(view)
                for frag, pv in new_fw.purities.items():
                    for f in view[frag]:
                        field_vals[self.fragment_names.index(f)] = abs(pv)
        return field_vals

    def fragment_scatterplot(self, errors=None, ax=None, **kwargs):
        """
        Defines the scatterplot to have a look to in order to interpret
        sequence data

        Args:
           errors (list): the errors of the field_vals in the order
               of fragment_names
           ax (matplotlib.pyplot.Axes): Axis of the matplotlib instance
           **kwargs: the same arguments of the `:py:func:colordict` method

        Returns:
           matplotlib.pyplot.Axes: reference to the axis employed for the plot
        """
        import matplotlib.pyplot as plt
        colors = self.colordict(**kwargs)
        field_vals = kwargs.get('field_vals')
        view = kwargs.get('view')
        if ax is None:
            fig, ax = plt.subplots()
        # else:
        #     fig = ax.get_figure()
        if field_vals is None:
            field_vals = self.fragment_values(criteria=kwargs.get('color_by'),
                                              view=view)
        elif view is not None:
            field_vals = _aggregate_values(self.fragment_names, field_vals,
                                           view)
        for i, (f, p) in enumerate(zip(self.fragment_names, field_vals)):
            j = self.fragment_ids[f]
            # im =
            ax.scatter(j, p, color=colors[f])
        if errors is not None:
            for iname, (y, e) in enumerate(zip(field_vals, errors)):
                x = self.fragment_ids[self.fragment_names[iname]]
                ax.errorbar(x, y, e, fmt='none', elinewidth=0.5, ecolor='k')
        ax.set_xlabel('Fragment ID')
        # fig.colorbar(im)
        return ax

    def represent(self, errors=None, with3d=False, with_fragment_labels=False,
                  boxcount=None, remove_letters=None, labeldict=None,
                  **kwargs):
        """
        Represent all the data of the systems, both in with the sequence
        and with the scatterplot. Useful only when there is data to be
        represented.

        Args:
           with3d (bool): if True represent the 3d vision of the system
           errors (list): the errors of the field_vals in the order
               of fragment_names
           **kwargs: the same arguments of the `py:meth:colordict` method

        Returns:
           list: list fo the axis of the plot
        """
        ax = self.fragment_scatterplot(errors=errors, **kwargs)
        axs = self.display_sequences(with_fragment_labels=with_fragment_labels,
                                     boxcount=boxcount, labeldict=labeldict,
                                     remove_letters=remove_letters,
                                     **kwargs)
        if with3d:
            self.display(**kwargs)
        return [ax] + axs

    def unmatched_frag_info(self):
        """
        Retrieve the information about the fragments which have not been
        matched inside the sequence

        Returns:
           dict: a Dictionary of the fragment that have not been recognized
        """
        from BigDFT.Atoms import AU_to_A
        from numpy import array
        info = {'expected': {}, 'found': {}}
        expected = []
        for inum, (frag, residue) in enumerate(zip(self.frag_to_residues,
                                                   self.residues)):
            if frag is not None:
                letter = self.fragment_letters[self.fragment_names.index(frag)]
            if frag is not None and letter is not None:
                continue  # fragment has been matched
            centroid = sum([a.coord for a in residue.get_atoms()])/len(residue)
            info['expected'][residue_name(residue)] = {
                 'centroid': list(centroid), 'nat': len(residue),
                 'residue': residue}
            expected += [{at.element: list(at.coord/AU_to_A), 'units': 'bohr'}
                         for at in residue.get_atoms()]
        found = System()
        for frag in self.unmatched_fragments:
            info['found'][frag] = {'centroid':
                                   list(array(self[frag].centroid)*AU_to_A),
                                   'nat': len(self[frag]),
                                   'fragment': self[frag]}
            found[frag] = self[frag]
        if len(expected) > 0:
            info['lookup'] = found.compute_matching(atlist=expected)
        return info

    def charge_at_pH(self, ph, closed_shell=True):
        """
        Identify the charge that the system should have for a given pH.
        Employ the
        `~py:meth:Bio.Bio.SeqUtils.ProtParam.ProteinAnalysis.charge_at_ph`
        method of BioPython

        Args:
            ph (float): the value of the ph
            closed_shell (bool): defines if the charge should be rounded
                to the nearest even integer considering the total number
                of electrons of the system.
        Returns:
            float : the value of the charge
        """
        from Bio.SeqUtils.ProtParam import ProteinAnalysis as PA
        protein = PA(str(sum(self.chains).sequence))
        charge = protein.charge_at_pH(ph)
        if closed_shell:
            nelec = float(sum(f.nel for f in self.values()))
            total_elec = round(nelec - charge)
            if int(total_elec/2)*2 != int(total_elec):
                charge += 0.5
        return round(charge) if closed_shell else charge

    def charge_by_protonation(self):
        """
        Identify the system's charge by looking at the protonation state.

        The protonation state of each amminoacid is only identified by the
        total number of atoms of the residue, except for histidine. It is
        the user's responsibility to check that the atoms are placed correctly.

        Warning:
            Histidines have to be titrated wit the correct atom names.
            Hydrogens which are badly named in the delta1 and epsilon2 position
            may provide incorrect charge.

        Returns:
            tuple: charge of the system, list of residues for which the
                charge cannot be determined.
        """
        # unambiguous aminoacids:
        aa = {'ALA': 0, 'ASN': 0, 'GLN': 0, 'GLY': 0, 'ILE': 0, 'LEU': 0,
              'MET': 0, 'PHE': 0, 'PRO': 0, 'SER': 0, 'THR': 0, 'TRP': 0,
              'VAL': 0, 'CYS': 0}
        # titrable aa, except histidine
        aat = {'GLU': {15: -1, 16: 0}, 'ASP': {12: -1, 13: 0},
               'TYR': {21: 0, 22: 1}, 'LYS': {22: 1, 21: 0},
               'ARG': {24: 1, 23: 0}}

        chg = 0
        unknown = []
        stats = {}
        # atom number difference at edges
        ndiff = [-2, -1]  # [NH > NH3+, CO > COO-]
        # update the number of atoms for the extremal residues
        extremes = {}
        for ch in self.sequences_to_fragments:
            for i in [0, -1]:
                extremes[ch[i]] = ndiff[i]
        for frag in self:
            ch, res, i = construct_frag_tuple(frag)
            fragment = self[frag]
            nat = len(fragment)
            nat_possible = nat + extremes.get(frag, 0)
            # neutral by hypothesis
            tchg = aa.get(res, 0)
            if res in aat and (nat in aat[res] or nat_possible in aat[res]):
                tchg = aat[res][nat_possible if frag in extremes else nat]
            elif res == 'HIS':
                labels = [at.store['name'] for at in fragment]
                if all(x in labels for x in ['HD1', 'HE2']):
                    tchg = 1
            elif res not in aa:
                unknown.append(frag)
            chg += tchg
            stats.setdefault(res, []).append(tchg)
        #
        # # scan all the residues
        # residues = self.residues
        # for ch in self.chains_to_residues:
        #     for i in ch:
        #         res = residues[i]
        #         nat = len(res)
        #         if i in [ch[0], ch[-1]]:
        #             nat += ndiff[[ch[0], ch[-1]].index(i)]
        #         name = res.resname
        #         if name in aa:
        #             tchg = aa[name]  # zero essentially
        #         elif name in aat and nat in aat[name]:
        #             tchg = aat[name][nat]
        #         elif name == 'HIS':
        #             labels = [x.name for x in res.get_atoms()]
        #             if all(x in labels for x in ['HD1', 'HE2']):
        #                 tchg = 1
        #             else:
        #                 tchg = 0
        #         else:
        #             frag = '%s-%s:%s' % (res.segid.strip(), name, i)
        #             unknown.append(frag)
        #             tchg = 0
        #         chg += tchg
        #         stats.setdefault(name, []).append(tchg)
        return chg, unknown, stats

    def override_fragment_association(self, fragment_names, new_names=None):
        """
        Force the association of the fragment provided by the fragment_names
        list into the data represented by the new_names.
        New names should be provided as 'Ch-RES:num' where ``Ch`` is the chain,
        ``RES`` is the aminoacid residue at the position ``num``.

        Args:
           fragments_names(list): list of the fragments to be reassociated.
               Should be present in the unmatched_fragment list.
           new_names(list): list of the new names to be produced,
               in fragment_names element order.
               If absent, the fragment names are employed.
        """
        previously_unknown_fragments = {residue_name(res): ires
                                        for ires, (frag, res) in enumerate(
                                        zip(self.frag_to_residues,
                                            self.residues))
                                        if frag is None}
        if new_names is None:
            new_names = fragment_names
        for oldfrag, newfrag in zip(fragment_names, new_names):
            if oldfrag not in self.unmatched_fragments:
                raise ValueError(
                    'The fragment "' + oldfrag +
                    '" is not present in the list of unmatched fragments')
            iold = self.fragment_names.index(oldfrag)
            if self.fragment_letters[iold] != 'X':
                raise ValueError(
                    'The fragment "' + oldfrag +
                    '" has already a letter associated with it')
            if newfrag not in previously_unknown_fragments:
                raise ValueError(
                     'The fragment "' + newfrag +
                     '" cannot be associated to a valid sequence fragment')
            ires = previously_unknown_fragments.pop(newfrag)
            self.frag_to_residues[ires] = oldfrag
            for ic, chain in enumerate(self.chains_to_residues):
                if ires in chain:
                    iseq = chain.index(ires)
                    self.sequences_to_fragments[ic][iseq] = oldfrag
                    break
            self.fragment_letters[iold] = residue_letter(
                    ires, [seq.sequence for seq in self.chains],
                    self.chains_to_residues)
            self.unmatched_fragments.remove(oldfrag)
        if hasattr(self, '_fragment_ids'):
            delattr(self, '_fragment_ids')

    def to_archive(self, archive, version='1.2'):
        """Create the archive from which the System can be loaded again.

        Args:
            version (str): version of the archive.
            archive (str): path of the archive to be created.
        """
        BioSystemSerialization(self, version=version).dump(archive)

    def residue_distribution(self, criteria=None, field_vals=None):
        """Create a dictionary of the distribution of field_vals per fragment.

        Arguments:
            field_vals (array-like): list of the values of the distribution
                to analyze in element orders.
            criteria (str): can can be 'charge', 'dipole', 'purity'

        Returns:
            dict: dictionary representing the data of each residue name.
        """
        from collections import defaultdict
        dist = defaultdict(list)
        data = field_vals
        if field_vals is None:
            data = self.fragment_values(criteria)
        for frag, d in zip(self.fragment_names, data):
            fragtuple = construct_frag_tuple(frag)
            dist[fragtuple.residue].append(d)
        return dist


def filter_field_vals(field_vals, lookup, fill_by=None):
    """Select the data in the field_vals array by the lookup.

    Performs a copy if lookup is not None

    Arguments:
        field_vals (array-like): the data to be filtered:
        lookup (array_like): the list of the indices to be selected.
           If none the entire array is returned.
        fill_by (float): the value to be employed if the index
           provided in the lookup array is None.
           Defaults to numpy.nan.

    Returns:
        array-like: list of the data filtered by lookup array.
           performs a copy if the lookup array is not None.
    """
    from numpy import array, nan
    if lookup is None:
        return field_vals
    if fill_by is None:
        fill_by = nan
    return array([field_vals[lu] if lu is not None else fill_by
                  for lu in lookup])


def graph_bond(fraglist, threshold, pairwise_bo, restrict_to=None):
    """
    Defines the connectivity matrix of the fragments

    Args:
       fraglist (list): the list of the fragment names
       threshold (float) : the threshold of the cumulative fragment bond order
            that is applied to define the connectivity
       pairwise_bo (dict): list of the fragment BO connections
       restrict_to (list): list of fragments to which the graph has to be
            restricted

    Returns:
       (matrix) : connectivity matrix of the graph
    """
    from numpy import zeros
    mat = zeros((len(fraglist), len(fraglist)))
    lookup = {y: x for x, y in enumerate(fraglist)}

    for i, fragid1 in enumerate(fraglist):
        if restrict_to is not None and fragid1 not in restrict_to:
            continue
        bo = pairwise_bo[fragid1]
        sorted_bo = sorted(bo, key=bo.get, reverse=True)

        remainder = sum(bo.values())
        for key in sorted_bo:
            mat[i, lookup[key]] = 1
            remainder -= bo[key]
            if remainder < threshold:
                break
    return mat


def _edge_width_function(wg):
    from numpy import log10, clip
    return 2.75 + 0.75*log10(clip(wg, 0.001, 1.0))


def _edge_width_legend(bo_cutoff, max_weight):
    import matplotlib.lines as mlines
    allegends = []
    for boval in ['0.001', '0.01', '0.1', '1']:
        bov = float(boval)
        if bov < bo_cutoff or bov > max_weight:
            continue
        lw = _edge_width_function(bov)
        lb = boval if boval != '1' else r'$\geq$1'
        lg = mlines.Line2D([], [], color='k', linewidth=lw, label=lb)
        allegends.append(lg)
    return allegends


def get_BO_network(connectivity_matrix):
    """
    Defines the connectivity matrix of the fragments
    Args:
       connectivity_matrix (matrix-like): matrix of the connnectivities of
           the system
       pairwise_bo (dict): list of the fragment BO connections

    Returns:
        tuple: graph,target_nodes,target_edges.
             Graph to be plotted and the list of target nodes and edges
             identified by the restriction if present.
    """
    import networkx as NX
    if hasattr(NX, 'from_numpy_matrix'):
        nw = NX.from_numpy_matrix(connectivity_matrix)
    else:
        nw = NX.from_numpy_array(connectivity_matrix)
    target_nodes = []
    target_edges = []
    for cc in NX.connected_components(nw):
        subgraph = nw.subgraph(cc)
        if len(cc) > 1:
            target_nodes += list(subgraph.nodes)
            target_edges += list(subgraph.edges)
    return nw, target_nodes, target_edges


def fragment_letters(fragnames, sequences, residue_list,
                     sequences_to_residues):
    """
    Give a list of the fragments in terms of their letter

    Args:
        fragnames (list): list of the names of the fragments
        residue_list (list): The fragments of the `system` in the order
              of the residues of the structure
        sequences_to residues (list): strings of the protein sequence
              in the FASTA sequence order
        sequences(list): Sequences of the system
    Returns:
        list: the labels of the fragments as letters. the label is set to 'X'
           if the letter is not recognized
    """
    letters = ['X'] * len(fragnames)
    for ifrag, frag in enumerate(fragnames):
        if frag not in residue_list:
            continue
        ires = residue_list.index(frag)
        letters[ifrag] = residue_letter(ires, sequences, sequences_to_residues)
    return letters


def residue_letter(ires, sequences, sequences_to_residues):
    """
    Find the letter associated with the residue

    Args:
        ires (int): id of the residue
        sequences(list): Sequences of the system
        sequences_to residues (list): strings of the protein sequence
              in the FASTA sequence order

    Returns:
        str: letter of the residue
    """
    for iseq, seq in enumerate(sequences_to_residues):
        if ires in seq:
            ilett = seq.index(ires)
            return sequences[iseq][ilett]


def _interaction_and_feedback(sys, target, criteria,
                              environment=None, view=None):
    from BigDFT.Systems import flatten_from_view
    interactions = sys.fragment_interaction_strengths(target,
                                                      criteria=criteria,
                                                      view=view)
    if environment is None:
        if view is None:
            fragments = sys.fragment_names
        else:
            fragments = list(view)
        environment = [f for f in fragments if f not in target]
    feedback = sys.fragment_interaction_strengths(environment,
                                                  criteria=criteria,
                                                  view=view)
    if view is None:
        lut = [sys.fragment_names.index(f)
               for f in flatten_from_view(target, view)]
        lue = [sys.fragment_names.index(f)
               for f in flatten_from_view(environment, view)]
        action_reaction = abs(sum(interactions[lue])-sum(
            feedback[lut]))
        assert action_reaction < 1.e-4, str(action_reaction)
    return interactions, feedback


def interaction_strengths(fragments, target_fragments, pairwise_bo):
    """
    Define the interaction strengths of the fragment list with the
    others with respect to a set of target fragments.

    Args:
        fragments (list) : the name of the fragments of the
            system in pairwise_bo.
        target_fragments (list) : the fragments constituting the target region.
        pairwise_bo (dict): the bond order between fragments.

    Returns:
        array: the  sum of the weigths of the interactions of the fragments
            in the target region.
    """
    import numpy as np
    lookup = [fragments.index(frag) for frag in target_fragments]
    BOtot = np.zeros(len(fragments))
    for ipair in lookup:
        frag_i = fragments[ipair]
        BOtot += np.array(
            [0.5*(pairwise_bo[frag_i][frag] + pairwise_bo[frag][frag_i])
             for frag in fragments])
    if len(lookup) > 0:
        BOtot[np.array(lookup)] = np.nan
    return BOtot


def find_relevant_fragments(sys, data, criteria, columns=None):
    """
    Identify the fragments of the system that fulfill the criteria
    provided by the function in argument

    Args:
        sys (BigDFT.System): the System to identify
        data (array, Dataframe, dict): data to take care of. If ana array,
            it is considered in order of fragment_names.
            If it is a dataframe or a dict, the name of fragments are the keys.
        criteria (func): function that can be applied to the data items.
            The function is applied to each of the data elements and the
            criteria is assumed to be satisfied
            if any of the element fulfill the criteria
        columns (list): the fragment to focus the search to.
            Useful in the case of a dictionary
    Returns:
        list: fragments that fulfill the criteria
    """
    from BigDFT.IO import reorder_fragments
    accepted = []
    for ikey, key in enumerate(sys.fragment_names):
        if isinstance(data, dict):
            if key in data:
                if columns is None:
                    columns = data[key].keys()
                datarr = [data[key][val] for val in columns]
            else:
                datarr = []
        else:  # this assumes that the value is a scalar
            datarr = [data[ikey]]
        condition = any(criteria(d) for d in datarr)
        if condition:
            accepted.append(key)
    return reorder_fragments(accepted)


def _get_system(system=None, archive=None, filename=None,
                logfile=None, deepcopy=False, **kwargs):
    from copy import deepcopy as dc
    if system is not None:
        return dc(system) if deepcopy else system
    if archive is not None:
        sys = load(archive,
                   serialization_version=kwargs.get('serialization_version'),
                   options=kwargs.get('options', {}))
        return sys
    if filename is not None:
        sys = BioSystem(filename, **kwargs.get('options', {}))
    if logfile is not None:
        sys.set_qm_run(logfile)
    return sys


class BioSystemPopulation(BioSystem):
    """
    An ensemble of BioSystem. Useful to provide and analyze averaged quantities

    Args:
       systems(dict, list): BioSystems defining the populations.
           They can be provided as a dict of pdb files plus logfiles,
           or as a dictionary of systems,
           or as a dictionary of archives for serialization.
           The dictionary is composed as follows:
           <label>: {'archive': <archive_filename>,
                     'system': <BioSystem instance>,
                     'filename': <pdbfile>,
                     'logfile': <logfile_path>,
                     'weight': weigth of the sample in the population,
                     'mapping': provides the expression of the fragment of
                         the representative in term of the fragments of the
                         item of the population}
            alternatively, a list can be employed, in which case the filling of
            the population is performed sequentially
       representative (str, int): label of the system representative of
           the population
       exclude_representative (bool): if True, the data of the population will
           be evaluated without considering the representative
       fragment_values (list): list of the internal fragment values that can
           be found inside each of the system. Can be left as an empty list
           to delegate all the evaluation to the populations.
       fragment_interactions (list): list of the attributes which correspond
           to the quantities which are associated to inter-fragment
           interactions.
       to_evaluate(dict) : dictionary of functions to be employed to
           evaluate at the creation of a population.
           They must provide a quantity that is related to a system.
       chessboard_cutoffs (list): list of the cutoffs that will have
           to be employed for the fragmentation.
           Use an empty list to deactivate.
       initial_view (dict): view of the superunits fragmentation that will be
           employed to the representative in the lowest cutoff
       **kwargs: arguments to be passed at the loading of the system
    """
    def __new__(cls, systems, representative, **kwargs):
        from futile.Utils import merge_two_dicts
        sys = _get_system(deepcopy=True,
                          **merge_two_dicts(systems[representative], kwargs))
        sys.__class__ = BioSystemPopulation
        return sys

    def __init__(self, systems, representative,
                 fragment_values=['charge', 'dipole', 'purity'],
                 to_evaluate=None,
                 exclude_representative=False,
                 chessboard_cutoffs=[0.08, 0.05, 0.045, 0.04, 0.035, 0.03,
                                     0.025],
                 initial_view=None,
                 fragment_interactions=['bond_orders', 'interactions',
                                        'electrostatic_interactions'],
                 **kwargs):
        from BigDFT.Stats import Population
        self.populations_items = fragment_values
        # Include further quantities if present in the representative
        self.populations_items += list(self._fragment_quantities)
        self.dataframe_populations = fragment_interactions
        self.populations = {key: Population(labels=self.fragment_names)
                            for key in self.populations_items +
                            self.dataframe_populations}
        self.extra_populations = {}
        self.representative = representative
        self.exclude_representative = exclude_representative
        self._extra_population('system_dfs', None)
        if to_evaluate is not None:
            for label, func in to_evaluate.items():
                self._extra_population(label, func)
        self.systems = systems
        if len(chessboard_cutoffs) > 0:
            self.chessboard_dict = super(
                BioSystemPopulation, self).chessboards(
                cutoffs=chessboard_cutoffs, initial_view=initial_view)
        else:
            self.chessboard_dict = None
        self._fill_populations(**kwargs)

    def _fill_populations(self, **kwargs):
        from futile.Utils import fill_dictionary_in_parallel, kw_pop
        new_kwargs, nthreads = kw_pop('nthreads', 1, **kwargs)
        new_kwargs['biopop'] = self
        new_kwargs['cbs'] = self.chessboard_dict
        if nthreads == 1:
            dict_sys = {}
            if isinstance(self.systems, dict):
                keys = [k for k in self.systems.keys()
                        if not self.exclude_representative or
                        k != self.representative]
            else:
                keys = range(len(self.systems))
                if self.exclude_representative:
                    keys.remove(self.representative)
            for label in keys:
                dict_sys[label] = _data_of_one_system(label, **new_kwargs)
        else:
            dict_sys = fill_dictionary_in_parallel(nthreads,
                                                   self.systems.keys(),
                                                   _data_of_one_system,
                                                   **new_kwargs)
        for results in dict_sys.values():
            for pop_label, pop in self.populations.items():
                pop.append(**results[pop_label])
        self._assign_chessboard()

    def _extra_population(self, label, func):
        from BigDFT.Stats import Population
        self.populations[label] = Population()
        self.populations_items.append(label)
        self.extra_populations[label] = func

    def examine(self, axs=None, view=None):
        from BigDFT import Systems as S
        res = {}
        res['Number of atoms (representative)'] = sum(len(f)
                                                      for f in self.values())
        for df in self.populations['system_dfs'].datas:
            df_res = S.examine_system_dataframe(df, view=view)
            k = 'Minimum Distance'
            if k in df_res:
                res[k] = min(res.get(k, 1e10), df_res[k])
            k = 'coord_bonds_forces'
            cbf = res.setdefault(k, [0, 0, 0])
            for icn, cn in enumerate(df_res[k]):
                common_cn = {}
                for kk, v in cn.items():
                    common_val = common_cn.setdefault(kk, [])
                    common_val += v
                cbf[icn] = common_cn
        titles = ['Coordination Number', 'Bonds (AU)', 'Forces (AU)']
        res['axs'] = S._plot_systems_violinplot(res[k], axs, titles)
        return res

    def _assign_chessboard(self):
        if self.chessboard_dict is not None:
            self._cached_refragment = {str(c): clean_view(cb[-1], self)
                                       for c, cb in
                                       self.chessboard_dict.items()}

    def serialize(self, archive, chessboard_dict=None, **kwargs):
        """
        Dump the entire population into an archive, containing
        the representative archive, if it is provided as such
        (otherwise the serialization of the system)
        as well as the numpy files of all the population data.

        Args:
             archive(str): archive to dump the population to
             chessboard_dict (dict): optional dictionary of the fragmentation
                 of the population that has been previously found with
                 a chessboard algorithm. If absent, the internal chessboard is
                 employed
             **kwargs: arguments to be passed to `BioSystemSerialization`
                 instantiation in the case of a system.
        """
        from BigDFT.Stats import dump_populations
        from futile.Utils import serialize_objects, create_tarball, kw_pop
        from os.path import isfile
        repr_dict = self.systems[self.representative]

        if 'archive' in repr_dict:
            if isfile(repr_dict['archive']):
                files = [repr_dict['archive']]
            else:
                sys_archive = repr_dict['archive']
                files = {sys_archive: {'archive': self.archive,
                                       'file': sys_archive}}
        elif 'filename' in repr_dict:
            if isfile(repr_dict['filename']):
                files = [repr_dict['filename']]
            else:
                filename = repr_dict['filename']
                files = {filename: {'archive': self.archive,
                                    'file': filename}}
        else:
            if not hasattr(self, '_cached_refragment') and \
                    chessboard_dict is not None:
                self._cached_refragment = {str(c): cb[-1] for c, cb in
                                           chessboard_dict.items()}
            new_kw, version = kw_pop('version', '1.1', **kwargs)
            archive = 'representative.tar.bz2'

            serialization = BioSystemSerialization(self, version=version,
                                                   **new_kw)
            serialization.dump(archive)
            files = [archive]
        popfiles = dump_populations(self.populations)
        if isinstance(files, list):
            files += list(popfiles)
            files = set(files)
        else:
            files.update({f: f for f in popfiles})
        if chessboard_dict is None:
            chessboard_dict = self.chessboard_dict
        if chessboard_dict is not None and len(chessboard_dict) > 0:
            chb_obj = serialize_objects({'chessboard.json': chessboard_dict})
        else:
            chb_obj = {}
        create_tarball(archive, files, chb_obj)

    @classmethod
    def load(cls, archive, **kwargs):
        """
        Create a BioSystemPopulation instance from a serialized archive.

        Args:
            archive (str): the path of the archive
            **kwargs: other arguments that have to be passed to the
             BioSystemPopulation instantiation

        Returns:
            BioSystemPopulation: a biosystem population instance
        """
        from futile.Utils import unpack_tarball
        from shutil import rmtree
        from os.path import join
        from BigDFT.Stats import Population
        import json

        tmpdir, files = unpack_tarball(archive)

        for f in files:
            if '.tar.bz2' in f:
                # we found the system
                sys_dict = [{'archive': join(tmpdir, f)}]
                break
            if '.pdb' in f:
                # we found the filename
                sys_dict = [{'filename': join(tmpdir, f)}]
        loaded = cls(systems=sys_dict, representative=0,
                     fragment_values=[], chessboard_cutoffs=[], **kwargs)
        # restore the file name without the tmpdir for future reserialization
        for k in list(loaded.systems[loaded.representative]):
            f = loaded.systems[loaded.representative][k].replace(tmpdir, '')
            if f.startswith('/'):
                f = f[1:]
            loaded.systems[loaded.representative][k] = f
        for f in files:
            if '.json' in f:
                ff = open(join(tmpdir, f), 'r')
                loaded.chessboard_dict = json.load(ff)
                loaded._assign_chessboard()
                break

        pop_data = {f.replace('.npy', ''): Population.load(join(tmpdir, f))
                    for f in files if '.npy' in f}
        loaded.populations = pop_data
        loaded.set_archive_name(archive)
        rmtree(tmpdir)
        return loaded

    def _present_as_population(self, method):
        return hasattr(self, 'populations') and method in self.populations \
            and len(self.populations[method].datas) > 0

    @property
    def purities(self):
        if self._present_as_population('purity'):
            pop = self.populations['purity']
            mean = {f: -pop.mean[i] for i, f in enumerate(pop.feature_labels)}
            return mean
        else:
            return super(BioSystemPopulation, self).purities

    @property
    def bond_orders(self):
        if self._present_as_population('bond_orders'):
            pop = self.populations['bond_orders']
            return pop.mean.to_dict()
        else:
            return super(BioSystemPopulation, self).bond_orders

    @property
    def interactions(self):
        if self._present_as_population('interactions'):
            pop = self.populations['interactions']
            return pop.mean.to_dict()
        else:
            return super(BioSystemPopulation, self).interactions

    @property
    def electrostatic_interactions(self):
        return self._population_attribute_if_available(
            'electrostatic_interactions')

    def _population_attribute_if_available(self, attribute):
        if self._present_as_population(attribute):
            pop = self.populations[attribute]
            return pop.mean.to_dict()
        else:
            return getattr(super(BioSystemPopulation, self), attribute)

    def fragment_values(self, criteria, view=None):
        if criteria is None:
            return None
        if criteria in self.populations:
            pop = self.populations[criteria]
            mean = pop.mean
            # always reorder in term of fragment names
            if set(pop.feature_labels) == set(self.fragment_names):
                lup = [pop.feature_labels.index(f)
                       for f in self.fragment_names]
                field_vals = mean[lup]
                errors = pop.std[lup]
            elif 'charge' in self.populations:  # from the charge population
                lup = [self.populations['charge'].feature_labels.index(f)
                       for f in self.fragment_names]
                field_vals = mean[lup]
                errors = pop.std[lup]
            else:
                field_vals = mean
                errors = pop.std
        else:
            field_vals = super(BioSystemPopulation, self).fragment_values(
                criteria=criteria, view=view)
            errors = None
            if field_vals is None:
                return None
        if view is not None:
            field_vals = _aggregate_values(self.fragment_names,
                                           field_vals, view)
        return {'field_vals': field_vals, 'errors': errors}

    def colordict(self, field_vals=None, **kwargs):
        from numpy import array
        if field_vals is None:
            field_vals = self.fragment_values(criteria=kwargs.get('color_by'))
            if field_vals is not None:
                field_vals = field_vals['field_vals']
        elif isinstance(field_vals, dict) and 'field_vals' in field_vals:
            field_vals = field_vals['field_vals']
        return super(BioSystemPopulation, self).colordict(
            field_vals=array(field_vals).flatten(), **kwargs)

    def fragment_scatterplot(self, field_vals=None, errors=None, **kwargs):
        colors = self.colordict(field_vals=field_vals, **kwargs)
        if errors is None and field_vals is None:
            errors = self.fragment_values(
                                    criteria=kwargs.get('color_by'))['errors']
        if field_vals is None:
            field_vals = self.fragment_values(
                                 criteria=kwargs.get('color_by'),
                                 view=kwargs.get('view'))['field_vals']
        return super(BioSystemPopulation, self).fragment_scatterplot(
            field_vals=field_vals, errors=errors, colordict=colors, **kwargs)


def _data_of_one_system(label, **kwargs):
    from futile.Utils import merge_two_dicts, write
    biopop = kwargs['biopop']
    args = biopop.systems[label]
    wg = args.get('weight', 1.0)
    verbose = kwargs.get('verbose', True)
    if verbose:
        write(str(label) + ':  # weight='+str(wg))
    sys = _get_system(**merge_two_dicts(args, kwargs))
    results = {}
    # fragment the population
    cbs = kwargs.get('cbs')
    cutoffs = list(cbs.keys()) if cbs is not None else []
    if len(cutoffs) > 0:
        loosest_coff = sorted(cutoffs, reverse=True)[0]
        previous_view = cbs[loosest_coff][-1]
        new_view = clean_view(previous_view, sys)
        sys_cbs = sys.chessboards(cutoffs, initial_view=new_view)
    else:
        sys_cbs = []
    for cutoff in sys_cbs:
        view = cbs[cutoff][-1]
        review = sys_cbs[cutoff][0]
        # review = update_fragmentation(cutoff, view, sys)
        cbs[cutoff].append(review)
        if len(view) != len(review):
            write('The number of fragments has been modified', len(view),
                  len(review))
    for pop_label in biopop.populations:
        of = pop_label
        if verbose:
            write('  - ' + str(pop_label))
        if of in biopop.extra_populations and of != 'system_dfs':
            array = biopop.extra_populations[of](sys)
        elif of in biopop.dataframe_populations:
            array = getattr(sys, of, 0.0)
        else:
            array = sys.fragment_values(of)
        if pop_label == 'system_dfs':
            order = [frag for frag in biopop.fragment_names if frag in sys]
            order += [frag for frag in sys if frag not in order]
            data = sys.to_dataframe(order=order)
        else:
            data = reorder(array, sys, biopop, mapping=kwargs.get('mapping'))
        results[pop_label] = dict(data=data, weight=wg, label=label)
    return results


def update_fragmentation(cutoff, view_old, sys):
    """
    Update the fragmentation views starting from the last element of
    a list of views

    Args:
         cutoff (float): the cutoff to employ for the fragmentation
         view_old (dict): previous view of the system
         sys (BioSystem): the system employed to update the frament list
    Returns:
         dict: new view of the system
    """
    view = clean_view(view_old, sys)
    # erase any previously existing refragmentation
    sys._cached_refragment = {}
    return sys.refragment(cutoff, view=view)


def reorder(array, of, with_respect_to, mapping=None):
    """
    Reorder an array of data of systems in such a way that it can be applied
    to characterize another one.

    Args:
        array (array-like, dict): data in the order of `of.fragment_names`.
            in case of a dictionary, it is assumed that it contains the data
            coming from interactions or bond orders.
        of (BioSystem): the system associated to the original data
        with_respect_to (BioSystem): the system to which reorder the data
        mapping (dict): dictionary of the view that decomposes the fragments of
           ``with_respect_to`` in terms of the fragment of ``of`` in case of
           multiple elements in the values, an aggregation is considered.
           If mapping is present, there should not be undefined fragments
           in their values

    Returns:
        numpy.array: data in the new order. It contains `numpy.nan` for the
            fragments which are not present in the new system.
    """
    from numpy import ones, nan
    from BigDFT.PostProcessing import superunits_quadratic_quantities
    if isinstance(array, dict):
        ks = ['field_vals', 'errors']
        if all([k in array for k in ks]):
            newdata = {}
            for k in ks:
                newdata[k] = reorder(array[k], of, with_respect_to, mapping)
        if mapping is not None:
            newdata = superunits_quadratic_quantities(array, mapping)
        else:
            newdata = array
        return newdata
    data = ones(len(with_respect_to.fragment_names))*nan
    if mapping is not None:
        newarray = _aggregate_values(of.fragment_names, array, view=mapping)
    else:
        newarray = array
    for ifrag, frag_orig in enumerate(with_respect_to.fragment_names):
        frag = frag_orig
        if frag not in of.fragment_names:
            continue
        jfrag = of.fragment_names.index(frag)
        data[ifrag] = newarray[jfrag]
    return data


def clean_view(view_orig, superunits):
    """
    Define a view of the system that comes from a view of another one.
    Superunits are cleaned in such a way that no inconsistencies are present
    in the new view.

    Args:
       view_orig (dict): the original view we would like to clean
       superunits (list): list of the new system's superunits
    Returns:
       dict: the new view of the system, where combined superunits are
           joined with the '+' symbol
    """
    if view_orig is None:
        return None
    view = view_orig.copy()
    allvals = []
    for k, val_orig in view_orig.items():
        val = [v for v in val_orig]
        for v in val_orig:
            if v not in superunits:
                previous_k = '+'.join(val)
                if k in view:
                    view.pop(k)
                else:
                    view.pop(previous_k)
                val.remove(v)
                rek = '+'.join(val)
                view[rek] = val
            else:
                allvals.append(v)
    for k in list(view.keys()):
        if len(view[k]) == 0:
            view.pop(k)
    for k in superunits:
        if k not in allvals:
            view[k] = [k]
    return view


def rename_residue(res):
    """
    Rename the residue of the system such that alphabetical order
    corresponds to sequence order

    Args:
        res (str): residue of the system, in form "chain-resname:pos"
    Returns:
        str: residue in the form "chain-pos:letter"
    Warning:
        Only put letters to residues which have letter associated
    """
    ch, namepos = res.split('-')
    name, pos = namepos.split(':')
    lt = name_letter(name)
    letter = name if lt == 'X' else lt
    # try:
    #     letter = index_to_one(three_to_index(name))
    # except Exception:
    #     letter = name
    rename = ch + '-' + str(pos).zfill(3) + ':' + letter
    return rename


def rename_labels(labels, as_dict=False, from_dict=False,
                  mappable=rename_residue):
    """
    Rename the names of the residues of a BioSystem in order
    to be compatible with other naming schemes.

    Args:
        labels (iterable): contains the list of residue to be renamed
        as_dict (bool): if True, returns a dictionary as a relabel
        from_dict (bool): if True assumes that the remapping has to be
           performed also on the labels values.
        mappable (func): the function that will be applied for renaming
    Returns:
        dict, list: dictionary or list of the renamed labels, depending on
            the arguments.
    """
    relabel = [] if not from_dict else {}
    for label in labels:
        rename = '+'.join([mappable(res) for res in label.split('+')])
        if from_dict:
            relabel[rename] = map(mappable, labels[label])
        else:
            relabel.append(rename)
    return {k: v for k, v in zip(labels, relabel)} if as_dict else relabel


def _three_point_dispersion(frag, sys, extra, Eextra):
    subs = [frag] if '+' not in frag else frag.split('+')
    e1 = sys.d3PBE_energy(subsystem=subs)
    e12 = sys.d3PBE_energy(subsystem=subs + extra)
    return e12 - e1 - Eextra
