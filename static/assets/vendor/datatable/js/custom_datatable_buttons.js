$('#datatable-buttons').DataTable( {
        dom: 'Bfrtip',
        buttons: [
            'excel', 'pdf', 'print'
        ],
        language: {
           paginate: {
             previous: "<i class='fas fa-angle-left'>",
             next: "<i class='fas fa-angle-right'>"
           }
         }

    } );
    $('.dt-buttons .buttons-html5, .buttons-print').removeClass('dt-button').addClass('btn-sm btn-default');