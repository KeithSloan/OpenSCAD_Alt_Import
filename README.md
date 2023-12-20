## Alternate OpenSCAD Importer

### NOTICES

Functions such as PrismaticToroid require facilities in the FreeCAD version 0.20 of Part

## Installation

It can be installed via the [Addon Manager](https://github.com/FreeCAD/FreeCAD-addons) (from Tools menu)


## Alternative Installation

Clone into FreeCAD's Mod directory see https://wiki.freecadweb.org/Installing_more_workbenches

   * Change to FreeCAD Mod directory
   * **git clone https://github.com/KeithSloan/OpenSCAD_Alt_Import.git**

* Start/Restart FreeCAD

## Now supports 

The idea to allow hybrid development ( FreeCAD and OpenSCAD )

* Importing SCAD files as FreeCAD Objects.
* Edit SCADObjects with an external editor
   
* Import of Minkowski request with a Sphere as a Part::Offset
* Import of Minkowski request with a Cylinder as Part::Offset & Part::Fillet

* **Matt Considine's** improvements utilizing python EZdxf library 
 
  * OpenSCAD DXF import
  * DXF importer
  * Now supports DXF files with INSERT tag.
  
  
### New OpenSCAD DXF importer 
  
  * For test files see directory testDXFfiles
  * Test of test files see Macro Macros/testSCAD_DXFfile.FCMacro
    ( Copy to FreeCAD Macro's directory )
  * If problems please report and drop back to main FreeCAD importer.
  * Note: If the scad file imports external files use one of
  
      New Importer : SCAD (importCSG)
      New Importer : SCADFileObject
      
  New Importer : SCADObject currently does not support import of external files    

### External Editor
  
  For a number of years OpenSCAD has supported an [External Editor](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Using_an_external_Editor_with_OpenSCAD)
  
  To use an external editor for SCADObjects
  
  You need to add a parameter to the OpenSCAD workbench
  
      FreeCAD | Tools | Edit parameters
  
      Group : Base App
          Preferences
             Mod
                OpenSCAD
                    externalEditor
                        Text : <path to editor > 
                        e.g. Text /usr/local/bin/code

### Use

With the workbench installed when opening a CSG or SCAD File with 


        FreeCAD | File | Open 

the user will be prompted with which importer to use.

![Image 20-02-2023 at 14 29](https://user-images.githubusercontent.com/2291247/220134298-944e8fe6-4ac6-4db7-b072-fe257e0b0905.jpg)

  * SCAD (ImportCSG)                : Uses OpenSCAD to convert SCAD file to CSG and then import as FreeCAD Brep Objects
  * SCADFileObject (ImportFileSCAD) : Imports as a FreeCAD SCADObject. Source remains the original file.
  * SCADObject (ImportSCAD)         : File is copied into FreeCAD and saved with FreeCAD file.
                        
  ### ImportCSG - Import CSG or SCAD file
  
  ### Changes from standard Importer

* **Minkowski**

Minkowski requests where the second object is a Sphere or Cyclinder is handled as follows

  **Sphere**
  
    $fn=50;
    minkowski()
      {
        cube([10,10,1]);
        sphere(1);
      }
    
Produces a suitable Part::Offset of the first Object i.e with rounded edges.

  ![Image 01-03-2023 at 09 04](https://user-images.githubusercontent.com/2291247/222143274-c61341f5-09ff-4485-8d94-7bdbba79f34d.jpg)

  **Cylinder**
  
    $fn=50;
    minkowski()
      {
        cube([10,10,1]);
        cylinder(r=2,h=1);
      }
      
Produces an Part::Fillet of a suitable Part::Offset of the first Object, fillet radius that of the cylinder.

![Image 01-03-2023 at 09 08](https://user-images.githubusercontent.com/2291247/222143356-2da246cf-095b-4257-af55-a2f05e0b55a6.jpg)

Where the FreeCAD has an editable Fillet

![Image 01-03-2023 at 09 09](https://user-images.githubusercontent.com/2291247/222143386-8ac5e8c4-a505-4f35-9fd6-e12202afd7ed.jpg)


* **Hull** A limited number of hull requests are converted to BREP equivalents
              
              - Collinear cylinders & cones
              - Two Spheres
              - Two Parallel Cylinders of equal length, orthogonaly displaced.
               
           others are dealt with as per standard importer i.e passed to OpenSCAD
           executable to create a Mesh
           
          
  
  ### SCADFileObject
  
  Created from imported File - Only file reference is saved with the FreeCAD Document
  
  **Properties**
  
  ![Image 20-02-2023 at 14 47](https://user-images.githubusercontent.com/2291247/220137934-2fa7cfc5-23aa-4e03-9130-b9ba89fb133c.jpg)
  
  * edit        : Toggling will invoke the external editor.
  * execute     : Will process the SCAD source ( Object or File ) to create a the Objects Shape.
  * message     : Any error messages from OpenSCAD.
  * mode        : Brep or Mesh.
  * timeout     : time out value for operations passed to OpenSCAD.
  * source      : Source file name
  * source File : Path to source file (ImportFileSCAD)
  
  #### Brep Mode
  
  OpenSCAD is used to create a CSG version that is then imported into a Work document as FreeCAD Objects.
  The Work document is processed to create/update the SCADObjects Shape as a Single Part::Compound
  
  *Brep Propertries*
  
  * fnmax     : Sets the fnmax parameter for the CSG import of this Object
  * keep_work : Option to save or close the Work document
  
  #### Mesh Mode
  
  OpenSCAD is used to create a STL version that is imported to create/update the SCADObjects Shape.
  
  *Mesh Properties*
  
  * mesh_recombine : For future option
    
  ### SCADObjects
  
  Created from imported file - Saved using JSON with the FreeCAD document
  
  For creating FreeCAD objects from SCAD source. 
  Should avoid SCAD files that depend on other files i.e. Have use or include statements.
  
  **Properties** : See SCADFileObjects properties.
  
  ### Using SCADObjects and OpenSCAD external editor.
  
  Using a combination of an external editor for SCADObjects and having OpenSCAD set up for an external editor allows.
  
  * One to edit the source for FreeCAD OpenSCAD objects
  * Preview any changes in a OpenSCAD Preview window
  * When happy with source definition
  
    * Save SCAD Source file
    * Toggle SCADObjects - execute property to have changes brought into FreeCAD

Example Screenshot.
![Image 20-02-2023 at 14 02](https://user-images.githubusercontent.com/2291247/220147105-8689b944-315c-47cc-92f7-c3806b088177.jpg)

### Advantage of using an external editor that is also setup for OpenSCAD

The performance of OpenSCAD Preview has been significantly improved since Feb 2022

[OpenSCAD 3D rendering just got an order of magnitude faster](https://ochafik.com/jekyll/update/2022/02/09/openscad-fast-csg-contibution.html)

                      
### Thanks to FreeCAD Users

* mconsidine
* wmayer
* chennes
* edwilliams16
* onekk
