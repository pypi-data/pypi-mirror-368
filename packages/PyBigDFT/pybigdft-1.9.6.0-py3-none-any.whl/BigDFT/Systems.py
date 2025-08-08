"""
This module contains the System level class of PyBigDFT. Systems are named
collections of fragments, and represent a complete system for simulation.
"""
from futile.Utils import write as safe_print

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping


class System(MutableMapping):
    """
    A system is defined as a named collection of fragments. You can manipulate
    a system as if it were a standard python dictionary, however it also has
    helper routines for performing operations on the full system.
    """

    def __init__(self, *args, **kwargs):
        from BigDFT.UnitCells import UnitCell
        self.store = dict()
        self.update(dict(*args, **kwargs))
        self.conmat = None
        self.cell = UnitCell()

    def dict(self):
        """
        Convert to a dictionary.
        """
        return self.store

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def __eq__(self, other):
        """
        Compare two systems. They are equal if all the fragments of
            the systems are identical.

        other (System): the fragment to compare with
        """
        try:
            if set(list(self)) != set(list(other)):
                return False
            for fragid in self:
                if self[fragid] != other[fragid]:
                    return False
        except TypeError:
            return False
        return True

    @property
    def centroid(self):
        """
        Center of mass of the system
        """
        from numpy import mean
        return mean([frag.centroid for frag in self.values()], axis=0).tolist()

    @property
    def central_fragment(self):
        """
        Returns the fragment whose center of mass is closest to the centroid

        Returns:
          (str): the name of the fragment.
          (Fragment): the fragment object
        """
        import numpy as np
        CMs = [frag.centroid for frag in self.values()]
        idx = np.argmin([np.dot(dd, dd.T)
                         for dd in (CMs - np.array(self.centroid))])
        return list(self.keys())[idx], list(self.values())[idx]

    def get_external_potential(self, units="bohr", charge_offset=False):
        """
        Transform the system information into a dictionary ready to be
        put as an external potential.

        Args:
          units (str): the units of the external potential.
          charge_offset (bool): by default the external potential ignores the
            counter charge from the protons. Setting this to true adds the
            positive charge to the potential.
        """
        ret_dict = {"units": units}
        ret_dict["values"] = []
        for frag in self.values():
            ret_dict["values"].extend(
                frag.get_external_potential(units, charge_offset))
        # ret_dict["global monopole"] = sum(
        #     x["q0"][0] for x in ret_dict["values"])
        return ret_dict

    def get_k_nearest_fragments(self, target, k, cutoff=None,
                                return_type='list'):
        """
        Given a fragment id in a system, this computes the nearest fragment.

        Args:
          target (str): the fragment to find the nearest neighbor of.
          k (int): the number of fragments to look for.
          cutoff (float): will only return fragments with a certain cutoff.
          return_type (str): 'list' or 'dict'
        Returns:
          (list, dict): the ids of the nearest fragments, or their distances
              as values in the case in which 'dict' is provided in the
              `return_type` argument
        """
        from scipy.spatial import KDTree

        # Setup the KD Tree for distance lookup
        poslist = []
        frag_lookup = []
        for fragid, frag in self.items():
            if fragid == target:
                continue
            for at in frag:
                poslist.append(at.get_position())
                frag_lookup.append(fragid)
        tree = KDTree(poslist)

        # Find the nearest fragments with a query of the tree.
        targetpost = [x.get_position() for x in self[target]]
        if cutoff is not None:
            ndist, nearest = tree.query(targetpost, k=k,
                                        distance_upper_bound=cutoff)
        else:
            ndist, nearest = tree.query(targetpost, k=k)

        # We now have the nearest atom to each atom in this fragment.
        # Next we combine this information and extract the closest
        # fragments.

        if k == 1:
            ndist = [ndist]
            nearest = [nearest]

        distdict = {}
        for i in range(0, len(nearest)):
            for idx, dist in zip(nearest[i], ndist[i]):
                try:
                    fragidx = frag_lookup[idx]
                except IndexError:
                    # kdtree returns invalid indices if it can't find enough
                    # points.
                    continue
                if fragidx not in distdict:
                    distdict[fragidx] = dist
                elif distdict[fragidx] > dist:
                    distdict[fragidx] = dist

        # Extract the k smallest values.
        minlist = []
        mindict = {}
        for i in range(0, k):
            if len(distdict) == 0:
                break
            key = min(distdict, key=distdict.get)
            minlist.append(key)
            mindict[key] = distdict[key]
            del distdict[key]

        if return_type == 'list':
            return minlist
        elif return_type == 'dict':
            return mindict

    def get_nearest_fragment(self, target):
        """
        Given a fragment id in a system, this computes the nearest fragment.

        Args:
          target (str): the fragment to find the nearest neighbor of.

        Returns:
          (str): the id of the nearest fragment.
        """
        return self.get_k_nearest_fragments(target, k=1)[0]

    def get_net_force(self):
        """
        Returns the net force on a system in Ha/Bohr.

        Returns:
          (list): Three values which describe the net force.
        """
        from numpy import array
        ret_val = array([0.0, 0.0, 0.0])
        for frag in self.values():
            ret_val += array(frag.get_net_force())
        return [float(x) for x in ret_val]

    def get_atoms(self, order=None):
        """Generator enabling to iterate on system's atoms.

        This function may be useful to control the order of the atoms
        positions.

        Args:
           order (list): order of the fragments. Useful on versions of python
               where the systems' dict are not ordered.
        Yields:
           BigDFT.Atoms.Atom: the next atom of the system.
        """
        if order is None:
            order = list(self)
        for frag in order:
            for at in self[frag]:
                yield at

    def get_posinp(self, units='angstroem', order=None):
        """
        Provide the dictionary which has to be passed to the ``posinp`` value
        of the :meth:`run` method of  the
        :class:`~BigDFT.Calculators.SystemCalculator` class instance.

        Args:
           units (str): The units of the file.
           order (list): order of the fragments to get the atoms from.

        Returns:
           dict: dictionary of the atomic positions ready to be employed.
        """
        from BigDFT.Atoms import IsReduced, MULTIPOLE_ANALYSIS_KEYS
        pos = []
        nokey = ['r', 'frag', 'Frozen', 'sym', 'units']
        nokey += MULTIPOLE_ANALYSIS_KEYS
        if order is None:
            order = list(self)
        for fragid in order:
            frag = self[fragid]
            for at in frag:
                atdict = {}
                atdict["frag"] = list(GetFragTuple(fragid))
                if frag.frozen:
                    atdict["Frozen"] = frag.frozen
                atdict.update({k: v for k, v in at.store.items()
                               if k not in nokey})
                atdict.update({at.sym: at.get_position(units, self.cell)})
                pos.append(atdict)

        result = {}
        result["positions"] = pos
        if IsReduced(units):
            result["units"] = "angstroem"
            result["cell"] = self.cell.get_posinp("angstroem")
            result["properties"] = {"reduced": "yes"}
        else:
            result["units"] = units
            result["cell"] = self.cell.get_posinp(units)

        return result

    def serialize(self, order=None, units='bohr'):
        """
        Transform the system in a list that can be employed for
        the construction of dataframes or pandas series.
        Args:
            order (list): list of fragments to serialize in order
            units (str): the units for the positions
        Returns:
            list: the serialized system as well as a lookup dictionary
                that contains the order of the fragment atoms in the series
        """
        if order is None:
            order = self
        positions = []
        lookup = {}
        iat = 0
        for key in order:
            frag = self[key]
            lookup[key] = [iat+i for i in range(len(frag))]
            iat += len(frag)
            positions += frag.serialize(name=key, units=units)
        return positions

    def subsystem(self, fragments):
        """Extract a subsystem.

        Create a subsystem from a collection of fragments.

        Args:
            fragments (list): the list of the original fragments which have
                to be inserted in the new system
        Returns:
            System: a new System class instance. The reference fragments are
                shallow-copied.
        """
        return System({frag: self[frag] for frag in fragments})

    @property
    def df(self):
        if not hasattr(self, '_df'):
            self._df = self.to_dataframe()
        return self._df

    def to_dataframe(self, **kwargs):
        """
        Convert the system into a dataframe, from the
        `py:meth:~System.serialize` method.

        Args:
            **kwargs: arguments to be passed to
                `py:meth:System.serialize` method
        """
        from pandas import DataFrame as DF
        df = DF(self.serialize(**kwargs))
        validate_dataframe_representation(self, df)
        return df

    def dataframe_slicing(self, df=None):
        """
        Define a dictionaries of two-element lists indicating the slicing
        (start and end points) of the corresponding fragment in the order
        provided by the dataframe

        Args:
            df (Dataframe): associated to the system

        Returns:
            dict:  dictionary of the slicings of the fragments in the dataframe
        """
        if df is None:
            df = self.df
        sl = fragment_slicing_from_system_dataframe(df)
        check_slicing(self, sl)
        return sl

    def distances_from_target(self, target):
        """
        Provide the dictionary of the distances from a target.

        Args:
            target (list): list of the fragments identifying the target.

        Returns:
            dict: dictionary of the minimum distance from the target per frag.
                Returns 0 if the fragment belongs to the target.
        """
        # from numpy import nan
        sl = self.dataframe_slicing()
        target_slicing = atom_slicing(sl, target)
        dist = self.PointParticles.R[target_slicing]
        alldist = {}
        for frag in self:
            if frag in target:
                val = 0.0
            else:
                frag_slicing = atom_slicing(sl, [frag])
                dist_restricted = dist[:, frag_slicing]
                val = min(dist_restricted.flatten())
            alldist[frag] = val
        return alldist

    def to_file(self, filename, **kwargs):
        """Dump the System instance into a file.

        Write the system information in the file system, according to the
        file extension

        Args:
            filename (str): path of the filename to write into. Automatically
                determine the format according to the file extension
            **kwargs: further kwyword arguments to be passed to the writing
                routine
        """
        from BigDFT import IO

        extension = filename.split('.')[-1].lower()

        with open(filename, 'w') as ofile:
            if extension == 'pdb':
                IO.write_pdb(system=self, ofile=ofile)
            if extension == 'xyz':
                IO.write_xyz(system=self, ofile=ofile)

    @property
    def PointParticles(self):
        """
        Transform the system into a `py:class:~PointParticles.PointParticles`
        object
        """
        from BigDFT.PointParticles import PointParticles as PP
        if not hasattr(self, '_PP'):
            self._PP = PP(**point_particle_objects(self.df))
        return self._PP

    @property
    def hartree_interactions(self):
        from BigDFT.PointParticles import PointParticles
        from numpy import array
        ppdict = point_particle_objects(self.df)
        ppdict['Z'] = array(len(ppdict['X'])*[[0.]])
        PP = PointParticles(**ppdict)
        return PP.Eel_dict(self.dataframe_slicing())

    @property
    def ionic_interactions(self):
        from BigDFT.PointParticles import PointParticles
        from numpy import array
        ppdict = point_particle_objects(self.df)
        ppdict.pop('P')
        ppdict['Q'] = array(len(ppdict['X'])*[[0.]])
        PP = PointParticles(**ppdict)
        return PP.Eel_dict(self.dataframe_slicing())

    @property
    def long_range_interactions(self):
        from pandas import DataFrame
        eh = DataFrame(self.hartree_interactions)
        ei = DataFrame(self.ionic_interactions)
        elr = ei-eh
        elr = 0.5*(elr + elr.T)
        return elr.to_dict()

    @property
    def electrostatic_interactions(self):
        """Dictionary of the Electrostatic interactions between fragments.
        """
        if not hasattr(self, '_Eel'):
            self._Eel = self.PointParticles.Eel_dict(self.dataframe_slicing())
        return self._Eel

    @property
    def q0(self):
        """
        Provides the global monopole of the system given as a sum of the
        monopoles of the atoms.
        """
        if len(self) == 0:
            return None
        return [sum(filter(None, [frag.q0[0] for frag in self.values()]))]

    @property
    def qcharge(self):
        """
        The total qcharge of a system.
        """
        return sum([frag.qcharge for frag in self.values()])

    def rename_fragments(self, fragment_mapping=None):
        """
        This procedure automatically names the fragments in a system.

        Args:
           fragment_mapping (dict) : Dictionary containing list
                 of fragments that are additionally added to each
                 of the original system's fragments.

        Returns:
          BigDFT.Systems.System: the same system, with the automatic naming
          scheme.
        """
        rnsys = System()
        for i, fragid in enumerate(self):
            if fragment_mapping is None:
                tuplek = "FRAG:"+str(i)
            else:
                additional_list = fragment_mapping[fragid]
                if not isinstance(additional_list, list):
                    tuplek = additional_list
                elif len(additional_list) == 0:
                    tuplek = fragid
                else:
                    # tuplek = (fragid, ) + tuple((f for f in additional_list))
                    tuplek = fragid + '+'+'+'.join(
                             [f for f in additional_list])
            rnsys[tuplek] = self[fragid]
        return rnsys

    def set_atom_multipoles(self, logfile, correct_charge=True):
        """
        After a run is completed, we have a set of multipoles defined on
        each atom. This routine will set those values on to each atom
        in the system.

        Args:
          logfile (Logfiles.Logfile): logfile with the multipole values.
          correct_charge (bool): currently there is an inconsistency in
            terms of gross charge, and this corrects it.
        """
        mp = logfile.electrostatic_multipoles
        for pole in mp["values"]:
            pole["units"] = mp["units"]
        lookup = self.compute_matching(mp["values"])

        # Assign
        for fragid, frag in self.items():
            for i, at in enumerate(frag):
                idx = lookup[fragid][i]
                if idx >= 0:
                    at.set_multipole(mp["values"][idx], correct_charge)

    def set_atom_forces(self, logfile):
        """
        After a run is completed, we have the forces on each atom in the
        logfile. This routine will set those values to each atom in this sytem.

        Args:
          logfile (Logfiles.Logfile): logfile with the forces.
        """
        from BigDFT.Fragments import Fragment
        posinp = logfile.log.get('posinp')
        if posinp is not None and not isinstance(posinp, str):
            atlist = Fragment(posinp=posinp)
        else:
            atlist = Fragment(astruct=logfile.astruct)
        lookup = self.compute_matching(atlist)

        # Assign forces
        try:
            forces = logfile.forces
        except AttributeError:
            forces = logfile.astruct["forces"]
        for fragid, frag in self.items():
            for i, at in enumerate(frag):
                idx = lookup[fragid][i]
                if idx >= 0:
                    at.set_force(list(forces[idx].values())[0])

    def compute_matching(self, atlist, check_matching=True):
        """
        Frequently we are passed a list of atom like objects from which we
        need to extract data and assign it to a system. However, a system
        can potentially store those atoms in any order, and may not have
        the same set of atoms. This helper routine creates a mapping between
        this list view, to the dictionary view of the system class.

        Args:
          atlist (list): a list of atom like objects.
          check_matching (bool): if set to True, this will raise an error
            if we can't match all of the atoms in the system.

        Returns:
          (dict): a mapping from a system to indices in the atom list. If
            an atom is not in the list, an index value of -1 is assigned.
        """
        from BigDFT.Atoms import Atom
        from numpy import array
        from scipy.spatial import KDTree

        # Convert everything to pure positions to avoid overhead.
        lookup = []
        poslist = []
        for i, x in enumerate(atlist):
            lookup.append(i)
            pos = array(Atom(x).get_position("bohr", cell=self.cell))
            poslist.append(pos)
            if self.cell[0, 0] != float("inf"):
                poslist.append([pos[0] + self.cell[0, 0], pos[1], pos[2]])
                lookup.append(i)
                poslist.append([pos[0] - self.cell[0, 0], pos[1], pos[2]])
                lookup.append(i)
            if self.cell[1, 1] != float("inf"):
                poslist.append([pos[0], pos[1] + self.cell[1, 1], pos[2]])
                lookup.append(i)
                poslist.append([pos[0], pos[1] - self.cell[1, 1], pos[2]])
                lookup.append(i)
            if self.cell[2, 2] != float("inf"):
                poslist.append([pos[0], pos[1], pos[2] + self.cell[2, 2]])
                lookup.append(i)
                poslist.append([pos[0], pos[1], pos[2] - self.cell[2, 2]])
                lookup.append(i)

        tree = KDTree(poslist)

        # Seach for the mapping values
        mapping = {}
        for fragid, frag in self.items():
            mapping[fragid] = []
            for at in frag:
                atpos = array(at.get_position("bohr", cell=self.cell))
                ndist, nearest = tree.query(atpos)
                if check_matching and ndist > 0.01:
                    raise ValueError("Unable to match atom" + str(dict(at)))
                mapping[fragid].append(lookup[nearest])

        return mapping

    def atomtype_system(self):
        """Returns a system Fragments along atom types. For display."""

        from BigDFT.Fragments import Fragment as F
        from collections import defaultdict

        sysd = defaultdict(F)
        for at in self.get_atoms():
            sysd[at.sym+':1'].append(at)

        return System(sysd)

    def display(self, colordict=None, field_vals=None, cartoon=False,
                by_types=False):
        """
        Display the system using the inline visualizer of Py3DMol.

        Arguments:

            cartoon(bool): define the cartoon representation.

            by_types(bool): when true, atoms are colorized by types.
                Other arguments are then ignored.

            colordict(dict): dictionary indicating the color per each fragment.

            field_vals(array-type): values in the fragment order of a scalar
                field defining the colors.

        """
        from BigDFT.Visualization import InlineVisualizer, _atoms
        viz = InlineVisualizer(400, 300)
        if by_types:
            sys = self.atomtype_system()
            cd = {f: _atoms[GetFragTuple(f)[0]] for f in sys}
        else:
            sys = self
            cd = colordict
        viz.display_system(sys, colordict=cd, field_vals=field_vals,
                           cartoon=cartoon)
        return viz

    def examine(self, axs=None, view=None):
        """ Provide quick overview of the system's quality.

        This routine displays information about the coordination numbers
        and the bond of the system. Useful to understand if some positions
        of the system need optimization.

        Args:
            axs: list of matplotlib axis in which to plot the information.
                If the forces are present it should be of size 3.
            view (dict): a Fragment view of the system in which to represent
                the fragment forces. If absent, the fragment forces are not
                represented.

        Returns:
            dict: Dictionary of the information about the system
        """
        res = {}
        res['Number of atoms'] = sum(len(f) for f in self.values())
        dist = self.PointParticles.R
        try:
            forces = {k: v.get_net_force() for k, v in self.items()}
        except Exception:
            forces = None
        res.update(examine_system_dataframe(self.df, dist, view,
                                            fragment_forces=forces))
        # Erase the Point Particle Object and the dataframe in the
        # case the coordinates change
        del self._PP
        del self._df
        titles = ['Coordination Number', 'Bonds (AU)']
        if forces is not None:
            titles += ['Forces (AU)']
        res['axs'] = _plot_systems_violinplot(res['coord_bonds_forces'], axs,
                                              titles)
        return res

    def set_electrons_from_log(self, log):
        """
        BigDFT uses pseudopotentials, so this will extract from a logfile
        the number of actual electrons modelled for each atom in the system.

        Args:
           log (Logfiles.Logfile) : A BigDFT run logfile.
        """
        electrons = {}
        for key in log.log:
            if "Properties of atoms in the system" not in key:
                continue
            try:
                for sys_i in log.log[key]:
                    electrons[sys_i['Symbol']] = sys_i['No. of Electrons']
            except TypeError:  # missing key in log
                pass

        for frag in self.values():
            for at in frag:
                at.nel = electrons[at.sym]

    def set_logfile_info(self, log):
        """
        Include the information of the logfile in the fragment quantities.

        Args:
           log (Logfiles.Logfile) : A BigDFT run logfile.
        """
        # provide the atomic information on the system
        if hasattr(log, 'electrostatic_multipoles'):
            self.set_atom_multipoles(log)
        if hasattr(log, 'forces'):
            self.set_atom_forces(log)
        self.set_electrons_from_log(log)

    def ase_potential_energy(self, ase_calculator):
        """
        Given a ASE calculator, calculates the potential energy
        of the system.

        Args:
            ase_calculator (ase.calculators.calculator.Calculator): ASE
              calculator.

        Returns:
            float: the potential energy, in Hartree
        """
        from BigDFT.Fragments import Fragment
        from BigDFT.Systems import System
        from BigDFT.Interop import ASEInterop
        bigsys = System()
        bigfrag = Fragment(system=self)
        bigsys['FULL:0'] = bigfrag
        return ASEInterop.ase_potential_energy(bigsys, ase_calculator)

    def reform_superunits(self, mapping):
        """
        Creates a new system from the provided mapping

        Args:
            mapping(dict): dictionary of the form {newfrag: [frag1,frag2]}
                defining the mapping between the old fragments and the new

        Returns:
            BigDFT.Systems.System: a new system from the remapping
        """
        newsys = System()

        for newfrag, fraglist in mapping.items():
            newsys[newfrag] = sum(self[f] for f in fraglist)

        return newsys

    def update_positions_from_dict(self, posinp):
        """
        Update the atomic positions of a system from a posinp dictionary.

        This method only works if the order of atoms match.

        Args:
            posinp (dict): a posinp dictionary.
        """
        from BigDFT.Atoms import Atom
        units = posinp.get("units", "angstroem")
        i = 0
        for frag in self.values():
            for at in frag:
                at2 = Atom(posinp["positions"][i], units=units)
                at.set_position(at2.get_position())
                i += 1

    def adjacency_matrix(self):
        """
        Generates a sparse adjacency matrix based on the connectivity of
        a system.

        Returns:
            (scipy.sparse.dok_matrix): the sparse adjacency matrix.
        """
        from scipy.sparse import dok_matrix

        # Check that connectivity matrix exists
        if self.conmat is None:
            raise ValueError("Connectivity matrix not generated")

        # Lookup table
        lookup = {}
        total = 0
        for fragid, frag in self.items():
            for i, at in enumerate(frag):
                lookup[fragid, i] = total
                total += 1

        # Iterate and fill
        mat = dok_matrix((total, total))
        for fragid1, frag1 in self.conmat.items():
            for i, at1 in enumerate(frag1):
                idx1 = lookup[(fragid1, i)]
                for (fragid2, j), bond_order in at1.items():
                    idx2 = lookup[(fragid2, j)]
                    mat[idx1, idx2] = bond_order
        return mat

    def fragment_view(self, purities, bond_orders, view=None):
        """Returns the fragment view of the system, according to a mapping.

        Args:
            view (dict): Mapping of the fragments to be taken initially.
            btool (BigDFT.PostProcessing.BigDFTool): Postprocessing class.
            purities (dict): purities of the fragments.
            bond_orders(dict): fragment bond orders.

            **kwargs: keyword arguments of
                `~py:func:BigDFT.PostProcessing.auto_fragment` method.

        Returns:
            FragmentView: the system fragment view
        """
        fw = FragmentView(purities, bond_orders,
                          charges={k: f.nel for k, f in self.items()})
        if view is None:
            new_fw = fw
        else:
            new_fw = fw.refragment(view)
        return new_fw

    def auto_fragment(self, btool, purities, bond_orders, view=None, **kwargs):
        """Calculates an automatic fragmentation of the system.

        Args:
            view (dict): Mapping of the fragments to be taken initially.
            btool (BigDFT.PostProcessing.BigDFTool): Postprocessing class.
            purities (dict): purities of the fragments.
            bond_orders(dict): fragment bond orders.

            **kwargs: keyword arguments of
                `~py:func:BigDFT.PostProcessing.auto_fragment` method.

        Returns:
            dict:  the new fragmentation obtained, provided as a mapping.
        """
        new_view = self.fragment_view(purities, bond_orders, view=view)
        if view is None:
            sys = System(self)
        else:
            sys = self.reform_superunits(view)
        remapping = btool.auto_fragment(sys, new_view, **kwargs)
        # the mapping has to be reworked in terms of a view
        # to prevent renaming of the original fragments
        if view is not None:
            remap = {}
            for frag, lst in remapping.items():
                if frag in view and lst == view[frag]:
                    remap[frag] = lst
                    continue
                remap[frag] = []
                for orig_frag in view:
                    if all(f in frag.split('+') for f in orig_frag.split('+')):
                        remap[frag] += view[orig_frag]
            remapping = remap
        return remapping

    def bare_nel(self):
        """Total number of electrons of the neutral system"""
        return float(sum(f.nel for f in self.values()))


