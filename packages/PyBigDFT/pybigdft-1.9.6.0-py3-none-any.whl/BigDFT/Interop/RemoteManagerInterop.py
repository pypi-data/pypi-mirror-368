"""
This module contains the definition of parser for computers which
guarantee full interoperability with remotemanager API and
commodity functions which are used on the context of PyBigDFT.
"""
from remotemanager import Dataset

def computerparser(resources):
    """Function to define a generic computer as a resource_parser.

    This function uses the resources dictionary by identifying three
    main blocks for the parser script: the prologue, the module
    and the epilogue. The prologue is defines by the pragma for the submitter
    and the options (flag and value) in the usual remotemanager way.
    The other two sections are based on the ``load`` and the
    ``export`` operations, which load modules and export environment
    variables. Both these section have a ``pre_`` and a ``post_``
    field, which define the list of the commands which require
    to be performed before and after the sections.

    """
    heuristics_opt = ['cores_per_node', 'mpi', 'nodes', 'gpus_per_node']


    def pragma_line(pragma, flag, value):
        if flag.endswith('=') or flag.endswith(':'):
            return ' '.join([pragma, flag + value])
        else:
            return ' '.join([pragma, flag, value])

    def get_from_resources(kwargs, key):
        from numpy import nan
        if key in kwargs:
            return kwargs[key].value
        else:
            return nan

    def submission_nodes(pg, kwargs):
        from numpy import isnan
        ncores = get_from_resources(kwargs, 'cores_per_node')
        nomp = get_from_resources(kwargs, 'omp')
        nmpi = get_from_resources(kwargs, 'mpi')
        nnodes = get_from_resources(kwargs, 'nodes')
        ngpus_nodes = get_from_resources(kwargs, 'gpus_per_node')
        ngpus = get_from_resources(kwargs, 'gpus')
        if not isnan(ncores):
            if nmpi is None:
                nmpi = int(ncores/nomp)*nnodes
            if nnodes is None:
                nnodes = int((nmpi*nomp-1) / ncores)+1
        if not isnan(nnodes*ncores*nomp*nmpi):
            assert nnodes*ncores >= nomp*nmpi, 'Overpopulated nodes are not allowed in computerparser, check omp and mpi'
        options = []
        if not isnan(nmpi):
            options.append(pragma_line(pg, kwargs['mpi'].flag, str(nmpi)))
        if not isnan(nnodes):
            options.append(pragma_line(pg, kwargs['nodes'].flag, str(nnodes)))
        if not isnan(ngpus) and ngpus is not None and not isnan(nmpi) and not isnan(nnodes):
            gpus = min(ngpus, nmpi/nnodes)
            options.append(pragma_line(pg, kwargs['gpus'].flag, str(gpus)))
        return options

    def substitute_carets(strvalue, kwargs):
        start = strvalue.find("<")
        end = strvalue.find(">")
        if start != -1 and end != -1:
          key = strvalue[start+1:end]
          val = kwargs[key].value  #should be present
          strvalue = strvalue.replace('<'+key+'>',val)
          return substitute_carets(strvalue, kwargs)
        else:
          return strvalue

    def prologue(header=None, pragma=None, **kwargs):
        pg = '#SBATCH' if pragma is None else str(pragma.value)
        if pg == '':  #no pragma, it means no prologue
            return [str(header.value)] if header else []

        options = submission_nodes(pg, kwargs)

        # then create the remaining part of script body
        for opt, value in kwargs.items():
            if not value or (opt in heuristics_opt):
                continue
            strvalue = substitute_carets(str(value.value), kwargs)
            options.append(pragma_line(pg, value.flag, strvalue))

        return ([str(header.value)] if header else []) + options

    def special(name):
        return ['pre_'+name, name, 'post_'+name]

    def items(spec, key):
        if key in spec:
            its=spec[key]
            if its:
                return its.value
            else:
                return []
        else:
            return []

    def actions(name, base, spec):
        pre, body, post = [items(spec, k)
                           for k in special(name)]
        mods = [action for action in pre]
        mods += [base+' '+mod for mod in body]
        mods += [action for action in post]
        return mods

    def modules(**kwargs):
        return actions('load', 'module load', kwargs)

    def epilogue(setenv='export', **kwargs):
        return actions('export', setenv, kwargs)

    # Remove the non-prologue informaton from the resources
    body = {k: resources.pop(k)
            for k in special('load') + special('export')
            if k in resources}

    return prologue(**resources) + modules(**body) + epilogue(**body)


def computer_spec_update(computer_spec, dt):
    for k, v in dt.items():
        if isinstance(v, dict):
            computer_spec.setdefault(k,{}).update(v)
        elif isinstance(v,list):
            computer_spec.setdefault(k,[]).extend(v)
        else:
            computer_spec[k] = v


def computer_spec_load(computer_spec,spc):
    import yaml
    dt = yaml.load(spc, Loader=yaml.Loader)
    if dt is None:
        return
    computer_spec_update(computer_spec, dt)
    return computer_spec


def computer_from_specs(specs, **kwargs):
    """Provide a `py:remotemanager:BaseComputer` instantiation.

    This function associate the spec list provided as argument
    to the spec of a `py:remotemanager:BaseComputer:from_dict`
    method.


    Args:
        spec (list): list of yaml compliant strings defining
            the computer according to the computerparser approach
        **kwargs: any other arguments which can be employed to
            update the spec dictionary. Overrides specs data.

    Returns:
        function: the classmethod `py:remotemanager:BaseComputer:from_dict`
            ready to be calles by other arguments (eg. passfile) to
            instantiate the computer class.
    """
    from remotemanager.connection.computers.base import BaseComputer
    from functools import partial
    computer_spec={"resource_parser": computerparser}
    base_spec="""
optional_resources:
  pragma: pragma
  export: export
  load: load
  pre_load: pre_load
  pre_export: pre_export
  post_load: post_load
  post_export: post_export
  header: header
  setenv: setenv
"""
    for spc in [base_spec] + specs:
        computer_spec_load(computer_spec, spc)
    computer_spec_update(computer_spec, kwargs)
    return partial(BaseComputer.from_dict,spec=computer_spec)

frontend_environment="""
 resources:
   sourcedir: SOURCEDIR=
 optional_defaults:
   pragma: export
"""

compilation="""
 resources:
   builddir: BUILDDIR=
 optional_resources:
   modulesets_dir: BIGDFT_SUITE_MODULESETS_DIR=
   checkoutroot: BIGDFT_SUITE_CHECKOUTROOT=
   prefix: BIGDFT_SUITE_PREFIX=
   tarballdir: BIGDFT_SUITE_TARBALLDIR=
   builder: BUILDER=
   python: PYTHON=
   rcfile: RCFILE=
   action: ACTION=
 optional_defaults:
   rcfile: buildrc
   action: '"buildone -f PyBigDFT"'
   builder: $SOURCEDIR/bundler/jhbuild.py
   python: python3
   post_export:
     - $PYTHON $BUILDER -f $RCFILE $ACTION 1>compile_stdout 2>compile_stderr
"""

git_remote_branch="""
 optional_resources:
   remote_branch: REMOTE_BRANCH=
 optional_defaults:
   remote_branch: tmp_update
"""

git_push_localhost="""
 resources:
   branch: BRANCH=
   remote: REMOTE=
   remote_sourcedir: REMOTE_SOURCEDIR=
 optional_resources:
   git: GIT=
   git_ssh: GIT_SSH_COMMAND=
 optional_defaults:
   git: git
   export:
      - REMOTE_URL=git+ssh://${REMOTE}/${REMOTE_SOURCEDIR}
   post_export:
      - echo "Including $REMOTE_URL as $REMOTE" 1>compile_stdout 2>compile_stderr
      - if git remote -v | grep -Fq "${REMOTE}"; then git remote set-url ${REMOTE} ${REMOTE_URL}; else git remote add ${REMOTE} ${REMOTE_URL}; fi 1>>compile_stdout 2>>compile_stderr
      - echo "Delete remote target if non empty" 1>>compile_stdout 2>>compile_stderr
      - ${GIT} push ${REMOTE} --delete ${REMOTE_BRANCH} || true 1>>compile_stdout 2>>compile_stderr
      - echo "Pushing external repo" 1>>compile_stdout 2>>compile_stderr
      - ${GIT} push ${REMOTE} ${BRANCH}:${REMOTE_BRANCH} 1>>compile_stdout 2>>compile_stdout
"""

git_update="""
 resources:
   branch: BRANCH=
 optional_defaults:
   post_export:
      - echo "Pulling external repo into build" 1>compile_stdout 2>compile_stderr
      - git checkout ${REMOTE_BRANCH} 1>>compile_stdout 2>>compile_stderr
      - git checkout -f 1>>compile_stdout 2>>compile_stderr
      - git checkout ${BRANCH} 1>>compile_stdout 2>>compile_stderr
      - git merge ${REMOTE_BRANCH} 1>>compile_stdout 2>>compile_stderr
"""


def execute_cmd_list(url, remote_dir, cmds, stdout, stderr):
    """Executes a list of commands on a remote dir and dump their results on remote stdout/err"""

    for cmd in commands:
        print('Executing: "'+cmd+'"...')
        print(url.cmd(remote_dir+' && '+cmd+'1 >>'+stdout+' 2>>'+stderr))


def file_tail(filename):
    import codecs
    with codecs.open(filename, 'r', encoding='unicode_escape') as ofile:
        lines = list(ofile.readlines())
    tail=min(5, len(lines))
    if len(lines) > 0:
        tailout = (('\n'.join(lines[-tail:])).encode('unicode_escape')).decode('utf-8')
    else:
        tailout = 'No Output'
    return tailout


