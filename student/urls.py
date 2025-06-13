from django.urls import path
from . import views

urlpatterns = [
    path('',views.student_list, name='student_list'),
    path('add/',views.add_student, name='add_student'),
    path('edit/<int:id>',views.edit_student,name='edit_student'),
    path('delete/<int:id>',views.delete_student,name='delete_student'),
    path('syllabus/add/', views.add_syllabus, name='add_syllabus'),
    path('syllabus/<int:course_id>/', views.view_syllabus, name='view_syllabus'),
    path('courses/union/', views.course_union_view, name='course_union'),
]
