#!/usr/bin/env python
"""
Process results using matplotlib.

"""

import numpy

def read_grinder_data(fh, test):
    """
    Read a data_*.log file for a particular test.

    Returns (t0, dt, errors) where t0 is the array of start times from
    start of test and dt is the array of test durations.

    """
    header = fh.readline().split(', ')
    assert header[0] == 'Thread'

    t0 = []
    dt = []
    start_t = None
    errors = 0
    for line in fh:
        (thread, run, test1, start, 
         duration, error) = (int(x) for x in line.split(', '))

        if test != test1:
            continue
        if thread != 1:
            continue

        if error:
            errors += 1
            continue
        if start_t is None:
            start_t = start
            start = 0
        else:
            start = start - start_t
    
        t0.append(start)
        dt.append(duration)

    return numpy.array(t0), numpy.array(dt), errors


def plot_parallel(plotprefix):
    import pylab

    hyrax_t0, hyrax_dt, e = read_grinder_data(open('data_hyrax_parallel.log'), 1)
    pydap_t0, pydap_dt, e = read_grinder_data(open('data_pydap_parallel.log'), 1)
    tds_t0, tds_dt, e = read_grinder_data(open('data_tds_parallel.log'), 1)
    
    pylab.figure()
    pylab.title('Parallel request distribution')
    pylab.hist(tds_dt, bins=100, range=(0, 400), label='tds')
    pylab.hist(pydap_dt, bins=100, range=(0, 400), label='pydap')
    pylab.hist(hyrax_dt, bins=100, range=(0, 400), label='hyrax')
    pylab.legend()
    pylab.xlabel('Request duration (ms)')
    pylab.ylabel('Frequency')
    pylab.savefig(plotprefix+'_fd.png')

    pylab.figure()
    pylab.title('Cumulative request distribution')
    pylab.hist((tds_t0+tds_dt)/1000, bins=len(tds_t0), 
               cumulative=True, 
               label='tds', histtype='step')
    pylab.hist((pydap_t0+pydap_dt)/1000, bins=len(pydap_t0), 
               cumulative=True, 
               label='pydap', histtype='step')
    pylab.hist((hyrax_t0+hyrax_dt)/1000, bins=len(hyrax_t0), 
               cumulative=True, 
               label='hyrax', histtype='step')
    pylab.legend(loc='upper left')
    pylab.xlabel('Time Elapsed (s)')
    pylab.ylabel('Cumulative frequency')
    pylab.savefig(plotprefix+'_cd.png')

    pylab.figure()
    pylab.title('Parallel request timeseries')
    pylab.plot(tds_t0, tds_dt, label='tds')
    pylab.plot(pydap_t0, pydap_dt, label='pydap')
    pylab.plot(hyrax_t0, hyrax_dt, label='hyrax')
    pylab.legend()
    pylab.ylim(0, 500)
    pylab.xlabel('Time from start (ms)')
    pylab.ylabel('Request duration (ms)')
    pylab.savefig(plotprefix+'_ts.png')

if __name__=='__main__':
    plot_parallel('parallel')
