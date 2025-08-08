"""
This module is useful to process a logfile of BigDFT run, in yaml format.
It also provides some tools to extract typical informations about the run,
like the energy, the eigenvalues and so on.
"""

# to be appropriately put in a suitable module
kcal_mev = 43.364
to_kcal = 1.0/kcal_mev*27.211386*1000

EVAL = "eval"
SETUP = "let"
INITIALIZATION = "globals"

PATH = 'path'
PRINT = 'print'
GLOBAL = 'global'
TYPE = 'type'
FLOAT_SCALAR = 'float'
MIXED_SCALAR = 'scalar of mixed type'

PRE_POST = [EVAL, SETUP, INITIALIZATION]

# Builtin paths to define the search paths
BUILTIN = {
    'number_of_orbitals': {PATH: [['Total Number of Orbitals']],
                           PRINT: "Total Number of Orbitals", GLOBAL: True},
    'posinp_file': {PATH: [['posinp', 'properties', 'source', ]],
                    PRINT: "source:", GLOBAL: True},
    'XC_parameter': {PATH: [['dft', 'ixc'], ['DFT parameters:', 'XC ID:']],
                     PRINT: "ixc:", GLOBAL: True, TYPE: MIXED_SCALAR},
    'grid_spacing': {PATH: [["dft", "hgrids"]],
                     PRINT: "hgrids:", GLOBAL: True},
    'spin_polarization': {PATH: [["dft", "nspin"]],
                          PRINT: "nspin:", GLOBAL: True},
    'total_magn_moment': {PATH: [["dft", "mpol"]],
                          PRINT: "mpol:", GLOBAL: True},
    'system_charge': {PATH: [["dft", "qcharge"]],
                      PRINT: "qcharge:", GLOBAL: True},
    'rmult': {PATH: [["dft", "rmult"]],
              PRINT: "rmult:", GLOBAL: True},
    # 'up_elec'::{PATH: [["occupation:","K point 1:","up:","Orbital \d+"]],
    #       PRINT: "Orbital \d+", GLOBAL: True},
    'astruct': {PATH: [['Atomic structure']]},
    'data_directory': {PATH: [['Data Writing directory']]},
    'dipole': {PATH: [['Electric Dipole Moment (AU)', 'P vector']],
               PRINT: "Dipole (AU)"},
    'electrostatic_multipoles': {PATH: [['Multipole coefficients']]},
    'energy': {PATH: [["Last Iteration", "FKS"], ["Last Iteration", "EKS"],
                      ["Energy (Hartree)"],
                      ['Ground State Optimization', -1,
                       'self consistency summary', -1, 'energy']],
               PRINT: "Energy", GLOBAL: False},
    'trH': {PATH: [['Ground State Optimization', -1, 'kernel optimization',
                    -2, 'Kernel update', 'Kernel calculation', 0, 'trace(KH)']]
            },
    'hartree_energy': {PATH: [["Last Iteration", 'Energies', 'EH'],
                              ['Ground State Optimization', -1,
                               'self consistency summary', -1,
                               'Energies', 'EH']]},
    'ionic_energy': {PATH: [['Ion-Ion interaction energy']]},
    'XC_energy': {PATH: [["Last Iteration", 'Energies', 'EXC'],
                         ['Ground State Optimization', -1,
                          'self consistency summary', -1,
                          'Energies', 'EXC']]},
    'trVxc': {PATH: [["Last Iteration", 'Energies', 'EvXC'],
                     ['Ground State Optimization', -1,
                      'self consistency summary', -1,
                      'Energies', 'EvXC']]},
    'evals': {PATH: [["Complete list of energy eigenvalues"],
                     ["Ground State Optimization", -1, "Orbitals"],
                     ["Ground State Optimization", -1,
                      "Hamiltonian Optimization", -1, "Subspace Optimization",
                      "Orbitals"]]},
    'fermi_level': {PATH: [["Ground State Optimization", -1, "Fermi Energy"],
                           ["Ground State Optimization", -1,
                            "Hamiltonian Optimization", -1,
                            "Subspace Optimization", "Fermi Energy"]],
                    PRINT: True, GLOBAL: False},
    'forcemax': {PATH: [["Geometry", "FORCES norm(Ha/Bohr)", "maxval"],
                        ['Clean forces norm (Ha/Bohr)', 'maxval']],
                 PRINT: "Max val of Forces"},
    'forcemax_cv': {PATH: [['geopt', 'forcemax']],
                    PRINT: 'Convergence criterion on forces',
                    GLOBAL: True, TYPE: FLOAT_SCALAR},
    'force_fluct': {PATH: [["Geometry", "FORCES norm(Ha/Bohr)", "fluct"]],
                    PRINT: "Threshold fluctuation of Forces"},
    'forces': {PATH: [['Atomic Forces (Ha/Bohr)']]},
    'gnrm_cv': {PATH: [["dft", "gnrm_cv"]],
                PRINT: "Convergence criterion on Wfn. Residue", GLOBAL: True},
    'kpts': {PATH: [["K points"]],
             PRINT: False, GLOBAL: True},
    'kpt_mesh': {PATH: [['kpt', 'ngkpt']], PRINT: True, GLOBAL: True},
    'magnetization': {PATH: [["Ground State Optimization", -1,
                              "Total magnetization"],
                             ["Ground State Optimization", -1,
                              "Hamiltonian Optimization", -1,
                              "Subspace Optimization", "Total magnetization"]],
                      PRINT: "Total magnetization of the system"},
    'memory_run': {PATH: [
      ['Accumulated memory requirements during principal run stages (MiB.KiB)']
    ]},
    'memory_quantities': {PATH: [
      ['Memory requirements for principal quantities (MiB.KiB)']]},
    'memory_peak': {PATH: [['Estimated Memory Peak (MB)']]},
    'nat': {PATH: [['Atomic System Properties', 'Number of atoms']],
            PRINT: "Number of Atoms", GLOBAL: True},
    'pressure': {PATH: [['Pressure', 'GPa']], PRINT: True},
    'sdos': {PATH: [['SDos files']], GLOBAL: True},
    'support_functions': {PATH: [["Gross support functions moments",
                                  'Multipole coefficients', 'values']]},
    'stress_tensor': {PATH: [['Stress Tensor',
                              'Total stress tensor matrix (Ha/Bohr^3)']],
                      PRINT: "Stress Tensor"},
    'symmetry': {PATH: [['Atomic System Properties', 'Space group']],
                 PRINT: "Symmetry group", GLOBAL: True}}