def lineup_system(sys):
    """
    Align the principal axis of inertia of a system along the
    coordinate axis. Also shift the system such as its centroid is zero.

    Args:
      (BigDFT.Systems.System): the system to transform.

    Returns:
      (BigDFT.Systems.System): the transformed system.
    """
    from BigDFT.Fragments import lineup_fragment, RotoTranslation
    from copy import deepcopy

    # Lineup the whole system as if it were one big fragment.
    frag = sum(sys.values())
    new_frag = lineup_fragment(frag)

    # Extract the rototranslation.
    rt = RotoTranslation(frag, new_frag)

    # Apply it to each item in the system.
    new_sys = deepcopy(sys)
    for fragid, frag in sys.items():
        new_sys[fragid] = rt.dot(frag)
    return new_sys


def fragment_slicing_from_system_dataframe(df):
    """
    Define the slicing tuple needed to identify the fragment blocks
    into a system dataframe

    Args:
        df (Dataframe): the system dataframe

    Returns:
        dict: dictionary of the slicing obtained in form of [start,end] list
    """
    current = df['frag'][0]
    slicing = {current: [0]}
    for i, f in enumerate(df['frag']):
        if f not in slicing:
            slicing[current].append(i)
            slicing[f] = [i]
            current = f
    slicing[current].append(i+1)
    return slicing


