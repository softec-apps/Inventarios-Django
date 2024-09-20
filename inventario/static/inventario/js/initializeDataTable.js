// Función para inicializar DataTables con parámetros dinámicos
function initializeDataTable(tableId, exportFileName = 'Lista de Productos', fixedColumnsStart = 0, scrollX = true) {
    let table = $(tableId).DataTable({
        language: {
            buttons: {
                sLengthMenu: "Mostrar _MENU_ resultados",
                pageLength: {
                    _: "Mostrar %d resultados",
                },
            },
            zeroRecords: "No hay coincidencias",
            info: "Mostrando _END_ resultados de _MAX_",
            infoEmpty: "No hay datos disponibles",
            infoFiltered: "(Filtrado de _MAX_ registros totales)",
            search: "Buscar",
            emptyTable: "No existen registros",
            paginate: {
                first: "Primero",
                previous: "<<",
                next: ">>",
                last: "Último",
            },
        },
        responsive: true,
        dom: "<'row'<'col-sm-12 col-md-8'B><'col-sm-12 col-md-4 d-flex justify-content-end'f>>" +
             "<'row'<'col-sm-12'tr>>" +
             "<'row mt-3'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 d-flex justify-content-end'p>>",
        buttons: [
            {
                extend: "pageLength",
                className: 'btn btn-light',
            },
            {
                extend: "colvis",
                className: "btn btn-light",
                text: 'Columnas',
                columns: ":not(.exclude)"
            },
            {
                extend: "csv",
                text: '<i class="fa fa-lg fa-file-csv me-2"></i>',
                className: 'ms-5 btn btn-outline-primary',
                exportOptions: {
                    columns: ":visible:not(.exclude)",
                },
                title: exportFileName,
                attr: {
                    'data-toggle': 'tooltip',
                    'data-placement': 'top',
                    'title': 'Descargar CSV'
                }
            },
            {
                extend: "excelHtml5",
                text: '<i class="fa fa-lg fa-file-excel me-2"></i>',
                className: 'ms-5 btn btn-outline-success',
                exportOptions: {
                    columns: ":visible:not(.exclude)",
                },
                title: exportFileName,
                attr: {
                    'data-toggle': 'tooltip',
                    'data-placement': 'top',
                    'title': 'Descargar Excel'
                }
            },
            {
                extend: "pdfHtml5",
                text: '<i class="fa fa-lg fa-print"></i>',
                className: 'btn btn-outline-danger tooltip-container',
                exportOptions: {
                    columns: ":visible:not(.exclude)",
                },
                download: 'open',
                title: exportFileName,
                attr: {
                    'data-toggle': 'tooltip',
                    'data-placement': 'top',
                    'title': 'Descargar PDF'
                }
            },
        ],
        lengthMenu: [10, 25, 50, 100],
        fixedColumns: {
            start: fixedColumnsStart
        },
        scrollX: scrollX,
        scrollCollapse: true,
        drawCallback: function() {
            // Inicializar tooltips después de cada renderización de la tabla
            $('[data-toggle="tooltip"]').tooltip();

            // Aplicar truncamiento a celdas con la clase 'truncate'
            $('.truncate').each(function() {
                var data = $(this).text();
                if (data.length > 20) {
                    $(this).html('<span title="' + data + '">' + data.substring(0, 100) + '...</span>');
                }
            });
        },
        columnDefs: [
            { targets: '.noVis', visible: false }
        ],
    });

    // Asegurarse de que las columnas con clase 'noVis' estén ocultas inicialmente
    table.columns('.noVis').visible(false);

    return table;
}