def code_updater(remote_sourcedir, **kwargs):
    """A Dataset to update the code remotely.

    This function creates a dataset that can be used to update the code
    in a remote machine prior to compilation.

    Args:

        remote_sourcedir (str): the remote directory.

        **kwargs: other arguments of the dataset. Used also to create the basecomputer and dataset.
            Main arguments are listed below.
        
            sourcedir (str): path of the local sourcedir. Defaults to $BIGDFT_SUITE_SOURCES.
            
            branch (str): the local branch to be remotely pushed. 'devel' branch is used as default.
            
            remote_branch (str): the remote branch in which the source tree will end.
                 Defaults to ``devel``.
        
            remote (str): the name git would employ for the remote host.
            
            intermediate_branch (str): the intermediate branch which will be used for the update.
            
            git_command (str): the git executable. Defaults to ``git``.
            
            git_ssh (str): the ssh command which will be used for the transfer, useful for the sshpass case.
                Defaults to ``url.ssh.rstrip(url.userhost)``.
           
    """
    def async_run(ds, name):
        ds.run(force=True, asynchronous=False)
        ds.fetch_results()
        assert all(ds.is_finished), name+' dataset not correctly ended'
        print(ds.results[0])
        print('Errors:')
        print(ds.errors[0])
        
    from remotemanager import Dataset, Script
    try:
        from remotemanager import Computer
    except Exception as e:
        from remotemanager import BaseComputer as Computer

    from os import environ
    from futile.Utils import kw_pop
   
    template_push="""#!/bin/bash
export SOURCEDIR=#sourcedir:default=$BIGDFT_SUITE_SOURCES#
export BRANCH=#branch:default=devel#
export REMOTE=#host_id:optional=False#
export REMOTE_ID=#remote:default={host_id}#
export REMOTE_SOURCEDIR=#remote_sourcedir:optional=False#
export REMOTE_BRANCH=#intermediate_branch:default=tmp_update#
export GIT="#git_command:default=git#"
export GIT_SSH_COMMAND="#git_ssh:default=ssh#" #environment variable for git
export REMOTE_URL=git+ssh://${REMOTE}${REMOTE_SOURCEDIR}
echo "Including $REMOTE_URL as $REMOTE_ID"
if ${GIT} remote -v | grep -Fq "${REMOTE_ID}"; then ${GIT} remote set-url ${REMOTE_ID} ${REMOTE_URL}; else ${GIT} remote add ${REMOTE_ID} ${REMOTE_URL}; fi
echo "Delete remote target if non empty"
${GIT} push ${REMOTE_ID} --delete ${REMOTE_BRANCH}
echo "Pushing external repo"
${GIT} push --tags ${REMOTE_ID} ${BRANCH}:${REMOTE_BRANCH}
echo 'Pushing ended'"""

    template_update="""#!/bin/bash
export SOURCEDIR=#remote_sourcedir:optional=False#
export BRANCH=#remote_branch:default=devel#
export REMOTE_BRANCH=#intermediate_branch:default=tmp_update#
echo "Pulling external repo into build"
git checkout ${REMOTE_BRANCH}
git checkout -f
git checkout ${BRANCH}
git merge ${REMOTE_BRANCH}
echo 'Merging finished'"""

    kwargs_tmp, template = kw_pop('template',
                                  None,
                                  **kwargs)
    kwargs_tmp, remote = kw_pop('remote',
                                None,
                                **kwargs_tmp)


    push_script = Script(template=template_push, **kwargs_tmp)
    update_script = Script(template=template_update, **kwargs_tmp)

    # localhost = Computer(template=template_push)
    # url = Computer(template=template_update, **kwargs)
    url = Computer(template=template,**kwargs_tmp)
    if remote is None:
        remote = url.host.split('.')[0]
    push = Dataset(push_script, name='push_to_remote',
                   # url=localhost,
                   remote_dir=kwargs.get('sourcedir', environ['BIGDFT_SUITE_SOURCES']),
                   **kwargs_tmp)
    push.wipe_runs()
    push.append_run(arguments=dict(git_ssh=kwargs.get('git_ssh', url.ssh.rstrip(url.userhost)),
                    host_id=url.userhost,remote=remote,
                    remote_sourcedir=remote_sourcedir))
    async_run(push, 'Push')
    push.hard_reset()

    update = Dataset(update_script, name='update_remote',
                     url=url,
                     remote_dir=remote_sourcedir, **kwargs_tmp)
    update.wipe_runs()
    update.append_run(arguments=dict(remote_sourcedir=remote_sourcedir))
    async_run(update, 'Update')
    update.hard_reset()
    
"""
    conditions: list of the conditions for compilation.

    targets: the modules which will have to be compiled in this rcfile. Defaults to ``spred``.

    fc: Fortran compiler.
    
    fcflags: Fortran compiler flags.

    ompflags: the flags required for activating openmp compilation.
    
    cc: C compiler.
    
    cflags: C compiler flags.
    
    cxx: C++ compiler.
    
    cxxflags: C++ compiler flags.
    
    linalg: the liking like of linear algebra, useful for ``ext-linalg`` configure line.

    gpu_line: the linking line for GPU compilation.

    configure_line: extra lines for configure.

    autogenargs_update: extra dictionary of the configure line to be employed on a per-package basis, for autotools.

    cmakeargs_update: extra dictionary of the configure line to be employed on a per-package basis, for cmake.

    extra_buildrc_lines: further lines to be added at the endo of the buildrc file if required.
"""

buildrc_template="""#This is the configuration file for the BigDFT installer
#This is a python script which is executed by the build suite

#Add the condition testing to run tests and includes PyYaml
conditions=set(list(conditions)+#conditions#)
#List the module the this rcfile will build
modules = #targets:default=['spred',]#

def env_configuration():
    conf_line = '' \\
       + 'FC="#FC#" ' \\
       + 'FCFLAGS="#FCFLAGS#" ' \\
       + 'CC="#CC#" ' \\
       + 'CFLAGS="#CFLAGS#" ' \\
       + 'CXX="#CXX#" ' \\
       + '--with-ext-linalg="#linalg#" ' \\
       + '#gpu_line# ' \\
       + '#configure_line# '
    return conf_line

#the following command sets the environment variable to give these settings
#to all the modules
import os
os.environ['BIGDFT_CONFIGURE_FLAGS']=env_configuration()
#here follow the configuration instructions for the modules built
#we specify the configurations for the modules to customize the options if needed
autogenargs = env_configuration()

os.environ['FC']="#FC#"
os.environ['CC']="#CC#"
os.environ['CXX']="#CXX#"


module_cmakeargs.update({
    'dftd3': '-Dpython=true -Dpython_version=${PYTHON}' \\
        + '-DBLAS_LIBRARIES="#linalg#"'
    ,'ntpoly': '-DFORTRAN_ONLY=Yes -DBUILD_SHARED_LIBS=Yes' \\
        + '-DCMAKE_Fortran_COMPILER="#FC#"' \\
        + '-DCMAKE_Fortran_FLAGS="#FCFLAGS# $MPI_FFLAGS"' \\
        + '-DCMAKE_Fortran_FLAGS_RELEASE="#FCFLAGS# $MPI_FFLAGS"' \\
        + '-DOpenMP_Fortran_FLAGS=#OMPFLAGS#'
        })

module_autogenargs.update({
            'biopython': "", 'simtk': "", 'pdbfixer': "", 'ase': "", 'dill': "", 'dnaviewer': ""
            })

module_autogenargs.update({#autogenargs_update#})

module_cmakeargs.update({#cmakeargs_update#})

#extra_buildrc_lines#

"""


