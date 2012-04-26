#!/usr/bin/env python
"""
Analyse results using pandas

"""

import os
import os.path as op
import sys
from glob import glob
import re

import pandas
import matplotlib.pyplot as plt
from matplotlib import rcParams

from dapbench.nmon import NmonOutput

RAMP_SLICES = [15,30,60,120,240,480,720,1440]

rcParams['legend.fontsize'] = 'small'


class Run(object):
    """
    Analyse the results of a run stored in a single logdirectory
    """

    def __init__(self, logdir, label=None):
        self.logdir = logdir
        self._read_data()

        if label is not None:
            self.label = label
        else:
            mo = re.match(r'.*run-(\d+)ms$', logdir)
            self.label = int(mo.group(1))

    def _read_data(self):
        concats = {}
        cc_keys = {}

        for test, target, datafile in self._find_datafiles():
            df = results_to_df(datafile)
            if test not in concats:
                concats[test] = [df['Test']]
                cc_keys[test] = ['Test']

            concats[test].append(df['Test time'])
            cc_keys[test].append(target)

        self.results = {}
        for test in concats:
            self.results[test] = pandas.concat(concats[test], keys=cc_keys[test], axis=1)

        self._read_nmon()

    def mean(self):
        ret = {}
        for test in self.results:
            ret[test] = self.results[test].groupby('Test').mean()

        return ret

    def _find_datafiles(self):
        for logfile in os.listdir(self.logdir):
            mo = re.match(r'data_(.*)-(.*)-0.log', logfile)
            if mo:
                test, target = mo.groups()
                yield (test, target, op.join(self.logdir, logfile))

    def _read_nmon(self):
        try:
            nmon_file = glob(op.join(self.logdir, '*.nmon'))[0]
        except IndexError:
            self.nmon = None
        else:
            self.nmon = NmonOutput(nmon_file)
        



class RunSet(object):
    """
    A collection of runs with common targets.
    """
    
    def __init__(self):
        self.runs = []
        
    def add(self, run):
        self.runs.append(run)

    def mean(self, test):
        means = []
        for run in self.runs:
            df = run.mean()[test]
            df.columns = pandas.MultiIndex.from_tuples([(run.label, x) for x in df.columns])
            means.append(df)

        return pandas.concat(means, axis=1)


class ResultView(object):
    """
    A view on a RunSet that exposes partucular results.

    Abstract base class.

    """
    test = None
    
    def __init__(self, runset):
        self.runset = runset
        self._setup()
        self._gather()

    def _setup(self):
        pass
        
    def _gather(self):
        """
        Gather all tests, calling self.add_result() for each result
        """
        for run in self.runset.runs:
            for test, result in run.results.items():
                if self._is_viewed(run.label, test, result):
                    self._add_result(run.label, test, result)

    def _is_viewed(self, run_label, test, result):
        return test == self.test

    def _add_result(self, run_label, test, result):
        raise NotImplementedError
    
    def frame(self):
        raise NotImplementedError

    def plot(self):
        raise NotImplementedError

class BasicDownloadView(ResultView):
    test = 'basic_download'

    def _setup(self):
        self.means = []

    def _add_result(self, run_label, test, result):
        df = result.drop(['Test'], axis=1)
        df.columns = pandas.MultiIndex.from_tuples([(run_label, x) for x in df.columns])
        self.means.append(df.mean())

    def frame(self):
        return pandas.concat(self.means).unstack()

    def plot(self, **kwargs):
        f = self.frame()
        # Scale to seconds
        f = f / 1000
        ax = f.plot(style='o-', **kwargs)
        ax.set_xlabel('Server delay (ms)')
        ax.set_ylabel('Download time (s)')
        ax.set_title('Basic Download test')
        return ax


class DownloadView(BasicDownloadView):
    test2 = 'ramp_slices'

    def _is_viewed(self, run_label, test, result):
        return test in [self.test, self.test2]

    def _add_result(self, run_label, test, result):
        if test == self.test:
            super(self.__class__, self)._add_result(run_label, test, result)
        elif test == self.test2:
            df = result[result['Test'] <= 3].groupby('Test').sum().stack()
            df.index = pandas.MultiIndex.from_tuples([(run_label, '%s_%d' % (b, a)) for (a, b) in df.index])
            self.means.append(df)
        else:
            raise ValueError("unknown test %s" % test)

class RampSlicesView(ResultView):
    test = 'ramp_slices'

    def _setup(self):
        self.totals = []

    def _add_result(self, run_label, test, result):
        df = result.groupby('Test').mean()
        df.columns = pandas.MultiIndex.from_tuples([(run_label, x) for x in df.columns])
        self.totals.append(df)

    def frame(self):
        return pandas.concat(self.totals, axis=1).select(lambda x: x>100)

    def plot(self, **kwargs):
        f = self.frame()
        # Change index to number of slices
        f.index = RAMP_SLICES
        # Scale values to seconds
        f = f / 1000
        ax = f.select(lambda (x, y): y=='pydap', axis=1).plot(style='o-', **kwargs)
        f.select(lambda (x, y): y=='tds', axis=1).plot(style='o--', ax=ax, **kwargs)
        ax.set_ylabel('Time to download (s)')
        ax.set_xlabel('Number of slices')
        ax.set_title('Ramp slices test')
        return ax


class ParallelSlicesView(ResultView):
    test = 'parallel_slices'

    def _setup(self):
        self.data = []
        
    def _add_result(self, run_label, test, result):
        df = result.drop(['Test'], axis=1)
        df.columns = pandas.MultiIndex.from_tuples([(run_label, x) for x in df.columns])
        self.data.append(df)

    def frame(self):
        return pandas.concat(self.data, axis=1)

    def plot(self, **kwargs):
        f = self.frame()
        f = f / 1000
        sample = [0, 10, 20, 40]
        f = f.select(lambda (x, y): x in sample, axis=1)
        fig = plt.figure()
        g = f.groupby(level=0, axis=1)
        for delay in g.groups:
            i = sample.index(delay)+1
            ax = fig.add_subplot(2, 2, i)
            ax.set_title('%dms delay' % delay)
            if i in [3, 4]:
                ax.set_xlabel('Request duration (s)')
            if i in [1, 4]:
                ax.set_ylabel('# requests')
            for key in g.groups[delay]:
                f[key].hist(axes=ax, range=(0, 10), bins=50,
                            histtype='step',
                            label=key[1],
                            **kwargs
                    )
            ax.legend()
        return fig



def results_to_df(grinder_datafile):
    df1 = pandas.read_csv(grinder_datafile, sep=r',\s*')
    df2 = pandas.DataFrame(df1, columns=['Test', 'Test time'])

    return df2



def read_data(logdir):
    test_results = {}

    for logfile in os.listdir(logdir):
        mo = re.match(r'data_(.*)-(.*)-0.log', logfile)
        if mo:
            print '== %s' % logfile
            test, server = mo.groups()
            df = results_to_df(op.join(logdir, logfile))
            entry = test_results.setdefault(test, {})
            entry[server] = df.groupby('Test').mean()['Test time']

    frames = {}
    for result in test_results:
        frames[result] = pandas.DataFrame(test_results[result])

    return frames



if __name__ == '__main__':
    import sys

    parent_dir, = sys.argv[1:]
    
    rs = RunSet()

    for logdir in os.listdir(parent_dir):
        rs.add(Run(op.join(parent_dir, logdir)))

    basic_download_view = BasicDownloadView(rs)
    ramp_view = RampSlicesView(rs)
    parallel_view = ParallelSlicesView(rs)
    download_view = DownloadView(rs)
