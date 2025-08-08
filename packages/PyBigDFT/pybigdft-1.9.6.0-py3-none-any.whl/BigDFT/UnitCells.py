"""
A module for handling unit cells for periodic calculations.
"""


def _yaml_float(f):
    """A yaml-compliant float representation."""
    from futile.Utils import floatify
    ft = floatify(f)
    if ft < float('inf'):
        return ft
    else:
        return '.inf'


class UnitCell:
    """
    Defines a wrapper for unit cells.

    Args:
        cell (list): a list of unit cell vectors. This can either be a 3x1 list
          or a 3x3 list. Currently, only orthorhombic cells are supported.
          units (str): the units of the cell parameters. If cell is set to
          None, the free boundary condition is enforced.
        units (str): the unit of length.
    """
    def __init__(self, cell=None, units="bohr"):
        from BigDFT.Atoms import AU_to_A, IsAngstroem
        from warnings import warn
        from futile.Utils import floatify

        # Early exit for free boundary condition
        if cell is None:
            self.cell = [[float("inf"), 0, 0],
                         [0, float("inf"), 0],
                         [0, 0, float("inf")]]
            return

        # Copy cell based on the format
        if isinstance(cell[0], list):
            self.cell = cell
        else:
            self.cell = [[floatify(cell[0]), 0, 0],
                         [0, floatify(cell[1]), 0],
                         [0, 0, floatify(cell[2])]]

        # Check that the unit cell is valid
        if self[2, 2] == float("inf") and not (self[1, 1] == float("inf") and
           self[0, 0] == float("inf")):
            raise ValueError("Boundary condition: ",
                             "If z is infinity, x and y must also be.")
        elif self[0, 0] == float("inf") and self[1, 1] != float("inf"):
            raise ValueError("Boundary condition: ",
                             "If x is infinity, y must also be.")
        elif self[0, 1] != 0 or self[0, 2] != 0 or \
                self[1, 0] != 0 or self[1, 2] != 0 or \
                self[2, 0] != 0 or self[2, 1] != 0:
            warn("Non-orthorhombic cells not well supported")

        for i in range(3):
            for j in range(3):
                if self[i, j] < 0:
                    raise ValueError("Unit cell must be non-negative values.")

        # Store internally in bohr
        if IsAngstroem(units):
            for i in range(3):
                for j in range(3):
                    self.cell[i][j] /= AU_to_A

    def __getitem__(self, idx):
        return self.cell[idx[0]][idx[1]]

    def get_boundary_condition(self, units="bohr"):
        """
        Get a string description of the boundary condition (i.e. free,
        surface, wire, periodic)

        Args:
            units (str): the units to report the cell in.

        Returns:
            (str): a string description of the boundary condition.
        """
        from BigDFT.Atoms import AU_to_A, IsAngstroem

        # Match units
        if IsAngstroem(units):
            conv = AU_to_A
        else:
            conv = 1

        if all([self[i, i] == float("inf") for i in range(3)]):
            return "free"
        elif self[0, 0] == float("inf") and self[1, 1] == float("inf"):
            return "wire 0.0 0.0 " + str(self[2, 2]*conv)
        elif self[1, 1] == float("inf"):
            return "surface " + str(self[0, 0]*conv) + " 0.0 " + \
                   str(self[2, 2]*conv)
        else:
            return "periodic " + " ".join([str(conv*self[i, i])
                                           for i in range(3)])

    def get_posinp(self, units="bohr"):
        """
        Create the dictionary representation of the cell that is passed to
        BigDFT.

        Returns:
            (list): a list of the three values of the unit cell.
        """
        from BigDFT.Atoms import AU_to_A, IsAngstroem, IsBohr
        if IsAngstroem(units):
            return [_yaml_float(self[i, i] * AU_to_A) for i in range(3)]
        elif IsBohr(units):
            return [_yaml_float(self[i, i]) for i in range(3)]
        else:
            raise ValueError("Posinp units must be bohr or angstroem")

    def minimum_image(self, pos, units="bohr"):
        """
        Given a vector of three positions, this wraps those positions inside
        the cell using the minimum image convention.

        Returns:
            (list): a list of the values of the wrapped position.
        """
        from BigDFT.Atoms import AU_to_A, IsAngstroem, IsReduced, IsBohr

        # Match units
        if IsAngstroem(units):
            conversion = 1/AU_to_A
        elif IsReduced(units):
            return pos
        elif IsBohr(units):
            conversion = 1
        else:
            raise ValueError("Invalid unit: " + units)

        bohrpos = [x*conversion for x in pos]

        # Adjust position
        for i in range(3):
            if self[i, i] == float("inf"):
                continue
            while(bohrpos[i] > self[i, i]):
                bohrpos[i] -= self[i, i]
            while(bohrpos[i] < 0):
                bohrpos[i] += self[i, i]

        # Convert back
        return [x/conversion for x in bohrpos]

    def to_cartesian(self, pos):
        """
        Convert a vector which is in reduced units to cartesian units.

        Returns:
            (list): the position in cartesian coordinates.
        """
        from numpy import array
        return array(self.cell).dot(pos)

    def to_reduced(self, pos):
        """
        Convert a vector which is in cartesian units to reduced units.

        Returns:
            (list): the position in reduced coordinates.
        """
        from numpy import array, round
        from numpy.linalg import solve

        return round(solve(array(self.cell), pos), 6)

    def get_length_angle(self, units="bohr"):
        """
        Returns a description of the unit cell in terms of side lengths
        and angles.

        Returns:
            (list): list of 3 sides.
            (list): list of 3 angles.
        """
        from numpy.linalg import norm
        from numpy import arccos, dot, pi
        from BigDFT.Atoms import AU_to_A, IsAngstroem

        if IsAngstroem(units):
            conv = AU_to_A
        else:
            conv = 1

        a = norm(self[0, :])
        b = norm(self[1, :])
        c = norm(self[2, :])

        alpha = arccos(dot(self[1, :], self[2, :]) / (b * c)) * (180 / pi)
        beta = arccos(dot(self[0, :], self[2, :]) / (a * c)) * (180 / pi)
        gamma = arccos(dot(self[0, :], self[1, :]) / (a * b)) * (180 / pi)

        return [a * conv, b * conv, c * conv], [alpha, beta, gamma]

    def mirror_point(self, pos):
        """
        Given a point in space, this returns a list of points replicated
        across all periodic boundaries.

        Args:
          pos (list): list of three points.

        Returns:
           (list): the list of points (including the original point).
        """
        plist = []
        if self[0, 0] != float("inf"):
            irange = range(-1, 2)
            ioff = self[0, 0]
        else:
            irange = range(0, 1)
            ioff = 0
        if self[1, 1] != float("inf"):
            jrange = range(-1, 2)
            joff = self[1, 1]
        else:
            jrange = range(0, 1)
            joff = 0
        if self[2, 2] != float("inf"):
            krange = range(-1, 2)
            koff = self[2, 2]
        else:
            krange = range(0, 1)
            koff = 0

        for i in irange:
            for j in jrange:
                for k in krange:
                    plist.append([pos[0] + ioff*i,
                                  pos[1] + joff*j,
                                  pos[2] + koff*k])

        return plist

    def tiling_vectors(self, n):
        """
        Given a cell, computed the displacement vectors associated to its 
        repetition n times in the periodic directions (from -n to n)

        Args:
            n (int or array): number of repetition

        Returns
            (list): the displacement vectors
            (list): the periodic cell indices
        """
        from numpy import meshgrid, where, array, isinf, nan_to_num

        if isinstance(n, int) or isinstance(n, float):
            n = [int(n) for i in range(3)]
        n = array(n)
        cell = self.cell
        id_inf, _ = where(isinf(cell))
        n[id_inf] = 0

        x, y, z = [range(-i, i+1) for i in n]
        X, Y, Z = meshgrid(x, y, z)
        X, Y, Z = X.flatten(), Y.flatten(), Z.flatten()  # lattice coefficients

        a1, a2, a3 = nan_to_num(cell, posinf=0)
        A1 = ((X*a1.reshape(-1, 1)).T).reshape(X.size, 3)
        A2 = ((Y*a2.reshape(-1, 1)).T).reshape(Y.size, 3)
        A3 = ((Z*a3.reshape(-1, 1)).T).reshape(Z.size, 3)
        R_ij = A1+A2+A3  # periodic images 
        idx = [(i, j, k) for i, j, k in zip(X, Y, Z)]

        return [list(i) for i in R_ij], idx