def code_compiler(builddir, **kwargs):
    """A Dataset to compile the code remotely.

    This function creates a dataset that can be used to compile the
    code on a remote url. In a nutshell it executes

    ``$PYTHON $BUILDER -f $RCFILE $BUILD_CONDITIONS $ACTION``

    after having created a base computer that will be employed for the
    compilation.

    Args:

        builddir: the remote build directory. Dataset will be executed there.
        
        **kwargs: extra arguments to the dataset and url creation, including some specific
            keywords,  which have to be put in `arguments` values. Those are:

            * python_interpreter: the python interpreter, defaults to ``$PYTHON``.
            
            * sourcedir: the source directory in the remote computer from which
                to issue the remote installation, defaults to ``$BIGDFT_SUITE_SOURCES``.

            * tarballdir: the directory in which the tarballs of BigDFT-suite are stored,
                including the plugins. Defaults to ``$BIGDFT_SUITE_TARBALLDIR``.

            * checkoutroot: directory of the checkout of the external plugins tarfiles.
                Defaults to ``$BIGDFT_SUITE_CHECKOUTROOT``.

            * modulesets: directory (URI) where the modulesets of the code have to be found.
                Defaults to ``$BIGDFT_SUITE_MODULESETS_DIR``.

            * prefix: the prefix in which the code will be installed.
                Defaults to ``builddir/install``.

            * rcfile: the file which will be used for the compilation. Defaults to buildrc.

            * builder: the command to be ran for building the code. Defaults to
                ``$SOURCEDIR/bundler/jhbuild.py``, but it can also be, for instance
                ``$SOURCEDIR/Installer.py -y``.

            * action: the build action, defaults to ``build``.

            * module_preload: the action to be launched before the module load.
                can be se to ``purge`` for instance.

            * modules: the sequences of modules to be loaded.

            * build_conditions: the conditions to be added to the builder.

            * upstream_prefixes: sequence of the directories where the upstream packages will be found
                by the builder.

    Returns:
        py:remotemanager:Dataset : the Dataset instance containing one
           single runner which issue the compilation.
           The `fetch_results()` command on such dataset retrieved in the
           `compile` directory, two files, the `compile_stdout` and `compile_stderr`
           which can be inspected for potential problems.
           The results of this single runner contains the last lines of the stdout file.

    """
    from remotemanager import Dataset, Script, URL
    try:
        from remotemanager import Computer
    except Exception as e:
        from remotemanager import BaseComputer as Computer
    
    frontend_compilation_template="""
export BIGDFT_SUITE_SOURCES=#sourcedir#
export BIGDFT_SUITE_TARBALLDIR=#tarballdir#
export BIGDFT_SUITE_CHECKOUTROOT=#checkoutroot# && mkdir -p $BIGDFT_SUITE_CHECKOUTROOT
export BIGDFT_SUITE_PREFIX=#prefix#
export BIGDFT_SUITE_MODULESETS_DIR=#modulesets#
export XDG_CACHE_HOME=#cachedir#
module #module_preload#
module load #modules#
export PYTHON=#python_interpreter#
#use jhbuild #jhbuild:default=True# 
export BUILDER=#builder:default={"$BIGDFT_SUITE_SOURCES/bundler/jhbuild.py" if jhbuild.value else "$BIGDFT_SUITE_SOURCES/Installer.py -y"}#
export RCFILE=#rcfile:default=buildrc#
export ACTION="#action:default=build#"
export BUILD_CONDITIONS="#build_conditions#"
export ACTUAL_RCFILE=$RCFILE #we should copy the file into a temporary one if suitable
echo "from os.path import abspath" >> $ACTUAL_RCFILE; echo "extra_prefixes=[" >> $ACTUAL_RCFILE; for prefix in #upstream_prefixes#; do echo "    abspath('${prefix}')," >> $ACTUAL_RCFILE; done; echo "    ]" >> $ACTUAL_RCFILE

#compilation_command:default=$PYTHON $BUILDER -f $RCFILE $BUILD_CONDITIONS $ACTION#

echo 'Compilation ended'"""

    template = kwargs.pop('template') if 'template' in kwargs else '#!/bin/bash'
    template += frontend_compilation_template

    url = Computer(template=template, **kwargs)

    compile = Dataset(None, name='compile', url=url, remote_dir=builddir,
                      **kwargs)
    compile.wipe_runs()

    return compile
       

#### Computer specifications



