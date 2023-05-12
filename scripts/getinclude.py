#! /usr/bin/env python
#
#
# C++ Insights, copyright (C) by Andreas Fertig
# Distributed under an MIT license. See LICENSE for details
#
#------------------------------------------------------------------------------

import os
import sys
import subprocess
import re

def main():
    cxx = sys.argv[1] if len(sys.argv) == 2 else 'g++'
    cmd = [cxx, '-E', '-x', 'c++', '-v', '/dev/null']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    m = re.findall(b'\n (/.*)', stderr)

    includes = ''.join(
        f'-isystem{os.path.normpath(x.decode())} '
        for x in m
        if x.find(b'(framework directory)') == -1
    )
    print(includes)

    return 1
#------------------------------------------------------------------------------

sys.exit(main())
#------------------------------------------------------------------------------
