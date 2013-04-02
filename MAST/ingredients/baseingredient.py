from MAST.utility import MASTObj

class BaseIngredient(MASTObj):
    def __init__(self, allowed_keys, **kwargs):
        allowed_keys_base = dict()
        allowed_keys_base.update(allowed_keys) 
        MASTObj.__init__(self, allowed_keys_base, **kwargs)
        #self.logger    = logger #keep this space
        self.structure = dict() 
    
    def get_structure_from_parent(self, parentpath):
        if self.keywords['program'] == 'vasp':
            from MAST.ingredients.checker import vasp_checker
            return vasp_checker.get_structure_from_parent(parentpath)
        else:
            print "Program not recognized (in get_structure_from_parent)"
            return None

    def generate_input(self):
        '''writes the files needed as input for the jobs'''

    def is_complete(self):
        '''Function to check if Ingredient is ready'''

    def images_complete(self):
        '''Checks if all images in an NEB calculation are complete.'''
        if self.keywords['program'] == 'vasp':
            from MAST.ingredients.checker import vasp_checker
            return vasp_checker.images_complete(self.keywords['dir_name'],self.keywords['images'])
        else:
            print "Program not recognized (in images_complete)"
            return None