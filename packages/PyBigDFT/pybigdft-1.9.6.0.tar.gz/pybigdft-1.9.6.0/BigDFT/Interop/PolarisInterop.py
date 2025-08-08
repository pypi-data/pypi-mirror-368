"""A module to define typical operations that can be done on biological systems
   starting from the API and the PDB standards employed in the Polaris code

"""


def read_polaris_sle(slefile):
    """
    Read the setup file of polaris with the atomic information.

    Args:
        slefile(str): the sle polaris file.

    Returns:
        list: a list of the atoms of the system with the same order of
            the pdbfile, ready to be passed to the atoms attribute
    """
    attributes = []
    iat = 0
    with open(slefile) as ifile:
        for line in ifile:
            sleline = line.split()
            try:
                zion, ch, pn, mass, chg,\
                    polchg, chi, name, chain, iat, ires, res = sleline
                attributes.append({'q0': [float(chg)], 'name': name,
                                   'resnum': ':'.join(map(str, (res, ires)))})
            except Exception:
                pass
    return attributes


def write_bigdft_charges_in_sle(charges, slefile, outfile):
    """
    Override polaris charges coming from BigDFT file in the sle

    Args:
        charges (dict): dictionary of the {iat: charges}, with iat from the pdb
        slefile (str): the sle polaris file.
        outfile (str): the output file
    """
    fout = open(outfile, 'w')
    with open(slefile) as ifile:
        for line in ifile:
            sleline = line.split()
            try:
                zion, ch, pn, mass, chg,\
                    polchg, chi, name, chain, iat, ires, res = sleline
                newchg = charges[int(iat)]
                fout.write(' '.join(map(str, (zion, ch, pn, mass, newchg,
                                              polchg, chi, name, chain, iat,
                                              ires, res, '\n'))))
            except Exception:
                fout.write(line)
    fout.close()


def read_polaris_pdb(pdbfile, chain_as_letter=False, slefile=None):
    """
    Read coordinates in the PDB format of POLARIS

    Args:
       pdbfile (str): path of the input file
       chain_as_letter (bool): If True, the fifth column
           is assumed to contain a letter
       slefile (str): path of the file ``.sle`` of Polaris from which
           to extract the system's attributes.

    Warning:
       Assumes Free Boundary conditions for the molecule.
       Only accepts atoms that have one letter in the symbol.
       Switch representation if there is a single letter in the fifth column

    Returns:
       System: A system class
    """
    from BigDFT.Fragments import Fragment
    from BigDFT.Systems import System, GetFragId
    from BigDFT.Atoms import Atom
    from BigDFT.UnitCells import UnitCell
    from warnings import warn
    sys = System()
    sys.cell = UnitCell()
    units = 'angstroem'
    failed_parsing = []
    with open(pdbfile) as ifile:
            for line in ifile:
                if 'ATOM' not in line:
                    continue
                atomline = line.split()
                try:
                    if chain_as_letter:
                        iat, name, frag, lett, ifrag, x, y, z, sn = \
                            atomline[1:10]
                        chain = lett
                        segname = sn
                    else:
                        iat, name, frag, ifrag, x, y, z, chlett = atomline[1:9]
                        chain = chlett[2]
                        segname = chlett
                except Exception as e:
                    failed_parsing.append(line)
                    continue
                atdict = {str(name[:1]): list(map(float, [x, y, z])),
                          'frag': [chain+'-'+frag, int(ifrag)], 'name': name,
                          'iat': int(iat), 'segname': segname}
                fragid = GetFragId(atdict, iat)
                sys.setdefault(fragid, Fragment()).append(Atom(atdict,
                                                               units=units))
    if len(failed_parsing) > 0:
        warn("The lines below have not been correctly parsed: " + '\n'.join(
             failed_parsing), UserWarning)

    if slefile is None:
        return sys
    attributes = read_polaris_sle(slefile)
    from BigDFT import Systems as S, Fragments as F, Atoms as A
    system = S.System()
    for name, frag in sys.items():
        refrag = F.Fragment()
        for at in frag:
            atdict = at.dict()
            att = attributes[atdict['iat']-1]
            assert att['name'] == atdict['name']
            atdict.update(att)
            refrag.append(A.Atom(atdict))
        system[name] = refrag
    return system