def get_logs(files):
    """
    Return a list of loaded logfiles from files, which is a list
    of paths leading to logfiles.

    Args:

    :param files: List of filenames indicating the logfiles
    :returns: List of Logfile instances associated to filename
    """
    from futile import YamlIO
    logs = []
    for filename in files:
        logs += YamlIO.load(filename, doc_lists=True, safe_mode=True)
    return logs


# This is a tentative function written to extract information from the runs
def document_quantities(doc, to_extract):
    """
    Extract information from the runs.

    .. warning::
        This routine was designed for the previous parse_log.py script and it
        is here only for backward compatibility purposes.
    """
    analysis = {}
    for quantity in to_extract:
        if quantity in PRE_POST:
            continue
        # follow the levels indicated to find the quantity
        field = to_extract[quantity]
        if not isinstance(field, list) and not isinstance(field, dict) \
                and field in BUILTIN:
            paths = BUILTIN[field][PATH]
        else:
            paths = [field]
        # now try to find the first of the different alternatives
        for path in paths:
            # print path,BUILTIN,BUILTIN.keys(),field in BUILTIN,field
            value = doc
            for key in path:
                # as soon as there is a problem the quantity is null
                try:
                    value = value[key]
                except (KeyError, TypeError):
                    value = None
                    break
            if value is not None:
                break
        analysis[quantity] = value
    return analysis


def perform_operations(variables, ops, debug=False):
    """
    Perform operations given by 'ops'.
    'variables' is a dictionary of variables i.e. key=value.

    .. warning::
       This routine was designed for the previous parse_log.py script and it is
       here only for backward compatibility purposes.
    """
    for key in variables:
        command = key+"="+str(variables[key])
        if debug:
            print(command)
        exec(command)
        # then evaluate the given expression
    if debug:
        print(ops)
    # exec(glstr+ops, globals(), locals())
    exec(ops, globals(), locals())


def process_logfiles(files, instructions, debug=False):
    """
    Process the logfiles in files with the dictionary 'instructions'.

    .. warning::
       This routine was designed for the previous parse_log.py script and it is
       here only for backward compatibility purposes.
    """
    import sys
    glstr = 'global __LAST_FILE__ \n'
    glstr += '__LAST_FILE__='+str(len(files))+'\n'
    if INITIALIZATION in instructions:
        for var in instructions[INITIALIZATION]:
            glstr += "global "+var+"\n"
            glstr += var + " = " + str(instructions[INITIALIZATION][var])+"\n"
            # exec var +" = "+ str(instructions[INITIALIZATION][var])
    exec(glstr, globals(), locals())
    for f in files:
        sys.stderr.write("#########processing "+f+"\n")
        datas = get_logs([f])
        for doc in datas:
            doc_res = document_quantities(doc, instructions)
            # print doc_res,instructions
            if EVAL in instructions:
                perform_operations(doc_res, instructions[EVAL], debug=debug)


