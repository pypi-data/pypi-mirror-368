"""
This module enables to compute the electronic properties of a solid state
system using the matrices produced by a linear scaling calculation in BigDFT
"""

###
# add periodicity to matching_index
# add crystal symmetry to map_sys
###

AU_eV = 27.21138386


class TightBinding():
    """
    Defines the tight-binding object associated to
        -a system (Systems.System)
        -an interaction radius (int)
    """
    from BigDFT.Systems import System

    def __init__(self, sys=System(), d=5):
        self.sys = sys
        self.BZ = self._BZ()
        self.sh = self._sites_in_shell(d)
        self.map = {}

    def _BZ(self):
        """
        Given a system, finds its Brillouin zone (BZ)
        """
        from numpy import array, cross, dot, where, roll, ones, \
            round, diag, inf, pi

        a = array(self.sys.cell.cell)
        a[where(a == inf)] = 1e12
        if a.ndim == 1:
            a = diag(a)
        V = dot(a[0], cross(a[1], a[2]))
        b = ones((3, 3))*2*pi/V

        idx = range(0, 3)
        for i in idx:
            i1, i2, i3 = roll(idx, -i)
            b[i1] *= cross(a[i2], a[i3])

        return {'cell': round(b, 12)}

    def _sites_in_shell(self, d):
        """
        Given a system, finds the pairs between atoms and their periodic images
        up to a specified distance, along with their Bravais vectors

        Args:
            sys (Systems.System): the periodic system
            d (float): the threshold distance, where d=0
            yields the on-site mapping

        Returns:
            sh (dict): a mapping between atom sites and their cell
            indices and Bravais vectors
        """
        from numpy import linalg, array, where, concatenate, ceil
        from scipy.spatial import distance_matrix
        # systems properties
        cell = self.sys.cell.cell
        pos = array([at.get_position(units='angstroem')
                     for at in self.sys.get_atoms()])
        Na = len(pos)
        # on-site mapping
        if d == 0:
            return {(i, i, (0, 0, 0)): {'R': [0, 0, 0]} for i in range(Na)}
        # periodic images
        nx, ny, nz = ceil(d/linalg.norm(cell, axis=1)).astype(int)
        R_n, id_n = self.sys.cell.tiling_vectors([nx, ny, nz])
        pos_n = array([]).reshape(-1, 3)
        for R_i in R_n:
            pos_n = concatenate((pos_n, pos+R_i))
        # box with relevant periodic images
        x0, x1 = min(pos[:, 0])-d, max(pos[:, 0])+d
        y0, y1 = min(pos[:, 1])-d, max(pos[:, 1])+d
        z0, z1 = min(pos[:, 2])-d, max(pos[:, 2])+d
        idx, = where((pos_n[:, 0] >= x0) & (pos_n[:, 0] <= x1) &
                     (pos_n[:, 1] >= y0) & (pos_n[:, 1] <= y1) &
                     (pos_n[:, 2] >= z0) & (pos_n[:, 2] <= z1))
        pos_b = pos_n[idx]
        # create shell dictionnary
        dist = distance_matrix(pos, pos_b)
        id_d = where(dist < d)
        Na = len(pos)
        sh = {}
        for i, jb in zip(*id_d):
            je = idx[jb]
            idk = id_n[je//Na]
            j = je % Na
            r_ij = pos_b[jb]-pos[i]
            sh.update({(i, j, idk): {'R': list(r_ij)}})

        return sh

    def map_sys(self, sys_e, r0_e=None, tol=.1):  # add crystal symmetry
        """
        Given two systems, finds the atom indices where the
        tb system maps the extended one.

        Args:
            sys_e (Systems.System): the extended system
            r0_e (3d-array): the origin of self.sys in sys_e
            tol (float): tolerance for matching systems

        Returns:
            (dict): a mapping between the atom indices that
            minimize the associated error
        """
        from numpy import array, mean, argmin
        from scipy.spatial import distance_matrix

        pos_e = array([at.get_position(units='angstroem')
                       for at in sys_e.get_atoms()])
        pos_s = array([at.get_position(units='angstroem')
                       for at in self.sys.get_atoms()])
        if r0_e is None:
            r0_e = mean(pos_e, axis=0)
        dist = distance_matrix(pos_e, r0_e.reshape(1, 3))
        ir0_e = argmin(dist)

        dd = {}
        for i, ri in enumerate(pos_s):  # add stop at mse<threshold
            pos_i = pos_s - ri + pos_e[ir0_e]
            dist = distance_matrix(pos_e, pos_i)
            ii = argmin(dist, axis=0)
            di = sum(sum([(i-j)**2 for i, j in zip(pos_e[ii], pos_i)]))
            dd[i] = {'idx': list(ii), 'mse': di}

        ddi = {k: v['mse'] for k, v in dd.items()}  # indexed mse array
        idmin = min(ddi, key=ddi.get)
        if dd[idmin]['mse'] > tol:
            print('Warning: matching less than tolerance')

        [self.map.update(i) for i in [dd[idmin], {'sys': sys_e}]]
        return dd

    def shell_index(self, metadata):
        """
        Given a mapping between atom sites and their periodic images,
        get their matrix indices from a linear-scaling calculation.

        Args:
            metadata (Spillage.MatrixMetadata): the information on the matrices
        """
        from numpy import array, argmin, cumsum
        from scipy.spatial import distance_matrix

        idx = self.map['idx']
        id_mat = [metadata.atoms[i].get('indices') for i in idx]
        id_sym = [metadata.atoms[i].get('sym') for i in idx]
        id_orb = list(cumsum([0]+[len(i) for i in id_mat]))

        sys = self.map['sys']
        pos = array([at.get_position(units='angstroem')
                     for at in sys.get_atoms()])

        for (i, j, idk), sh_ij in self.sh.items():  # i<j and apply symmetry
            r_j = array([pos[idx[i]] + sh_ij['R']])
            d_ij = distance_matrix(pos, r_j)
            idx_j = argmin(d_ij)  # lattice aperiodicity !!
            idH_i = metadata.atoms[idx[i]].get('indices')
            idH_j = metadata.atoms[idx_j].get('indices')
            self.sh[(i, j, idk)].update({'orbI': idH_i, 'orbJ': idH_j})

        self.map.update({'sym': id_sym, 'orbs': id_orb})
        return None

    def shell_matrix(self, mat):
        """
        Given a mapping between atom sites and their periodic images,
        get their matrices from a linear-scaling calculation.

        Args:
            mat (list): the sparse matrices, H and S (scipy.sparse.csc_matrix)

        Returns:
            (dict): a mapping between atom sites and their matrices
        """
        from numpy import meshgrid

        h, s = [i.todense() for i in mat]

        m_sh = {}
        for (i, j, idk), sh_ij in self.sh.items():  # i<j and apply symmetry
            idH_i = sh_ij['orbI']
            idH_j = sh_ij['orbJ']
            X, Y = meshgrid(idH_i, idH_j)
            h_ij, s_ij = h[X, Y], s[X, Y]
            m_sh.update({(i, j, idk): {'h': h_ij, 's': s_ij}})

        return m_sh

    def compute_onsite_channels(self, v_sh, cp=.99, sp=.99):  # sorting on No
        """
        Given on-site eigenvectors, computes the distribution
        in terms of support functions (noted here as channels)

        Args:
            v_sh (numpy.array): on-site eigenvectors
            cp (float): channel purity, the threshold to
            consider a channel as pure
            sp (float): sites purity, the threshold to
            consider a set of channels as valid

        Returns:
            (dict): maps for each eigenvec the smallest set
            of channels that meet the purity condition
        """
        from numpy import flip, sort, argsort, zeros, \
            sum, unique, logical_xor

        a = v_sh**2                              # eigenvecs coefficients
        Ns, No, Nv = a.shape                     # sites, orbitals, eigenvecs
        a_n = sum(a, axis=1)
        a_s = flip(sort(a, axis=1), axis=1)      # sorted coefficients
        ids = flip(argsort(a, axis=1), axis=1)   # index of sorted coefficients

        v_ch = {}
        for j in range(Nv):                      # number of on-site eigenvecs
            hb = zeros((No, Ns))                 # bit-wise history
            for i in range(No):                  # number of channels
                cp_ji = sum(a_s[:, :i+1, j], axis=1)  # sites-resolved purity
                si_ji = (cp_ji/a_n[:, j]) > cp        # sites index
                sp_ji = sum(si_ji)/Ns                 # sites purity
                hb[i] = logical_xor(si_ji, sum(hb[:i+1], axis=0))
                if sp_ji > sp:
                    cnt = {i+1: [list(k) for k in
                                 unique(ids[:, :i+1, j][hi == 1],
                                        return_counts=True)]
                           for i, hi in enumerate(hb) if not all(hi == 0)}
                    v_ch[j] = cnt
                    break
        return v_ch

    def k_grid(self, n=[0, 0, 0]):  # add Monkhorst-Pack definition
        """

        """
        # k = self.BZ['kpts']
        return None

    def k_path(self, hsp, n=101):  # add similar sampling between hsp
        """
        Given a set of high-symmetry points, finds the k-path

        Args:
            hsp (dict): the high-symmetry points labels and
            coordinates

        Returns:
            (numpy.array): the path in k-space
        """
        from numpy import dot, zeros, linspace, concatenate

        b = self.BZ['cell']
        path = [dot(i, b) for i in hsp.values()]
        # lk = np.linalg.norm(path[1:]-path[:-1], axis=1)
        # np.rint(101*lk/np.sum(lk))
        k_p = zeros((0, 3))
        for hs0, hs1 in zip(path[:-1], path[1:]):
            k_p = concatenate((k_p, linspace(hs0, hs1, n)))

        return k_p

    def k_matrix(self, k, m_sh):
        """
        Given a mapping between atom sites and their perdiodic images,
        Bravais vectors and matrix elements, this function computes
        the k-resolved matrices

        Args:
            k (array): the k-points sampling
            m_sh (list): a mapping between the atom sites and matrices
            idmat (list): orbitals number per atom

        Returns:
            The k-resolved matrices and energy spectrum
        """
        from numpy import array, zeros, meshgrid, dot, outer, exp, complex64

        id_orb = self.map['orbs']
        Nk, No = len(k), id_orb[-1]
        Hk = zeros((Nk, No, No), dtype=complex64)
        Sk = zeros((Nk, No, No), dtype=complex64)

        for (i, j, idk), sh_ij in self.sh.items():
            i0, i1 = id_orb[i], id_orb[i+1]
            j0, j1 = id_orb[j], id_orb[j+1]
            idm_i = [i0+ii for ii in range(i1-i0)]
            idm_j = [j0+jj for jj in range(j1-j0)]
            X, Y = meshgrid(idm_i, idm_j)  # indexing
            li, lj = len(idm_i), len(idm_j)
            h_ij = m_sh[(i, j, idk)]['h']
            s_ij = m_sh[(i, j, idk)]['s']
            R_ij = sh_ij['R']
            a = exp(-1j*dot(k, array(R_ij)))
            Hk[:, X, Y] += outer(a, h_ij).reshape(Nk, lj, li)
            Sk[:, X, Y] += outer(a, s_ij).reshape(Nk, lj, li)

        return Hk, Sk

    def eigen(self, k, Hk, Sk, eigvals_only=True):  # opt. small k, large m_sh
        """
        Given the k_path, Hamiltonian and Overlap matrices, finds
        the eigenvals and eigenvecs (if specified).

        Agrs:
            k (numpy.array): the k_path
            Hk (numpy.array): the Hamiltonian matrix
            Sk (numpy.array): the Overlap matrix

        Returns:
            (numpy.array): the eigvals and eigvecs
        """
        from numpy import zeros, real
        from scipy.linalg import eigh

        Ek = zeros(Hk.shape[:2])
        vk = zeros(Hk.shape)
        for ik in range(len(k)):
            try:
                w, v = eigh(Hk[ik], b=Sk[ik])
            except ValueError:
                print("Error at ik=", ik)
            Ek[ik, :] = w
            vk[ik, :] = real(v)

        if eigvals_only:
            return Ek
        else:
            return Ek, vk

    def spectral_weights(self, vk, mapping):  # mode='sf'
        """
        Given eigenvecs, computes their spectral weights
        in terms of their support functions (SFs), depending on
        a mapping that defines the different group of SFs

        Args:
            vk (numpy.array): the eigenvecs
            mapping (dict): written as {at: [...]}, where the list
            contains sub-list of SFs indices grouped together

        Returns:
            (numpy.array): the spectral weights
        """
        from numpy import zeros, array, sum, tile, concatenate, cumsum, linalg

        Nmi = [len(v) for v in mapping.values()]
        iNm = concatenate(([0], cumsum(Nmi)))
        cnk = zeros((iNm[-1],)+vk.shape[:2])
        vn2 = tile(linalg.norm(vk, axis=1)**2, (iNm[-1], 1, 1))

        vk2 = vk**2
        for ik, (k, v) in enumerate(mapping.items()):
            id_k = array([list(range(self.map['orbs'][i],
                                     self.map['orbs'][i+1]))
                          for i, ai in enumerate(self.map['sym']) if ai == k])
            i0, i1 = iNm[ik], iNm[ik+1]  # indices of SFs
            cnk[i0:i1] = array([sum(vk2[:, id_k[:, vi].flatten(), :], 1)
                                for vi in v])/vn2[i0:i1]

        return cnk

    def spectral_map(self, cnk, Ek, dE=2e-3, sig=0.3):
        """
        Given spectral weights, computes a 2d map using
        Gaussiam smearing.

        Args:
            cnk (numpy.array): the spectral weights
            Ek (numpy.array): the eigenvals
            dE, sig (floats): the Gaussian smearing parameters

        Returns:
            Eg (numpy.array): energy interpolation
            wg (numpy.array): 2d map of spectral weights
        """
        from numpy import ogrid, min, max, zeros, exp

        Eg = ogrid[min(Ek)-1:max(Ek)+1:dE]  # units='AU'
        Nc, Nk, No = cnk.shape
        wg = zeros((Nc, Nk, len(Eg)))
        for j, cnk_j in enumerate(cnk):
            for io in range(No):
                for ik in range(Nk):
                    E_io = ((Eg-Ek[ik, io])*AU_eV)**2
                    wg[j, ik, :] += cnk_j[ik, io]*exp(-E_io/(2*sig**2))

        return Eg, wg


def k_norm(k_path):
    """
    Given a k_path, computes its normalized vector
    """
    from numpy import linalg, concatenate, cumsum

    dk = linalg.norm(k_path[1:]-k_path[:-1], axis=1)
    k_n = concatenate(([0], cumsum(dk)))

    return k_n


def plot_bs(k_p, Ek, ax=None, prms={}):
    """
    Given a k-path and its eigenvals, plot the band structure
    """
    from matplotlib import pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(3.2, 4.8))
    k_n = k_norm(k_p)
    ax.plot(k_n, Ek*AU_eV, ms=.7, **prms)
    ax.set_xlim([0, k_n[-1]])
    ax.set_xticks([])
    # ax.set_yticklabels(size=8)
    ax.set_ylabel('Energy (eV)', size=10)

    return ax