def split_pdb_trajectory(directory, filename, prefix):
    """
    Split a trajectory file into various PDB files containing a single
    snapshot.

    Args:
        directory (str): the path of the directory in which the trajectory
            file exists
        filename (str): the trajectory file name
        prefix (str): the name to be provided to the resulting files.
           Files are numbered by `prefix`0,1, etc.

    Returns:
        list: list of the files created, including the directory
    """
    files_to_treat = []
    from os.path import join
    f = open(join(directory, filename))
    fileid = 0
    for line in f.readlines():
        if 'CRYST1' in line:
            newfilename = join(directory, prefix + str(fileid) + '.pdb')
            newf = open(newfilename, 'w')
        newf.write(line)
        if 'ENDMDL' in line:
            newf.close()
            files_to_treat.append(newfilename)
            fileid += 1
    f.close()
    return files_to_treat


def calculate_fragment_charge(cion):
    """Charge of the counter ions of the fragment.

    Args:
        cion (~BigDFT.Fragments.Fragment) the counter_ion fragment.

    Returns:
        int: the charge to be applied once this fragment removed.
    """

    counter_ions = {'CL': -1, 'NA': 1}
    chg = 0
    for at in cion:
        chg += counter_ions.get(at['name'].upper(), 0)
    return -chg


def convert_pdb(filein, fileout, counter_ion_frag='O-ION:999', **kwargs):
    """
    Call the `func:read_polaris_pdb` function to convert the system, and verify
    that the converted filename is giving the same system.

    Args:
        filein (str): input file path
        fileout (str): output file path. Can be identical to filein
        counter_ion_frag (str): name of the counter ion fragment
        **kwargs: arguments to be passed to `func:read_polaris_pdb`

    Returns:
        int: the charge of the system with the counterion removed
    """
    from BigDFT.IO import write_pdb
    sys = read_polaris_pdb(filein, **kwargs)
    if counter_ion_frag in sys:
        charge = calculate_fragment_charge(sys.pop(counter_ion_frag))
    else:
        charge = 0
    ofile = open(fileout, 'w')
    write_pdb(system=sys, ofile=ofile)
    ofile.close()
    return charge


def reduce_sys(sys):
    for frag in sys.values():
        for at in list(range(len(frag)))[::-1]:
            if frag[at]['segname'][-1] == '1':
                frag.pop(at)
    for frag in list(sys.keys()):
        if len(sys[frag]) == 0:
            sys.pop(frag)
    return sys


def restrict_sys(sys):
    from futile.Utils import unique_filename
    from BigDFT.IO import read_pdb, write_pdb
    from os import remove
    sys = reduce_sys(sys)
    tmpfile = unique_filename(prefix='tmpcplx_')+'.pdb'
    ofile = open(tmpfile, 'w')
    write_pdb(system=sys, ofile=ofile)
    ofile.close()
    sys = read_pdb(open(tmpfile, 'r'))
    remove(tmpfile)
    return sys