computers_database="""
localhost:
   template: |
      #!/bin/bash
      # #cores_per_node:default=8#  #feature of the machine
      export MPI=#mpi:optional=False#
      export OMP_NUM_THREADS=#omp:optional=False#
      export PREFIX=#prefix:default=/opt/bigdft/install#
      export BIGDFT_MPIRUN="#mpirun:default=mpirun -np# $MPI"
      export FUTILE_PROFILING_DEPTH=0
      source $PREFIX/bin/bigdftvars.sh  
      export GENESIS_ROOT=$BIGDFT_ROOT
      export GENESIS_MPIRUN=$BIGDFT_MPIRUN
      export I_MPI_FABRICS=shm #for oneapi container
      export PYTHON=#python_interpreter:default=python3#
      #extra_lines#

irene: ### Irene TGCC
    submitter: ccc_msub
    template: |
      #!/bin/bash
      # #cores_per_node:default=128#  #feature of the machine
      #MSUB -n #mpi:optional=False#
      #MSUB -N #nodes:default={(mpi*omp)/cores_per_node}#
      #MSUB -c #omp:optional=False#
      #MSUB -t #time:optional=False#
      #MSUB -A #project:default=gen12049#
      #MSUB -r #jobname:default=job#
      #MSUB -q #queue:default=rome#
      #MSUB -m #filesystem:default=work,scratch#
      #MSUB -o #output:default={jobname}.o#
      #MSUB -e #error:default={jobname}.e#
      module #module_preload#
      module load #modules:default=python3 cmake inteloneapi/24.0.0 mpi/intelmpi/24.0.0 mkl/24.0.0#

      set -x
      cd $BRIDGE_MSUB_PWD

      export PREFIX=#prefix:default=/ccc/work/cont003/gen12049/genovesl/binaries/intel_oneapi_mpi/suite#
      export MKL_DEBUG_CPU_TYPE=5
      export BIGDFT_MPIRUN=ccc_mprun
      export FUTILE_PROFILING_DEPTH=0
      export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
      source $PREFIX/bin/bigdftvars.sh  
      export GENESIS_ROOT=$BIGDFT_ROOT
      export GENESIS_MPIRUN=$BIGDFT_MPIRUN

    frontend_template: |
      #!/bin/bash
      module #module_preload#
      module load #modules:default=python3 cmake inteloneapi/24.0.0 mpi/intelmpi/24.0.0 mkl/24.0.0#
      export PREFIX=#prefix:default=/ccc/work/cont003/gen12049/genovesl/binaries/intel_oneapi_mpi/suite#
      export MKL_DEBUG_CPU_TYPE=5
      export FUTILE_PROFILING_DEPTH=0
      source $PREFIX/bin/bigdftvars.sh  
      export GENESIS_ROOT=$BIGDFT_ROOT
      export GENESIS_MPIRUN=$BIGDFT_MPIRUN
      #command:optional=False#

    gnu_mpi:
      fc: mpif90
      fcflags: -m64 -I${MKLROOT}/include -O2 -fPIC -fopenmp
      cc: mpicc
      cflags: -O2 -g -fPIC
      ompflags: -fopenmp
      cxx: mpicxx
      linalg: -m64  -L${MKLROOT}/lib -Wl,--no-as-needed -lmkl_gf_lp64 -lmkl_gnu_thread -lmkl_core -lgomp -lpthread -lm -ldl
      configure_line: --enable-dynamic-libraries LIBS="-lstdc++"
      module_preload: purge
      modules: python3 cmake gnu mpi mkl/24.0.0
      python_interpreter: python
      sourcedir: /ccc/work/cont003/drf/genovesl/1.9.5
      tarballdir:        /ccc/work/cont003/gen12049/genovesl/bigdft-upstream-tarballs
      builddir:          /ccc/work/cont003/gen12049/genovesl/binaries/compile/gnu_mpi
      upstream_prefixes: /ccc/work/cont003/gen12049/genovesl/binaries/gnu_mpi/upstream
      prefix:            /ccc/work/cont003/gen12049/genovesl/binaries/gnu_mpi/suite

    intel_mpi:
      fc: mpif90 -fc=ifort
      fcflags: -I${MKLROOT}/include -O2 -fPIC -qopenmp
      cc: mpicc -cc=icc
      cflags: -O2 -g -fPIC
      ompflags: -qopenmp
      cxx: mpicxx -cc=icpc
      linalg:  -L${MKLROOT}/lib/intel64 -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core -liomp5 -lpthread -lm -ldl
      configure_line: --enable-dynamic-libraries F77=ifort
      build_conditions: --conditions=-vdw
      module_preload: purge
      modules: python3 cmake intel mpi mkl
      python_interpreter: python
      sourcedir: /ccc/work/cont003/drf/genovesl/1.9.5
      tarballdir:        /ccc/work/cont003/gen12049/genovesl/bigdft-upstream-tarballs
      builddir:          /ccc/work/cont003/gen12049/genovesl/binaries/compile/intel_mpi
      upstream_prefixes: /ccc/work/cont003/gen12049/genovesl/binaries/intel_mpi/upstream
      prefix:            /ccc/work/cont003/gen12049/genovesl/binaries/intel_mpi/suite

    intel_intelmpi:
      fc: mpif90 -fc=ifort
      fcflags: -I${MKLROOT}/include -O2 -fPIC -qopenmp
      cc: mpicc -cc=icc
      cflags: -O2 -g -fPIC
      ompflags: -qopenmp
      cxx: mpicxx -cc=icpc
      linalg:  -L${MKLROOT}/lib/intel64 -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core -liomp5 -lpthread -lm -ldl
      configure_line: --enable-dynamic-libraries F77=ifort
      build_conditions: --conditions=-vdw
      module_preload: purge
      modules: python3 cmake intel mpi/intelmpi mkl
      python_interpreter: python
      sourcedir: /ccc/work/cont003/drf/genovesl/1.9.5
      tarballdir:        /ccc/work/cont003/gen12049/genovesl/bigdft-upstream-tarballs
      builddir:          /ccc/work/cont003/gen12049/genovesl/binaries/compile/intel_intelmpi
      upstream_prefixes: /ccc/work/cont003/gen12049/genovesl/binaries/intel_intelmpi/upstream
      prefix:            /ccc/work/cont003/gen12049/genovesl/binaries/intel_intelmpi/suite

    intel_oneapi:
      fc: ifx
      fcflags: -I${MKLROOT}/include -O2 -fPIC -qopenmp
      cc: icx
      cflags: -O2 -g -fPIC
      ompflags: -qopenmp
      cxx: icpx
      linalg: -L${MKLROOT}/lib -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core -liomp5 -lpthread -lm -ldl
      configure_line: --enable-dynamic-libraries F77=ifx
      module_preload: purge
      modules: python3 cmake inteloneapi/24.0.0 mpi/intelmpi/24.0.0 mkl/24.0.0
      python_interpreter: python
      sourcedir: /ccc/work/cont003/drf/genovesl/1.9.5
      tarballdir:        /ccc/work/cont003/gen12049/genovesl/bigdft-upstream-tarballs
      builddir:          /ccc/work/cont003/gen12049/genovesl/binaries/compile/intel_oneapi
      upstream_prefixes: /ccc/work/cont003/gen12049/genovesl/binaries/intel_oneapi/upstream
      prefix:            /ccc/work/cont003/gen12049/genovesl/binaries/intel_oneapi/suite

    intel_oneapi_mpi:
      fc: mpif90 -fc=ifx
      fcflags: -I${MKLROOT}/include -O2 -fPIC -qopenmp
      cc: mpicc -cc=icx
      cflags: -O2 -g -fPIC
      ompflags: -qopenmp
      cxx: icpx
      linalg: -L${MKLROOT}/lib -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core -liomp5 -lpthread -lm -ldl
      configure_line: --enable-dynamic-libraries F77=ifx
      module_preload: purge
      modules: python3 cmake inteloneapi/24.0.0 mpi/intelmpi/24.0.0 mkl/24.0.0
      python_interpreter: python
      sourcedir: /ccc/work/cont003/drf/genovesl/1.9.5
      tarballdir:        /ccc/work/cont003/gen12049/genovesl/bigdft-upstream-tarballs
      builddir:          /ccc/work/cont003/gen12049/genovesl/binaries/compile/intel_oneapi_mpi
      upstream_prefixes: /ccc/work/cont003/gen12049/genovesl/binaries/intel_oneapi/upstream
      prefix:            /ccc/work/cont003/gen12049/genovesl/binaries/intel_oneapi_mpi/suite
"""

