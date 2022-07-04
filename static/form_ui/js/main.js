jQuery.validator.addMethod("alpha_space", function(value, element, param) {
  return value.match(new RegExp("^" + param + "*$"));
});
jQuery.validator.addMethod("exactlength", function(value, element, param) {
 return this.optional(element) || value.length == param;
}, $.validator.format("Please enter exactly {0} characters."));

jQuery.extend(jQuery.validator.messages, {
    required: "This field is required.",
    remote: "Please fix this field.",
    email: "Please enter a valid email address.",
    url: "Please enter a valid URL.",
    date: "Please enter a valid date.",
    dateISO: "Please enter a valid date (ISO).",
    number: "Please enter a valid number.",
    digits: "Please enter only digits.",
    creditcard: "Please enter a valid credit card number.",
    equalTo: "Please enter the same value again.",
    accept: "Please enter a value with a valid extension.",
    maxlength: jQuery.validator.format("Please enter no more than {0} characters."),
    minlength: jQuery.validator.format("Please enter at least {0} characters."),
    rangelength: jQuery.validator.format("Please enter a value between {0} and {1} characters long."),
    range: jQuery.validator.format("Please enter a value between {0} and {1}."),
    max: jQuery.validator.format("Please enter a value less than or equal to {0}."),
    min: jQuery.validator.format("Please enter a value greater than or equal to {0}."),
    alpha_space:jQuery.validator.format("Please enter alphabets only"),

});


