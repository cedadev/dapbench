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

RUNS = ['run-0ms', 'run-20ms']

class DapbenchRun(object):
    """
    Analyse the results of a run stored in a single logdirectory
    """

    def __init__(self, logdir):
        self.logdir = logdir


    def _read_data2(self):
        self.results = {}
        for test, target, datafile in self._find_datafiles():
            self.results[(test, target)] = results_to_df(datafile)
            #!TODO: ...

    def _read_data(self):
        #!DEPRECATED
        test_results = {}
        for test, target, datafile in self._find_datafiles():
            results = test_results.setdefault(test, {})
            results[target] = results_to_df(datafile)

        # Now convert to dictionary of dataframes
        self.results = {}
        for test in test_results:
            keys = test_results[test].keys()
            values = test_results[test].values()
            self.results[test] = pandas.concat(values, keys=keys, names=('target', ))
            

    def _find_datafiles(self):
        for logfile in os.listdir(self.logdir):
            mo = re.match(r'data_(.*)-(.*)-0.log', logfile)
            if mo:
                test, target = mo.groups()
                yield (test, target, op.join(self.logdir, logfile))

    def mean(self, test):
        means = {}
        for test, target in self.


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
