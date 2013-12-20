import os
import shutil
import logging
from MAST.utility import MASTObj
from MAST.utility import MASTError
from MAST.utility import dirutil
from MAST.utility import Metadata
from MAST.utility import loggerutils
from pymatgen.core.structure import Structure
from pymatgen.io.vaspio import Poscar
from pymatgen.io.cifio import CifParser

class BaseChecker(MASTObj):
    """Base checker class. This class switches between
        program-specific functions.
        For example, phon-related functions or vasp-related
        functions get their own checker class.
    """
    
    def __init__(self, allowed_keys, **kwargs):
        allowed_keys_base = dict()
        allowed_keys_base.update(allowed_keys) 
        MASTObj.__init__(self, allowed_keys_base, **kwargs)
        try:
            self.logger = logging.getLogger(os.path.join(os.path.dirname(self.keywords['name']),"mast_recipe.log"))
        except: #if no logger is found, may be in subfolder. Move up one level.
            self.logger = logging.getLogger(os.path.join(os.path.dirname(os.path.dirname(self.keywords['name'])),"mast_recipe.log"))

    
    def is_complete(self):
        raise NotImplementedError
    def is_started(self):
        raise NotImplementedError
    def is_ready_to_run(self):
        raise NotImplementedError
    def get_coordinates_only_structure_from_input(self):
        """Get coordinates-only structures from mast_coordinates
            ingredient keyword
            Args:
                keywords <dict>: ingredient keywords
            Returns:
                coordstrucs <list>: list of Structure objects
        """
        coordposlist=self.keywords['program_keys']['mast_coordinates']
        coordstrucs=list()
        coordstruc=None
        for coordpositem in coordposlist:
            if ('poscar' in os.path.basename(coordpositem).lower()):
                coordstruc = Poscar.from_file(coordpositem).structure
            elif ('cif' in os.path.basename(coordpositem).lower()):
                coordstruc = CifParser(coordpositem).get_structures()[0]
            else:
                error = 'Cannot build structure from file %s' % coordpositem
                raise MASTError(self.__class__.__name__, error)
            coordstrucs.append(coordstruc)
        return coordstrucs
    def softlink_a_file(self, childpath, filename):
        """Softlink a parent file to a matching name in the child folder.
            Args:
                childpath <str>: path to child ingredient
                filename <str>: file name (e.g. "CHGCAR")
        """
        parentpath = self.keywords['name']
        dirutil.lock_directory(childpath)
        import subprocess
        #print "cwd: ", os.getcwd()
        #print parentpath
        #print childpath
        if os.path.isfile("%s/%s" % (parentpath, filename)):
            if not os.path.isfile("%s/%s" % (childpath, filename)):
                curpath = os.getcwd()
                os.chdir(childpath)
                mylink=subprocess.Popen("ln -s %s/%s %s" % (parentpath,filename,filename), shell=True)
                mylink.wait()
                os.chdir(curpath)
            else:
                self.logger.warning("%s already exists in %s. Parent %s not softlinked." % (filename,childpath,filename))
        else:
            raise MASTError(self.__class__.__name__,"No file in parent path %s named %s. Cannot create softlink." % (parentpath, filename))
        dirutil.unlock_directory(childpath)
    
    def copy_a_file(self, childpath, pfname, cfname):
        """Copy a parent file to an arbitrary name in the child folder.
            Args:
                childpath <str>: path to child ingredient
                pfname <str>: file name in parent folder (e.g. "CONTCAR")
                cfname <str>: file name for child folder (e.g. "POSCAR")
        """
        parentpath = self.keywords['name']
        dirutil.lock_directory(childpath)
        if os.path.isfile("%s/%s" % (parentpath, pfname)):
            if not os.path.isfile("%s/%s" % (childpath, cfname)):
                shutil.copy("%s/%s" % (parentpath, pfname),"%s/%s" % (childpath, cfname))
            else:
                self.logger.warning("%s already exists in %s. Parent file %s not copied from %s into child %s." % (cfname,childpath,pfname,parentpath,cfname))
        else:
            raise MASTError(self.__class__.__name__,"No file in parent path %s named %s. Cannot copy into child path as %s." % (parentpath, pfname, cfname))
        dirutil.unlock_directory(childpath)