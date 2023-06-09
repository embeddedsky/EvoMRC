'''raw_reader.py is the work of user snmishra on the blog Grok Circuits (grokcircuits.com).
It was tweaked by Rachel Sassella for use in interpreting Ngspice-produced rawfiles.'''
from __future__ import division
import numpy as np
BSIZE_SP = 512 # Max size of a line of data; we don't want to read the
               # whole file to find a line, in case file does not have
               # expected structure.
MDATA_LIST = [b'title', b'date', b'plotname', b'flags', b'no. variables',
              b'no. points', b'dimensions', b'command', b'option']

def rawread(fname):
    """Read ngspice binary raw files. Return tuple of the data, and the
    plot metadata. The dtype of the data contains field names. This is
    not very robust yet, and only supports ngspice.
    >>> darr, mdata = rawread('test.py')
    >>> darr.dtype.names
    >>> plot(np.real(darr['frequency']), np.abs(darr['v(out)']))
    """
    # Example header of raw file
    # Title: rc band pass example circuit
    # Date: Sun Feb 21 11:29:14  2016
    # Plotname: AC Analysis
    # Flags: complex
    # No. Variables: 3
    # No. Points: 41
    # Variables:
    #         0       frequency       frequency       grid=3
    #         1       v(out)  voltage
    #         2       v(in)   voltage
    # Binary:

    # if there isn't fname, I need to return something else
    ############
    # this snippet of code is the only alteration by R. Sassella to the original raw_reader.py
    try:
        fp = open(fname, 'rb')
    except:
        return (None, None)
    ##############
    plot = {}
    count = 0
    array= np.zeros((5,5), dtype=float)
    plots = []
    while (True):
        try:
            #mdata = fp.readline(BSIZE_SP).split(b':', maxsplit=1)
            mdata = fp.readline(BSIZE_SP).split(b':', 1)
        except:
            raise
        if len(mdata) == 2:
            if mdata[0].lower() in MDATA_LIST:
                plot[mdata[0].lower()] = mdata[1].strip()
            if mdata[0].lower() == b'variables':
                nvars = int(plot[b'no. variables'])
                npoints = int(plot[b'no. points'])
                plot['varnames'] = []
                plot['varunits'] = []
                for varn in range(nvars):
                    varspec = (fp.readline(BSIZE_SP).strip()
                               .decode('ascii').split())
                    assert(varn == int(varspec[0]))
                    plot['varnames'].append(varspec[1])
                    plot['varunits'].append(varspec[2])

            if mdata[0].lower() == b'values':
                nvars = int(plot[b'no. variables'])
                npoints = int(plot[b'no. points'])
                arrs = np.zeros((nvars, npoints),dtype=float)
                for i in range(int(plot[b'no. points'])):
                    for j in range(int(plot[b'no. variables'])):
                        Line=fp.readline()
                        if j==0:
                            Line=Line.split(b'\t',1)[1]
                        Line=Line.strip()
                        arrs[j][i]=Line
                    fp.readline()
                array = arrs
        else:
            break
    fp.close()

    return (array, plots)

if __name__ == '__main__':
    arrs, plots = rawread('test.raw')


# Local Variables:
# mode: python
# End:
