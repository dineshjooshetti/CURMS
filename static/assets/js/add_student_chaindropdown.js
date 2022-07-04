function getInstitution(obj) {
    if (obj.value === '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: '/user/get_institutions',
        data: "id=" + obj.value,
        success: function (result) {
            $("#institution_id").html('<option value="">Select Institution</option>');
            for (var i = 0; i < result.length; i++) {
                $("#institution_id").append('<option value="' + result[i]["institution__id"] + '">' + result[i]["institution__name"] + '</option>');
            }
        }
    });
}

function getQualification(obj) {
    if (obj.value === '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: '/user/get_qualification',
        data: "id=" + obj.value,
        success: function (result) {
            $("#qualification_id").html('<option value="">Select Qualification</option>');
            for (var i = 0; i < result.length; i++) {
                $("#qualification_id").append('<option value="' + result[i]["qualification__id"] + '">' + result[i]["qualification__name"] + '</option>');
            }
        }
    });
}

function getCourse(obj) {
    if (obj.value === '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: '/user/get_course',
        data: "id=" + obj.value,
        success: function (result) {
            $("#course_id").html('<option value="">Select Course</option>');
            for (var i = 0; i < result.length; i++) {
                $("#course_id").append('<option value="' + result[i]["course__id"] + '">' + result[i]["course__name"] + '</option>');
            }
        }
    });
}

function getDepartment(obj) {
    if (obj.value === '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: '/user/get_department',
        data: "id=" + obj.value,
        success: function (result) {
            $("#department_id").html('<option value="">Select Department</option>');
            for (var i = 0; i < result.length; i++) {
                $("#department_id").append('<option value="' + result[i]["department__id"] + '">' + result[i]["department__name"] + '</option>');
            }
        }
    });
}

function getSection(obj) {
    if (obj.value === '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: '/user/get_section',
        data: {"department_id":$("#department_id").val(),"campus_id":$("#campus_id").val(),"batch_id":$("#batch_id").val(),"course_id":$("#course_id").val()},
        success: function (result) {
            console.log(result);
            $("#section_id").html('<option value="">Select Section</option>');
            for (var i = 0; i < result.length; i++) {
				$("#section_id").append('<option value="' + result[i]["section__id"] + '">' + result[i]["section__name"] + '</option>');
            }
        }
    });
 }
function getBatch(obj) {
    if (obj.value === '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: '/user/get_batches',
        data: {"id":$("#department_id").val(),"campus_id":$("#campus_id").val(),"batch_id":obj.value,"course_id":$("#course_id").val()},
        success: function (result) {
            console.log(result);
            $("#batch_id").html('<option value="">Select Batch</option>');
            for (var i = 0; i < result.length; i++) {
				$("#batch_id").append('<option value="' + result[i]["id"] + '">' + result[i]["batch"] + '</option>');
            }
        }
    });
 }