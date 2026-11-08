# -*- coding: utf8 -*-
#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2026 Keith Sloan <keith@sloan-home.co.uk>               *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#***************************************************************************
'''
Regression tests for the Alternate OpenSCAD importer (SCAD -> CSG -> FreeCAD)

Run headless :   freecadcmd <path>/testCases/runTests.py
or in the GUI :  exec(open('<path>/testCases/runTests.py').read())

Needs the OpenSCAD executable (preference or a standard install location).
Test files that need a library (e.g. BOSL2) must find it via OPENSCADPATH
or OpenSCAD's own library folder; missing test files are skipped.

Each test imports the .scad file and checks
  - no CSG syntax errors and no exception during the import
  - a single top level object (everything consumed by the CSG tree)
  - that object has a valid shape whose volume is within a tolerance of
    the volume OpenSCAD itself reports for the same model
    (OpenSCAD uses facets, FreeCAD true circles - hence the tolerance)
'''
import FreeCAD
import os
import sys
import time
import traceback

# name : (reference volume from OpenSCAD's own mesh, relative tolerance)
TESTS = {
    'Micro_8088_Case_Modular.scad' : (1056930.93, 0.01),
    'Keyring_Container_v2.1.scad'  : (1490.81, 0.01),
    'pegboard.scad'                : (22032.8, 0.01),
}


def testDir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.path.join(FreeCAD.getUserAppDataDir(), 'Mod',
                            'OpenSCAD_Alt_Import', 'testCases')


def runTest(path, refVolume, tol):
    import importAltCSG
    syntaxErrors = []
    originalError = importAltCSG.p_error

    def countingError(p):
        syntaxErrors.append(p)
        originalError(p)

    importAltCSG.p_error = countingError
    problems = []
    start = time.time()
    doc = None
    try:
        doc = importAltCSG.open(path)
    except Exception as e:
        problems.append(f'exception {type(e).__name__}: {e}')
        traceback.print_exc()
        doc = FreeCAD.ActiveDocument
    finally:
        importAltCSG.p_error = originalError
    elapsed = time.time() - start

    if syntaxErrors:
        problems.append(f'{len(syntaxErrors)} CSG syntax errors')
    summary = ''
    if doc is not None:
        doc.recompute()
        roots = [o for o in doc.Objects if not o.InList]
        if len(roots) != 1:
            problems.append(f'{len(roots)} top level objects, expected 1')
        if roots:
            shape = getattr(roots[0], 'Shape', None)
            if shape is None or shape.isNull():
                problems.append('top level shape is null')
            else:
                volume = shape.Volume
                summary = f'volume {volume:.3f}'
                if not shape.isValid():
                    problems.append('top level shape is not valid')
                if refVolume is not None and \
                        abs(volume - refVolume) > tol * refVolume:
                    problems.append(f'volume {volume:.3f} differs from '
                                    f'OpenSCAD {refVolume} by more than '
                                    f'{tol * 100:.1f}%')
    status = 'FAIL' if problems else 'PASS'
    print(f'{status} {os.path.basename(path)} ({elapsed:.1f}s) {summary}')
    for problem in problems:
        print(f'     {problem}')
    return not problems


def runTests():
    print(f'FreeCAD {".".join(FreeCAD.Version()[:3])}, '
          f'Python {sys.version.split()[0]}')
    results = []
    for name, (refVolume, tol) in TESTS.items():
        path = os.path.join(testDir(), name)
        if not os.path.exists(path):
            print(f'SKIP {name} (file not present)')
            continue
        results.append(runTest(path, refVolume, tol))
    print(f'{results.count(True)} passed, {results.count(False)} failed')
    return all(results)


runTests()
