(function() {
    // Monkeypatch RequireJS loader to block fetch of nb_cell_indexing.js safely
    if (typeof requirejs !== 'undefined') {
        const originalLoad = requirejs.load;
        requirejs.load = function(context, moduleName, url) {
            if (moduleName === 'nb_cell_indexing') {
                console.log('Blocked loading nb_cell_indexing to prevent 404 and errors');

                // Create dummy <script> element to satisfy RequireJS internals
                let script = document.createElement('script');
                script.type = 'text/javascript';
                script.async = true;

                // Simulate successful load event asynchronously
                setTimeout(() => {
                    if (script.onload) {
                        script.onload({ type: 'load', target: script });
                    }
                }, 0);

                return script;
            } else {
                return originalLoad.apply(this, arguments);
            }
        };
        console.log('RequireJS loader monkeypatched to block nb_cell_indexing loading.');
    }

    // Stub the nb_cell_indexing module so RequireJS thinks it is loaded
    if (typeof define === 'function' && define.amd) {
        define('nb_cell_indexing', [], function() {
            console.log('Stub nb_cell_indexing module registered');
            return {};
        });
    }

    // Cell indexing logic: assign and save metadata indices
    function assign_cell_indices() {
        let cells = Jupyter.notebook.get_cells();
        let index = 0;
        cells.forEach(cell => {
            if (cell.cell_type === 'code') {
                cell.metadata.cell_index = index;
                index += 1;
            }
        });
        Jupyter.notebook.save_notebook();
    }

    // Load the extension: assign indices and hook events
    function load_extension() {
        assign_cell_indices();

        // Update indices on cell create, delete, move, or notebook save
        events.on('create.Cell delete.Cell move_cell.Cell notebook_saved.Notebook', assign_cell_indices);

        // Undefine module cache to keep RequireJS clean
        if (typeof requirejs !== 'undefined') {
            try {
                requirejs.undef('nb_cell_indexing');
                console.log('✅ Unregistered nb_cell_indexing from RequireJS cache');
            } catch (e) {
                console.warn('Failed to undefine nb_cell_indexing:', e);
            }
        }
    }

    // Wait for Jupyter and events, then initialize
    require(['base/js/namespace', 'base/js/events'], function(Jupyter_, events_) {
        window.Jupyter = Jupyter_;
        window.events = events_;
        if (Jupyter.notebook._fully_loaded) {
            load_extension();
        } else {
            events.one('notebook_loaded.Notebook', load_extension);
        }
    });
})();