def check_slicing(system, slicing):
    """
    Assert the validity of a system's slicing
    """
    for frag, ss in slicing.items():
        assert len(system[frag]) == (ss[1]-ss[0])


def atom_slicing(sl, fragments):
    """Slicing of the atoms of the provided fragment list."""
    fsl = []
    for frag in fragments:
        fsl += list(range(*sl[frag]))
    return fsl


def point_particle_objects(df):
    """
    Return the dictionary of the point particle quantities from a
    Systems' dataframe
    """
    if 'x_coord' in df:
        X = _dataframe_values(df[['x_coord', 'y_coord', 'z_coord']])
    else:
        X = _dataframe_values(df[['r_0', 'r_1', 'r_2']])
    # The folowing quantities are present only if a run has been performed
    if 'q1_0' in df:
        P = _dataframe_values(df[['q1_2', 'q1_0', 'q1_1']])
    else:
        P = None
    if 'qel_0' not in df and 'q0_0' in df:
        from BigDFT.Atoms import _nzion_default_psp as nzion
        from numpy import array, nan
        # The line below is potentially not needed
        df['zion'] = array([nzion.get(s, nan) for s in df['sym']])
        # we assume net monopole definition
        nzion = df['nel'] if 'nel' in df else df.get('nzion', df.get('zion'))
        df['qel_0'] = df['q0_0'] - nzion
    Q = _dataframe_values(df[['qel_0']]) if 'qel_0' in df else None
    Z = _dataframe_values(df[['nel']] if 'nel' in df else
                          (df[['nzion']] if 'nzion' in df else df[['zion']]))
    return {'X': X, 'P': P, 'Q': Q, 'Z': Z}


