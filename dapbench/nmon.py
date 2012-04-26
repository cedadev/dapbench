# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
Utilities for processing nmon output.

"""

import csv
import pandas
import datetime as DT

import matplotlib.pyplot as plt

DATETIME_FORMAT = '%H:%M:%S %d-%b-%Y'
TIMESTEP_STREAM = 'ZZZZ'

INCLUDE_STREAMS = [
    'DISKXFER',
    'DISKREAD',
    'MEM',
    #'CPU02',
    #'CPU01',
    'VM',
    'DISKBUSY',
    'DISKWRITE',
    'CPU_ALL',
    'NET',
    'PROC',
    #'JFSFILE',
    #'NETPACKET',
    'DISKBSIZE'
 ]

class NmonOutput(object):
    def __init__(self, filename):
        self._streams = {}
        self._timesteps = {}
        self._read_data(open(filename))

    def _read_data(self, fh):
        reader = csv.reader(fh)
        for row in reader:
            stream_name = row.pop(0)

            # timesteps are special
            if stream_name == TIMESTEP_STREAM:
                self._process_timestep(row)

            # skip unwanted streams
            if stream_name not in INCLUDE_STREAMS:
                continue

            if stream_name in self._streams:
                header, data = self._streams[stream_name]
                trow = self._apply_timestep(row)
                data.append(trow)
            else:
                # row is header
                self._streams[stream_name] = (row, [])

    def _process_timestep(self, data):
        label, time, day = data
        self._timesteps[label] = DT.datetime.strptime('%s %s' % (time, day), DATETIME_FORMAT)

    def _apply_timestep(self, row):
        # first item in row is assumed to be a timestep label
        if row[0] in self._timesteps:
            return [self._timesteps[row[0]]] + row[1:]
        else:
            return row

    def get_header(self, stream_name):
        return self._streams[stream_name][0]

    @property
    def streams(self):
        return self._streams.keys()

    def get_col(self, stream_name, column, filter=None):
        header, data = self._streams[stream_name]
        i = header.index(column)
        for row in data:
            if filter:
                yield filter(row[i])
            else:
                yield row[i]

    def as_dict(self, stream_name):
        header, data = self._streams[stream_name]
        cols = zip(*data)
        D = dict(zip(header, cols))
        return D

    def _filter_dataframe(self, stream_name, dataframe):
        #!TODO: make this method into some sort of callout per stream
        if stream_name == 'CPU_ALL':
            return dataframe.drop(['Busy', 'CPUs'], axis=1)
        elif stream_name == 'MEM':
            return dataframe[['memfree', 'cached', 'memtotal']]
        elif stream_name == 'NET':
            return dataframe[['eth0-read-KB/s', 'eth0-write-KB/s']]
        elif stream_name == 'DISKREAD':
            return dataframe['xvdb']
        else:
            return dataframe


    def as_dataframe(self, stream_name):
        df = pandas.DataFrame.from_dict(self.as_dict(stream_name))
        df = df.set_index(self.get_header(stream_name)[0])
        return self._filter_dataframe(stream_name, df)

    def plot(self, **kwargs):
        #streams = ['DISKREAD', 'MEM', 'CPU_ALL', 'NET']
        streams = ['MEM', 'CPU_ALL', 'NET']
        fig = plt.figure(figsize=(10,3))
        for i, stream in enumerate(streams):
            ax = fig.add_subplot(1, 3, i+1)
            ax.set_title(stream)
            df = self.as_dataframe(stream)
            df.plot(ax=ax, **kwargs)
