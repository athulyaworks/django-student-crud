from django.shortcuts import render, redirect, get_object_or_404
from .models import Student
import datetime

# Create your views here.

def student_list(request):
    students = Student.objects.all()

    #filtering by course 
    course = request.GET.get('course')
    if course:
        students = students.filter(course__iexact=course)

    #excluding students with mark<35(F)
    exclude_failed = request.GET.get('exclude_failed')
    if exclude_failed == 'true':
        students = students.exclude(mark__lt=35) #less than lookup

    return render(request, 'student/student_list.html', {'students': students})

def add_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        dob = request.POST['dob']
        age = request.POST['age']
        course = request.POST['course']
        mark = request.POST['mark']

        Student.objects.create(name=name, dob=dob, age=age, course=course, mark=mark)
        return redirect('student_list')

    return render(request, 'student/add_student.html')


def edit_student(request, id):
    student = get_object_or_404(Student, id=id)
    
    if request.method == 'POST':
        dob_str = request.POST.get('dob')
        if not dob_str:
            return render(request, 'student/edit_student.html', {
                'student': student,
                'error': 'Date of birth is required.'
            })
        
        dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()

        student.name = request.POST['name']
        student.dob = dob
        student.age = request.POST['age']
        student.course = request.POST['course']
        student.mark = request.POST['mark']
        student.save()
        
        return redirect('student_list')
    
    return render(request, 'student/edit_student.html', {'student': student})


def delete_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'student/delete_student.html',{'student':student})