def find_timefile(log):
    """Find the filename of the log which is associated to the timefile."""
    from os.path import isfile, dirname, basename, join
    from os import system
    from itertools import product

    run_datadir = getattr(log, 'datadir', None)
    possible_dirs = [] if run_datadir is None else [run_datadir]

    basedir = dirname(log.label)
    datadir = getattr(log, 'data_directory', None)
    possible_dirs += [] if datadir is None else [join(basedir, datadir),
                                                 basedir]

    radical = log.log.get('radical')
    if radical is None:  # sometimes it is None in the yaml file
        radical = ''
    logname = basename(log.label)
    possible_radicals = [radical, logname.replace('log-',
                                                  '').replace('.yaml',
                                                              '')]
    for directory, rad in product(possible_dirs, possible_radicals):
        filename = 'time' + ('-'+rad if len(rad) > 0 else '') + '.yaml'
        timefile = join(directory, filename)
        if isfile(timefile):
            # to solve yaml compliancy for old runs
            system(r"sed -i s/^\ *\:\ null/\ \ \ \ null/g "+timefile)
            return timefile


def build_tuple(inp):
    """recursively build a tuple from a dict, for hashing

    Arguments:
        inp (dict):
            input dictionary to be "tuple-ised"

    Returns:
        tuple
    """
    store = []
    if isinstance(inp, dict):
        for k, v in inp.items():
            if isinstance(v, dict):
                store.append((k, build_tuple(v)))
            elif isinstance(v, (set, list, tuple)):
                store.append((k, tuple(build_tuple(x) for x in v)))
            else:
                store.append((k, v))

    return tuple(store)


def get_scf_curves(iters):
    xy = {}
    it = 0
    for itout in iters:
        for k in ['wfn', 'rho', 'outer']:
            lxy = {}
            for i, dtt in enumerate(itout[k]):
                lxy.setdefault('x', []).append(it)
                lxy.setdefault('y', []).append(dtt)
                lxy.setdefault('label', []).append(i + 1)
                it += 1
            if len(lxy) > 0:
                xy.setdefault(k, []).append(lxy)
    if 'outer' in xy:
        xy['outer'] = {k: [v[k][0] for v in xy['outer']]
                       for k in 'xy'}
    return xy


def iteration_list(d, keylist):
    dt = d
    for key in keylist:
        dt = dt.get(key)
        if dt is None:
            break
    return dt if dt is not None else []


def extend_list(lt, d, keylist):
    dt = iteration_list(d, keylist)
    if dt != []:
        lt.append(dt)
        return True
    return False


def find_iterations(log):
    """Identify the different block of the iterations of the SCF cycle.

    Arguments:
            log (dictionary): logfile to be loaded.

    Returns:
           2-array: wavefunction residue per iterations,
                per each outer loop iteration.
    """
    outer = []
    inner_rho = []
    outer_rho = []
    gnrm_sp = []
    cubic = False
    for itrp in iteration_list(log, ['Ground State Optimization']):
        # cubic scaling version
        for itsp in iteration_list(itrp, ['Hamiltonian Optimization']):
            for it in iteration_list(itsp, ['Subspace Optimization',
                                            'Wavefunctions Iterations']):
                extend_list(gnrm_sp, it, ['gnrm'])
                extend_list(outer_rho, it, ['RhoPot delta per volume unit'])
                cubic = True
        # extend_list(outer_rho, itrp, ['RhoPot Delta'])
        # linear scaling version
        for it in iteration_list(itrp, ['support function optimization']):
            extend_list(gnrm_sp, it, ['fnrm'])
        for it in iteration_list(itrp, ['kernel optimization']):
            extend_list(inner_rho, it, ['summary', 'delta'])
        for it in iteration_list(itrp, ['self consistency summary']):
            extend_list(outer_rho, it, ['delta out'])
        if len(outer_rho) == 1 or cubic:
            outer.append({'wfn': gnrm_sp, 'rho': inner_rho,
                          'outer': outer_rho})
            inner_rho = []
            outer_rho = []
            gnrm_sp = []
    return outer


def get_convergence_quality(log):
    """Inform about the quality of the convergence."""
    iters = find_iterations(log)
    return iters[-1]['outer'][-1]


