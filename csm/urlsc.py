from django.urls import path
from . import csmc





urlpatterns = [
    path('', csmc.index, name='index'),
    path('create_course', csmc.create_course, name='create_course'),
    path('dev_details_save', csmc.dev_details_save, name='dev_details_save'),
    path('course_details_save', csmc.course_details_save, name='course_details_save'),
    path('about_course_save', csmc.about_course_save, name='about_course_save'),
    path('syllabus_save', csmc.syllabus_save, name='syllabus_save'),
    path('course_details/<str:course_id>', csmc.course_details, name='course_details'),
    path('co_po_pso_save/<str:course_id>', csmc.co_po_pso_save, name='co_po_pso_save'),
    path('course_preview/<str:course_id>', csmc.course_preview, name='course_preview'),
    path('course_book_save/<str:course_id>', csmc.course_book_save, name='course_book_save'),
    path('update_file/<int:course_id>', csmc.update_file, name='update_file'),
    path('previous_step', csmc.previous_step, name='previous_step'),
    path('course_preview_submit/<str:course_id>', csmc.course_preview_submit, name='course_preview_submit'),
]