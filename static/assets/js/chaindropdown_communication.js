
function getCampus(obj){
    $.ajax({
        method: "POST",
        url: '/communication/get_campus',
        data: id=obj.value,
        success: function (result) {
            // console.log(result)
            $("#campus_id").html('');
            for (var i = 0; i < result.length; i++) {
                $("#campus_id").append('<option value="' + result[i]["id"] + '">' + result[i]["name"] + '</option>');
            }
        }
    })
 }
function getInstitution(obj) {
    if (obj.value === '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: '/communication/get_institutions',
        data: "campus_id=" +$("#campus_id").val() ,
        success: function (result) {
            $("#institution_id").html('');
            for (var i = 0; i < result.length; i++) {
                $("#institution_id").append('<option value="' + result[i]["institution__id"] + '">' + result[i]["institution__name"] + '</option>');
            }
                   $("#institution_div").show();

        }
    });
}

 function getCourses(obj) {
        if (obj.value === '') {
            return false;
        }
        $("#course_div").fadeIn();
        $.ajax({
            method: "POST",
            url: '/communication/get_institution_courses',
            data: "institution_id=" + $("#institution_id").val(),
            success: function (result) {
                $("#course_div").show();
                $("#course_id").html('');
                for (var i = 0; i < result.length; i++) {
                    $("#course_id").append('<option value="' + result[i]["course__id"] + '">' + result[i]["course__name"] + '</option>');
                }
            }
        });
    }

    function getDepartments(obj) {
        if (obj.value === '') {
            return false;
        }
        $("#department_div").fadeIn();
        $.ajax({
            method: "POST",
            url: '/communication/get_courses_department',
            data: "course_id=" + $("#course_id").val(),
            success: function (result) {
                $("#department_id").html('');
                $("#department_id").append('<option value="">Select Departments</option>');
                for (var i = 0; i < result.length; i++) {
                    $("#department_id").append('<option value="' + result[i]["department__id"] + '">' + result[i]["department__name"] + '</option>');
                }
            }
        });
    }

    function getSections(obj) {
        camp = $("#campus_id").val();
        d = $("#department_id").val();
        var g = $("#group").val();
        var len = g.length
        // alert(camp)
        // alert(d)
        if (obj.value === '') {
            return false;
        }
        for (var i = 0; i < len; i++) {
            if (g[i] == '1') {
                $("#batch_div").fadeIn();
                $("#section_div").fadeIn();

                $.ajax({
                    method: "POST",
                    url: '/communication/get_department_sections',
                    data: 'department_id=' + d + '&campus_id=' + camp,
                    success: function (result) {

                        $("#batch_div").show();
                        $("#section_div").show();
                        $("#section_id").append('<option value="">Select Sections</option>');
                        for (var i = 0; i < result.length; i++) {
                            $("#section_id").append('<option value="' + result[i]["section__id"] + '">' + result[i]["section__name"] + '</option>');
                        }


                    }
                });
            }
            else {
                $("#batch_div").hide();
                $("#section_div").hide();
            }
        }
    }



