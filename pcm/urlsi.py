from django.urls import path
from . import pcmi
from csm import csmc

urlpatterns = [
    path('', pcmi.index, name='index'),
    path('programs', pcmi.programs, name='programs'),
    path('pcmi_program_detail/<str:p_id>', pcmi.pcmi_program_detail, name='pcmi_program_detail'),
    path('program_structure_upload', pcmi.program_structure_upload, name='program_structure_upload'),
    path('program_forward/<int:p_id>', pcmi.program_forward, name='program_forward'),
    path('course_assign', pcmi.course_assign, name='course_assign'),
    path('get_csm_incharges', pcmi.get_csm_incharges, name='get_csm_incharges'),
    path('course_preview_pcmi/<str:course_id>', pcmi.course_preview_pcmi, name='course_preview_pcmi'),
    path('course_structure_need_more/<str:c_id>', pcmi.course_structure_need_more, name='course_structure_need_more'),
    path('course_structure_approve/<str:c_id>', pcmi.course_structure_approve, name='course_structure_approve'),
    path('forward_program_to_bosc_by_pcmi/<str:p_id>', pcmi.forward_program_to_bosc_by_pcmi, name='forward_program_to_bosc_by_pcmi'),
    path('course_details/<str:course_id>', csmc.course_details, name='course_details'),
    path('add_course/<str:program_id>', pcmi.add_course, name='add_course'),
    path('get_campus', pcmi.get_campus, name='get_campus'),
    path('get_institution_by_campus', pcmi.get_institution_by_campus, name='get_institution_by_campus'),
    path('get_dept_by_institution', pcmi.get_dept_by_institution, name='get_dept_by_institution'),

    #new
    path('pcmi_co_po_pso_save/<str:course_id>', pcmi.pcmi_co_po_pso_save, name='pcmi_co_po_pso_save'),
    path('program_course_mapping', pcmi.program_course_mapping, name='program_course_mapping'),
    path('program_course_specific_outcome_delete', pcmi.program_course_specific_outcome_delete, name='program_course_specific_outcome_delete'),
    path('program_course_outcome_delete', pcmi.program_course_outcome_delete, name='program_course_outcome_delete'),
    path('program_course_category_count', pcmi.program_course_category_count, name='program_course_category_count'),
    path('pcmi_program_courses/<str:p_id>/<int:id>', pcmi.pcmi_program_courses, name='pcmi_program_courses'),
    path('po_pso_mapping/<str:p_id>/<int:c_id>', pcmi.po_pso_mapping, name='po_pso_mapping'),
    path('course_preview_by_pcmi/<str:p_id>/<str:c_id>', pcmi.course_preview_by_pcmi, name='course_preview_by_pcmi'),
    path('delete_course_from_program/<str:p_id>/<str:c_id>', pcmi.delete_course_from_program, name='delete_course_from_program'),

    #Minor Program Mapping
    path('minor_program_mapping/<str:p_id>', pcmi.minor_program_mapping, name='minor_program_mapping'),
    path('minor_core_programs_mapping', pcmi.minor_core_programs_mapping, name='minor_core_programs_mapping'),
    path('delete_minor_core_program/<str:p_id>/<str:mp_id>', pcmi.delete_minor_core_program, name='delete_minor_core_program'),
    #Baskets
    path('baskets/<str:p_id>/<int:id>', pcmi.baskets, name='baskets'),
    path('add_basket', pcmi.add_basket, name='add_basket'),
    path('basket_delete', pcmi.basket_delete, name='basket_delete'),
    #Groups
    path('groups/<str:p_id>/<int:id>', pcmi.groups, name='groups'),
    path('add_group', pcmi.add_group, name='add_group'),

    #minor program details
    path('pcmi_minor_program_detail/<str:p_id>', pcmi.pcmi_minor_program_detail, name='pcmi_minor_program_detail'),
    path('pcmi_minor_program_courses/<str:p_id>', pcmi.pcmi_minor_program_courses,name='pcmi_minor_program_courses'),

]