class Trajectory():
    def __init__(self, trajfile):
        self.trajectory_file = trajfile

    def split_into_files(self, prefix, directory='.', force=False):
        from futile.Utils import file_list, ensure_dir
        from os.path import basename
        from warnings import warn
        self.prefix = prefix
        self.directory = directory
        ensure_dir(self.directory)
        previous_list = file_list(directory=self.directory,
                                  prefix=self.prefix,
                                  include_directory_path=True,
                                  exclude=basename(self.trajectory_file))
        if len(previous_list) > 0 and not force:
            warn('The trajectory has already been splitted, force to split')
            self.trajectory_files = previous_list
        else:
            self.trajectory_files = split_pdb_trajectory(
                directory=self.directory, filename=self.trajectory_file,
                prefix=self.prefix)

    def set_reference_system(self, snapshot=0, **kwargs):
        from os.path import join
        if not hasattr(self, 'sys0'):
            self.sys0 = read_polaris_pdb(
                pdbfile=join(self.directory,
                             self.prefix + str(snapshot) + '.pdb'), **kwargs)
        return self.sys0

    def set_distances_and_rmsds(self, dist_csv=None, rmsd_csv=None,
                                reduced_system=True, **kwargs):
        """Dataframe of the RMDSs with the reference system."""
        from BigDFT.Fragments import Fragment
        from BigDFT.Systems import distance_matrix
        from pandas import DataFrame, read_csv
        from copy import deepcopy
        from os.path import basename
        do_d = True
        do_r = True
        if dist_csv is not None:
            alld = read_csv(dist_csv)
            do_d = False
        if rmsd_csv is not None:
            allr = read_csv(rmsd_csv)
            do_r = False
        if not do_d and not do_r:
            return alld, allr
        rmsds = {}
        alldists = {}
        sys0 = self.sys0
        if reduced_system:
            rsys0 = deepcopy(sys0)
            rsys0 = restrict_sys(rsys0)
        else:
            rsys0 = sys0
        frag0 = Fragment(system=sys0)
        for i, ff in enumerate(self.trajectory_files):
            f = basename(ff).replace(self.prefix, '').replace('.pdb', '')
            sys = read_polaris_pdb(pdbfile=ff, **kwargs)
            if do_r:
                frag = Fragment(system=sys)
                rmsds[f] = [frag.rmsd(reference=frag0)]
            if do_d:
                if reduced_system:
                    sys = restrict_sys(sys)
                alldists[f] = distance_matrix(sys=sys, ref=rsys0)
            print(i, f, sum(len(f) for f in sys.values()))
        if do_d:
            alld = DataFrame(alldists)
        if do_r:
            allr = DataFrame(rmsds)
        return alld, allr


def select_snapshots(clustering, ratio=10):
    gd = clustering
    tot = []
    for cluster in sorted(gd):
        snapshots = list(map(str, sorted([int(n) for n in gd[cluster]])))
        selection = [s for i, s in enumerate(snapshots)
                     if i % ratio == ratio-1]
        tot += selection
    return tot


def save_linkage_info(alldf, linkage_file, names_file):
    from scipy.cluster import hierarchy as hc
    from numpy import savetxt, array
    zaverage = hc.linkage(alldf.values.T, method='average',
                          metric='correlation')
    names = array(list(alldf.columns))
    savetxt(X=zaverage, fname=linkage_file)
    savetxt(X=names, fname=names_file, fmt='%s')


def gather_rmsd(allclusters, allrmsd):
    from BigDFT.Atoms import AU_to_A
    from pandas import DataFrame
    alldata = {'snapshot': [], 'rmsd': [], 'cluster': []}
    for c, names in allclusters.items():
        for n in names:
            alldata['snapshot'].append(n)
            alldata['rmsd'].append(AU_to_A*float(allrmsd[n]))
            alldata['cluster'].append(c)
    return DataFrame(alldata)


def analyze_clustering(z, names, t, rmsds, axs):
    from BigDFT.Stats import plot_clusters
    data = plot_clusters(z, names, t, ax=axs[0])
    df = gather_rmsd(data, rmsds)
    df.boxplot('rmsd', by='cluster', ax=axs[1])
    return data


class ProgressBar():
    from sys import stdout

    def __init__(self, nsteps, width=40, stream=stdout):
        self.toolbar_width = width
        self.stream = stream
        self.nsteps = nsteps
        self.setup()

    # setup toolbar
    def setup(self):
        self.stream.write("[%s]" % (" " * self.toolbar_width))
        self.stream.flush()
        self.stream.write("\b" * (self.toolbar_width+1))  # return after '['
        self.istep = 0

    def step(self, istep):  # should be monotonic
        x = float(istep) / float(self.nsteps) * float(self.toolbar_width)
        jstep = int(x)
        for i in range(self.istep, jstep):
            # update the bar
            self.stream.write("-")
            self.stream.flush()
        self.istep = jstep

    def release(self):
        self.stream.write("]\n")  # this ends the progress bar
        self.istep = 0
