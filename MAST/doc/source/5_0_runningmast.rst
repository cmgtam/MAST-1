###################
Running MAST
###################

*************************
General notes
*************************
Depending on your cluster, you might find it polite to *nice* your processes::

    nice -n 19 mast -i input.inp
    nice -n 19 mast

Nice-ing allows the headnode to put its regular functions before the mast processes. MAST should start running within several seconds.

*************************
Inputting an input file
*************************
To parse an input file, use ::

    mast -i input.inp

or ::

    mast -i //full/path/to/input/file/myinput.inp

If your input file specifies any POSCAR or CIF files, those files must be in your current working directory at the time you call MAST.

The input file will be parsed and a recipe directory should be created inside the ``$MAST_SCRATCH`` directory, with the appropriate ingredient subdirectories.

Look at the ``personalized_recipe.txt``, ``input.inp``, ``archive_input_options.txt``, and ``archive_recipe_plan.txt`` files in the recipe directory to see if the setup agrees with what you think it should be.

*********************
Running MAST
*********************

Running MAST is separate from inputting input files. Use this command::

    mast

This command will do two things:

1.  Submit all ingredient runs listed in the ``$MAST_CONTROL/submitlist`` list to the queue. 

    *  The submission command (``sbatch``, ``qsub``, etc.) is based on the platform chosen when you ran ``python $MAST_INSTALL_PATH initialize.py`` during installation.
    *  The exact commands can be found in ``$MAST_INSTALL_PATH/submit/platforms/<platform name>/queue_commands.py``.
    *  If you make changes to that ``queue_commands.py`` file, run ``python $MAST_INSTALL_PATH initialize.py`` again.

Individual ingredients' submission scripts are created automatically through a combination of the ``$ingredients`` section in the input file, and your the template submission script for your platform 

    *  The template submission script is found in ``$MAST_INSTALL_PATH/submit/platforms/<platform name>/submit_template.sh``). 
    *  If you make changes to the template, run ``python $MAST_INSTALL_PATH initialize.py`` again. 

2.  Spawn a MAST monitor, or *mastmon*, process on the queue. 

*  Your ``$MAST_INSTALL_PATH/submit/platforms/<platform name>/mastmon_submit.sh`` script is responsible for submitting this process.
*  The script should be set up to use the shortest, fastest turnover queue available (e.g. a serial queue with a maximum walltime of 4 hours, or morganshort on bardeen).
*  If you make changes to the script, run ``python $MAST_INSTALL_PATH initialize.py`` again. 
 
The mastmon process will generate additional entries on ``$MAST_CONTROL/submitlist``, but these entries will not be submitted to the queue until MAST is called again.

=======================
The MAST monitor
=======================

The MAST monitor, or mastmon, process goes through the ``$MAST_SCRATCH`` directory. It looks at the folders there, which are recipe directories. For each recipe directory, the MAST monitor builds a .recipe plan. from a combination of the input.inp file, the personal_recipe.txt file, and the status.txt file. It then uses the recipe plan to assess the next steps appropriate for the recipe.

For human troubleshooting of a recipe, the archive_recipe_plan.txt file gives information about which ingredients are parents/children of which other ingredients, and which method each parent should use to update each of its child ingredients.

The status.txt files gives the status of each ingredient.

Ingredient statuses are:

*  I = initialized: The ingredient has just been created from inputting the input file, but nothing has been run.

*  W = waiting: The ingredient is waiting for parents to complete before it can be staged.

*  S = staged: All parents have updated this child, but the run is not yet ready to run

*  P = proceed: The ingredient has written its input files, all parents have updated it, and its run method has been called. The run method usually adds the ingredient to the list at ``$MAST_CONTROL/submitlist``, to be submitted to the queue the next time mast is called. There is no MAST status change between an ingredient proceeding to the submitlist and being submitted to the queue off of the submitlist. However, ``$MAST_CONTROL/submitted`` can be used to see which ingredients were just submitted to the queue.

*  C = complete: The ingredient is complete

*  E = error: The ingredient has errored out, and ``mast_auto_correct`` was set to False in the input file (the default is True)

*  skip = skip: You can set ingredients to skip in the status.txt file by manually editing the file.

The MAST monitor checks the status of all ingredients whose status is not yet complete. The MAST monitor updates each ingredient status in the recipe plan. 

Each ingredient is checked to see if it is complete (this is a redundant fast-forward check, since sometimes it is useful to copy over previously completed runs into a MAST ingredient directory.)