def _get_coordinate_keys(df):
    """Keys associated to atom coordinate in system's dataframe.
    """
    if 'x_coord' in df:
        return ['x_coord', 'y_coord', 'z_coord']
    else:
        return ['r_0', 'r_1', 'r_2']


def _coordination_number_dict(syms, dist):
    from numpy import count_nonzero, argmin, array
    cn = {}
    ds = {}
    resyms = array(syms)
    for sym, arr in zip(syms, dist):
        rearr = arr[arr > 0]
        imin = argmin(rearr)
        resym = resyms[arr > 0]
        minsym = resym[imin]
        k = '-'.join(sorted([sym, minsym]))
        md = rearr.min()
        nc = count_nonzero(rearr < md + 0.1)
        cn.setdefault(sym, []).append(nc)
        # ds.setdefault(sym, []).append(md)
        ds.setdefault(k, []).append(md)
    return [cn, ds]


def _forces_dict(syms, fcs, view=None, fragment_forces=None):
    from numpy.linalg import norm
    fd = {}
    for sym, f in zip(syms, fcs):
        fd.setdefault(sym, []).append(norm(f))
    if view is not None:
        for sym, list_of_fragments in view.items():
            for frag in list_of_fragments:
                fd.setdefault(sym, []).append(norm(fragment_forces[frag]))
    return fd


