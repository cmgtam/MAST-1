Change log
==========

Version 2.5.5
-------------

1. Bug fix release for cifio for rhombohedral structures.
2. Miscellaneous bug fixes and speedups.

Version 2.5.4
-------------
1. Vastly improved Gaussian input file parsing that supports more varieties
   of input specifications.
2. StructureNL now supports molecules as well as structures.
3. Updated atomic and vdw radius for Elements.
4. Miscellaneous bug fixes and speedups.

Version 2.5.3
-------------
1. Bug fix for StructureNotationalLanguage.
2. Support for LDA US potential. matgenie.py script option to generate POTCARs.
3. Beta version of StructureNotationLanguage, a markup format for Structure
   data with metadata such as authors and references. (Anubhav Jain)
4. Vasprun parsing now parses dielectric constant where available. (Geoffroy
   Hautier)
5. New custom ipython shell script for pymatgen.
6. Miscellaneous bug fixes and speedups.

Version 2.5.1
-------------
1. Bug fixes for primitive cell finder.
2. Remove deprecated use_external_qhull option in PhaseDiagram classes.
3. Miscellaneous bug fixes and speedups.

Version 2.5.0
-------------
1. Added optimization package with linear assignment class.
2. Improved robustness of StructureMatcher using linear assignment.
3. Improved primitive cell search (faster and more robust).
4. Cleanup of deprecated methods, including
   pymatgen.alchemy.materials.TransformedMaterial.undo/redo_last_transformation,
   pymatgen.core.site.Site.distance_and_image_old, Poscar.struct,
   StructureFitter and tests.
5. Miscellaneous bug fixes and speedups.

Version 2.4.3
-------------
1. Bug fix for StructureMatcher.
2. Miscellaneous speedups.

Version 2.4.0
-------------
1. New StructureMatcher that effectively replaces StructureFitter. Orders of
   magnitude faster and more robust. StructureFitter is now deprecated.
2. Vastly improved PrimitiveCellTransformation.
3. A lot of core methods have been rewritten to take advantage of vectorization
   in numpy, resulting in orders of magnitude improvement in speed.
4. Miscellaneous bug fixes and speedups.

Version 2.3.2
-------------
1. More utilities for working with Periodic Boundary Conditions.
2. Improved MPRester that supports more data and a new method of specifying
   the API key for heavy users via a MAPI_KEY environment variable. Please
   refer to the :doc:`usage pages </usage>` for more information.
3. Vastly improved POTCAR setup script in scripts directly that is now
   installed as part of a default pymatgen installation.
4. Miscellaneous bug fixes and speedups.

Version 2.3.1
-------------
1. Significant improvements to the high-level interface to the Materials API.
   New interface provides more options to make it easier to get structures and
   entries, better warnings and error handling. It uses the *requests*
   library for a cleaner API.
2. Bug fix for VolumetricData parsing and methods such as CHGCAR and LOCPOT.
   Previously, the parsing was done incorrectly because VASP actually provides
   data by running through the x-axis first, followed by y, then z.
3. Bug fix for reverse_readline so that it works for gzipped and bzipped
   strucutures (courtesy of Anubhav Jain).
4. Fix "lossy" composition to_dict method.  Now composition.to_dict properly
   returns a correct species string as a key for compositions using species,
   instead of just the element symbols.
5. Miscellaneous bug fixes.

Version 2.3.0
-------------
1. Remove usage of scipy and external qhull callers. Now uses pyhull package.
   Please note that this change implies that the pyhull package is now a
   required dependency. If you install pymatgen through the usual
   easy_install or pip install methods, this should be taken care of
   automatically for you. Otherwise, please look for the pyhull package on
   PyPI to download and install it.
2. Miscellaneous bug fixes.

Version 2.2.6
-------------
1. Brand new *beta* bond valence analyzer based on a Maximum A Posteriori
   algo using data-mined ICSD data.
2. Speed up and improvements to core classes.
3. Improved structure fitter (credits to Geoffroy Hautier).
4. Brand new entry_tools module (pymatgen.entries.entry_tools).
5. Vastly improved Outcar parser based on reverse parsing that speeds up
   reading of OUTCAR files by orders of magnitude.
6. Miscellaneous bug fixes.

Version 2.2.4
-------------

1. Fixed bug in hexagonal cell KPOINTS file generation.
2. New RelaxationAnalyzer to compare structures.
3. New *beta* bond valence analyzer.
4. Miscellaneous bug fixes.

Version 2.2.3
-------------

