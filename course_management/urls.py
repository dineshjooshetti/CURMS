from django.urls import path
from . import views, course_operations

urlpatterns = [
    path('course_edit/<str:course_id>', course_operations.course_edit, name='course_edit'),
    path('course_del', course_operations.course_del, name='course_del'),
    # path('create_course', views.create_course, name='create_course'),
    # path('dev_details_save', views.dev_details_save, name='dev_details_save'),
    # path('course_details_save', views.course_details_save, name='course_details_save'),
    # path('about_course_save', views.about_course_save, name='about_course_save'),
    # path('syllabus_save', views.syllabus_save, name='syllabus_save'),
    # path('course_details/<str:course_id>', views.course_details, name='course_details'),
    # path('co_po_pso_save/<str:course_id>', views.co_po_pso_save, name='co_po_pso_save'),
    # path('course_preview/<str:course_id>', views.course_preview, name='course_preview'),
    # path('course_book_save', views.course_book_save, name='course_book_save'),
    # path('update_file/<int:course_id>', views.update_file, name='update_file'),
    # path('previous_step', views.previous_step, name='previous_step'),

]