# Test cases

## SCAD import regression tests

`runTests.py` imports each test model with the alternate importer
(SCAD → OpenSCAD → CSG → FreeCAD) and checks that

* there are no CSG syntax errors or exceptions during the import,
* the result is a single top level object (nothing left detached from its transforms),
* that object has a valid shape whose volume is within 1% of the volume
  OpenSCAD reports for the same model.

Run it headless

    freecadcmd ~/Library/Application\ Support/FreeCAD/v26-3/Mod/OpenSCAD_Alt_Import/testCases/runTests.py

or from the FreeCAD Python console

    exec(open('<path to addon>/testCases/runTests.py').read())

The OpenSCAD executable is taken from the OpenSCAD preferences, or found in
its standard install location. Test files that are not present are skipped.

| File | Exercises | Source / licence |
|------|-----------|------------------|
| `Micro_8088_Case_Modular.scad` (+ `ISA_Brackets.scad`) | text, minkowski, hull, linear_extrude, colour, large CSG tree | [skiselev/micro_8088_case](https://github.com/skiselev/micro_8088_case/tree/master/printed), GPL-3.0-or-later, Sergey Kiselev. From [FreeCAD #20192](https://github.com/FreeCAD/FreeCAD/issues/20192) |
| `Keyring_Container_v2.1.scad` (not included) | BOSL2: empty `union();` nodes, textured polyhedra, threads, hull | Darren Faulke (Autistech), CC BY-NC-SA 4.0. Needs [BOSL2](https://github.com/BelfrySCAD/BOSL2) on `OPENSCADPATH`. From [FreeCAD #17103](https://github.com/FreeCAD/FreeCAD/issues/17103) |
| `pegboard.scad` (not included) | hull of cylinders, rotate_extrude, colour | [michaelmob/openscad-models](https://github.com/michaelmob/openscad-models/blob/master/pegboard.scad) (PEGSTR, Marius Gheorghescu); no licence stated. From [FreeCAD #17103](https://github.com/FreeCAD/FreeCAD/issues/17103) |

The keyring and pegboard models are listed in `runTests.py` and are tested
when copied into this folder.

## Other files

`testbend_*` and `testImport.scad` are test data for the DXF / SVG import paths.
