import json
from operator import index

from IPython import get_ipython
from IPython.display import display, Javascript
from importlib.resources import read_text

from .utils import notebook_name, notebook_path, filepath, ISType, open_shelf_with_cleanup
from .states import quick_save, quick_load
from .items import clear_shelf

def get_previous_cell_id(cell_id):
    """Returns the index of the previous cell"""
    nb_name = notebook_name()

    # Load current JSON
    path = notebook_path()
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    code_cell_ids = [cell['id'] for cell in nb['cells'] if cell['cell_type'] == 'code']
    if cell_id in code_cell_ids:
        cell_id_index = code_cell_ids.index(cell_id)
        if cell_id_index >= 1:
            return code_cell_ids[cell_id_index - 1]
        else:
            return None
    else:
        raise ValueError(f'cell_id not found: {cell_id}')


def get_cell_id(cell_code):
    """Matches cell code against JSON to determine cell id

       If there is no exact match (maybe user didn't save before running), this cell won't save/load a checkpoint"""
    # Load current JSON
    path = notebook_path()
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    code_2_id = {"".join(cell['source']): cell['id'] for cell in nb['cells'] if cell['cell_type'] == 'code' and 'id' in cell}
    # print(f'\ncode_2_id = {code_2_id}\n')

    cell_code = cell_code.strip()
    # print(f'cell_code:\n{cell_code}')

    if cell_code in code_2_id:
        return code_2_id[cell_code]
    else:
        return None

# --------------------------------------------

def pre_run_cell(info):
    """Runs before each cell, performs quick_load"""
    cell_code = info.raw_cell  # actual code
    cell_id = get_cell_id(cell_code)
    previous_id = get_previous_cell_id(cell_id) if cell_id else None
    # print(f'previous id: {previous_id}')
    if previous_id:
        # print(f"Loading checkpoint #{index}")  # For debugging
        quick_load(cell_id=previous_id)


def post_run_cell(result):
    """Runs after each cell, performs quick_save"""
    if hasattr(result, "info"):
        cell_code = result.info.raw_cell
    else:  # Get last cell from IPython history
        shell = get_ipython()
        cell_code = shell.history_manager.input_hist_raw[result.execution_count]

    cell_id = get_cell_id(cell_code)
    # print(f'current id: {cell_id}')
    if cell_id:
        # print(f"Saving checkpoint #{index}")  # For debugging
        quick_save(cell_id=cell_id)


# --------------------------------------------

def load_ipython_extension(ipython):
    """Tells IPython to load JS extension and perform before-cell and after-cell actions"""
    ipython.events.register('pre_run_cell', pre_run_cell)
    ipython.events.register('post_run_cell', post_run_cell)


def unload_ipython_extension(ipython):
    """Clean up IPython"""
    ipython.events.unregister('pre_run_cell', pre_run_cell)
    ipython.events.unregister('post_run_cell', post_run_cell)