computers_database_old="""
localhost:
  specs:
    base:
      host: localhost
    scheduler:
      resources:
        mpi: MPI=
        omp: OMP=
      optional_resources:
        mpirun: MPIRUN=
      optional_defaults:
        mpirun: '"mpirun -np"'
        pragma: export
  environments:
    container_oneapi:
      export:
          - I_MPI_FABRICS=shm
          - BIGDFT_MPIRUN="$MPIRUN $MPI"
          - FUTILE_PROFILING_DEPTH=0
          - OMP_NUM_THREADS=$OMP
archer2:
  specs:
    base:
      optional_resources:
          cores_per_node: cores_per_node
      optional_defaults:
          cores_per_node: 128
      host: archer2
    scheduler:
      resources:
        omp: --cpus-per-task=
        time: --time=
      required_or:
         - mpi: --ntasks=
           nodes: --nodes=
      optional_resources:
        qos: --qos=
        partition: --partition=
        jobname: --job-name=
        queue: -q
        output: -o
        error: -e
        export_flag: --export=
      optional_defaults:
        qos: standard
        partition: <qos>
        jobname: job
        output: <jobname>.o
        error: <jobname>.e
        pragma: "#SBATCH"
        export_flag: none
      submitter: sbatch
  flavours:
    gnu:
      pre_load:
         - module swap PrgEnv-cray PrgEnv-gnu
      load:
         - cray-python
         - mpi/openmpi/4.0.5
         - mkl
         - cmake
  environments:
    1.9.4-gnu-sep2023:
      post_export:
          - "source $PREFIX/bin/bigdftvars.sh"
      export:
          - PREFIX=/work/e572/e572/shared/bigdft_luigi/Build/install/
          - BIGDFT_MPIRUN='srun --hint=nomultithread --distribution=block:block'
          - FUTILE_PROFILING_DEPTH=0
          - OMP_PLACES=cores
          - OMP_PROC_BIND=true
          - SRUN_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK
          - OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
irene:
  specs:
    base:
      optional_resources:
          cores_per_node: cores_per_node
      optional_defaults:
          cores_per_node: 128
      host: irene
    scheduler:
      resources:
        omp: -c
        time: -t
        project: -A
      required_or:
         - mpi: -n
           nodes: -N
      optional_resources:
        jobname: -r
        queue: -q
        filesystem: -m
        output: -o
        error: -e
      optional_defaults:
        jobname: job
        output: <jobname>.o
        error: <jobname>.e
        filesystem: work,scratch
        pragma: "#MSUB"
        pre_export:
         - "set -x"
         - "cd $BRIDGE_MSUB_PWD"
      submitter: ccc_msub
  flavours:
    gnu:
      pre_load:
         - module purge
      load:
         - gnu/8.3.0
         - mpi/openmpi/4.0.5
         - mkl
         - python3
         - cmake
         - hdf5/1.8.20
    oneapi:
      pre_load:
          - module purge
      load:
          - inteloneapi
          - mpi/intelmpi
          - python3
          - cmake
          - mkl/23.1.0
    frontend:
      pre_load:
          - module purge
      load:
          - python3

  environments:
    1.9.4-gnu:
      queue: rome
      post_export:
          - "source $PREFIX/bin/bigdftvars.sh"
      export:
          - PREFIX=/ccc/work/cont003/drf/genovesl/binaries/bigdft-gnu-1.9.4-2/install
          - OMPI_MCA_orte_base_help_aggregate=0
          - OMPI_MCA_coll="^ghc,tuned"
          - MKL_DEBUG_CPU_TYPE=5
          - BIGDFT_MPIRUN=ccc_mprun
          - FUTILE_PROFILING_DEPTH=0
          - OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    1.9.4-intel:
      queue: rome
      post_export:
          - "source $PREFIX/bin/bigdftvars.sh"
      export:
          - PREFIX=/ccc/work/cont003/drf/genovesl/binaries/1.9.4-oneapi2/install
          - MKL_DEBUG_CPU_TYPE=5
          - BIGDFT_MPIRUN=ccc_mprun
          - FUTILE_PROFILING_DEPTH=0
          - OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    1.9.5-intel:
      queue: rome
      post_export:
          - "source $PREFIX/bin/bigdftvars.sh"
      export:
          - PREFIX=/ccc/work/cont003/drf/genovesl/binaries/1.9.4-oneapi3/install
          - MKL_DEBUG_CPU_TYPE=5
          - BIGDFT_MPIRUN=ccc_mprun
          - FUTILE_PROFILING_DEPTH=0
          - OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    1.9.5-intel-tcdft:
      queue: rome
      post_export:
          - "source $PREFIX/bin/bigdftvars.sh"
      export:
          - PREFIX=/ccc/work/cont003/drf/genovesl/binaries/1.9.4-oneapi4/install
          - MKL_DEBUG_CPU_TYPE=5
          - BIGDFT_MPIRUN=ccc_mprun
          - FUTILE_PROFILING_DEPTH=0
          - OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK



leonardo:
  specs:
    base:
      optional_resources:
          cores_per_node: cores_per_node
          gpus_per_node: gpus_per_node
      optional_defaults:
          cores_per_node: 32
          gpus_per_node: 4
      host: leonardo
    scheduler:
      resources:
        omp: -c
        time: -t
      required_or:
         - mpi: -n
           nodes: -N
      optional_resources:
        account: --account=
        partition: -p
        jobname: -J
        queue: -q
        output: -o
        error: -e
        gpu: "--gres=gpu:"
        memory: --mem=
      optional_defaults:
        account: Max3_devel_2
        partition: boost_usr_prod
        memory: 300000
        jobname: job
        output: <jobname>.o
        error: <jobname>.e
        pragma: "#SBATCH"
      submitter: sbatch
  flavours:
    frontend:
      load:
         - python/3.10.8--gcc--8.5.0
    nvhpc:
      load:
         - nvhpc/23.1
         - openmpi/4.1.4--nvhpc--23.1-cuda-11.8
         - python/3.10.8--gcc--8.5.0
         - cuda/11.8
    gnu:
      load:
         - openmpi/4.1.4--gcc--11.3.0-cuda-11.8
         - python/3.10.8--gcc--11.3.0
         - cuda/11.8
         - intel-oneapi-mkl/2022.2.1
  environments:
    1.9.4-nvhpc:
      post_export:
          - "source $PREFIX/bin/bigdftvars.sh"
      export:
          - PREFIX=/leonardo_work/Max3_devel_2/bigdft/1.9.4-nvhpc
          - BIGDFT_MPIRUN=srun
          - FUTILE_PROFILING_DEPTH=0
          # - OMP_PLACES=cores
          # - OMP_PROC_BIND=true
          - SRUN_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK
          - OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
    1.9.4-gnu:
      post_export:
          - "source $PREFIX/bin/bigdftvars.sh"
      export:
          - PREFIX=/leonardo_work/Max3_devel_2/bigdft/1.9.4-gnu
          - BIGDFT_MPIRUN=srun
          - FUTILE_PROFILING_DEPTH=0
          # - OMP_PLACES=cores
          # - OMP_PROC_BIND=true
          - SRUN_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK
          - OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
          - MKL_NUM_THREADS=$OMP_NUM_THREADS

"""