def examine_system_dataframe(df, dist=None, view=None,
                             fragment_forces=None):
    from BigDFT.PointParticles import PointParticles as PP
    res = {}
    if dist is None:
        dist = PP(**point_particle_objects(df)).R
        mindist = dist[dist != 0].min()
        res['Minimum Distance'] = mindist
    cns = _coordination_number_dict(df['sym'], dist)
    if 'force_0' in df:
        fcs = _dataframe_values(df[['force_0', 'force_1', 'force_2']])
        if view is None:
            fd = _forces_dict(df['sym'], fcs)
        else:
            if fragment_forces is None:
                fragment_forces = df_fragment_forces(df)
            fd = _forces_dict(df['sym'], fcs, view, fragment_forces)
        cns.append(fd)
    res['coord_bonds_forces'] = cns
    return res


def df_fragment_forces(df):
    fragment_forces = {}
    for sym, frag, fx, fy, fz in df[['sym', 'frag',
                                     'force_0', 'force_1', 'force_2']].values:
        ff = fragment_forces.setdefault(frag, [0, 0, 0])
        ff[0] += fx
        ff[1] += fy
        ff[2] += fz
    return fragment_forces


def _plot_systems_violinplot(cns, axs, titles):
    from matplotlib import pyplot as plt
    from BigDFT.PostProcessing import dict_distplot
    nsubplots = len(cns)
    if axs is None:
        fig, axs = plt.subplots(1, nsubplots)
    else:
        fig = None
    for ax, cn, title in zip(axs, cns, titles):
        ax.set_title(title)
        dict_distplot(cn, ax, reuse_ticks=True, widths=1.0)
    if fig is not None:
        fig.tight_layout()
    return axs


