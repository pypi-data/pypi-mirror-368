"""
This module contains some wrappers for using OpenMM to perform
various operations on BigDFT molecules.

http://docs.openmm.org/development/api-python/index.html
"""

from BigDFT.Systems import System


def get_available_ff_names():
    import os
    import sys
    names = []
    for path in sys.path:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".xml"):
                    filename = os.path.join(root, file)
                    if 'data' in filename and 'openmm' in filename:
                        iname = filename.index('data')+5
                        names.append(filename[iname:])
    return names


class OMMSystem(System):
    """
    Class of OpenMM binder system which enables functionalities
    of openMM on a BigDFT system

    Args:
        system (System): a instance of a system class
        filename (str): name of the PDB file to instantiate the system
    """
    def __init__(self, system=None, filename=None):
        from openmm.app.pdbfile import PDBFile
        from openmm import app
        from BigDFT.IO import read_pdb, write_pdb
        from tempfile import NamedTemporaryFile as tmp
        if filename is not None:
            pdb = PDBFile(open(filename))
            sys = read_pdb(open(filename))
        elif system is not None:
            sys = system
            ofile = tmp('w+')
            write_pdb(system=system, ofile=ofile)
            ofilename = ofile.name
            pdb = PDBFile(open(ofilename))
            ofile.close()
        System.__init__(self, **sys.dict())
        self.pdb = pdb
        self.modeller = app.Modeller(pdb.topology, pdb.positions)

    def set_forcefields(self, *ff_list):
        """
        Define a set of force fields that will be used in the geometry ops.

        Args:
            *ff_list: list of the force fields to be included,
                in priority order.
                Use the :func:py:`get_available_ff_names` to identify the
                available force fields
        """
        from openmm import app
        self.forcefield = app.ForceField(*ff_list)

    @property
    def OMMsystem(self):
        from openmm import app
        if not hasattr(self, '_system'):
            self._system = self.forcefield.createSystem(
                self.modeller.topology, nonbondedMethod=app.NoCutoff,
                constraints=None)
        return self._system

    def set_integrator(self, T=298.15):
        from openmm import unit as u
        import openmm.openmm as mm
        temperature = T * u.kelvin
        self.integrator = mm.LangevinIntegrator(
            temperature, 1 / u.picosecond,  0.0005 * u.picoseconds)

    @property
    def OMMsimulation(self):
        from openmm import app
        if not hasattr(self, '_simulation'):
            self._simulation = app.Simulation(self.modeller.topology,
                                              self.OMMsystem, self.integrator)
            self._simulation.context.setPositions(self.modeller.positions)
        return self._simulation

    def OMMenergy(self, units='kcal/mol'):
        from openmm.openmm import KcalPerKJ
        energy = self.OMMsimulation.context.getState(
             getEnergy=True).getPotentialEnergy()
        return energy._value * KcalPerKJ

    @property
    def OMMposition(self):
        return self.OMMsimulation.context.getState(
            getPositions=True).getPositions()

    def write(self, ofile):
        from openmm import app
        app.PDBFile.writeFile(self.OMMsimulation.topology, self.OMMposition,
                              open(ofile, 'w'))

    def optimize(self, iters):
        return self.OMMsimulation.minimizeEnergy(maxIterations=iters)

    @property
    def forcegroups(self):
        forcegroups = {}
        for i in range(self.OMMsystem.getNumForces()):
            force = self.OMMsystem.getForce(i)
            force.setForceGroup(i)
            forcegroups[force] = i
        return forcegroups

    def get_energies(self):
        from openmm.openmm import KcalPerKJ

        def component_name(k):
            return str(k).split('.')[-1].split(';')[0].lstrip('"')

        energies = {}
        for f, i in self.forcegroups.items():
            en = self.OMMsimulation.context.getState(
                getEnergy=True, groups=2**i).getPotentialEnergy()
            name = component_name(f)
            energies[name] = en._value * KcalPerKJ
        return energies

    def freeze_nonhydrogen_atoms(self):
        """Lock the position of the elements which are not hydrogen."""
        from openmm.app.element import hydrogen
        os = self.OMMsystem
        for at in self.modeller.topology.atoms():
            if at.element is not hydrogen:
                os.setParticleMass(at.index, 0.0)


def ligand_molecule(lig):
    from BigDFT import IO
    from os import system
    from openff.toolkit.topology import Molecule
    IO.write_pdb(ofile=open('lig.pdb', 'w'), system=lig)
    system('obabel -ipdb lig.pdb -osdf > lig.sdf')
    return Molecule.from_file('lig.sdf', file_format='SDF',
                              allow_undefined_stereo=True)


