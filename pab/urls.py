from django.urls import path
from . import pab

urlpatterns = [
    path('', pab.index, name='index'),
    path('programs', pab.programs, name='programs'),
    path('program_detail/<str:p_id>', pab.program_detail, name='program_detail'),
    path('program_structure_need_more/<str:p_id>', pab.program_structure_need_more, name='program_structure_need_more'),
    # path('program_structure_upload', pcmi.program_structure_upload, name='program_structure_upload'),
    # path('program_forward/<int:p_id>', pcmi.program_forward, name='program_forward'),
    # path('course_assign', pcmi.course_assign, name='course_assign'),
    # path('get_csm_incharges', pcmi.get_csm_incharges, name='get_csm_incharges'),
    path('course_preview/<str:course_id>', pab.course_preview, name='course_preview'),
    # path('course_structure_need_more/<str:c_id>', pcmi.course_structure_need_more, name='course_structure_need_more'),
    # path('course_structure_approve/<str:c_id>', pcmi.course_structure_approve, name='course_structure_approve'),
    # path('forward_program_to_bosc_by_pcmi/<str:p_id>', pcmi.forward_program_to_bosc_by_pcmi, name='forward_program_to_bosc_by_pcmi'),

]