def plot_wfn_convergence(xy, gnrm_cv, label=None, ax=None):
    """
    Plot the convergence of the wavefunction coming from the find_iterations
    function.

    Arguments:
        wfn_it (list): list of dictionary coming from :func:`find_iterations`.
        gnrm_cv (float): convergence criterion for the residue of the
            wfn_it list.
        label(str): label for the given plot.

    Returns:
        matplotlib.Axes: Axes of the plot.
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.4, 4.8))
    else:
        ax = ax

    # ax.axhline(gnrm_cv, color='k', linestyle='dashdot')
    lb = 'wfn'
    for dt in xy[lb]:
        ax.semilogy(dt['x'], dt['y'], marker='o',
                    linestyle='solid', color='b', label=lb)
        lb = None
        ax.axvline(dt['x'][-1], color='k', linestyle='dashdot',
                   lw=0.1)

    if any(k in xy for k in ['rho', 'outer']):
        twins = ax.get_shared_x_axes().get_siblings(ax)
        if len(twins) == 1:
            ax2 = ax.twinx()
        else:
            ax2 = twins[0]
        ax2.set_ylabel('Density/Potential RMSD')

    lb = 'rho'
    for dt in xy.get('rho', []):
        ax2.semilogy(dt['x'], dt['y'], marker='s',
                     linestyle='solid', color='orange', label=lb)
        lb = None
        ax.axvline(dt['x'][-1], color='k', linestyle='dashdot',
                   lw=0.2)

    lb = 'outer'
    if 'outer' in xy:
        dt = xy[lb]
        ax2.semilogy(dt['x'], dt['y'], marker='s',
                     linestyle='solid', color='purple', label=lb)
        ax2.legend(loc="upper right")

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel('Inner Iterations')
    ax.set_ylabel('Norm of Residue')
    ax.legend(loc="center left")
    ax.set_title(label)
    return ax


class Logfile:
    """
    Import a Logfile from a filename in yaml format, a list of filenames,
    an archive (compressed tar file), a dictionary or a list of dictionaries.

    Args:
        *args: sequence of logfiles to be parsed. If it is longer than
            one item, the logfiles are considered as belonging to the same run.
        **kwargs: describes how the data can be read. Keywords can be:

           * archive: name of the archive from which retrieve the logfiles.

           * member: name of the logfile within the archive. If absent, all the
               files of the archive will be considered as args.

           * label: the label of the logfile instance

           * dictionary: parsed logfile given as a dictionary,
               serialization of the yaml logfile

    Example:
       >>> l = Logfile('one.yaml','two.yaml')
       >>> l = Logfile(archive='calc.tgz')
       >>> l = Logfile(archive='calc.tgz',member='one.yaml')
       >>> l = Logfile(dictionary=dict1)
       >>> l = Logfile(dictionary=[dict1, dict2])

    Todo:
       Document the automatically generated attributes, perhaps via an inner
       function in futile python module.
    """

    def __init__(self, *args, **kwargs):
        import os
        dicts = []
        # Read the dictionary kwargs
        arch = kwargs.get("archive")
        member = kwargs.get("member")
        label = kwargs.get("label")
        dictionary = kwargs.get("dictionary")
        # if arch is not None:
        #     self.archive_path
        if arch:
            # An archive is detected
            import tarfile
            from futile import YamlIO
            tar = tarfile.open(arch)
            members = [tar.getmember(member)] if member else tar.getmembers()
            # print members
            for memb in members:
                f = tar.extractfile(memb)
                dicts += YamlIO.load(stream=f.read())
                # Add the label (name of the file)
                # dicts[-1]['label'] = memb.name
            srcdir = os.path.dirname(arch)
            label = label if label is not None else arch
        elif dictionary:
            # Read the dictionary or a list of dictionaries or from a generator
            # Need to return a list
            dicts = [dictionary] if isinstance(dictionary, dict) else [
                d for d in dictionary]
            srcdir = ''
            label = label if label is not None else 'dict'
        elif args:
            # Read the list of files (member replaces load_only...)
            dicts = get_logs(args)
            label = label if label is not None else args[0]
            srcdir = os.path.dirname(args[0])
        #: Label of the Logfile instance
        self.label = label
        #: Absolute path of the directory of logfile
        self.srcdir = os.path.abspath('.' if srcdir == '' else srcdir)
        if not dicts:
            raise ValueError("No log information provided.")
        # So we have a list of a dictionary or a list of dictionaries
        # Initialize the logfile with the first document
        self._initialize_class(dicts[0])
        #
        if len(dicts) > 1:
            # first initialize the instances with the previous logfile such as
            # to provide the correct information (we should however decide what
            # to do if some run did not converged)
            self._instances = []
            for i, d in enumerate(dicts):
                # label=d.get('label','log'+str(i))
                label = 'log'+str(i)
                dtmp = dicts[0]
                # Warning: recursive call!!
                instance = Logfile(dictionary=dtmp, label=label)
                # now update the instance with the other value
                instance._initialize_class(d)
                if (instance.datadir is None):
                    instance.datadir = self.datadir
                self._instances.append(instance)
            # then we should find the best values for the dictionary
            print('Found', len(self._instances), 'different runs')
            import numpy
            # Initialize the class with the dictionary corresponding to the
            # lower value of the energy
            ens = [(ll.energy if hasattr(ll, 'energy') else 1.e100)
                   for ll in self._instances]
            #: Position in the logfile items of the run associated to lower
            #  energy
            self.reference_log = numpy.argmin(ens)
            # print 'Energies',ens
            self._initialize_class(dicts[self.reference_log])

    def __getitem__(self, index):
        if hasattr(self, '_instances'):
            return self._instances[index]
        elif isinstance(index, str):
            raise ValueError(
                'No multiple instances and string used in getitem.')
        else:
            # print('index not available')
            raise ValueError(
                'This instance of Logfile has no multiple instances.')

    def __str__(self):
        """Display short information about the logfile"""
        return self._print_information()

    def __len__(self):
        if hasattr(self, '_instances'):
            return len(self._instances)
        else:
            return 0  # single point run

    def __toType(self, val, tp=None):
        from futile.Utils import floatify
        if tp == FLOAT_SCALAR:
            return floatify(val)
        elif tp == MIXED_SCALAR:
            try:
                return floatify(val)
            except ValueError:
                pass
        elif tp is not None:
            raise ValueError("Unsupported type '%s' to convert '%s'." % (tp,
                                                                         val))
        return val

    def __hash__(self):
        return hash(build_tuple(self.log))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.__hash__() == other.__hash__()

    def _initialize_class(self, d):
        import numpy
        import os
        from BigDFT import BZ
        # : dictionary of the logfile (serialization of yaml format)
        self.log = d
        # here we should initialize different instances of the logfile class
        # again
        sublog = document_quantities(self.log, {val: val for val in BUILTIN})
        for att, val in sublog.items():
            if val is not None:
                setattr(self, att, self.__toType(val, BUILTIN[att].get(TYPE)))
            elif hasattr(self, att) and not BUILTIN[att].get(GLOBAL):
                delattr(self, att)
        # then postprocess the particular cases
        if not hasattr(self, 'fermi_level') and hasattr(self, 'evals'):
            self._fermi_level_from_evals(self.evals)

        if hasattr(self, 'kpts'):
            #: Number of k-points, present only if meaningful
            self.nkpt = len(self.kpts)
            if hasattr(self, 'evals'):
                # self.occupation_numbers =
                self.evals = self._get_bz(self.evals, self.kpts)
            if hasattr(self, 'forces') and hasattr(self, 'astruct'):
                self.astruct.update({'forces': self.forces})
                delattr(self, 'forces')
        elif hasattr(self, 'evals'):
            #: Eigenvalues of the run, represented as a
            #  :class:`BigDFT.BZ.BandArray` class instance
            self.evals = [BZ.BandArray(self.evals), ]
        if hasattr(self, 'sdos'):
            # load the different sdos files
            sd = []
            for f in self.sdos:
                try:
                    data = numpy.loadtxt(os.path.join(self.srcdir, f))
                except IOError:
                    data = None
                if data is not None:
                    xs = []
                    ba = [[], []]
                    for line in data:
                        xs.append(line[0])
                        ss = self._sdos_line_to_orbitals(line)
                        for ispin in [0, 1]:
                            ba[ispin].append(ss[ispin])
                    sd.append({'coord': xs, 'dos': ba})
                else:
                    sd.append(None)
            #: Spatial density of states, when available
            self.sdos = sd
        # memory attributes
        self.memory = {}
        for key in ['memory_run', 'memory_quantities', 'memory_peak']:
            if hasattr(self, key):
                title = BUILTIN[key][PATH][0][0]
                self.memory[title] = getattr(self, key)
                if key != 'memory_peak':
                    delattr(self, key)
        if ('outdir' in self.log):
            datadir = os.path.join(self.log['outdir'],
                                   self.log['Data Writing directory'])
            self.datadir = datadir
        else:
            self.datadir = None

        self.timefile = find_timefile(self)

    def _fermi_level_from_evals(self, evals):
        import numpy
        # this works when the representation of the evals is only with
        # occupied states
        # write('evals',self.evals)
        fl = None
        fref = None
        for iorb, ev in enumerate(evals):
            e = ev.get('e')
            if e is not None:
                fref = ev['f'] if iorb == 0 else fref
                fl = e
                if ev['f'] < 0.5*fref:
                    break
            e = ev.get('e_occ', ev.get('e_occupied'))
            if e is not None:
                fl = e if not isinstance(
                    e, list) else numpy.max(numpy.array(e))
            e = ev.get('e_vrt', ev.get('e_virt'))
            if e is not None:
                break
        #: Chemical potential of the system
        self.fermi_level = fl

    def _sdos_line_to_orbitals_old(self, sorbs):
        from BigDFT import BZ
        evals = []
        iorb = 1
        # renorm=len(xs)
        # iterate on k-points
        if hasattr(self, 'kpts'):
            kpts = self.kpts
        else:
            kpts = [{'Rc': [0.0, 0.0, 0.0], 'Wgt':1.0}]
        for i, kp in enumerate(kpts):
            ev = []
            # iterate on the subspaces of the kpoint
            for ispin, norb in enumerate(self.evals[0].info):
                for iorbk in range(norb):
                    # renorm postponed
                    ev.append({'e': sorbs[iorb+iorbk],
                               's': 1-2*ispin, 'k': i+1})
                    # ev.append({'e':np.sum([ so[iorb+iorbk] for so in sd]),
                    #            's':1-2*ispin,'k':i+1})
                iorb += norb
            evals.append(BZ.BandArray(
                ev, ikpt=i+1, kpt=kp['Rc'], kwgt=kp['Wgt']))
        return evals

    def _sdos_line_to_orbitals(self, sorbs):
        import numpy as np
        iorb = 1
        sdos = [[], []]
        for ikpt, band in enumerate(self.evals):
            sdoskpt = [[], []]
            for ispin, norb in enumerate(band.info):
                if norb == 0:
                    continue
                for i in range(norb):
                    val = sorbs[iorb]
                    iorb += 1
                    sdoskpt[ispin].append(val)
                sdos[ispin].append(np.array(sdoskpt[ispin]))
        return sdos

    def _get_bz(self, ev, kpts):
        """Get the Brillouin Zone."""
        evals = []
        from BigDFT import BZ
        for i, kp in enumerate(kpts):
            evals.append(BZ.BandArray(
                ev, ikpt=i+1, kpt=kp['Rc'], kwgt=kp['Wgt']))
        return evals

    def get_dos(self, **kwargs):
        """Get the density of states from the logfile.

        Fill a `py:class:~BigDFT.DoS.DoS` class object with the information
        which is stored in this logfile.

        Args:
            **kwargs: Keyword Arguments of the `py:class:~BigDFT.DoS.DoS`
                class.

        Returns:
            BigDFT.DoS.DoS: class instance. Filled with bandarrays and
               fermi_level.
        """
        from BigDFT import DoS
        args = {'label': self.label}
        if hasattr(self, 'sdos'):
            args['sdos'] = self.sdos
        args.update(kwargs)
        return DoS.DoS(bandarrays=self.evals, units='AU',
                       fermi_level=self.fermi_level, **kwargs)

    def get_brillouin_zone(self):
        """
        Return an instance of the BrillouinZone class, useful for band
        structure.
        :returns: Brillouin Zone of the logfile
        :rtype: :class:`BigDFT.BZ.BrillouinZone`
        """
        from BigDFT import BZ
        if self.nkpt == 1:
            print('WARNING: Brillouin Zone plot cannot be defined properly'
                  ' with only one k-point')
            # raise
        mesh = self.kpt_mesh  # : K-points grid
        if isinstance(mesh, int):
            mesh = [mesh, ]*3
        if self.astruct['cell'][1] == float('inf'):
            mesh[1] = 1
        return BZ.BrillouinZone(self.astruct, mesh, self.evals,
                                self.fermi_level)

    def SCF_convergence(self, ax=None):
        """
        Plot the wavefunction convergence.
        :Example:
           >>> tt=Logfile('log-with-wfn-optimization.yaml',label='a label')
           >>> tt.wfn_plot()
        """
        wfn_it = find_iterations(self.log)
        return plot_wfn_convergence(get_scf_curves(wfn_it), self.gnrm_cv,
                                    label=self.label, ax=ax)

    def geopt_plot(self, ax=None):
        """
        For a set of logfiles construct the convergence plot if available.
        Plot the Maximum value of the forces against the difference between
        the minimum value of the energy and the energy of the iteration.
        Also an errorbar is given indicating the noise on the forces for a
        given point. Show the plot as per plt.show() with matplotlib.pyplots as
        plt

        :Example:
           >>> tt=Logfile('log-with-geometry-optimization.yaml')
           >>> tt.geopt_plot()
        """
        import matplotlib.pyplot as plt
        if ax is None:
            self.fig, self.ax1 = plt.subplots(figsize=(6.4, 4.8))
        else:
            self.fig = ax.get_figure()
            self.ax1 = ax
        energies = []
        forces = []
        ferr = []
        if not hasattr(self, '_instances'):
            print('ERROR: No geopt plot possible, single point run')
            return
        for ll in self._instances:
            if hasattr(ll, 'forcemax') and hasattr(ll, 'energy'):
                forces.append(ll.forcemax)
                energies.append(ll.energy-self.energy)
                ferr.append(0.0 if not hasattr(ll, 'force_fluct') else (
                    self.force_fluct if hasattr(self, 'force_fluct') else 0.0))
        if len(forces) > 1:
            self.ax1.errorbar(energies, forces, yerr=ferr, fmt='.-',
                              label=self.label)
            self.ax1.legend(loc='best')
            self.ax1.loglog()
            self.ax1.set_xlabel('Energy - min(Energy)')
            self.ax1.set_ylabel('Forcemax')
            if hasattr(self, 'forcemax_cv'):
                self.ax1.axhline(self.forcemax_cv, color='k', linestyle='--')
            # plt.show()
        else:
            print('No plot necessary, less than two points found')
        return self.ax1

    def to_json(self, outfile):
        """Convert the logfile stream into a JSON file.

        Args:
           outfile (str): Path of the JSON output file.
        """
        import json

        def clean_timestamp(dt):
            timestr = str(dt['Timestamp of this run'])
            dt['Timestamp of this run'] = timestr

        if len(self) == 0:
            jsondict = self.log.copy()
            clean_timestamp(jsondict)
        else:
            jsondict = []
            for lf in self:
                dt = lf.log.copy()
                clean_timestamp(dt)
                jsondict.append(dt)
        with open(outfile, 'w') as ofl:
            json.dump(jsondict, ofl)

    def get_performance_info(self):
        """Retrieve a dictionary of the information about code performance."""
        from numpy import nan

        ks_first = {'Hostname': 'Root process Hostname',
                    'Date': 'Timestamp of this run',
                    'MPI': 'Number of MPI tasks',
                    'OMP': 'Maximal OpenMP threads per MPI task',
                    'SF': 'Total No. Support Functions',
                    'Orbitals': 'Total Number of Orbitals',
                    'Electrons': 'Total Number of Electrons'}
        ks_last = {'Mem': 'Memory Consumption Report',
                   'Walltime': 'Walltime since initialization'}
        if len(self) == 0:
            first = self
            last = self
        else:
            first = self[0]
            last = self[-1]
        df = {k: first.log.get(v, nan) for k, v in ks_first.items()}
        df.update({k: last.log.get(v, nan) for k, v in ks_last.items()})
        if ks_last['Mem'] in last.log:
            peak = df['Mem']['Memory occupation']['Memory Peak of process']
            df['Mem'] = float(peak.rstrip('MB'))
        df['Nat'] = len(self.astruct['positions'])
        df['cores'] = df['MPI']*df['OMP']
        df['TotMem'] = df['MPI']*df['Mem']
        df['MPI/Node'] = df.get('MPI tasks of root process node', 1)
        df['Nodes'] = int((df['MPI'] - 1)/df['MPI/Node']) + 1
        df['NodeMem'] = df['MPI/Node']*df['Mem']
        df['CPUhours'] = df['cores']*df['Walltime']/3600.0
        df['CPUmin/at'] = df['CPUhours']*60.0/df['Nat']
        df['Memory/at'] = df['TotMem']/df['Nat']
        for k in ['SF', 'Orbitals']:
            key = k + '/Node'
            df[key] = df[k]/df['Nodes']
        return df

    def get_summary(self):
        """Get a dictionary of the physical content of the logfile."""
        summary = []
        if 'Atomic System Properties' in self.log:
            summary.append(
                {'Atom types': self.log['Atomic System Properties'].get(
                    'Types of atoms', None)})
        if hasattr(self, 'astruct'):
            summary.append({'cell': self.astruct.get('cell', 'Free BC')})
        # normal printouts in the document, according to definition
        for field in BUILTIN:
            name = BUILTIN[field].get(PRINT)
            if name:
                name = field
            if not name or not hasattr(self, field):
                continue
            summary.append({name: getattr(self, field)})
        if hasattr(self, 'evals'):
            nspin = self.log.get('dft', {}).get('nspin', 0)
            if nspin == 4:
                nspin = 1
            cmt = (' per k-point' if hasattr(self, 'kpts') else '')
            summary.append(
                {'No. of KS orbitals'+cmt: self.evals[0].info[0:nspin]})
        return summary

    def _print_information(self):
        """Display short information about the logfile (used by str)."""
        import yaml
        summary = self.get_summary()
        return yaml.dump(summary, default_flow_style=False)

    def get_is_linear(self):
        """
        Returns True if this calculation was done in the linear scaling mode.

        Todo: there should be a more intentional way to do this.

        Returns:
            (logical): True if linear scaling calculation mode.
        """
        return self.log["dft"]["inputpsiid"] >= 100 and \
            self.log["dft"]["inputpsiid"] < 1000

    def get_intermediate_energies(self):
        """
        Gathers all the intermediary energy values and puts them in a list.

        For the case of mixing, this is the FKS values.
        For linear scaling, it is the energies computed during kernel
        optimization.

        Returns:
            (list): list of intermediary energy values.
        """
        vals = []
        gso = self.log["Ground State Optimization"]
        if self.get_is_linear():
            for step in gso:
                if "kernel optimization" not in step:
                    continue
                for opt in step["kernel optimization"]:
                    vals.append(opt["summary"]["energy"])
        else:
            for step in gso:
                if "Hamiltonian Optimization" not in step:
                    continue
                hmo = step["Hamiltonian Optimization"][0]
                wfit = hmo["Subspace Optimization"]["Wavefunctions Iterations"]
                for opt in wfit:
                    if "EKS" in opt:
                        vals.append(opt["EKS"])
                    elif "FKS" in opt:
                        vals.append(opt["FKS"])
        return vals

    def check_convergence(self):
        """
        Check if a calculation has converged.

        Returns:
            (logical): True if converged.
        """
        return self.log['BigDFT infocode'] == 0

    def check_convergence_cdft(self, cdft=False, cdft_thresh=0.01):
        """
        Check if a calculation has converged when doing CDFT.

        Args:
            cdft (logical): if CDFT is used a separate check is activated.
            cdft_thresh (float): the threshold for the deviation of Tr(KW)
            from 1.0.

        Returns:
            (logical): True if converged.
        """
        from warnings import warn

        converged = True
        gso = self.log['Ground State Optimization'][-1]

        summary = gso['kernel optimization'][-1]['summary']
        kw = summary['summary']['Constraint 1']['Tr(KW)']
        if abs(1.0 - kw) > cdft_thresh:
            converged = False
            warn("WARNING, Tr(KW) != 1.0, " + str(kw))

        return converged


def _identify_value(line, key):
    to_spaces = [',', ':', '{', '}', '[', ']']
    ln = line
    for sym in to_spaces:
        ln = ln.replace(sym, ' ')
    istart = ln.index(key) + len(key)
    copy = ln[istart:]
    return copy.split()[0]


def _log_energies(filename, into_kcal=False):
    from numpy import nan
    TO_SEARCH = {'Energy (Hartree)': 'Etot',
                 'Ion-Ion interaction energy': 'Eion',
                 'trace(KH)': 'Ebs', 'EH': 'Eh', 'EvXC': 'EVxc',
                 'EXC': 'EXC'}
    data = {}
    previous = {}
    f = open(filename, 'r')
    for line in f.readlines():
        for key, name in TO_SEARCH.items():
            if key in line:
                previous[name] = data.get(name, nan)
                todata = _identify_value(line, key)
                try:
                    todata = float(todata) * (to_kcal if into_kcal else 1.0)
                except Exception:
                    todata = nan
                data[name] = todata
    f.close()
    return data, previous


class Energies():
    """
    Find the energy terms from a BigDFT logfile.
    May also accept malformed logfiles that are issued, for instance,
    from a badly terminated run that had I/O error.

    Args:
        filename (str): path of the logfile
        units (str): may be 'AU' or 'kcal/mol'
        disp (float): dispersion energy (will be added to the total energy)
        strict (bool): assume a well-behaved logfile
    """
    def __init__(self, filename, units='AU', disp=None, strict=True):
        from numpy import nan
        TO_SEARCH = {'energy': 'Etot',
                     'ionic_energy': 'Eion',
                     'trH': 'Ebs', 'hartree_energy': 'Eh', 'trVxc': 'EVxc',
                     'XC_energy': 'EXC'}
        self.into_kcal = units == 'kcal/mol'
        self.conversion_factor = to_kcal if self.into_kcal else 1.0
        data, previous = _log_energies(filename,
                                       into_kcal=self.into_kcal)
        try:
            log = Logfile(filename)
            data = {name: getattr(log, att, nan) * self.conversion_factor
                    for att, name in TO_SEARCH.items()}
        except Exception:
            pass
        self._fill(data, previous, disp=disp, strict=strict)

    def _fill(self, data, previous, disp=None, strict=True):
        from numpy import nan
        if disp is None:
            self.dict_keys = []
            self.Edisp = 0
        else:
            self.dict_keys = ['Edisp']
            self.Edisp = disp
        for key, val in previous.items():
            setattr(self, key, val)
            self.dict_keys.append(key)
            setattr(self, key+'_last', data[key])
            self.dict_keys.append(key+'_last')
        for key in ['Etot', 'Eion', 'Ebs']:
            setattr(self, key, data.get(key, nan))
            self.dict_keys.append(key)
        try:
            self.Etot_last = self.Ebs_last + self.Eion - self.Eh_last + \
                             self.EXC_last - self.EVxc_last
            self.Etot_approx = self.Ebs - self.Eh + self.Eion
            self.sanity_error = self.Ebs - self.Eh + self.EXC - self.EVxc + \
                self.Eion - self.Etot
            self.dict_keys += ['Etot_last', 'Etot_approx']
            self.Etot_last += self.Edisp
            self.Etot_approx += self.Edisp
        except Exception:
            if strict:
                raise ValueError('the data is malformed', data, previous)
            self.sanity_error = 0.0
        if abs(self.sanity_error) > 1.e-4 * self.conversion_factor:
            raise ValueError('the sanity is too large', self.sanity_error)
        self.dict_keys += ['sanity_error']
        self.Etot += self.Edisp

    @property
    def to_dict(self):
        """
        Generate dictionary of log file attributes

        Returns:
            dict: log attributes
        """
        dd = {key: getattr(self, key) for key in self.dict_keys}
        return dd


if __name__ == "__main__":
    #  Create a logfile: should give an error
    # (ValueError: No log information provided.)
    from sys import argv  # we should use argparse
    name = argv[1]
    exclude = argv[2:]
    lf = Logfile(name).create_tar(name+'.tar.gz', exclude=exclude)