def validate_dataframe_representation(sys, df):
    """
    Control if the units of the positions in the dataframe are in Bohr.
    Update the coordinate values if this is not so.

    Args:
        sys (BigDFT.System): System which provides the reference positions
        df (pandas.DataFrame): system's dataframe
    """
    import numpy as np
    from BigDFT.Atoms import AU_to_A
    from pandas import DataFrame
    assert all(df['units'] == 'bohr'), 'Dataframe units should be in Bohr'
    sl = sys.dataframe_slicing(df)
    keys = _get_coordinate_keys(df)
    all_coords = _dataframe_values(df[keys])
    for frag in sl:
        ist, ien = sl[frag]
        dfarr = all_coords[ist:ien]
        for at, coords in zip(sys[frag].atoms, dfarr):
            rxyz = np.array(at.get_position('bohr'))
            delta = rxyz - coords
            if np.linalg.norm(delta) > 1.e-3:  # this means angstroem
                dfarr /= AU_to_A
                delta = rxyz - coords
            assert np.linalg.norm(delta) <= 1.e-3, 'Atoms are not equivalent'
    df.update(DataFrame(all_coords, columns=keys))


def distance_matrix(sys, ref):
    """Calculate a distance descriptor between a system and a reference."""
    from BigDFT.PointParticles import PointParticles as PP
    from scipy.spatial import distance as d
    df = sys.to_dataframe(order=list(ref))
    pp = PP(**point_particle_objects(df))
    compactform = d.pdist(pp.X)
    return compactform


class FragmentView():
    """
    The representation of a system in terms of fragments and
    groups of superunits.

    Args:
        purities (dict): dictionary of the purities of the system
        bond_order (dict): double dictionary of the bond orders of
            the superunits
        charges (dict): dictionary of the number of the electrons of
            the superunits
    """
    def __init__(self, purities, bond_orders, charges):
        self.purities = purities
        self.bond_orders = bond_orders
        self.charges = charges

    def __deepcopy__(self, memo):
        """
        Here we manually override deepcopy for performance reasons.
        """
        new_bo = {}
        new_pv = {}
        new_charges = {}
        for f1 in self.bond_orders:
            new_bo[f1] = {}
            for f2 in self.bond_orders[f1]:
                new_bo[f1][f2] = self.bond_orders[f1][f2]
            new_pv[f1] = self.purities[f1]
            new_charges[f1] = self.charges[f1]

        copy = FragmentView(new_pv, new_bo, new_charges)
        memo[id(self)] = copy
        return copy

    def refragment(self, mapping):
        newp, newbo = update_purity_and_bo(mapping, self.purities,
                                           self.bond_orders, self.charges)
        newchg = {}
        for refrag, remap in mapping.items():
            newchg[refrag] = sum(self.charges[f] for f in remap)
        return FragmentView(newp, newbo, newchg)

    def remove_fragment(self, fragid):
        """
        Remove a particular fragment from this view.

        Args:
          fragid (str): the id of the fragment to remove.
        """
        self.purities.pop(fragid)
        self.charges.pop(fragid)
        self.bond_orders.pop(fragid)

        for f in self.bond_orders:
            self.bond_orders[f].pop(fragid)


def select_from_view(view, targets):
    """
    Identify the fragments of the view that contain
    at least one of the targets

    Args:
        view (dict): if present, identifies the fragments that contain the
            relevant units
        targets (list): list of the fragments to search in the view
    Returns:
        list: fragments to select
    """
    reselect = []
    for frag in targets:
        for key, val in view.items():
            if frag in val and key not in reselect:
                reselect.append(key)
                break
    return reselect


