from custodian.vasp import handlers
from pymatgen.core.structure import Structure
import inspect
import os
import logging
from MAST.ingredients.errorhandler import BaseError
class GenericError(BaseError):
    """Generic error-handling functions 
    """
    def __init__(self, **kwargs):
        allowed_keys = {
            'name' : (str, str(), 'Name of directory'),
            'program_keys': (dict, dict(), 'Dictionary of program keywords'),
            'structure': (Structure, None, 'Pymatgen Structure object')
            }
        BaseError.__init__(self, allowed_keys, **kwargs)

    def loop_through_errors(self):
        """Loop through all errors in the error handlers.
        """
        errct = 0
        return errct
    