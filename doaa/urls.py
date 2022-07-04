from django.urls import path
from . import doaa,reports
from .pdf import Pdf

urlpatterns = [
   path('', doaa.index, name='index'),
    path('dept_index', doaa.dept_index, name='dept_index'),
    path('doaa_program_detail/<str:p_id>',doaa.doaa_program_detail,name="doaa_program_detail"),
    path('forward_program_to_pre_ac_by_doaa/<str:p_id>',doaa.forward_program_to_pre_ac_by_doaa,name="forward_program_to_pre_ac_by_doaa"),
    path('program_structure_need_more_doaa/<str:p_id>',doaa.program_structure_need_more_doaa,name="program_structure_need_more_doaa"),
    path('program_publish_by_doaa/<str:p_id>',doaa.program_publish_by_doaa,name="program_publish_by_doaa"),
    path('course_preview_doaa/<str:course_id>',doaa.course_preview_doaa,name="course_preview_doaa"),
    # # path('course_structure_need_more/<str:c_id>', doaa.course_structure_need_more, name='course_structure_need_more'),
    # # path('course_structure_approve/<str:c_id>', doaa.course_structure_approve, name='course_structure_approve'),
    # # path('course_structure_notapprove/<str:c_id>', doaa.course_structure_notapprove, name='course_structure_notapprove'),
    path('curriculum_status',reports.curriculum_status,name="curriculum_status"),
    path('curriculum_status_program_details/<str:program_id>',reports.curriculum_status_program_details,name="curriculum_status_program_details"),
    path('curriculum_status_download/<str:program_id>',reports.curriculum_status_download,name="curriculum_status_download"),
    path('render/pdf/<str:p_id>', Pdf.as_view()),
    path('program_course_preview/<str:p_id>/<str:c_id>', doaa.program_course_preview, name='program_course_preview'),
    path('doaa_approve/<str:p_id>', doaa.doaa_approve, name='doaa_approve'),

]