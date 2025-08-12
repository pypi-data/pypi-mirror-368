import json

from IPython import get_ipython
from IPython.display import display, Javascript
from importlib.resources import read_text

from .utils import notebook_path
from .states import quick_save, quick_load


def get_cell_index_for_code(cell_code):
    path = notebook_path()
    if path is None:
        raise RuntimeError("Cannot find notebook path")

    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if source.strip() == cell_code.strip():
                return cell.get('metadata', {}).get('cell_index')
    return None


# --------------------------------------------

def pre_run_cell(info):
    """Runs before each cell, performs quick_load"""
    cell_code = info.raw_cell  # actual code
    index = get_cell_index_for_code(cell_code) - 1
    if index >= 0:  # It should be, but just to be sure
        # print(f"Loading checkpoint #{index}")  # For debugging
        quick_load(index=index)


def post_run_cell(result):
    """Runs after each cell, performs quick_save"""
    if hasattr(result, "info"):
        cell_code = result.info.raw_cell
    else:  # Get last cell from IPython history
        shell = get_ipython()
        cell_code = shell.history_manager.input_hist_raw[result.execution_count]

    index = get_cell_index_for_code(cell_code)
    # print(f"Saving checkpoint #{index}")  # For debugging
    quick_save(index=index)


# --------------------------------------------

def load_ipython_extension(ipython):
    """Tells IPython to load JS extension and perform before-cell and after-cell actions"""
    # add_cell_index_to_cells()  # Annotate the notebook before anything else
    _load_js_extension()
    ipython.events.register('pre_run_cell', pre_run_cell)
    ipython.events.register('post_run_cell', post_run_cell)


def unload_ipython_extension(ipython):
    """Clean up IPython"""
    ipython.events.unregister('pre_run_cell', pre_run_cell)
    ipython.events.unregister('post_run_cell', post_run_cell)


# ---------------------------------

def _load_js_extension():
    """Load and run cell indexing extension"""
    js_code = read_text('immersim', 'nb_cell_indexing.js')  # Load Extension
    display(Javascript(js_code))  # Run that extension
    # print("Cell indexing JS extension loaded!")
