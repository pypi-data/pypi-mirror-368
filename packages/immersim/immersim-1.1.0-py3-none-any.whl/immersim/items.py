import inspect

from .utils import notebook_name, filepath, ISType, open_shelf_with_cleanup

# -------------------------------------------------------------------
# Using shelve to easily load and store specific items
# Idea: Each notebook has two associated shelves, a "temp" shelf and a "permanent" shelf
# The "temp" shelf could be reset near the start of the file, to contain results from last run experiment
#   or alternatively, some sort of stack of results that haven't been saved or discarded yet

def store(*items):
    """Store one (or more) items on this notebook's shelf

       Expects variables passed in (not just values)"""
    nb_name = notebook_name()

    # Get caller's local variables
    caller_locals = inspect.currentframe().f_back.f_locals

    # Derive caller's variable names for the requested items
    item_dict = {}
    for item in items:
        # match item to name: item pair
        names = [name for name, value in caller_locals.items() if value is item and not name.startswith('_')]
        if not names:  # Doesn't exist
            raise ValueError(f'Could not find variable name for object: {item}')
        item_dict[names[0]] = item

    # Put onto shelf
    with open_shelf_with_cleanup(filepath(nb_name, ISType.SHELVE), flag='c') as shelf:
        for name, item in item_dict.items():
            shelf[name] = item

    return


def get_shelf_dict():
    """Return the shelf dict associated with calling file."""
    nb_name = notebook_name()
    with open_shelf_with_cleanup(filepath(nb_name, ISType.SHELVE), flag='r') as shelf:
        shelf_dict = dict(shelf)
    return shelf_dict


def open_shelf(flag='c', directory=None, filename=notebook_name()):
    """Return the opened shelf associated with calling file, unless another filename/directory specified.
       Should be used in "with" statement.

       Example:
           with open_shelf() as my_shelf:
               my_shelf['lighting'] = 'mood'"""
    kwargs = {'directory': directory} if directory is not None else {}  # Conditionally override directory
    return open_shelf_with_cleanup(filepath(filename, ISType.SHELVE, **kwargs), flag=flag)


def retrieve(*items, directory=None, filename=notebook_name()):
    """Retrieve one (or more) items from shelf associated with calling file,
       unless another filename/directory specified."""
    kwargs = {'directory': directory} if directory is not None else {}  # Conditionally override directory
    with open_shelf_with_cleanup(filepath(filename, ISType.SHELVE, **kwargs), flag='r') as shelf:
        shelf_dict = dict(shelf)

    retrieved_items = []
    for item in items:
        if item not in shelf_dict:  # Doesn't exist
            raise ValueError(f'Could not find stored item: {item}')
        retrieved_items.append(shelf_dict[item])

    return tuple(retrieved_items)


def clear_shelf(*items, directory=None, filename=notebook_name()):
    """Delete one (or more) items from shelf associated with calling file,
       unless another filename/directory specified.

       By default, calling with no items passed will clear ALL items from shelf.

       Example:
           clear_shelf()

           clear_shelf(var1, var2)

           clear_shelf(filename='workbench')"""
    # Get caller's local variables
    caller_locals = inspect.currentframe().f_back.f_locals

    kwargs = {'directory': directory} if directory is not None else {}  # Conditionally override directory

    with open_shelf_with_cleanup(filepath(filename, ISType.SHELVE, **kwargs), flag='c') as shelf:
        if items:
            # Derive caller's variable names for the requested items
            item_list = []
            for item in items:
                # match item to name: item pair
                names = [name for name, value in caller_locals.items() if value is item and not name.startswith('_')]
                if not names:  # Doesn't exist
                    raise ValueError(f'Could not find variable name for object: {item}')
                item_list.append(names[0])
        else:
            item_list = list(shelf.keys())

        for item in item_list:
            del shelf[item]
    return