def ligand_inclusive_forcefield(**kwargs):
    from simtk import unit
    from openmm import app
    from openmmforcefields.generators import SystemGenerator
    from futile.Utils import kw_pop
    forcefield_kwargs = {'constraints': app.HBonds,
                         'rigidWater': True,
                         'removeCMMotion': False,
                         'hydrogenMass': 4*unit.amu}
    new_kw, ff_kw = kw_pop('forcefield_kwargs', {}, **kwargs)
    forcefield_kwargs.update(ff_kw)
    # Initialize a SystemGenerator using GAFF
    return SystemGenerator(forcefield_kwargs=forcefield_kwargs,
                           cache='db.json', **new_kw)


def omm_system(sys, ligand=None, *ff_list, **kwargs):
    """ Instantiate a omm system from a system and a force field.

    Args:
        *ff_list: list of the force fields to be included,
            in priority order.
            Use the :func:py:`get_available_ff_names` to identify the
            available force fields.
    Returns:
        OMMSystem: Instance ready to be optimized.
    """
    symm = OMMSystem(sys)
    if ligand is not None:
        if isinstance(ligand, list):
            lig = []
            for liga in ligand:
                ligt = ligand_molecule(liga)
                symm.modeller.add(ligt.to_topology().to_openmm(),
                                  ligt.conformers[0].to_openmm())
                lig.append(ligt)
        else:
            lig = ligand_molecule(ligand)
            symm.modeller.add(lig.to_topology().to_openmm(),
                              lig.conformers[0].to_openmm())
        system_generator = ligand_inclusive_forcefield(**kwargs)
        symm._system = system_generator.create_system(symm.modeller.topology,
                                                      molecules=lig)
    else:
        symm.set_forcefields(*ff_list)
    symm.set_integrator()
    return symm


def optimize_system(sys, outfile, *forcefields):
    """Take a BigDFT system and optimize it according to a set of OMM FFs.

    Args:
        sys (BigDFT.System): the system to optimize.
        outfile (str): The file to write the optimized system to.
        *forcefields: sequence of forcefields to be employed in the
             optimization.

    Returns:
        The objects returned by the `py:meth:minimizeEnergy` method of OpenMM.
    """
    symm = omm_system(sys, None, *forcefields)
    obj = symm.optimize(0)
    symm.write(outfile)
    return obj


def three_point_energies(sys, subs1, subs2, *forcefields):
    """Calculate three_point_energies of two portion of a system.
    Args:
        sys (BigDFT.System): the system to optimize.
        subs1 (list): list of fragments composing subsystem 1
        subs2 (list): list of fragments composing subsystem 2
        *forcefields: sequence of forcefields to be employed in the
             optimization.

    Returns:
        collections.namedtuple: tuple of the three energies, eT, e1, e2.
    """
    from collections import namedtuple
    sys1 = omm_system(sys.subsystem(subs1), None, *forcefields)
    e1 = sys1.OMMenergy()
    sys2 = omm_system(sys.subsystem(subs2), None, *forcefields)
    e2 = sys2.OMMenergy()
    sysT = omm_system(sys, None, *forcefields)
    eT = sysT.OMMenergy()
    ThreePoint = namedtuple('ThreePoint', 'eT e1 e2')
    return ThreePoint(eT, e1, e2)


def get_mutation_name(mut, offset=0):
    """From a usual mutation notation AXXXB get the PDBfixer-compliant tuple.

    Args:
        mut (str): Mutation written in the AxxxB format.
        offset (int): offest to be applied to the ``xxx`` format.

    Returns:
        str: the mutation name.
    """
    from Bio.PDB.Polypeptide import one_to_three
    wt = mut[0]
    mt = mut[-1]
    num = int(mut[1:-1]) - offset
    return '-'.join([one_to_three(wt), str(num), one_to_three(mt)])


def _remove_extremal_missing_residues(fixer):
    chains = list(fixer.topology.chains())
    keys = list(fixer.missingResidues.keys())
    for key in keys:
        chain = chains[key[0]]
        if key[1] == 0 or key[1] == len(list(chain.residues())):
            del fixer.missingResidues[key]


def fixed_system(pH=None, mutations=[], system=None, filename=None, pdbid=None,
                 select_chains=None, remove_extremal_missing_residues=True,
                 custom_fixing_function=None, add_missing_residues=True,
                 keepIds=False, convert_from_charmm_format=False, variants={},
                 **kwargs):
    """
    Create a system with the pdbfixer tool.

    Args:
        pH (float): the pH of the environment. Add missing hydrogens according
            to this pH if provided.
        mutations (list): the mutation to be applied to the original structure.
            should be a list of two-element lists, the first being the list
            of mutations to be applied to the chain_id, provided by the second.
        system (BigDFT.System): the system to be fixed.
        filename (str): the PDB file from which the system has to be read.
           If system is provided, this arguments indicate the PDB file in which
           the system is written, *prior* to fixing. After fixing, such file
           may have to be overwritten.
        pdbid (str): the id of the PDB database.
        select_chains (list): if provided indicate the chains to be selected.
            Useful when pdbid is provided. All the chains will be included
            if omitted.
        remove_extremal_missing_residues (bool): if True only the internal
            missing residues are restored.
        custom_fixing_function (func): a function that has a `BigDFT.System`
            as an argument and returns the object to be provided.
        add_missing_residues (bool): include missing residues if true.
        keepIds (bool): If True, keep the residue and chain IDs specified
            in the Topology rather than generating new ones.
        convert_from_charmm_format (bool): Accept the PDB format which is
            usually provided as the output of charmm-gui.
            The chain id is provided as the last letter of each line.
        variants (dict): dictionary of ``chain_id,res_id: name`` of the
            variants which have to be imposed for the protonation state.
            Allowed names are ASH, ASP, CYS, CYX, GLH, GLU, HID, HIE, HIP,
            HIN, LYN, LYS, with obvious meaning of the names
            (see OpenMM documentation).

    Warning:
        (From OpenMM documentation)
        When keepIds=True, it is up to the caller to make sure these are
        valid IDs that satisfy the requirements of the PDB format.
        Otherwise, the output file will be invalid.

    Returns:
        BigDFT.BioQM.BioSystem: Fixed system, or returned object of
            `custom_fixing_function` if present.
    """
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile
    from BigDFT import IO, BioQM
    from os.path import isfile
    from os import remove
    from futile.Utils import unique_filename

    if system is not None and not isfile(filename):
        with open(filename, 'w') as ofile:
            IO.write_pdb(ofile=ofile, system=system)
    if filename is not None:
        if convert_from_charmm_format:
            fileout = unique_filename(prefix='charmm_conversion_') + '.pdb'
            _include_charmm_chains(filename, fileout)
            fixer = PDBFixer(filename=fileout)
            remove(fileout)
        else:
            fixer = PDBFixer(filename=filename)
    else:
        fixer = PDBFixer(pdbid=pdbid)
    if len(mutations) > 0:
        for muts in mutations:
            fixer.applyMutations(*muts)
    if filename is None and select_chains is not None:
        numChains = len(list(fixer.topology.chains()))
        fixer.removeChains([ch for ch in range(numChains)
                            if ch not in select_chains])
    fixer.findMissingResidues()
    if remove_extremal_missing_residues:
        _remove_extremal_missing_residues(fixer)
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms()
    if add_missing_residues:
        fixer.addMissingAtoms()
    if pH is not None:
        if len(variants) == 0:
            fixer.addMissingHydrogens(pH)
        else:
            protonation_states(fixer, pH, variants, **kwargs)
    tmpfile = unique_filename(prefix='fixer_output_') + '.pdb'
    ofile = open(tmpfile, 'w')
    PDBFile.writeFile(fixer.topology, fixer.positions, ofile,
                      keepIds=keepIds)
    ofile.close()
    ofile = open(tmpfile, 'r')
    sys = IO.read_pdb(ofile, include_chain=True, ignore_connectivity=True,
                      ignore_unit_cell=True)
    ofile.close()
    remove(tmpfile)

    if custom_fixing_function is not None:
        resys = custom_fixing_function(sys)
    else:
        resys = sys.rename_fragments(BioQM.fragment_name_conversion(sys))
        resys = BioQM.BioSystem.from_sys(resys)

    return resys


def _include_charmm_chains(filein, fileout):
    """Set the chains as they are specified in charmm."""
    ifile = open(filein, 'r')
    ofile = open(fileout, 'w')
    for iline in ifile.readlines():
        oline = iline
        if 'PRO' == iline[72:75]:
            oline = iline[:21] + iline[75] + iline[22:]
        ofile.write(oline)
    ofile.close()
    ifile.close()


def protonation_states(fixer, pH, variants, **kwargs):
    import openmm.app as app
    modeller = app.Modeller(fixer.topology, fixer.positions)
    if len(variants) == 0:
        new_variants = modeller.addHydrogens(pH=pH, **kwargs)
    else:
        # create variants array
        tmpvar = []
        for ich, ch in enumerate(fixer.topology.chains()):
            for ires, res in enumerate(ch.residues()):
                key = (ich, ires)
                tmpvar.append(variants.get(key))
        new_variants = modeller.addHydrogens(pH=pH, variants=tmpvar, **kwargs)
        assert len(new_variants) == len(tmpvar),\
            'Error in determining protonation'
    fixer.topology = modeller.topology
    fixer.positions = modeller.positions
    return new_variants