1. New filter framework for filtering structures in pymatgen.alchemy.
2. Updated feff io classes to support FEFF 9.6 and other code improvements.
3. Miscellaneous bug fixes.

Version 2.2.2
-------------

1. Bug fix release for REST interface.
2. Improvements to unittests.

Version 2.2.1
-------------

1. Improvements to feffio.
2. Master matgenie.py script which replaces many analysis scripts.
3. More memory efficient parsing of VolumetricData.
4. Beta version of structure prediction classes.
5. Changes to MPRester to work with v1 release of the Materials API.
6. Miscellaneous bug fixes and speed improvements.

Version 2.2.0
-------------

1. Beta modules (pymatgen.io.feffio) for io for FEFF, courtesy of Alan Dozier.
2. New smartio module that intelligently reads structure input files based on
   file extension.
3. Spglib_adaptor module has been renamed to finder for brevity.
4. Upgraded spglib to version 1.2.2. Improved handling of spglib install on
   Mac OS X and Solaris.
5. Major cleanup of code for PEP8 compliance.
6. Cssr module now supports reading of input files.
7. Miscellaneous bug fixes and speed improvements.

Version 2.1.2
-------------

1. Brand new CompoundPD class that allows the plotting of phase diagrams that
   do not have elements as their terminal points.
2. Spglib is now completely integrated as part of the setup.py installation.
3. Major (but completely backwards compatible) refactoring of sites and vaspio.
4. Added a EnumerateStructureTransformation with optional dependency on the enum
   library by Gus Hart. This provides a robust way to enumerate derivative
   structures,
5. Implemented LLL lattice reduction algorithm. Also added option to sanitize
   a Structure on copy.
6. Bug fix for missing Compatibility file in release distribution.
7. Vastly improved StructureFitter which performs cell reduction where necessary
   to speed up fitting.
8. Miscellaneous bug fixes and speed improvements.

Version 2.0.0
-------------

1. Brand new module (pymatgen.matproj.rest) for interfacing with the
   MaterialsProject REST interface.
2. Useful aliases for commonly used Objects, similar in style to numpy.
   Supported objects include Element, Composition, Structure, Molecule, Spin
   and Orbital. For example, the following will now work::

      import pymatgen as mg

      # Elemental Si
      fe = mg.Element("Si")

      # Composition of Fe2O3
      comp = mg.Composition("Fe2O3")

      # CsCl structure
      structure = mg.Structure(mg.Lattice.cubic(4.2), ["Cs", "Cl"],
                              [[0, 0, 0], [0.5, 0.5, 0.5]])

3. New PDAnalyzer method to generate chemical potential maps.
4. Enhanced POSCAR class to support parsing of velocities and more formatting
   options.
5. Reorganization of Bandstructure module. Beta support for projected
   bandstructure and eigenvalues in vaspio and electronic_structure.
6. Miscellaneous bug fixes and speed improvements.

Version 1.9.0
-------------

1. Completely new json encoder and decoder that support serialization of almost
   all pymatgen objects.
2. Simplification to Borg API utilizing the new json API.
3. Bandstructure classes now support spin-polarized runs.
4. Beta classes for battery (insertion and conversion) analysis.

Version 1.8.3
-------------

1. spglib_adaptor now supports disordered structures.
2. Update to support new spglib with angle_tolerance.
3. Changes to Borg API to support both file and directory style paths.
4. Speed up for COMPLETE_ORDERING algo for PartialRemoveSpecieTransformation.


Version 1.8.1
-------------

1. Revamped transmuter classes for better readability and long term support.
2. Much improved speed for PartialRemoveSpecieTransformations.
3. Misc bug fixes.

Version 1.8.0
-------------

1. Support for additional properties on Specie (Spin) and Site (magmom, charge).
2. Molecule class to support molecules without periodicity.
3. Beta io class for XYZ and GaussianInput.

Version 1.7.2
-------------

1. Bug fixes for vaspio_set and compatibility classes.

Version 1.7.0
-------------

1. Complete reorganization of modules for electronic structure.
2. Beta of band structure classes.
3. Misc improvements to vaspio classes.
4. Bug fixes.

Version 1.6.0
-------------

1. Beta of pymatgen.borg package implemented for high-throughput data assimilation.
2. Added ComputedEntry classes for handling calculated data.
3. New method of specifying VASP pseudopotential location using a VASP_PSP_DIR
   environment variable.
4. Bug fix for pymatgen.symmetry
5. Ewald sum speed up by factor of 2 or more.
