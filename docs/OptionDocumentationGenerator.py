#! /usr/bin/env python3
#------------------------------------------------------------------------------

import sys
import argparse
import os
import re
import subprocess
import base64
#------------------------------------------------------------------------------

def runCmd(cmd, data=None):
    if input is None:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
    else:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=data)

    return stdout.decode('utf-8'), stderr.decode('utf-8'), p.returncode
#------------------------------------------------------------------------------

def getDefaultIncludeDirs(cxx):
    cmd = [cxx, '-E', '-x', 'c++', '-v', '/dev/null']
    stdout, stderr, retCode = runCmd(cmd)

    m = re.findall('\n (/.*)', stderr)

    return [f'-isystem{x}' for x in m if x.find('(framework directory)') == -1]
#------------------------------------------------------------------------------

def replaceSource(match):
    fileName = match.group(2)

    cpp = '<!-- source:%s.cpp -->\n' %(fileName)
    cpp += '```{.cpp}\n'
    cpp += open(f'examples/{fileName}.cpp', 'r').read().strip()
    cpp += '\n```\n'
    cpp += f'<!-- source-end:{fileName}.cpp -->'

    return cpp
#------------------------------------------------------------------------------

def cppinsightsLink(code, std='2a', options=''):
    # currently 20 is not a thing
    if std == '20':
        print('Replacing 20 by 2a')
        std = '2a'

    # per default use latest standard
    if std == '':
        std = '2a'

    std = f'cpp{std}'

    if options:
        options += f',{std}'
    else:
        options = std

    return f"https://cppinsights.io/lnk?code={base64.b64encode(code).decode('utf-8')}&insightsOptions={options}&rev=1.0"
#------------------------------------------------------------------------------

def replaceInsights(match, parser, args):
    cppFileName = f'{match.group(2)}.cpp'

    insightsPath  = args['insights']
    remainingArgs = args['args']
    defaultCppStd = f"-std={args['std']}"

    defaultIncludeDirs = getDefaultIncludeDirs(args['cxx'])
    cpp = '<!-- transformed:%s -->\n' %(cppFileName)
    cpp += 'Here is the transformed code:\n'
    cpp += '```{.cpp}\n'

    cmd = [insightsPath, f'examples/{cppFileName}', '--', defaultCppStd, '-m64']
    stdout, stderr, retCode = runCmd(cmd)

    cpp += stdout

    cppData = open(f'examples/{cppFileName}', 'r').read().strip().encode('utf-8')


    cpp += '\n```\n'
    cpp += '[Live view](%s)\n' %(cppinsightsLink(cppData))
    cpp += f'<!-- transformed-end:{cppFileName} -->'

    return cpp
#------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--insights',       help='C++ Insights binary',  required=True)
    parser.add_argument('--cxx',            help='C++ compiler to used', default='/usr/local/clang-current/bin/clang++')
    parser.add_argument('--std',            help='C++ Standard to used', default='c++17')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = vars(parser.parse_args())

    insightsPath  = args['insights']
    remainingArgs = args['args']
    defaultCppStd = f"-std={args['std']}"

    print(insightsPath)
    defaultIncludeDirs = getDefaultIncludeDirs(args['cxx'])

    for f in os.listdir('.'):
        if not f.startswith('opt-') or not f.endswith('.md'):
            continue

        optionName = os.path.splitext(f)[0][4:].strip()

        data = open(f, 'r').read()

        cppFileName = f'cmdl-examples/{optionName}.cpp'

        cpp = open(cppFileName, 'r').read().strip()

        data = data.replace(f'{optionName}-source', cpp)

        cmd = [
            insightsPath,
            cppFileName,
            f'--{optionName}',
            '--',
            defaultCppStd,
            '-m64',
        ]
        stdout, stderr, retCode = runCmd(cmd)

        data = data.replace(f'{optionName}-transformed', stdout)

        open(f, 'w').write(data)

    regEx = re.compile('(<!-- source:(.*?).cpp -->(.*?)<!-- source-end:(.*?) -->)', re.DOTALL)
    regExIns = re.compile('(<!-- transformed:(.*?).cpp -->(.*?)<!-- transformed-end:(.*?) -->)', re.DOTALL)

    for f in os.listdir('examples'):
        if not f.endswith('.md'):
            continue

        exampleName = os.path.splitext(f)[0].strip()

        mdFileName = os.path.join('examples', f'{exampleName}.md')

        mdData = open(mdFileName, 'r').read()

        mdData = regEx.sub(replaceSource, mdData)

        rpl = lambda match : replaceInsights(match, parser, args)
        mdData = regExIns.sub(rpl, mdData)

        open(mdFileName, 'w').write(mdData)

#------------------------------------------------------------------------------

sys.exit(main())
#------------------------------------------------------------------------------

