define([
    'base/js/namespace',
    'base/js/events'
], function(Jupyter, events) {

    function assign_checkpoint_indices() {
        let cells = Jupyter.notebook.get_cells();
        let index = 0;
        cells.forEach(cell => {
            if (cell.cell_type === 'code') {
                cell.metadata.checkpoint_index = index;
                index += 1;
            }
        });
        // console.log('Checkpoint indices assigned/updated.');  // For debugging
    }

    function load_ipython_extension() {
        // console.log('Loading checkpoint index extension...');  // For debugging

        assign_checkpoint_indices();

        events.on('create.Cell', assign_checkpoint_indices);
        events.on('delete.Cell', assign_checkpoint_indices);
        events.on('move_cell.Cell', assign_checkpoint_indices);
        events.on('notebook_saved.Notebook', assign_checkpoint_indices);

        // console.log('Cell indexing extension loaded.');  // For debugging
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});
