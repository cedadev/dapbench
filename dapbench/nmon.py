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

class NmonOutput(object):
    def __init__(self, filename):
        self._streams = {}
        self._read_data(open(filename))

    def _read_data(self, fh):
        reader = csv.reader(fh)
        for row in reader:
            stream_name = row.pop(0)
            
            if stream_name in self._streams:
                header, data = self._streams[stream_name]
                data.append(row)
            else:
                # row is header
                self._streams[stream_name] = (row, [])

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