def _example():
    # Create a basic unit cell
    cell = UnitCell([10, 8, 4], units="angstroem")

    # Print out the posinp representation
    print(cell.get_posinp())
    print(cell.get_posinp(units="angstroem"))

    # Right now we enforce the orthorhombic condition
    try:
        cell = UnitCell([[10, 0, 0], [0, 8, 0], [0, 4, 10]])
    except ValueError as e:
        print(e)
    cell = UnitCell([[10, 0, 0], [0, 8, 0], [0, 0, 4]])
    print(cell.get_boundary_condition("angstroem"))

    # Wire boundary condition
    wire = UnitCell([float("inf"), float("inf"), 4])
    print(wire.get_posinp())
    print(wire.get_boundary_condition())

    # Surface boundary condition
    surface = UnitCell([10, float("inf"), 4])
    print(surface.get_posinp())
    print(surface.get_boundary_condition())

    # Wrap positions to the minimum image convention.
    pos = [-5, -2, -3]
    print(cell.minimum_image(pos))
    print(wire.minimum_image(pos))
    print(surface.minimum_image(pos))

    pos = [15, 12, 13]
    print(cell.minimum_image(pos))
    print(wire.minimum_image(pos))
    print(surface.minimum_image(pos))


if __name__ == "__main__":
    _example()
