#############################
What's new in version 1.3.0
#############################

**Additions:**

* A STEM image processing addition has been added to structopt. See **NO TAG YET**
* A charge-density-based pathfinding method has been added as an alternative to linear interpolation for NEBs. See **NO TAG YET**
* An optional atom indexing feature has been implemented for structures which are expected to undergo significant atomic relaxation when relaxed and/or defected. See :doc:`3_1_1_structure`.
* A 14-frequency concentrated diffusion model has been added to the Diffusion Coefficient post-processing tool. See :doc:`6_0_postprocessingtools`.
* The new MAST "modify recipe" function allows existing recipes to be modified. See :doc:`5_0_runningmast`.

**Fixes:**


**Changes for users:**

* Scaling is its own section in the input file, and is no longer under the structure section. See :doc:`3_1_9_scaling` for format changes.
* Instead of a mast_recipe.log file in each recipe directory, there is now one large mast.log file in $MAST_CONTROL.
* Instead of recipe-level trapped errors causing MAST to fail, MAST will create a MAST_ERROR document in the recipe directory and log a warning to ``$MAST_CONTROL/mast.log``

**Changes for programmers:**

* In order to see some logged messages that are now logged to the DEBUG level, set environment variable MAST_DEBUG to any value.