def get_host_specs(host=None, uri=None, **extra_platform_kwargs):
    """Retrieve the dictionary of the spec and resources of a computer.

    With this function the specification of a host are retrieved.
    A dictionary which presents the available platforms and applications
    is then provided. 

    The platform dictionary can be employed for the instantiation
    of a `py:class:remotemanager:Computer` class, whereas the application
    dictionary can be used in the dataset runner arguments
    (globally or locally).

    Arguments:
        host (str): the name of the yaml file containing the specification.

        uri (str): path of the directory where the yaml files are defined.

        **extra_platform_kwargs (dict): dictionary of extra arguments which can be
            employed to update the platform dictionary. This is useful to specify
            the hostname or the project to be employed in the platform instantiation

    Returns: 
        tuple: (platforms, applications) the dictionary of
                the platforms and of the applications available for this host.
    """
    from yaml import load, Loader
    from os.path import abspath, realpath, join, dirname
    if uri is None:
        basedir = abspath(dirname(realpath(__file__)))
    else:
        basedir = uri
    with open(join(basedir, host+'.yaml')) as ifile:
        hostname_dict = load(ifile, Loader=Loader)
    platforms = {}
    employed_keys = ['platforms']
    for platform, cargs in hostname_dict['platforms'].items():
        employed_keys.append(platform)
        kwargs = {k:v for k, v in cargs.items() if k != 'kwargs'}
        for kwarg, key in cargs.get('kwargs',{}).items():
            employed_keys.append(key)
            kwargs[kwarg] = hostname_dict[key]
        kwargs.update(extra_platform_kwargs)
        platforms[platform] = {k:v for k, v in kwargs.items()}

    applications = {k: v for k, v in hostname_dict.items()
                    if k not in employed_keys}

    return platforms, applications


