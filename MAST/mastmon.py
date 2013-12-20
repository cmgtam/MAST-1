import os
import time
import shutil
import logging
from MAST.utility import MASTError
from MAST.utility import dirutil
from MAST.utility import loggerutils
from MAST.parsers.inputparser import InputParser
from MAST.recipe.recipesetup import RecipeSetup


class MASTmon(object):
    """The MAST monitor runs on a submission node and checks
        the status of each recipe in the MAST_SCRATCH directory.
        Attributes:
            self.scratch <str>: MAST_SCRATCH
            self._ARCHIVE <str>: MAST_ARCHIVE
            self.logger <logging logger>
            self.loggerdict <dictionary of recipe-level loggers>
    """ 
    def __init__(self):

        self.scratch = dirutil.get_mast_scratch_path()
        self._ARCHIVE = dirutil.get_mast_archive_path()
        self.make_directories() 
        self.loggerdict=dict()
        self.logger = loggerutils.initialize_short_logger(os.path.join(os.getenv("MAST_CONTROL"),"mast.log"))
        self.logger.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        self.logger.info("\nMAST monitor started at %s.\n" % time.asctime())
        self.logger.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        self.run(1)

    def make_directories(self):
        """Attempt to make scratch and archive directories
            if they do not exist.
        """
        try:
            if not os.path.exists(self.scratch):
                os.makedirs(self.scratch)
            if not os.path.exists(self._ARCHIVE):
                os.makedirs(self._ARCHIVE)
        except:
            raise MASTError(self.__class__.__name__,
                    "Error making directory for MASTmon and completed recipes")

    def check_recipe_dir(self, fulldir, verbose):
        """Check a recipe directory.
            Args:
                fulldir <str>: full path of recipe directory
                verbose <int>: verbosity
        """
        shortdir = os.path.basename(fulldir) #only the recipe directory name
        if not os.path.exists(fulldir):
            raise MASTError(self.__class__.__name__, "No recipe directory at %s" % fulldir)
        self.loggerdict[fulldir] = loggerutils.initialize_logger(os.path.join(fulldir, "mast_recipe.log"))
        if os.path.exists(os.path.join(fulldir, "MAST_SKIP")):
            self.logger.warning("Skipping recipe %s due to the presence of a MAST_SKIP file in the recipe directory." % shortdir)
            return
        if os.path.exists(os.path.join(fulldir, "MAST_ERROR")):
            self.logger.error("ATTENTION!: Skipping recipe %s due to the presence of a MAST_ERROR file in the recipe directory." % shortdir)
            return
        self.logger.info("--------------------------------")
        self.logger.info("Processing recipe %s" % shortdir)
        self.logger.info("--------------------------------")
        os.chdir(fulldir) #need to change directories in order to submit jobs?
        myipparser = InputParser(inputfile=os.path.join(fulldir, 'input.inp'))
        myinputoptions = myipparser.parse()
        rsetup = RecipeSetup(recipeFile=os.path.join(fulldir,'personal_recipe.txt'),
                inputOptions=myinputoptions,
                structure=myinputoptions.get_item('structure','structure'),
                workingDirectory=fulldir)
        recipe_plan_obj = rsetup.start()
        recipe_plan_obj.get_statuses_from_file()
        try:
            recipe_plan_obj.check_recipe_status(verbose)
        except Exception:
            import sys,traceback
            ex_type, ex, trbck = sys.exc_info()
            errortext = traceback.print_tb(trbck)
            del trbck
            raise MASTError(self.__class__.__name__,"Error in recipe %s as follows: %s %s %s" % (shortdir, ex_type, ex, errortext))
        os.chdir(self.scratch)
        if recipe_plan_obj.status == "C":
            shutil.move(fulldir, self._ARCHIVE)
        self.logger.info("-----------------------------")
        self.logger.info("Recipe %s processed." % shortdir)
        self.logger.info("-----------------------------")


    def run(self, verbose=0):
        """Run the MAST monitor.
        """
        curdir = os.getcwd()
        try:
            os.chdir(self.scratch)    
        except:
            os.chdir(curdir)
            errorstr = "Could not change directories to MAST_SCRATCH at %s" % self.scratch
            raise MASTError(self.__class__.__name__, errorstr)
        
        #dirutil.lock_directory(self.scratch, 1) # Wait 5 seconds
        #Directory is now locked by mast initially, but gets
        #unlocked at the end of the mastmon run.
        
        recipe_dirs = dirutil.walkdirs(self.scratch,1,1)
        if verbose == 1:
            self.logger.info("================================")
            self.logger.info("Recipe directories:")
            for recipe_dir in recipe_dirs:
                self.logger.info(recipe_dir)
            self.logger.info("================================")

        for recipe_dir in recipe_dirs:
            self.check_recipe_dir(recipe_dir, verbose)
                
        dirutil.unlock_directory(self.scratch) #unlock directory
        os.chdir(curdir)