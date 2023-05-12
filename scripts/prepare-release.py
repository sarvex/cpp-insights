#! /usr/bin/env python3
#
#
# C++ Insights, copyright (C) by Andreas Fertig
# Distributed under an MIT license. See LICENSE for details
#
#------------------------------------------------------------------------------

import re
import os
import subprocess
#------------------------------------------------------------------------------

def main():
    versionH = open('version.h.in', 'r').read()

    oldClangStable = '14'
    newClangStable = '15'
    newInsightsVersion = '0.10'
    oldInsightsVersion = re.search(
        'INSIGHTS_VERSION\s+"(.*?)"', versionH, re.DOTALL | re.MULTILINE
    )[1]


    print('Preparing a new release:')
    print(f' Current Clang stable      : {oldClangStable}')
    print(f' New Clang stable          : {newClangStable}')
    print(f' Current Insights version  : {oldInsightsVersion}')
    print(f' New Insights version      : {newInsightsVersion}')

    print('  - Updating .github/workflows/ci.yml')
    travis = open('.github/workflows/ci.yml', 'r').read()

    regEx = re.compile('[clang|llvm]-([0-9]+)')

    travis = re.sub('(clang|llvm|clang\+\+|llvm-config|llvm-toolchain-bionic|clang-format|clang-tidy|llvm-toolchain-trusty)(-%s)' %(oldClangStable), '\\1-%s' %(newClangStable) , travis)
    travis = re.sub(
        f'(clang|Clang|llvm|LLVM) ({oldClangStable})',
        '\\1 %s' % (newClangStable),
        travis,
    )
    travis = re.sub(
        f"(LLVM_VERSION=)('{oldClangStable})",
        r"\1'%s" % (newClangStable),
        travis,
    )
    travis = re.sub(r"(LLVM_VERSION:)\s*(%s.0.0)" %(oldClangStable), r"\1 %s.0.0" %(newClangStable) , travis)
    travis = re.sub(r'(llvm_version:\s*)("%s)(.0.0",)' %(oldClangStable), '\\1"%s.0.0",' %(newClangStable), travis)
    travis = re.sub(f"clang({oldClangStable})0", f"clang{newClangStable}0", travis)
    travis = re.sub(
        f"(llvm-toolchain-xenial)-({oldClangStable})",
        r"\1-%s" % (newClangStable),
        travis,
    )
    travis = re.sub(
        f"(./llvm.sh) ({oldClangStable})", r"\1 %s" % (newClangStable), travis
    )

#    print(travis)
    open('.github/workflows/ci.yml', 'w').write(travis)


    print('  - Updating CMakeLists.txt')
    cmake = open('CMakeLists.txt', 'r').read()
    cmake = re.sub('(set\(INSIGHTS_MIN_LLVM_MAJOR_VERSION)( %s)\)' %(oldClangStable), '\\1 %s)' %(newClangStable) , cmake)
    open('CMakeLists.txt', 'w').write(cmake)


    print(f'  - Updating version.h {oldInsightsVersion} -> {newInsightsVersion}')
    version = open('version.h.in', 'r').read()
    version = re.sub('(INSIGHTS_VERSION )"(.*)"', '\\1"%s"' %(newInsightsVersion) , version)
    open('version.h.in', 'w').write(version)


    print('  - Generating CHANGELOG.md')
    os.system(
        f'gren changelog --override --username=andreasfertig --repo=cppinsights {oldInsightsVersion}...continous'
    )

    cmd = [
        'gren',
        'changelog',
        '--override',
        '--username=andreasfertig',
        '--repo=cppinsights',
        f'{oldInsightsVersion}...continous',
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    if p.returncode != 0:
        print('ERR: gren failed')
        print(stderr)
        return 1

    changeLog = open('CHANGELOG.md', 'r').read()
    changeLog = re.sub('(## Continuous build.*?---)\n', '', changeLog, flags=re.DOTALL)
    open('CHANGELOG.md', 'w').write(changeLog)

    gitTag = f'v_{oldInsightsVersion}'
    print(f'  - Tagging {gitTag}')

    #cmd = ['git', 'tag', '-a', '-m', gitTag, gitTag, 'main']
    cmd = ['git', 'tag', gitTag, 'main']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    if p.returncode != 0:
        print('ERR: git tag failed!')
        print(stderr)
        return 1

    cppInsightsDockerBaseFile = '../cppinsights-docker-base/Dockerfile'

    print(f'  - Updating cppinsights-docker-base ({cppInsightsDockerBaseFile})')

    dockerFile = open(cppInsightsDockerBaseFile, 'r').read()
    dockerFile = re.sub('(ENV\s+CLANG_VERSION=)([0-9]+)', r'\g<1>%s' %(newClangStable), dockerFile)
    open(cppInsightsDockerBaseFile, 'w').write(dockerFile)
#------------------------------------------------------------------------------

main()
#------------------------------------------------------------------------------

