import os
import shelve
import sqlite3
import types
from enum import Enum
from pickle import PicklingError

import dill
from ipynbname import name as notebook_name
from ipynbname import path as notebook_path


warehouse_directory = r'warehouse'
pickle_extension = r'.pkl'
shelf_extension = r'.shelf'
saved_module_name = 'save_state'  # Name given to modules that are saved and loaded with this package
saved_vars_blacklist = ['In', 'Out', 'open', 'exit', 'quit', 'get_ipython', 'ipykernal', # IPython vars
                        'shell', 'InteractiveShell', # Command-Line vars
                        'pydev_jupyter_vars', 'pydev_jupyter_utils', 'remove_imported_pydev_package',  # Pycharm vars
                        'debugpy', 'ptvsd']  # VSCode vars

class ISType(Enum):
    PICKLE = "pickle"
    SHELVE = "shelve"

def ensure_directory(directory=warehouse_directory, filename=None, checkpoints=False):
    """Ensure all necessary directories exist, creating if necessary

       Also creates README.md for warehouse directory"""
    if filename:  # Ensure directory for a notebook
        os.makedirs(os.path.join(directory, filename), exist_ok=True)

        if checkpoints:  # Also ensure directory for checkpoints
            os.makedirs(os.path.join(directory, filename, '.checkpoints'), exist_ok=True)

    else:  # Ensure warehouse directory (probably only run at import time)
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, 'README.md'), 'w') as label_file:
            label_file.write(f'This directory (/{warehouse_directory}) '
                             f'provides storage for the Immersive Simulations package')

ensure_directory()


def filepath(filename: str, method: ISType, directory: str=warehouse_directory, index: int=None, funcs=False) -> str:
    """Returns the exact filepath for a specific file and operation"""
    match method:  # Get correct extension
        case ISType.PICKLE:  # Quick-Save or Checkpoint
            if index is not None:  # Used for checkpoints
                if funcs:
                    save_filename = f'.checkpoints/checkpoint_{index}_funcs{pickle_extension}'
                else:
                    save_filename = f'.checkpoints/checkpoint_{index}{pickle_extension}'
            else:  # Used for quick-save
                if funcs:
                    save_filename = f'quicksave_funcs{pickle_extension}'
                else:
                    save_filename = f'quicksave{pickle_extension}'



        case ISType.SHELVE:  # Shelf
            save_filename = f'storage{shelf_extension}'

        case _:
            raise ValueError(f'Invalid method: {method}')

    # Ensure room in the warehouse
    ensure_directory(directory=directory, filename=filename, checkpoints=index is not None)

    return os.path.join(directory, filename, save_filename)  # Ex. warehouse/workbench/quicksave.pkl


class ShelfWithCleanup:
    """A shelf wrapper class that removes -wal and -shm objects upon close"""
    def __init__(self, path, flag='c'):
        self.path = path
        self.flag = flag
        self.shelf = None

    def __enter__(self):
        self.shelf = shelve.open(self.path, self.flag)
        return self.shelf

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shelf.close()
        # Clean up SQLite WAL/SHM files if they exist
        for ext in ('-wal', '-shm'):
            try:
                os.remove(self.path + ext)
            except FileNotFoundError:
                pass
        return False  # don't suppress exceptions

def open_shelf_with_cleanup(path, flag='c'):
    """Opens and returns a ShelfWithCleanup, which is a shelf that deletes temporary files to clean up after use"""
    return ShelfWithCleanup(path, flag)


def is_picklable(item) -> bool:
    """Indicates whether an item is picklable via dill"""
    try:
        dill.dumps(item)
        return True
    except PicklingError:
        return False
    except Exception as e:
        raise ValueError(f'Unexpected error while trying to pickle {item}: {e}')


def is_nb_function(item):
    """Indicates whether an item is a function defined in the notebook

       Functions defined in the notebook may have problems pickling in the module, and should be pickled separately"""
    return (isinstance(item, types.FunctionType) or isinstance(item, types.MethodType)) and item.__module__ == '__main__'
