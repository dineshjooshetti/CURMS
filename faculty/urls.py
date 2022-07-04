from django.urls import path
from . import staff

urlpatterns = [
    path('', staff.index, name='index'),
    path('course_preview_staff/<str:course_id>', staff.course_preview_staff, name='course_preview_staff'),
    path('staff_suggestion/<str:c_id>', staff.staff_suggestion, name='staff_suggestion'),
]