If complete, the ingredient updates its children and is changed to Complete

For each Initialized ingredient:

*  If the ingredient has any parents, it is given status Waiting
*  Otherwise, it is given status Staged

For each Proceed-to-run ingredient:

*  If the ingredient is now complete, it updates its children and is changed to Complete

For each Waiting ingredient:

*  If all parents are now marked complete, the ingredient is changed to Staged

For each Staged ingredient:

*  If the ingredient is not already ready to run, its write method is called for it to write its input files.
*  The ingredient.s run method is called, which usually adds its folder to ``$MAST_CONTROL/submitlist``, except in the case of special run methods like run_defect (to induce a defect)
*  The ingredient.s status is changed to Proceed.

When all ingredients in a recipe are complete, the entire recipe folder is moved from ``$MAST_SCRATCH`` to ``$MAST_ARCHIVE``

=====================
The CONTROL folder
=====================

The ``$MAST_CONTROL`` folder houses several files:

*  errormast: Contains any queue errors from running the MAST monitor on the queue
*  mastoutput: Contains all queue output from running the MAST monitor on the queue, including a printout of the ingredient statuses for all recipes in the $MAST_SCRATCH directory
*  submitlist: The list of all ingredient folders to be submitted to the queue
*  submitted: A list of all ingredients submitted to the queue the last time the MAST monitor ran
*  mast.log and archive.<timestamp>.log: contains MAST runtime information

Every file except ``submitlist`` can be periodically deleted to save space.

The ``errormast`` file is written when there is an error, and will need to be deleted for MAST to continue running.

======================
The SCRATCH folder
======================

The ``$MAST_SCRATCH`` folder houses all recipe folders. It also houses a ``mast.write_files.lock`` file while the MAST monitor is running, in order to prevent several versions of MAST from running at once and simultaneously checking and writing ingredients.

*  Occasionally, MAST may report that it is locked. If there is no *mastmon* process running or queued on the queue, you may delete the ``mast.write_files.lock`` file manually.

-------------------------------------------------------------------------
Skipping recipes or ingredients in the SCRATCH folder
-------------------------------------------------------------------------

If a certain recipe has some sort of flaw, or if you want to stop tracking it halfway through, you may have MAST skip over this recipe:

* Create an empty (or not, the contents don.t matter) file named MAST_SKIP in the recipe directory. 
* Go through $MAST_CONTROL/submitlist and delete all ingredients associated with that recipe to keep them from being submitted during the next MAST run.

If you would like to skip certain ingredients of a single recipe, edit the recipe's status.txt file and replace ingredients to be skipped with the status *skip* (use the whole word).

*  To un-skip these ingredients, set them back to W for waiting for parents in status.txt. 

    *  **Be careful if deleting any files for skipped ingredients.**
    *  **Do not delete the metadata.txt file.**
    *  **If deleting a file that was obtained from a parent, like a POSCAR file, also set the parent ingredient back to P when you un-skip the child ingredient.**

*  No recipe can be considered complete by MAST if it includes skipped ingredients. However, if you consider the recipe complete, you can move the entire recipe directory out of ``$MAST_SCRATCH`` and into ``$MAST_ARCHIVE`` or another directory.

===========================
The ARCHIVE folder
===========================

When all ingredients in a recipe are complete, the entire recipe directory is moved from ``$MAST_SCRATCH`` to ``$MAST_ARCHIVE``.

*********************************
Running MAST repeatedly
*********************************

The command ``mast`` needs to be run repeatedly in order to move the status of the recipe forward. In order to run mast automatically, use a crontab. 

Important notes:

*  Some clusters may not allow the use of cron. Please check the cluster policy before setting up cron.

*  Be ready for a lot of notification emails. Crontab on a well-behaved system should send you an email each time it runs, giving you what would have been the output on the screen.

*  Include ``. $HOME/.bashrc`` or a similar line to get your MAST environment variables and your usual path setup.

Crontab commands are as follows:

*  ``crontab -e`` to edit your crontab
*  ``crontab -l`` to view your crontab
*  ``crontab -r`` to remove your crontab

This crontab line will run mast every hour at minute 15, and is usually suitable for everyday use::

    15 * * * * . $HOME/.bashrc; nice -n 19 mast

This crontab line will run mast every 15 minutes and is ONLY suitable for short testing::

    */15 * * * * . $HOME/.bashrc; nice -n 19 mast

