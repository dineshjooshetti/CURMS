from django.urls import path
from . import bosc,course
from csm import csmc


urlpatterns = [
    path('', bosc.index, name='index'),
    path('programme', bosc.programme, name='programme'),
    path('create_program', bosc.create_program, name='create_program'),
    path('program_edit/<str:program_id>', bosc.program_edit, name='program_edit'),
    path('program_delete', bosc.program_delete, name='program_delete'),
    path('get_levels_by_ptype',bosc.get_levels_by_ptype,name='get_levels_by_ptype'),
    path('get_pcm_coordinators',bosc.get_pcm_coordinators,name="get_pcm_coordinators"),
    path('get_pcm_incharges',bosc.get_pcm_incharges,name="get_pcm_incharges"),
    path('bosc_program_detail/<str:p_id>',bosc.bosc_program_detail,name="bosc_program_detail"),
    path('program_structure_approve/<str:p_id>',bosc.program_structure_approve,name="program_structure_approve"),
    path('program_structure_need_more/<str:p_id>',bosc.program_structure_need_more,name="program_structure_need_more"),
    path('program_structure_syllabus_need_more/<str:p_id>',bosc.program_structure_syllabus_need_more,name="program_structure_syllabus_need_more"),
    path('forward_program_to_bos_by_bosc/<str:p_id>',bosc.forward_program_to_bos_by_bosc,name="forward_program_to_bos_by_bosc"),
    path('view_pab',bosc.view_pab,name="view_pab"),
    path('add_pab_user',bosc.add_pab_user,name="add_pab_user"),
    path('pab_upload',bosc.pab_upload,name="pab_upload"),
    path('get_pab_members',bosc.get_pab_members,name="get_pab_members"),
    path('assign_program_pab/<str:p_id>',bosc.assign_program_pab,name="assign_program_pab"),
    path('course_details/<str:course_id>', csmc.course_details, name='course_details'),
    path('course_structure_need_more/<str:c_id>', bosc.course_structure_need_more, name='course_structure_need_more'),
   
    

    #course
    path('course_assigned', course.course_assigned, name='course_assigned'),
    path('course_unassigned', course.course_unassigned, name='course_unassigned'),
    path('course_approved', course.course_approved, name='course_approved'),
    path('course_pending', course.course_pending, name='course_pending'),
    path('course_list', course.course_list, name='course_list'),
    path('course_upload', course.course_upload, name='course_upload'),
    path('course_edit/<str:course_id>', course.course_edit, name='course_edit'),
    path('course_del', course.course_del, name='course_del'),
    path('add_course', course.add_course, name='add_course'),
    path('bosc_course_final_submit', course.bosc_course_final_submit, name='bosc_course_final_submit'),
    path('course_preview/<str:course_id>',course.course_preview,name="course_preview"),
    path('course_need_more/<str:c_id>', course.course_need_more, name='course_need_more'),
     path('course_approve/<str:c_id>', course.course_approve, name='course_approve'),

   path('program_course_preview/<str:p_id>/<str:c_id>', bosc.program_course_preview, name='program_course_preview'),
    #ajax call validation
    path('validate_ltpjs_dept_inst_camp', course.validate_ltpjs_dept_inst_camp, name='validate_ltpjs_dept_inst_camp'),
    path('get_coursedepartment_by_campusinst', course.get_coursedepartment_by_campusinst, name='get_coursedepartment_by_campusinst'),


]