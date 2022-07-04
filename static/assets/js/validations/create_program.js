//ceritification_form js
$( "#create_program" ).validate({
      rules: {
        p_name: {
          required: true,
          maxlength: 100,
        },
        p_type: {
          required: true,
         },
        p_level: {
          required: true,
         },
         campus: {
          required: true,
         },
        pcmi: {
          required: true,
         },
         pcmc: {
          required: true,
         },
         //   program_category: {
         //  required: true,
         // },

      },
      errorElement : 'div',
        errorPlacement: function(error, element) {
          var placement = $(element).data('error');
          if (placement) {
            $(placement).append(error)
          } else {
            $(element).closest('div').after(error)
          }
        },

    });
	
//ceritification_form js
$( "#edit_program" ).validate({
      rules: {
        p_name: {
          required: true,
          maxlength: 100,
        },
        p_type: {
          required: true,
         },
        p_level: {
          required: true,
         },
         campus: {
          required: true,
         },
        pcmi: {
          required: true,
         },
         pcmc: {
          required: true,
         },
      },
      errorElement : 'div',
        errorPlacement: function(error, element) {
          var placement = $(element).data('error');
          if (placement) {
            $(placement).append(error)
          } else {
            $(element).closest('div').after(error)
          }
        },

    });	