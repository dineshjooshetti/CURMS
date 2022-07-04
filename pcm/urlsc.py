from django.urls import path
from . import pcmc

urlpatterns = [
    path('', pcmc.index, name='index'),
    path('pcmc_program_detail/<str:p_id>', pcmc.pcmc_program_detail, name='pcmc_program_detail'),
    path('course_preview/<str:course_id>', pcmc.course_preview, name='course_preview'),
    # path('update_file/<int:course_id>', views.update_file, name='update_file'),

]