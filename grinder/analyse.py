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

RUNS = [
    ('run-0ms', 0),
        ('run-5ms', 5),
    ('run-10ms', 10),
    ('run-15ms', 15),
    ('run-20ms', 20),
    ]

class DapbenchRun(object):
    """
    Analyse the results of a run stored in a single logdirectory
    """

    def __init__(self, logdir, label=None):
        self.logdir = logdir
        self._read_data()

        if label:
            self.label = label
        else:
            mo = re.match(r'.*run-(.*)$', logdir)
            self.label = mo.group(1)

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



class DapbenchRunset(object):
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
    rs = DapbenchRunset()
    for logdir, label in RUNS:
        rs.add(DapbenchRun(logdir, label))

    M = rs.mean('ramp_slices')
