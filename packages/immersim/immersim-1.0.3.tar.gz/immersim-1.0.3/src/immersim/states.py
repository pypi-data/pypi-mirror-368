import sys
from types import ModuleType

import dill

from .utils import notebook_name, filepath, ISType, saved_vars_blacklist, saved_module_name, is_nb_function


# -------------------------------------------------------------------
# Using dill (saving/loading the entire session)
def quick_save(index=None):
    """Save all user vars and modules in their current state

       Will not save variables beginning with _

       Saves modules by reference, not value"""
    nb_name = notebook_name()

    # Old Method (no filter, saves all metadata, which can screw up loading)
    # dill.dump_module(save_directory+ nb_name +pickle_extension, refimported=True)

    # New Method (can filter, saves new module with only useful variables)
    main_module = sys.modules['__main__']
    filtered_namespace = {var: value for var, value in main_module.__dict__.items()
                          if not var.startswith('_') and var not in saved_vars_blacklist}

    # Separate into functions defined in the notebook, and everything else
    nb_funcs = {var: value for var, value in filtered_namespace.items() if is_nb_function(value)}  # Pickle Separately
    final_namespace = {var: value for var, value in filtered_namespace.items() if var not in nb_funcs}  # Pickle in module

    # Pickle notebook functions
    dill.dump(nb_funcs, open(filepath(nb_name, ISType.PICKLE, index=index, funcs=True), 'wb'))

    # Create a new module with filtered namespace
    saved_module = ModuleType(saved_module_name)
    saved_module.__dict__.update(final_namespace)

    # pprint(filtered_namespace)

    dill.dump_module(filepath(nb_name, ISType.PICKLE, index=index), saved_module,  refimported=True)


def quick_load(index=None):
    """Load all user vars and modules from a quick_save

       Will overwrite variables with the same name as saved variables

       Will not remove current variables that were not part of the save

       Example:
           x = 5; quick_save(); y = 9; quick_load(); # namespace is x=5, y=9"""
    nb_name = notebook_name()

    # Old Method
    # dill.load_module(save_directory+ nb_name +pickle_extension)

    # New Method (load named module to update main module from)
    loaded_module = dill.load_module(filepath(nb_name, ISType.PICKLE, index=index))  # Module
    loaded_funcs = dill.load(open(filepath(nb_name, ISType.PICKLE, index=index, funcs=True), 'rb'))  # Notebook Funcs

    # Copy saved variables into __main__ (doesn't copy save module metadata, which includes wrong __name__, etc.)
    main_namespace = sys.modules['__main__'].__dict__
    main_namespace.update({var: value for var, value in loaded_module.__dict__.items() if not var.startswith('__')})
    main_namespace.update(loaded_funcs)  # Notebook specific functions

# --- Fun Aliases ---
F5 = quick_save
F9 = quick_load