def flatten_from_view(target, view):
    """Include all the fragments of the view which define the target."""
    if view is None:
        flattened_target = target
    else:
        flattened_target = []
        for t in target:
            flattened_target += view[t]
    return flattened_target


def system_from_dict_positions(positions, units='angstroem', cell=None,
                               **useless_kwargs):
    """
    Build a system from a set of positions from a dictionary whose yaml
    serialisation is compliant with the BigDFT yaml position format

    Args:
       positions (list): list of the atomic specifications
       units (str): units of measure
       cell (list): description of the cell

    Returns:
       BigDFT.Systems.System: an instance of the system class.
          The employed fragment specification is specified in the file.
    """
    from BigDFT.Atoms import Atom
    from BigDFT.Fragments import Fragment
    from BigDFT.UnitCells import UnitCell
    sys = System()
    for iat, at in enumerate(positions):
        frag = GetFragId(at, iat)
        if frag not in sys:
            sys[frag] = Fragment()
        sys[frag].append(Atom(at, units=units))
    if cell is not None:
        sys.cell = UnitCell(cell=cell, units=units)
    return sys


def system_from_log(log, fragmentation=None):
    """
    This function returns a :class:`~BigDFT.Fragment.System` class out of a
    logfile. If the logfile contains information about fragmentation and atomic
    multipoles, then the system is created accordingly.
    Otherwise, the fragmentation scheme is determined by the fragmentation
    variable.

    Args:
       log (Logfile): the logfile of the QM run. In general the execution
           should be performed with Linear Scaling formalism, but
           also other executions are possible (dry_run for instance).
       fragmentation (str): the scheme to be used for the fragmentation in the
           case if not provided internally by the logfile.
           The possible values are ``atomic`` and ``full``, in which case the
           system as as many fragments as the number of atoms, or only one
           fragment, respectively.
    Returns:
        (BigDFT.Systems.System): The instance of the class containing
        fragments.
    """
    from BigDFT.Fragments import Fragment
    from BigDFT.UnitCells import UnitCell
    name = log.log.get('run_name', 'FULL') + ':0'

    full_system = System()
    posinp = log.log.get('posinp')
    useless_posinp = posinp is None or isinstance(posinp, str)
    if not useless_posinp:
        full_system[name] = Fragment(posinp=posinp)
        cell = UnitCell(cell=posinp.get('cell'),
                        units=posinp.get('units', 'angstroem'))
    else:
        full_system[name] = Fragment(astruct=log.astruct)
        cell = UnitCell(cell=log.astruct.get('cell'),
                        units=log.astruct.get('units', 'angstroem'))
    full_system.cell = cell
    full_system.set_logfile_info(log)

    # now we may defragment the system according to the provided scheme
    if fragmentation == 'full':
        return full_system
    elif fragmentation == 'atomic' or useless_posinp:
        atomic_system = System()
        atomic_system.cell = cell
        for iat, at in enumerate(full_system[name]):
            atomic_system['ATOM:' + str(iat)] = Fragment([at])
        return atomic_system
    else:
        frag_dict = {}
        for iat, tupl in enumerate(zip(posinp['positions'],
                                       full_system[name])):
            at, obj = tupl
            fragid = at.get('frag', 'ATM:' + str(iat+1))
            if isinstance(fragid, list):
                fragid = ':'.join(map(str, fragid))
            if fragid not in frag_dict:
                frag_dict[fragid] = [obj]
            else:
                frag_dict[fragid].append(obj)
        frag_system = System()
        frag_system.cell = cell
        for fragid in frag_dict:
            frag_system[fragid] = Fragment(frag_dict[fragid])
        return frag_system


def system_from_df(df):
    """System instance from system dataframe.

    Returns a System from a dataframe. Useful to reconstruct a
    dataframe-serialized system in case one needs to extract quantities of
    relevance.

    Args:
        df (pandas.DataFrame): the System Dataframe as returned usually from
            `py:func:System.df` property.

    Returns:
        System: the instance derived from the dataframe.
    """
    from BigDFT.Systems import System
    from BigDFT.Fragments import Fragment
    from BigDFT.Atoms import Atom
    dft = df.transpose()
    sys = System()
    sys._df = df
    for at in dft:
        atdict = dft[at].to_dict()
        frag = atdict.pop('frag')
        sys.setdefault(frag, Fragment()).append(Atom(atdict))
    return sys


def plot_fragment_information(axs, datadict, colordict=None):
    """
    Often times we want to plot measures related to the different fragments
    in a system. For this routine, you can pass a dictionary mapping
    fragment ids to some kind of value. This routine takes care of the
    formatting of the axis to easily read the different fragment names.

    Args:
      axs (matplotlib.Axes): an axes object to plot on.
      datadict (dict): a dictionary from fragment ids to some kind of data
        value.
      colordict (dict): optionally, a dictionary from fragment ids to a
        color value.
    """
    # Sort by fragment id
    slabels = sorted(datadict.keys(),
                     key=lambda x: int(GetFragTuple(x)[1]))
    svalues = [datadict[x] for x in slabels]

    # Label the axis by fragments
    axs.set_xlabel("Fragment", fontsize=12)
    axs.set_xticks(range(len(datadict.keys())))
    axs.set_xticklabels(slabels, rotation=90)

    # Plot the actual values
    axs.plot(svalues, 'x', markersize=12, color='k')

    # Plot the colored values.
    if colordict:
        for i, key in enumerate(slabels):
            if key not in colordict:
                continue
            axs.plot(i, svalues[i], 'x', markersize=12, color=colordict[key])


def GetFragId(atdict, iat):
    """
    Obtain the fragment identifications from the atom description

    Args:
      atdict(dict): dictionary of the atom
      iat (int): position of the atom in the list

    Returns:
      str: fragment_id
    """
    fragid = atdict.get('frag', 'ATOM:' + str(iat))

    if all(':' in elem for elem in fragid):
        fragid = '+'.join(map(str, fragid))
    elif len(fragid) == 2 and ':' in str(fragid[1]):
        fragid = '-'.join(map(str, fragid))
    elif isinstance(fragid, list):
        fragid = ':'.join(map(str, fragid))
    return fragid


