"""Handling of the input options

This module contains the useful quantities to deal with the preparation and
the usage of inputfiles for BigDFT code. The main object is the
:class:`Inputfile` class, which inherits from a python dictionary. Such
inheritance is made possible by the internal representation of the BigDFT
inputfile, which employs the YAML syntax. This means that there is a one-to-one
correspondence between a python dictionary and a BigDFT inputfile.

"""


class Inputfile(dict):
    """ The BigDFT inputfile.

    Principal object needed to run a  BigDFT calculation.
    Might be initialized either from a dictionary, a (yaml-compliant) filename
    path or a:py:class:`~BigDFT.Logfiles.Logfile` instance.

    Note:

       Each of the actions of the module :py:mod:`~BigDFT.InputActions`, which
       is defined on a generic dictionary, also corresponds to a method of of
       the `Inputfile` class, and it is applied to the class instance.
       Therefore also the first argument of the corresponding action is
       implicitly the class instance. For the
       :py:func:`~BigDFT.InputActions.remove` method, the action has to be
       invoked should come from the :py:mod:`~BigDFT.InputActions` module.


    .. _input_action_example:
    Example:

       >>> import InputActions as A, Inputfiles as I
       >>> inp=I.Inputfile()
       >>> inp.set_hgrids(0.3) # equivalent to A.set_hgrids(inp,0.3)
       >>> inp
       {'dft': {'hgrids': 0.3}}
       >>> inp.optimize_geometry() # equivalent to A.optimize_geometry(inp)
       >>> inp
       {'dft': {'hgrids': 0.3},'geopt': {'method': 'FIRE',
                                         'ncount_cluster_x': 50} }
       # equivalent to A.remove(inp,A.optimize_geometry)
       >>> inp.remove(A.optimize_geometry)
       >>> inp
       {'dft': {'hgrids': 0.3}}
       # read an input from a yaml file
       >>> inp = I.Inpufile.from_yaml('filename.yaml')
       # exemple of input file from Logfile instance
       >>> inp = I.Inputfile.from_log(log)
    """

    def __init__(self, *args, **kwargs):
        import BigDFT.InputActions as A
        dict.__init__(self, *args, **kwargs)
        functions = dir(A)
        for action in functions:
            if "__" in action:
                continue
            from functools import partial
            func = getattr(A, action)
            setattr(self, action, partial(func, self))
            method = getattr(self, action)
            method.__doc__ = func.__doc__

    @classmethod
    def from_log(cls, log, **kwargs):
        """
        Create a Inputfile instance from the information in a
        :py:class:`~BigDFT.Logfiles.Logfile` class.

        Args:
            log (:py:class:`~BigDFT.Logfiles.Logfile`): Logfile instance.
            **kwargs: other arguments that have to be passed to the
                 instantiation.

        Returns:
            Inputfile: the Inputfile instance.
        """

        valid_dict = {k: v for k, v in log.log.items()
                      if not (any([c.isupper() for c in k]) or ' ' in k) or
                      'psppar' in k}
        for purge in ['radical', 'outdir', 'logfile',
                      'run_from_files', 'skip']:
            if purge in valid_dict:
                valid_dict.pop(purge)
        nlcc = 'Non Linear Core Correction term'
        nav = '__not_a_value__'
        for key in valid_dict:
            if 'psppar' not in key:
                continue
            if valid_dict[key].get(nlcc, '') == nav:
                valid_dict[key].pop(nlcc)
        return cls(valid_dict)

    @classmethod
    def from_yaml(cls, filename, **kwargs):
        """
        Create a Inputfile instance from the information in a
        ``yaml`` file class.

        Args:
            filename (str): Path of the yaml filename.
            **kwargs: other arguments that have to be passed to the
                 instantiation.

        Returns:
            Inputfile: the Inputfile instance.

        Warning:
            It is assumed that the yaml file contains one single document.
        """
        import yaml
        with open(filename) as ifile:
            return cls(yaml.load(ifile, Loader=yaml.Loader))
