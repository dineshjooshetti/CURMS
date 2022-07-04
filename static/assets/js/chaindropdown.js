
function getInstitution(obj) {
    if (obj.value === '') {
        return false;
    }
    $.ajax({
        method: "POST",
        url: '/user_management/get_institutions',
        data: "id=" + obj.value,
        success: function (result) {
            $("#institution_id").html('<option value="" selected disabled>' + 'Select Institution' + '</option>');
            for (var i = 0; i < result.length; i++) {
                $("#institution_id").append('<option value="' + result[i]["institution__id"] + '">' + result[i]["institution__name"] + '</option>');
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
        url: '/user_management/get_department_by_institution',
        data: "id=" + obj.value,
        success: function (result) {
            $("#department_id").html('<option value="" selected disabled>' + 'Select Department' + '</option>');
            for (var i = 0; i < result.length; i++) {
                $("#department_id").append('<option value="' + result[i]["department__id"] + '">' + result[i]["department__name"] + '</option>');
            }
        }
    });
}