def GetFragTuple(fragid):
    """
    Fragment ids should have the form: "NAME:NUMBER" or "NAME-NUMBER". This
    splits the fragment into the name and number value.

    Args:
      fragid (str): the fragment id string.

    Return:
      (tuple): fragment name, fragment number
    """
    markers = [":", "-", "+"]
    if all(x not in fragid for x in markers):
        raise ValueError("Invalid format for fragment ID")
    if '+' in fragid:
        return tuple(fragid.split("+"))
    # elif '-' in fragid:
    #     return tuple(fragid.split("-"))
    elif isinstance(fragid, str):
        return tuple(fragid.split(":"))
    else:
        return tuple(fragid)


def copy_bonding_information(sys1, sys2):
    """
    This routine will take the bonding information of sys1 and copy it
    over to sys2. This routine requires that both systems have the exact
    same atoms in them. This is useful if you refragment a system and
    want to fix the bonding information.

    Args:
      sys1 (BigDFT.Systems.System): the system to copy bonding information
        from.
      sys2 (BigDFT.Systems.System): the system to copy information to.
    """
    # Check parameters
    if sys1.conmat is None:
        raise ValueError("The connectivity matrix of the first argument " +
                         "must be set")

    # Create at atom level connectivity matrix
    lookup = {}
    j = 0
    for fragid, frag in sys1.items():
        for i, at in enumerate(frag):
            lookup[(fragid, i)] = j
            j += 1

    atom_connectivity = {}
    for fid1, conn in sys1.conmat.items():
        for ati, links in enumerate(conn):
            i = lookup[(fid1, ati)]
            for (fid2, atj), v in links.items():
                j = lookup[(fid2, atj)]
                atom_connectivity[(i, j)] = v

    # Generate the matching
    atlist = []
    for fragid, frag in sys1.items():
        for at in frag:
            atlist.append(at)
    matching = sys2.compute_matching(atlist)
    rlookup = {}
    for fragid, frag in matching.items():
        for i, v in enumerate(frag):
            rlookup[matching[fragid][i]] = (fragid, i)

    # Copy over
    sys2.conmat = {}
    for fragid, frag in sys2.items():
        sys2.conmat[fragid] = []
        for i, at in enumerate(frag):
            sys2.conmat[fragid].append({})

    for (i, j), v in atom_connectivity.items():
        fragid1, at1 = rlookup[i]
        fragid2, at2 = rlookup[j]
        sys2.conmat[fragid1][at1][(fragid2, at2)] = v


def update_purity_and_bo(mapping, purity, bo, charges):
    """
    When merging fragments together, you will need to update the bond
    orders and purity values. This can be done by using
    `run_compute_purity` and `compute_bond_orders`, but this process is
    potentially slow. In this function, we use the old bond orders and
    purity values for update, which is much faster.

    Arguments:
        mapping (dict): a dictionary where the keys are the new fragments
          and the values are a list of old fragments that make up this
          new fragment.
        purity (dict): the old purity values of each fragment.
        bo (dict): the old bond orders of each fragment.
        charges (dict): the charges of each fragment (the sum of the
          number of electrons).

    Returns:
        (dict, dict): the new purity and bond order values.
    """
    # Purity loop
    new_purity = {}
    for f in mapping:
        new_purity[f] = 0
        old = mapping[f]

        # Sum the bond orders
        for o1 in old:
            for o2 in old:
                if o1 != o2:
                    new_purity[f] += bo[o1][o2]

        # Sum the un-normalized atomic purity values
        for o1 in old:
            new_purity[f] += purity[o1] * charges[o1] / 2.0

        # Normalize
        new_charge = sum([charges[x] for x in old])
        new_purity[f] *= 2.0 / new_charge

    # Bond order loop
    new_bo = {}
    for f1 in mapping:
        old1 = mapping[f1]
        new_bo[f1] = {}
        for f2 in mapping:
            old2 = mapping[f2]
            new_bo[f1][f2] = 0

            for o1 in old1:
                for o2 in old2:
                    new_bo[f1][f2] += bo[o1][o2]

    return new_purity, new_bo


def _dataframe_values(df):
    """Wrapper to avoid API problem in case to_numpy() method is missing."""
    try:
        values = df.to_numpy()
    except Exception:
        values = df.values
    return values


def _example():
    """Example of using a system"""
    from BigDFT.IO import XYZReader
    from BigDFT.Fragments import Fragment

    safe_print("Read in some files for the fragments..")
    reader = XYZReader("SiO")
    frag1 = Fragment(xyzfile=reader)
    reader = XYZReader("Si4")
    frag2 = Fragment(xyzfile=reader)

    safe_print("Now we move on to testing the system class.")
    sys = System(frag1=frag1, frag2=frag2)
    for at in sys["frag1"]:
        safe_print(dict(at))
    for at in sys["frag2"]:
        safe_print(dict(at))
    safe_print()

    safe_print("What if we want to combine two fragments together?")
    sys["frag1"] += sys.pop("frag2")
    for at in sys["frag1"]:
        safe_print(dict(at))
    safe_print("frag2" in sys)
    safe_print()

    safe_print("What if I want to split a fragment by atom indices?")
    temp_frag = sys.pop("frag1")
    sys["frag1"], sys["frag2"] = temp_frag[0:3], temp_frag[3:]
    for at in sys["frag1"]:
        safe_print(dict(at))
    for at in sys["frag2"]:
        safe_print(dict(at))
    safe_print()


if __name__ == "__main__":
    _example()
