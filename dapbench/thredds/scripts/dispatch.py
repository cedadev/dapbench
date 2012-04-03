# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
Main dispatcher script for the 4 subscripts:
  1. check_url.py
  2. check_files.py
  3. check_catalog.py
  4. check_metadata.py

Execute with the first argument as 'url', 'files', 'catalog' or 'metadata' to execute
the required script.

"""

import sys
import os.path as op

from check_url import main as url_main
from check_files import main as files_main
from check_catalog import main as catalog_main
from check_metadata import main as metadata_main

USAGE = '''\
Usage: %(prog)s command [options] [args]

Where command is:
  %(commands)s
'''

COMMANDS = {'url': url_main, 
            'files': files_main, 
            'catalog': catalog_main, 
            'metadata': metadata_main,
            }

def usage():
    print USAGE % dict(prog=op.basename(sys.argv[0]), commands=' '.join(COMMANDS.keys()))


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    command = sys.argv[1]
    if command not in COMMANDS:
        usage()
        sys.exit(1)

    # Fake argv[0] and dispatch
    argv0 = '%s %s' % (sys.argv[0], command)
    sys.argv = [argv0] + sys.argv[2:]
    
    COMMANDS[command]()

if __name__ == '__main__':
    main()