def plot_spectral_map(k_p, Eg, wg, ax=None,
                      cmap=['white', 'tab:blue']):  # sorting on No
    """
    Given a k-path and its interpolated eigenvals and spectral weights,
    plot the spectral map
    """
    from matplotlib import pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap as LSC

    if ax is None:
        _, ax = plt.subplots(figsize=(3.2, 4.8))
    k_n = k_norm(k_p)
    lscmap = LSC.from_list('', cmap)
    ax.pcolormesh(k_n, Eg*AU_eV, wg.T, cmap=lscmap)
    ax.set_xlim([0, k_n[-1]])
    ax.set_xticks([])
    ax.set_ylabel('Energy (eV)', size=10)

    return ax


def show_eigen(v_sh):
    """
    Given eigenvecs, plot the distribution in terms of support
    functions and their average weights
    """
    from numpy import sum
    from matplotlib import cm
    from matplotlib import pyplot as plt
    from matplotlib.colors import Normalize
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    fig, axs = plt.subplots(1, 2, figsize=(8, 3))
    Na, Nv, No = v_sh.shape
    a = v_sh**2
    for i in range(Nv):
        axs[0].violinplot((a[:, i, :]))
    axs[0].set_xticks([i+1 for i in range(Nv)],
                      [rf'$\psi_{i}$' for i in range(Nv)])
    axs[0].set_yticks([0, 1])
    axs[0].set_ylabel('$a_{ij}^2$')
    im = axs[1].imshow(sum(a, 0)/Na,
                       norm=Normalize(vmin=0, vmax=1),
                       cmap=cm.Blues, aspect='equal')
    axs[1].set_xticks([i for i in range(Nv)],
                      [rf'$\psi_{i}$' for i in range(Nv)])
    axs[1].set_yticks([i for i in range(No)],
                      [rf'$\phi_{i}$' for i in range(No)])
    divider = make_axes_locatable(axs[1])
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im, cax=cax, orientation='vertical', label='average weight')
    fig.tight_layout()

    return fig, axs
