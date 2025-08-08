"""Calculation datasets.

This module deals with the handling of series of calculations.
Classes and functions of this module are meant to simplify the approach to
ensemble calculations with the code, and to deal with parallel executions of
multiple instances of the code.
"""

import logging
from BigDFT.LogUtils import format_iterable
from BigDFT.Calculators import Runner


# create and link logger
module_logger = logging.getLogger(__name__)


def _is_WSL():
    """Determine if we are running on WSL

    ':' is an illegal character on windows filesystems,
    determine if the current run is on a Windows Subsystem for Linux and alter
    the file transfer accordingly

    Returns:
        bool: Whether we are running in a WSL environment or not
    """

    import os
    osinfo = os.uname().release
    WSL = 'WSL' in osinfo
    module_logger.debug(f'checking for WSL using os release: {osinfo}: '
                        f'{WSL}')
    return WSL


def name_from_id(id):
    """Hash the id into a run name
    Construct the name of the run from the id dictionary

    Args:
        id (dict): id associated to the run

    Returns:
       str: name of the run associated to the dictionary ``id``
    """
    jchar = '__'  # '' if _is_WSL() else ':'
    return '-_-'.join([jchar.join([k, str(id[k])]) for k in sorted(id)])
    # keys = list(id.keys())
    # keys.sort()
    # name = ''
    # for k in keys:
    #     name += k + '=' + str(id[k]) + ','
    # ','.join([k+'='+str(i))
    # return name.rstrip(',')


def names_from_id(id):
    """
       Hash the id into a list of run names to search with the
       function id_in_names
       and add the separator '-_-' to have the proper value of a key
       (to avoid 0.3 in 0.39)
    """
    if id is None:
        return ['']
    else:
        return [name_from_id({k: v})+'-_-' for k, v in id.items()]


