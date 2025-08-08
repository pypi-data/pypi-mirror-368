import os
import shutil


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.

    Important to clean out any testing folders
    """
    print('Pre-testing setup begins')

    rundir = os.getcwd()

    avail = os.listdir(rundir)

    to_wipe = [os.path.join(rundir, fld)
               for fld in avail if fld.startswith('fake_')]

    for folder in to_wipe:
        if os.path.isdir(folder):
            print(f'\tremoving {folder}')
            shutil.rmtree(folder)

def pytest_collectstart(collector):
    if collector.fspath and collector.fspath.ext == '.ipynb':
        collector.skip_compare += 'text/html', \
                                  'application/javascript', \
                                  'stderr',
