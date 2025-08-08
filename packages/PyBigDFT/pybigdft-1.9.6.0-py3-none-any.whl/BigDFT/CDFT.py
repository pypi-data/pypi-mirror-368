"""Module to define the Constraints to be employed in the case of CDFT."""


class OrbitalComponents():
    def __init__(self, fragment=None, orbitals={}):
        self.fragmented_components = {}
        for orb, coeff in orbitals.items():
            self.append_component(fragment, orb, coeff)

    def append_component(self, fragment, orbital, coefficient):
        self.fragmented_components.setdefault(fragment, {}).setdefault(
            orbital, coefficient)

    def sanity_check(self):
        total_sum = 0
        for orbitals in self.fragmented_components.values():
            for coefficients in orbitals.values():
                total_sum += coefficients
        # assert total_sum == 1.0, 'Malformed constraint, check values'

    def to_dict(self, orbital_conversion_function=None):
        self.sanity_check()
        represent = []
        for frag, orbitals in self.fragmented_components.items():
            if orbital_conversion_function is not None:
                orbs = {orbital_conversion_function(frag, k): v
                        for k, v in orbitals.items()}
            else:
                orbs = orbitals
            represent.append({'fragment': frag, 'orbitals': orbs})
        return represent

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self)


class CDFTConstraint():
    def __init__(self, kind):
        self.kind = 'None'
        self.important_attributes = []
        self.extra = {}

    def set_Vc(self, Vc):
        self.Vc = Vc

    def to_dict(self, **kwargs):
        d = {'Vc': self.Vc, 'constraint_type': self.kind}
        d.update({attr: getattr(self, attr).to_dict(**kwargs)
                  for attr in self.important_attributes})
        d.update(self.extra)
        return d


class OpticalConstraint(CDFTConstraint):
    """

    Args:
        kind (str): should be 'SINGLET' or 'TRIPLET'
    """
    kind = 'OPTICAL'

    def __init__(self, kind):
        self.hole = OrbitalComponents()
        self.electron = OrbitalComponents()
        self.important_attributes = ['hole', 'electron']
        self.extra = {'excitation_type': kind}

    def append_hole_component(self, fragment, orbital, coefficient):
        self.hole.append_component(fragment, orbital, coefficient)

    def append_electron_component(self, fragment, orbital, coefficient):
        self.electron.append_component(fragment, orbital, coefficient)