class Dataset(Runner):
    """A set of calculations.

    Such class contains the various instances of a set of calculations with the
    code.
    The different calculations are labelled by parameter values and information
    that might then be retrieved for inspection and plotting.

    Args:
      label (str): The label of the dataset. It will be needed to identify the
          instance for example in plot titles or in the running directory.
      run_dir (str): path of the directory where the runs will be performed.
      input (dict): Inputfile to be used for the runs as default,
             can be overridden by the specific inputs of the run

    """

    def __init__(self, label='BigDFT dataset', run_dir='runs', **kwargs):
        """
        Set the dataset ready for appending new runs
        """
        self._logger = logging.getLogger(__name__ + '.Dataset')
        self._logger.info('initialise a dataset with args:')
        self._logger.info(f'{format_iterable(locals())}')
        from copy import deepcopy
        newkwargs = deepcopy(kwargs)
        Runner.__init__(self, label=label, run_dir=run_dir, **newkwargs)
        self.runs = []
        """
        List of the runs which have to be treated by the dataset these runs
        contain the input parameter to be passed to the various runners.
        """
        self.calculators = []
        """
        Calculators which will be used by the run method, useful to gather the
        inputs in the case of a multiple run.
        """

        self.results = {}
        """
        Set of the results of each of the runs. The set is not ordered as the
        runs may be executed asynchronously.
        """

        self.ids = []
        """
        List of run ids, to be used in order to classify and fetch the results
        """

        self.names = []
        """
        List of run names, needed for distinguishing the logfiles and
        input files. Each name should be unique to correctly identify a run.
        """

        self._post_processing_function = None

    def append_run(self, id, runner, **kwargs):
        """Add a run into the dataset.

        Append to the list of runs to be performed the corresponding runner and
           the arguments which are associated to it.

        Args:
          id (dict): the id of the run, useful to identify the run in the
             dataset. It has to be a dictionary as it may contain
             different keyword. For example a run might be classified as
             ``id = {'hgrid':0.35, 'crmult': 5}``.
          runner (Runner): the runner class to which the remaining keyword
             arguments will be passed at the input.

        Raises:
          ValueError: if the provided id is identical to another previously
             appended run.

        Todo:
           include id in the runs specification

        """
        from copy import deepcopy
        name = name_from_id(id)
        if name in self.names:
            raise ValueError('The run id', name,
                             ' is already provided, modify the run id.')
        self.names.append(name)
        # create the input file for the run, combining run_dict and input
        inp_to_append = deepcopy(self._global_options)
        inp_to_append.update(deepcopy(kwargs))
        # get the number of this run
        irun = len(self.runs)
        # append it to the runs list
        self.runs.append(inp_to_append)
        # append id and name
        self.ids.append(id)
        # search if the calculator already exists
        found = False

        for run in self.calculators:
            calc = run["calc"]

            options = {k: v for k, v in calc.global_options().items()
                       if k in inp_to_append}

            if options == inp_to_append:
                run["runs"].append(irun)
                found = True
                break

        if not found:
            self.calculators.append({'calc': runner, 'runs': [irun]})

    def process_run(self):
        """
        Run the dataset, by performing explicit run of each of the item of the
           runs_list.
        """
        self._run_the_calculations()
        return {}

    def _run_the_calculations(self, selection=None, extra_run_args=None):
        self._logger.info('running all calculations')
        from copy import deepcopy
        for c in self.calculators:
            calc = c['calc']
            # we must here differentiate between a taskgroup run and a
            # separate run
            for r in c['runs']:
                if selection is not None and r not in selection:
                    self._logger.debug(f'{r} not selected, skipping')
                    continue
                inp = self.runs[r]
                name = self.names[r]
                local_inp = {k: v
                             for k, v in self.local_options.items()
                             if k in inp}
                if len(local_inp) == 0:
                    tmp_inp = inp
                else:
                    tmp_inp = deepcopy(inp)
                    tmp_inp.update(local_inp)
                if extra_run_args is not None:
                    tmp_inp.update(extra_run_args)
                self.results[r] = calc.run(name=name, **tmp_inp)

    def set_postprocessing_function(self, func):
        """Set the callback of run.

        Calls the function ``func`` after having performed the appended runs.

        Args:
           func (func): function that process the `inputs` `results` and
               returns the value of the `run` method of the dataset.
               The function is called as ``func(self)``.

        """
        self._logger.info(f'setting postprocessing function to {func}')
        self._post_processing_function = func

    def post_processing(self, **kwargs):
        """
        Calls the Dataset function with the results of the runs as arguments
        """
        if self._post_processing_function is not None:
            return self._post_processing_function(self)
        else:
            return self.results

    def fetch_results(self, id=None, attribute=None, run_if_not_present=False):
        """Retrieve some attribute from some of the results.

        Selects out of the results the objects which have in their ``id``
        at least the dictionary specified as input. May return an attribute
        of each result if needed.

        Args:
           id (dict): dictionary of the retrieved id. Return a list of the runs
               that have the ``id`` argument inside the provided ``id`` in the
               order provided by :py:meth:`append_run`.
               If absent, then the entire list of runs is returned.
           attribute (str): if present, provide the attribute of each of the
               results instead of the result object
           run_if_not_present (bool): If the run has not yet been performed
               in the dataset then perform it.

        Example:
           >>> study=Dataset()
           >>> study.append_run(id={'cr': 3}, input={'dft':{'rmult':[3,8]}})
           >>> study.append_run(id={'cr': 4}, input={'dft':{'rmult':[4,8]}})
           >>> study.append_run(id={'cr': 3, 'h': 0.5},
           >>>                  input={'dft':{'hgrids': 0.5, 'rmult':[4,8]}})
           >>> #append other runs if needed
           >>> #run the calculations (optional if run_if_not_present=True)
           >>> study.run()
           >>> # returns a list of the energies of first and the third result
           >>> # in this example
           >>> data=study.fetch_results(id={'cr': 3}, attribute='energy')
        """
        self._logger.info('fetching dataset results')
        if id is None:
            fetch_indices = list(range(len(self.names)))
            if run_if_not_present:
                selection_to_run = fetch_indices
            else:
                selection_to_run = []
            self._logger.debug('no id specified, indices are:')
            self._logger.debug(f'{format_iterable(fetch_indices)}')
        else:
            names = names_from_id(id)
            fetch_indices = []
            selection_to_run = []
            for irun, name in enumerate(self.names):
                # add the separator '-_-' to have the proper value of a key
                # (to avoid 0.3 in 0.39)
                if not all([(n in name+'-_-') for n in names]):
                    continue
                if run_if_not_present and irun not in self.results:
                    selection_to_run.append(irun)
                fetch_indices.append(irun)
            self._logger.debug('specified id:')
            self._logger.debug(f'{format_iterable(id)}')
            self._logger.debug('indices are:')
            self._logger.debug(f'{format_iterable(fetch_indices)}')
        # TODO(lbeal) ensure that forcing anyfile=True here is safe
        if len(selection_to_run) > 0:
            self._run_the_calculations(selection=selection_to_run,
                                       extra_run_args=dict(anyfile=True,
                                                           force=False))
        self._logger.debug('run section complete, retreiving results...')
        data = []
        for irun in fetch_indices:
            self._logger.debug(f'...for run {irun}')
            r = self.results.get(irun, None)
            if r is None:
                self._logger.debug('results returned None, possibly due to '
                                   'async run. Attempting to call the '
                                   'individual runner.')
                calc = self.calculators[irun]['calc']
                # ensure the remote_dir and local_dir is propagated to runner
                if not hasattr(calc, 'remote_directory'):
                    remote_dir = self._global_options.get('remote_dir', None)
                    calc.remote_directory = remote_dir
                    self._logger.debug(f'update run {irun} remote_dir '
                                       f'option to {remote_dir}')
                if not hasattr(calc, 'local_directory'):
                    local_dir = self._global_options.get('local_dir', None)
                    if local_dir is None:
                        local_dir = self._global_options.get('run_dir', None)
                    calc.local_directory = local_dir
                    self._logger.debug(f'update run {irun} local_dir '
                                       f'option to {local_dir}')
                resultfile = calc.remote_function._make_run('',
                                                            dry_run=True)
                self._logger.debug('updating calc result file to '
                                   f'{resultfile}')
                calc.resultfile = resultfile
                if hasattr(calc, 'resultfiles'):
                    calc.resultfiles.append(resultfile)
                else:
                    calc.resultfiles = [resultfile]

                r = calc.fetch_result()

            data.append(r if attribute is None else getattr(r, attribute))
        self._logger.debug(f'Done. data len: {len(data)}')
        return data

    def seek_convergence(self, rtol=1.e-5, atol=1.e-8, selection=None,
                         **kwargs):
        """
        Search for the first result of the dataset which matches the provided
        tolerance parameter. The results are in dataset order
        (provided by the :py:meth:`append_run` method) if `selection` is not
        specified.
        Employs the numpy :py:meth:`allclose` method for comparison.

        Args:
          rtol (float): relative tolerance parameter
          atol (float): absolute tolerance parameter
          selection (list): list of the id of the runs in which to perform the
               convergence search. Each id should be unique in the dataset.
          **kwargs: arguments to be passed to the :py:meth:`fetch_results`
               method.

        Returns:
          id,result (tuple): the id of the last run which matches the
                convergence, together with the result, if convergence is
                reached.

        Raises:
           LookupError: if the parameter for convergence were not found.
               The dataset has to be enriched or the convergence parameters
               loosened.
        """
        from numpy import allclose
        from futile.Utils import write
        to_get = self.ids if selection is None else selection

        id_ref = to_get[0]
        write('Fetching results for id "', id_ref, '"')
        ref = self.fetch_results(id=id_ref, **kwargs)
        ref = ref[0]
        for id in to_get[1:]:
            write('Fetching results for id "', id, '"')
            val = self.fetch_results(id=id, **kwargs)
            val = val[0]
            if allclose(ref, val, rtol=rtol, atol=atol):
                res = self.fetch_results(id=id_ref)
                label = self.get_global_option('label')
                write('Convergence reached in Dataset "' +
                      label+'" for id "', id_ref, '"')
                return (id_ref, res[0])
            ref = val
            id_ref = id
        raise LookupError('Convergence not reached, enlarge the dataset'
                          ' or change tolerance values')

    def get_times(self):
        """
        Return the TimeData from the time-*.yaml files in the run_dir
        """
        from os import path as p
        from futile import Time as T
        time_files = {}
        run_dir = self.get_global_option('run_dir')
        time_files = [p.join(run_dir,
                             self.fetch_results(id=self.ids[c],
                                                attribute='data_directory')[0],
                             'time-' + self.names[c] + '.yaml'
                             ) for c in self.results
                      ]
        return T.TimeData(*time_files)

    def wait(self):
        """!skip"""
        from IPython.display import display, clear_output
        from aiida.orm import load_node
        running = len(self.results)
        while(running != 0):

            import time
            time.sleep(1)
            running = len(self.results)
            for c in self.results:
                pk = self.results[c]['node'].pk
                node = load_node(pk)
                if(node.is_finished):
                    running -= 1
                    # print(node.is_finished_ok)
            clear_output(wait=True)
            display(str(running)+" processes still running")

    def get_logfiles(self):
        """
        Attempt to obtain the logfiles for completed runs

        Returns:
            dict:
                {runname: Logfile}
        """
        logfiles = {}
        for c in self.results:
            try:
                logfiles[c] = self.calculators[0]['calc'].get_logs(
                    self.results[c]['node'].pk, self.names[c])
            except ValueError:
                logfiles[c] = self.results[c]
                print("no logfile for " + str(c))
        return logfiles


def combine_datasets(*args):
    """
    Define a new instance of the dataset class that should provide
    as a result a list of the runs of the datasets
    """
    full = Dataset(label='combined_dataset')
    # append the runs or each dataset
    for dt in args:
        for irun, runs in enumerate(dt.runs):
            calc = dt.get_runner(irun)
            id, dt.get_id(irun)
            full.append_run(id, calc, **runs)

    full.set_postprocessing_function(_combined_postprocessing_functions)


def _combined_postprocessing_functions(runs, results, **kwargs):
    pass
