############################################################################
# MAterials Simulation Toolbox (MAST)
# Version: January 2013
# Programmers: Tam Mayeshiba, Tom Angsten, Glen Jenness, Hyunwoo Kim,
#              Kumaresh Visakan Murugan, Parker Sear
# Created at the University of Wisconsin-Madison.
# Replace this section with appropriate license text before shipping.
# Add additional programmers and schools as necessary.
############################################################################
import os
import numpy as np

from pymatgen.core.sites import PeriodicSite
from pymatgen.core.structure import Structure
from pymatgen.core.structure_modifier import StructureEditor
from pymatgen.util.coord_utils import find_in_coord_list
from pymatgen.io.vaspio import Poscar

from MAST.utility import MASTObj
from MAST.utility import MASTError
from MAST.ingredients.baseingredient import BaseIngredient


class InduceDefect(BaseIngredient):
    def __init__(self, **kwargs):
        #TTM move allowed_keys into __init__ and match order of other sections
        allowed_keys = {
            'name' : (str, str(), 'Name of optimization directory'),
            'program': (str, str(), 'DFT program, e.g. "vasp"'),
            'program_keys': (dict, dict(), 'Dictionary of program keywords'),
            'child_dict': (dict, dict(), 'Dictionary of children'),
            'structure': (Structure, None, 'Pymatgen Structure object')
            }
        BaseIngredient.__init__(self, allowed_keys, **kwargs)

        #print 'Initializing InduceDefect'
        #if (self.keywords['coordtype'] == 'cartesian'):
        #    self.keywords['position'] = self._cart2frac(self.keywords['position'])

    def induce_defect(self, base_structure, defect, coord_type, threshold):
        """Creates a defect, and returns the modified structure
            mast_defect is a dictionary like this: 
            'defect_1': {'symbol': 'cr', 'type': 'interstitial', 
                        'coordinates': array([ 0. ,  0.5,  0. ])}}
            'defect_2': {'symbol': 'o', 'type': 'vacancy', 
                        'coordinates': array([ 0.25,  0.25,  0.25])}
            'coord_type': 'fractional' 
        """
        #base_structure = self.get_new_structure()
        #base_structure = self.keywords['structure']
        #print 'Defect in induce_defect', defect
        #print 'base_structure in induce_defect', base_structure
        struct_ed = StructureEditor(base_structure) #should be updated using get_new_structure)
        symbol = defect['symbol'].title() #Cap first letter

        # If we have cartesian coordinates, then we convert them to fractional here.
        if ('cartesian' in coord_type):
            defect['coordinates'] = self._cart2frac(defect['coordinates'])

        if (defect['type'] == 'vacancy'):
            print 'Creating a %s vacancy at %s' % (symbol, str(defect['coordinates']))

            #print defect['coordinates']
            index = find_in_coord_list(base_structure.frac_coords,
                                       defect['coordinates'],
                                       atol=threshold)
            #print base_structure.frac_coords
            #print 'Index of deleted atom is', index
            struct_ed.delete_site(index)
        elif (defect['type'] == 'interstitial'):
            print 'Creating a %s interstitial at %s' % (symbol, str(defect['coordinates']))

            struct_ed.append_site(symbol,
                                  defect['coordinates'],
                                  coords_are_cartesian=False,
                                  validate_proximity=True)
        elif (defect['type'] in ['antisite', 'substitution']):
            print 'Creating a %s antisite at %s' % (symbol, str(defect['coordinates']))

            index = find_in_coord_list(base_structure.frac_coords,
                                       defect['coordinates'],
                                       atol=threshold)

            struct_ed.replace_site(index, symbol)
        else:
            raise RuntimeError('Defect type %s not supported' % defect['type'])

        return struct_ed.modified_structure

    def _cart2frac(self, position):
        """Converts between cartesian coordinates and fractional coordinates"""
        fractional =  self.keywords['structure'].lattice.get_fractional_coords(position)
        for i in range(len(fractional)):
            if (fractional[i] < 0.0):
                fractional[i] += 1.0
            elif (fractional[i] > 1.0):
                fractional[i] -= 1.0
        return fractional

    def write_files(self):
        name = self.keywords['name']
        print "write_files:", name
        self.get_new_structure()

        defect_label = 'defect_' + name.split('/')[-1].split('_')[-1]
        self.metafile.write_data('debug', [name, name.split('/')])
        defect = self.keywords['program_keys'][defect_label]
        #print 'Defect in write_files:', defect

        base_structure = self.keywords['structure'].copy()
        for key in defect:
            if 'subdefect' in key:
                subdefect = defect[key]
                base_structure = self.induce_defect(base_structure, subdefect, defect['coord_type'], defect['threshold'])
                #base_structure = modified_structure
            else:
                pass

        if self.keywords['program'].lower() == 'vasp':
            #myposcar = Poscar(modified_structure)
            myposcar = Poscar(base_structure)
            #print "poscar OK"
            self.lock_directory()
            #print "lock OK"
            myposcar.write_file(name + '/CONTCAR')
            #print "Write sucessful"
            self.unlock_directory()
            #print "Unlock sucessful"
        else:
            raise MASTError(self.__class__.__name__, "Program %s not supported." % self.keywords['program'])

        return
    
    def is_ready_to_run(self):
        if self.directory_is_locked():
            return False
        if self.keywords['program'].lower() == 'vasp':
            if os.path.exists(self.keywords['name'] +'/POSCAR'):
                return True
            else:
                return False
        else:
            raise MASTError(self.__class__.__name__, "Program %s not supported." % self.keywords['program'])

    def run(self, mode='noqsub'):
        if self.is_ready_to_run():
            self.write_files()
        return True

    def is_complete(self):
        if self.directory_is_locked():
            return False
        if self.keywords['program'].lower() == 'vasp':
            if os.path.exists(self.keywords['name'] +'/CONTCAR'):
                return True
            else:
                return False
        else:
            raise MASTError(self.__class__.__name__, "Program %s not supported." % self.keywords['program'])

    def update_children(self):
        for childname in self.keywords['child_dict'].iterkeys():
            self.forward_parent_structure(self.keywords['name'], childname)

    def get_new_structure(self):
        if self.keywords['program'].lower() == 'vasp':
            if os.path.isfile(self.keywords['name'] + "/POSCAR"):
                myposcar = Poscar.from_file(self.keywords['name'] + "/POSCAR")
                self.keywords['structure'] = myposcar.structure
        else:
            raise MASTError(self.__class__.__name__, "Program %s not supported." % self.keywords['program'])
        return
    
    def get_my_number(self):
        """For defect in the format <sys>_induce_defect<N>, return N.
        """
        tempname = self.keywords['name'].lower()
        numstr = tempname[tempname.find("defect")+6:]
        if numstr.find("defect") == -1:
            pass
        else:
            numstr = numstr[numstr.find("defect")+6:] #allow 'defect' to be in <sys>
        defectnum = int(numstr)
        return defectnum