(function($) {
    var form = $("#signup-form");
    $('.err').text('')

    form.validate({
        errorPlacement: function errorPlacement(error, element) {
            element.next().find('.err').after(error);
        },
        ignore: ".ignore, :hidden",

			//
        rules: {
            type_of_course:{
                required:true,
            },
            level_of_course:{
                required:true,
            },
            // course_category:{
            //     required:true,
            // },
            course_title:{
                required:true,
            },
            L:{
                required:true,
                // integer: true,
                range: [0, 5]
            },
            T:{
                required:true,
                // integer: true,
                range: [0, 5]
            },
            P:{
                required:true,
                // integer: true,
                range: [0, 7]
            },
            S:{
                required:true,
                // integer: true,
                range: [0, 10]
            },
            J:{
                required:true,
                // integer: true,
                range: [0, 20]
            },
            total_hours:{
                required : true,
            },
            pre_requisites:{
                required : true,
            },
            alt_exposure:{
                required : true,
            },
            co_requisites:{
                required : true,
            },
            course_description:{
                required : true,
            },
            course_objectives:{
                required : true,
            },
			sdg_description:{
				required : true,
			},
			sdg:{
				required : true,
			},
            pso:{
                required : true,
            },
            pre_requisites_yes:{
                required : true,
            },
            pre_requisites_courses:{
                required : true,
            },
            co_requisites_courses:{
              required:true
            },
            course_outcome:{
                required : true,
                maxlength: 250,
            },
            course_codes:{
                required : true,
            },
            unit_name:{
                required : true,
            },
            short_title:{
                required : true,
            },
            contact_hours:{
                required : true,
            },
            learning_outcome_1:{
                required : true,
            },
            learning_outcome_2:{
                required : true,
            },
            learning_outcome_3:{
                required : true,
            },
            learning_outcome_4:{
                required : true,
            },
            learning_outcome_5:{
                required : true,
            },
            level_1:{
                required : true,
            },
            level_2:{
                required : true,
            },
            level_3:{
                required : true,
            },
             level_4:{
                required : true,
            },
             level_5:{
                required : true,
            },
            pedagogy_tool_1:{
                required : true,
            },
            pedagogy_tool_2:{
                required : true,
            },
            book_author:{
                required : true,
            },
            book_year:{
                required : true,
            },
            book_title:{
                required : true,
            },
            book_edition:{
                required : true,
            },
            book_publisher:{
                required : true,
            },
            book_publication:{
                required : true,
            },
            ref_author:{
                required : true,
            },
            ref_year:{
                required : true,
            },
            ref_title:{
                required : true,
            },
            ref_edition:{
                required : true,
            },
            ref_publisher:{
                required : true,
            },
            ref_publication:{
                required : true,
            },
            instruction_plan:{
                required : function () {
                    if ($("input[name='instruction_paln_file']").val()){
                        return false
                    }
                    else {
                        return true
                    }
                },
            },
            syllabus_topic:{
                required : true,
            },
            syllabus_type:{
                required : true,
            },
            practical_referance:{
                required: true,
            },
            prctical_topic_mapping:{
                required: true,
            },
            project_topic:{
                required: true,
            },
            online_resources:{
                required: true,
            },
            p_type:{
                required: true,
            },
            p_level:{
                required: true,
            },
            campus:{
                required: true,
            },
            pcmi:{
                required: true,
            },
            pcmc:{
                required: true,
            },
            p_name:{
                required: true,
            },
            isbn:{
                required: true,
            },
            pedagogy_tools_1:{
              required: true,
            },
            pedagogy_tools_2:{
              required: true,
            },
            pedagogy_tools_3:{
              required: true,
            },
            pedagogy_tools_4:{
              required: true,
            },
            pedagogy_tools_5:{
              required: true,
            },
            unit_mapping:{
              required: true,
            },
            ref_isbn:{
              required: true,
            },
            ref_unit_mapping:{
              required: true,
            },
        },
        errorElement : 'div',
        errorPlacement: function(error, element) {
          var placement = $(element).data('error');
		  if(element.attr("name") == "sdg") {
				error.appendTo(element.closest('.col-md-6'));
			} 
          else if (placement) {
            $(placement).append(error)
          } else {
            error.insertAfter(element);
          }
        },
        // errorElement: 'span',
        // errorClass: 'help-inline',
        // errorPlacement: function(error, element) {
        //
        //         error.insertAfter(element);
        //
        //
        // },
        // onfocusout: function(element) {
        //     $(element).valid();
        // },

    });

    form.steps({
        headerTag: "h3",
        bodyTag: "fieldset",
        transitionEffect: "slideLeft",
        labels: {
            // previous: 'Previous',
            next: 'Next',
            finish: 'Final Preview',
            current: ''
        },
        titleTemplate: '<div class="title"><span class="number">#index#</span>#title#</div>',
        onStepChanging: function(event, currentIndex, newIndex) {
            // form.validate().settings.ignore = ":disabled,:hidden";
			console.log(currentIndex)	
			console.log(newIndex)	
            if(currentIndex == 10 && newIndex==11){

                if (form.valid()) {
                    var data = $.parseJSON($.ajax({
                        url: '/csmc/dev_details_save',
                        data: $('#signup-form').serialize(),
                        type: "POST",
                        async: false,
                        error: function (xhr, ajaxOptions, thrownError) {
                            alert(xhr.statusText);
                        }
                    }).responseText);
                    if (data.status == 200) {
                        return true;
                    } else {
                        alert(data.error)
                        return false
                    }
                }


            }
            if(currentIndex == 11 && newIndex==12){
                 return true;
                //if (form.valid()) {
                    // var data = $.parseJSON($.ajax({
                    //     url: '/csmc/course_details_save',
                    //     data: $('#signup-form').serialize(),
                    //     type: "POST",
                    //     async: false,
                    //     error: function (xhr, ajaxOptions, thrownError) {
                    //         alert(xhr.statusText);
                    //     }
                    // }).responseText);
                    // if (data.status == 200) {
                    //     window.location.href = "/csmc/course_details/" + data.enc_id;
                    // } else {
                    //     alert(data.error)
                    //     return false
                    // }
                //}


            }else if(currentIndex==0 && newIndex==1){
                if (form.valid()) {
                    var data = $.parseJSON($.ajax({
                        url: '/csmc/about_course_save',
                        data: $('#signup-form').serialize(),
                        type: "POST",
                        async: false,
                        error: function (xhr, ajaxOptions, thrownError) {
                            alert(xhr.statusText);
                        }
                    }).responseText);
                    if (data.status == 200) {
                        location.reload()
                        return true;
                    } else {
                        alert(data.error)
                        return false
                    }
                }
            }else if(currentIndex==1 && newIndex==2){
                if (form.valid()) {
                    // alert('in')
                    var data = $.parseJSON($.ajax({
                        url: '/csmc/syllabus_save',
                        data: $('#signup-form').serialize(),
                        type: "POST",
                        async: false,
                        error: function (xhr, ajaxOptions, thrownError) {
                            alert(xhr.statusText);
                        }
                    }).responseText);
                    if (data.status == 200) {
                        // alert(data.status)
                        location.reload()
                        return true;
                    } else {
                        alert(data.error)
                        return false
                    }
                }

            // }else if(currentIndex==4 && newIndex==5){
            //     if (form.valid()) {
            //         // alert('in')
            //         var data = $.parseJSON($.ajax({
            //             url: '/csmc/course_book_save',
            //             data: $('#signup-form').serialize(),
            //             type: "POST",
            //             async: false,
            //             error: function (xhr, ajaxOptions, thrownError) {
            //                 alert(xhr.statusText);
            //             }
            //         }).responseText);
            //         if (data.status == 200) {
            //             //location.reload()
            //             //return true;
            //             window.location.href = "/csmc/co_po_pso_save/" + data.enc_id;
            //         } else {
            //             alert(data.error)
            //             return false
            //         }
            //     }

            }
            else {
                $.ajax({
                    type: 'POST',
                    url: '/csmc/previous_step/',
                    data: {step:newIndex,post_data:$('#signup-form').serialize()},
                    success: function (result) {
                        return true
                    }
                });
                return true
            }

        },
        onFinishing: function(event, currentIndex) {
            return form.valid();
        },
        onFinished: function(event, currentIndex) {
            $("#signup-form").submit()
        },

    });

    // jQuery.extend(jQuery.validator.messages, {
    //     required: "",
    //     remote: "",
    //     url: "",
    //     date: "",
    //     dateISO: "",
    //     number: "",
    //     digits: "",
    //     creditcard: "",
    //     equalTo: ""
    // });


    // $.dobPicker({
    //     daySelector: '#expiry_date',
    //     monthSelector: '#expiry_month',
    //     yearSelector: '#expiry_year',
    //     dayDefault: 'DD',
    //     yearDefault: 'YYYY',
    //     minimumAge: 0,
    //     maximumAge: 120
    // });

    // $('#password').pwstrength();

    $('.file_button').click(function () {
        $(this).closest('.form-file').find("input[type='file']").trigger('click');
    })
    var course = $("#c_id").val()
    /* $("input[type='file']").change(function () {
        var this_file=$(this)
        var fd=new FormData();
        var files = $('#'+this.id)[0].files;
        console.log(files)
        this_file.next().find('.err').next().remove()
		a= ValidateFileUpload(files[0],this_file)
        if(files.length > 0 && a==true){
            fd.append(this.name,files[0])
            $.ajax({
            type: "POST",
            url: "/csmc/update_file/"+course,
            data: fd,
            contentType: false,
            processData: false,
            success: function (data) {
                if(data.status==200){
                    alert('Uploaded Sucessfully')
                    this_file.data('value',20); //setter
                    // this_file.data('value',files[0].name)
                    this_file.closest('.form-file').find('.file_val').text(files[0].name)
                    this_file.next().find('.err').next().remove()

                }else{

                }
                console.log(data)
            },
            error: function (xhr, status) {
                alert(status)
                console.log(xhr)
                // loading.close()
            }
         });
        }else{
            this_file.val('')
        }
        // a=ValidateFileUpload()
    }) */

$("#instruction_plan").change(function () {
        var this_file=$(this)
        var fd=new FormData();
        var files = $('#'+this.id)[0].files;
        console.log(files)
        this_file.next().find('.err').next().remove()
		a= ValidateFileUpload(files[0],this_file)
        if(files.length > 0 && a==true){
            fd.append(this.name,files[0])
            $.ajax({
            type: "POST",
            url: "/csmc/update_file/"+course,
            data: fd,
            contentType: false,
            processData: false,
            success: function (data) {
                if(data.status==200){
                    alert('Uploaded Sucessfully')
                    this_file.data('value',20); //setter
                    // this_file.data('value',files[0].name)
                    this_file.closest('.form-file').find('.file_val').text(files[0].name)
                    this_file.next().find('.err').next().remove()
                    $("#instruction_paln_file").val(files[0].name)
                }else{

                }
                console.log(data)
            },
            error: function (xhr, status) {
                alert(status)
                console.log(xhr)
                // loading.close()
            }
         });
        }else{
            this_file.val('')
        }
        // a=ValidateFileUpload()
    })
    $("#instruction_plan_practical").change(function () {
        var this_file=$(this)
        var fd=new FormData();
        var files = $('#'+this.id)[0].files;
        console.log(files)
        this_file.next().find('.err').next().remove()
		a= ValidateFileUpload(files[0],this_file)
        if(files.length > 0 && a==true){
            fd.append(this.name,files[0])
            $.ajax({
            type: "POST",
            url: "/csmc/update_file/"+course,
            data: fd,
            contentType: false,
            processData: false,
            success: function (data) {
                if(data.status==200){
                    alert('Uploaded Sucessfully')
                    this_file.data('value',20); //setter
                    // this_file.data('value',files[0].name)
                    this_file.closest('.form-file').find('.file_val').text(files[0].name)
                    this_file.next().find('.err').next().remove()

                }else{

                }
                console.log(data)
            },
            error: function (xhr, status) {
                alert(status)
                console.log(xhr)
                // loading.close()
            }
         });
        }else{
            this_file.val('')
        }
        // a=ValidateFileUpload()
    })

function ValidateFileUpload(file,this_file) {
    this_file.next().find('.err').text('')
    var filename = file.name;
    var filesize = file.size;
	Extension = filename.substr( (filename.lastIndexOf('.') +1) );
	if (Extension == "pdf") {
		if (filesize > 2000000){
			this_file.next().find('.err').text('Max file size 2MB');
			return false
		}else{

			return true
		}
	}else {
            //alert("files not allow");
            this_file.next().find('.err').text('Upload only PDF files ');
			if (filesize > 2000000){
				this_file.next().find('.err').text('Max file size 2MB');
			}
			return false
		}
    }



})(jQuery);