def get_computer_resources(host=None, computer_spec=None, flavour=None, environment=None):
    """Retrieve the dictionary of the computer resources.

    This function is usefut to retrieve the arguments to be employed
    to update the resources on a computer which is related to the same host.

    Args:
        host(str): the name of the computer from the database.
            Could be None if ``computer_spec`` is specified.

        flavour(str): the set of modulefiles to be loaded expressed by the
            key of the ``flavours`` field. Could be None if not necessary.
            Ignored when `host` is None.
        environment(str): the set of export variables to be loaded expressed by the
            key of the ``environments`` field.
            If set to None, the frontend computer is returned.
        computer_spec (dict): Specifications that can be provided in alternative to `host`.

    Returns:
        dict: the dictionary of kwargs that can be passed to `update_resources`.

    """
    computer = {}
    if host is not None:
        computer = get_host_specs(host)

    if computer_spec is not None:
        computer.update(computer_spec)

    resources_dict = {}
    if flavour is not None:
        resources_dict.update(computer['flavours'][flavour])
    if environment is not None:
        resources_dict.update(computer['environments'][environment])

    return resources_dict


def get_computer_specs(host=None, action='submit', computer_spec={}):
    """Retrieve a instance of a BaseComputer to be used as URL.

    The dictionary of ``computers`` is employed as a database to
    create the instance.

    Args:
        host(str): the name of the computer from the database.
            Could be None if ``computer_spec`` is specified.
        computer_spec (dict): Extra specifications which can override the
            previous data.
        action (str): can be 'compile', 'submit', 'push_to_remote', 'update'.
        **kwargs: other arguments for the Basecomputer instantiation.

    Returns:
        tuple: the specs, kwargs arguments that can be passed to the
            ``computer_from_specs```function.

    """

    specs = [] if action == 'submit' else [frontend_environment]

    if action == 'compile':
        specs.append(compilation)
    if action == 'push_to_remote':
        specs.append(git_remote_branch)
        specs.append(git_push_localhost)
    if action == 'update':
        specs.append(git_remote_branch)
        specs.append(git_update)

    spec_dict = {}
    if host is not None:
        computer = get_host_specs(host)

        if action == 'submit':
            computer_spec_update(spec_dict, computer['specs']['scheduler'])

        computer_spec_update(spec_dict, computer['specs']['base'])

    computer_spec_update(spec_dict, computer_spec)
    return specs, spec_dict


def get_computer(host=None, flavour=None, environment=None, computer_spec={}, **kwargs):
    """Retrieve a instance of a BaseComputer to be used as URL.

    The dictionary of ``computers`` is employed as a database to
    create the instance.

    Args:
        host(str): the name of the computer from the database.
            Could be None if ``computer_spec`` is specified.
        flavour(str): the set of modulefiles to be loaded expressed by the
            key of the ``flavours`` field. Could be None if not necessary.
            Ignored when `host` is None.
        environment(str): the set of export variables to be loaded expressed by the
            key of the ``environments`` field.
            If set to None, the frontend computer for compilation is returned.
        computer_spec (dict): Extra specifications which can override the
            previous data.
        **kwargs: other arguments for the Basecomputer instantiation.

    Returns:
        BaseComputer: The class instance, ready for usage.

    """

    if host is None and len(computer_spec) == 0:
        raise ValueError('Host or computer_spec should be present')

    action = 'submit' if environment is not None else 'compile'
    specs, spec_dict = get_computer_specs(host=host, action=action,
                                          computer_spec=computer_spec)

    cp = computer_from_specs(specs, **spec_dict)(**kwargs)

    resources_dict = get_computer_resources(host=host, computer_spec=computer_spec,
                                            flavour=flavour, environment=environment)
    cp.update_resources(**resources_dict)

    return cp


def recompile_locally(asynchronous=False, **kwargs):
    """Commodity function to recompile locally.

    Useful for systems where the code is installed in `$BIGDFT_ROOT`
    and the sources are in `$BIGDFT_SUITE_SOURCES`

    Args:
        asynchronous (bool): do not wait for the compilation to finish
        **kwargs: the args of code_compiler

    Returns:
        str, Dataset: the output of the compilation or the compilation Dataset,
           if `asynchronous` is False or True respectively.

    """
    from os import environ, path, pardir
    from futile.Utils import kw_pop
    kwargs_tmp, builddir = kw_pop('builddir',
                                  path.abspath(path.join(environ['BIGDFT_ROOT'],pardir, pardir)),
                                  **kwargs)
    kwargs_tmp, action = kw_pop('action',
                                'buildone -f pybigdft',
                                **kwargs_tmp)
    ds = code_compiler(builddir=builddir, **kwargs_tmp)
    ds.append_run(action=action)
    ds.run(asynchronous=asynchronous)
    if not asynchronous:
        ds.fetch_results()
        output = ds.results[0]
        errors = ds.errors[0]
        ds.hard_reset()
        return '\n'.join([output, 'Errors:', errors])
    else:
        return ds
