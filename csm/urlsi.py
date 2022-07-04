from django.urls import path
from . import csmi,csmc

urlpatterns = [
    path('', csmi.index, name='index'),
    path('course_details/<str:course_id>', csmc.course_details, name='course_details'),
    path('course_preview/<str:course_id>', csmi.course_preview, name='course_preview'),
    path('course_forward_to_faculty/<str:course_id>', csmi.course_forward_to_faculty, name='course_forward_to_faculty'),
    path('course_forward_to_bosc/<str:course_id>', csmi.course_forward_to_bosc, name='course_forward_to_bosc'),
    path('course_new_version_by_csmi/<str:course_id>', csmi.course_new_version_by_csmi, name='course_new_version_by_csmi'),

]