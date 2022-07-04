from django.urls import path
from . import bos

urlpatterns = [
    path('', bos.index, name='index'),
    path('bos_program_detail/<str:p_id>',bos.bos_program_detail,name="bos_program_detail"),
    path('forward_program_to_doaa_by_bos/<str:p_id>',bos.forward_program_to_doaa_by_bos,name="forward_program_to_doaa_by_bos"),
    path('program_structure_need_more_bos/<str:p_id>',bos.program_structure_need_more_bos,name="program_structure_need_more_bos"),
    path('course_preview_bos/<str:course_id>',bos.course_preview_bos,name="course_preview_bos"),
    path('course_structure_need_more/<str:c_id>', bos.course_structure_need_more, name='course_structure_need_more'),
    path('course_structure_approve/<str:c_id>', bos.course_structure_approve, name='course_structure_approve'),

    # path('program_course_preview/<str:p_id>/<str:c_id>', bos.program_course_preview, name='program_course_preview'),
]