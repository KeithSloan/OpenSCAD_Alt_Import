# Update 1.0.2 (branch `Fix17103`)

Fixes for SCAD/CSG import problems reported in FreeCAD issues
[#17103](https://github.com/FreeCAD/FreeCAD/issues/17103) and
[#20192](https://github.com/FreeCAD/FreeCAD/issues/20192).

## Fixes

### Empty CSG operations - `union();`

OpenSCAD writes an operation that has no children as `name(...);`, for example
`union();`. BOSL2 based models produce many of these. The CSG grammar did not
accept them, the syntax errors were silently ignored and the parser discarded
parts of the tree, leaving objects detached from their transforms.

* The grammar now accepts empty `union`, `difference`, `intersection`, `hull`,
  `minkowski`, `multmatrix`, `color`, `render`, `linear_extrude`, `offset`,
  `resize`, `projection` and `rotate_extrude`.
* Empty `difference`, `intersection`, `multmatrix` and `offset` no longer leave
  an undefined result on the parse stack.
* CSG syntax errors are now always reported in the Report view, with the line
  number.

### Hull

* Hull objects were given a group view provider although they are not groups.
  Drawing the Model tree then raised
  `ExtensionContainer::getExtension: No extension of given type available`;
  on macOS that aborts FreeCAD (no Report view output).
* Documents saved with hulls from earlier versions are repaired when reopened.
* Hull of two parallel cylinders of equal radius no longer gives a null shape;
  circles use the object's own axis, and the hull is extruded along it.

### DXF - ezdxf only

FreeCAD's own DXF importer/exporter is no longer used or attempted. It needs
separately downloaded DXF libraries and stops to ask for them.

* `text()` and 2D shapes sent to OpenSCAD (e.g. `hull` / `minkowski` of 2D
  objects) are written and read with **ezdxf**.
* If ezdxf is not installed the import stops with an error saying so. Install it
  with the Addon Manager (Python dependency of this addon).
* OpenSCAD 2025 writes R12 DXF files with `LWPOLYLINE` entities that lack the
  `AcDbPolyline` subclass marker. `ezdxf.recover` rejects these, so the reader
  falls back to `ezdxf.readfile`.
* `text()` arguments with the value `"default"` (written by newer OpenSCAD) are
  no longer passed back to OpenSCAD.

### Other

* The OpenSCAD executable is found in its standard install location if the
  preference is not set (a new FreeCAD version starts with a new `user.cfg`).
* `minkowski` works without the GUI (`freecadcmd`).
* Much less console output during import.
* `package.xml` version 1.0.2.

## Test cases

In `testCases`:

| File | Exercises |
|------|-----------|
| `Micro_8088_Case_Modular.scad` (+ `ISA_Brackets.scad`) | text, minkowski, hull, linear_extrude, colour, large CSG tree. From [skiselev/micro_8088_case](https://github.com/skiselev/micro_8088_case), GPL-3.0 |
| `runTests.py` | Regression runner |
| `README.md` | Test case sources and licences |

Not included (licence), tested when copied into `testCases`:

| File | Exercises |
|------|-----------|
| `Keyring Container v2.1.scad` / `Keyring_Container_v2.1.scad` | BOSL2: empty `union();`, textured polyhedra, threads, hull. Needs BOSL2 in the OpenSCAD library path |
| `pegboard.scad` | hull of cylinders, rotate_extrude, colour ([michaelmob/openscad-models](https://github.com/michaelmob/openscad-models/blob/master/pegboard.scad) and a variant) |

`runTests.py` checks each model imports with no syntax errors or exceptions,
as one top level object with a valid shape, whose volume is within 1% of the
volume OpenSCAD reports (OpenSCAD uses facets, FreeCAD true circles).

Run from the FreeCAD Python console

    exec(open('<addon folder>/testCases/runTests.py').read())

or headless

    freecadcmd <addon folder>/testCases/runTests.py

## Testing

macOS (Apple silicon), OpenSCAD 2025.03.10, GUI import with the addon installed
as a real folder (git clone) in the user `Mod` folder.

| | FreeCAD 1.1.4 | FreeCAD 26.3rc2 |
|-|---------------|-----------------|
| Build | Python 3.11.14, ezdxf 1.4.3 | 26.3.0 20261018, Python 3.13.15, OCCT 8.0.1, ezdxf 1.4.5 |
| `Micro_8088_Case_Modular.scad` | PASS - 1,056,933.7 (OpenSCAD 1,056,930.9) | PASS - 1,056,933.7 |
| `Keyring Container v2.1.scad` | PASS - 1,490.62 (OpenSCAD 1,490.83) | PASS - 1,490.62 |
| `pegboard.scad` (variant) | PASS - 9,891.9 (OpenSCAD 9,876.1) | PASS - 9,886.2 |

Reference volumes: keyring and pegboard from OpenSCAD 2025.03.10 renders on
the same machine; Micro 8088 from OpenSCAD 2021.01 (the value in `runTests.py`).

All imports gave one top level object, no CSG syntax errors, no crash, and
FreeCAD's DXF importer was not loaded. On 26.3rc2 a saved pegboard document
reopened with its Python features (`RefineShape`) restored.

Also tested on Linux with `runTests.py` under `freecadcmd`, FreeCAD 1.1.3
(OCCT 7.9.3, Python 3.11) and the 26.3 development build of 2026-09-16
(OCCT 8.0.1, Python 3.13), OpenSCAD 2021.01 and BOSL2 master: all three test
cases pass on both (pegboard here is the michaelmob version, 22,071.2 against
OpenSCAD 22,032.8).

## Notes

* **Symlinked addon on FreeCAD 26.3:** when reopening a saved document, 26.3
  blocks loading the addon's Python classes if the addon folder in `Mod` is a
  symlink (`blocked import of module ... during document restore`). Install the
  addon as a real folder. Imports themselves are not affected.
* **Addon Manager installs a zip by default** (folder `Alternate_OpenSCAD`, with
  `AM_INSTALLATION_DIGEST.txt`, no `.git`). To have it install with git, set the
  string parameter `force_git_in_repos` in `BaseApp/Preferences/Addons` to
  `parts_library,Alternate_OpenSCAD` and reinstall.
* **One copy only:** the addon's modules have plain names (`importAltCSG`,
  `OpenSCADHull`, ...). With two copies installed, whichever is first on the
  Python path is used. Disable extra copies with an empty `ADDON_DISABLED` file.
