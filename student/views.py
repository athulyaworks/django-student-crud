from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Course,Club, Profile, Syllabus
import datetime
from .forms import SyllabusForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SyllabusForm



# Create your views here.

def student_list(request):
    students = Student.objects.select_related('course', 'profile', 'course__syllabus').prefetch_related('clubs').all()

    # Filter by course title
    course_title = request.GET.get('course')
    if course_title:
        students = students.filter(course__title__iexact=course_title)

    # Exclude failed students (mark < 35)
    if request.GET.get('exclude_failed') == 'true':
        students = students.exclude(mark__lt=35)

    # Search by name (case-insensitive)
    search = request.GET.get('search')
    if search:
        students = students.filter(name__icontains=search)

    # Filter by min_mark and max_mark independently
    min_mark = request.GET.get('min_mark')
    max_mark = request.GET.get('max_mark')

    try:
        if min_mark:
            min_mark_val = int(min_mark)
            students = students.filter(mark__gte=min_mark_val)  # mark >= min_mark
        if max_mark:
            max_mark_val = int(max_mark)
            students = students.filter(mark__lte=max_mark_val)  # mark <= max_mark
    except ValueError:
        
        pass

    #summary
    first_student = students.first()
    last_student = students.last()
    student_exists = students.exists()
    total_students = students.count()
    student_data = students.values('name', 'mark')
    names = students.values_list('name', flat=True)
    distinct_courses = Course.objects.values_list('title', flat=True).distinct()
    ordered_students = students.order_by('-mark')
    top_students = students.order_by('-mark')[:5]
    empty_qs = not student_exists

    return render(request, 'student/student_list.html', {
        'students': students,
        'first_student': first_student,
        'last_student': last_student,
        'student_exists': student_exists,
        'total_students': total_students,
        'distinct_courses': distinct_courses,
        'ordered_students': ordered_students,
        'student_data': student_data,
        'names': names,
        'top_students': top_students,
        'empty_qs': empty_qs
    })




def add_student(request):
    courses = Course.objects.all()
    clubs = Club.objects.all()

    if request.method == "POST":
        name = request.POST['name']
        dob = request.POST['dob']
        age = request.POST['age']
        course_id = request.POST['course']
        mark = request.POST['mark']
        bio = request.POST.get('bio','')  
        club_ids = request.POST.getlist('clubs')  

        course = Course.objects.get(id=course_id)
        student = Student.objects.create(
            name=name,
            dob=dob,
            age=age,
            course=course,
            mark=mark,
            
        )

        if club_ids:
            student.clubs.set(club_ids)  

        Profile.objects.create(student=student, bio=bio)
        
        return redirect('student_list')

    return render(request, 'student/add_student.html', {
        'courses': courses,
        'clubs': clubs
    })

def edit_student(request, id):
    student = get_object_or_404(Student, id=id)
    courses = Course.objects.all()
    clubs = Club.objects.all()

    if request.method == 'POST':
        dob_str = request.POST.get('dob')
        if not dob_str:
            return render(request, 'student/edit_student.html', {
                'student': student,
                'error': 'Date of birth is required.',
                'courses':courses,
                'clubs':clubs
            })
        
        dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()

        student.name = request.POST['name']
        student.dob = dob
        student.age = request.POST['age']
        course_id = request.POST['course']
        student.course = Course.objects.get(id=course_id)
        student.bio = request.POST.get('bio','')
        student.mark = request.POST['mark']
        
        club_ids = request.POST.getlist('clubs')
        if club_ids:
            student.clubs.set(club_ids)
        else:
            student.clubs.clear()

        student.save()

        bio = request.POST.get('bio', '')
        profile, created = Profile.objects.get_or_create(student=student)
        profile.bio = bio
        profile.save()
        
        return redirect('student_list')
    
    return render(request, 'student/edit_student.html', {
        'student':student,
        'courses':courses,
        'clubs':clubs
        })

def delete_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'student/delete_student.html',{'student':student})


from django.shortcuts import render, redirect, get_object_or_404
from .forms import SyllabusForm
from .models import Course

def add_syllabus(request):
    if request.method == 'POST':
        form = SyllabusForm(request.POST)
        if form.is_valid():
            
            syllabus = form.save(commit=False)
            
            existing = Syllabus.objects.filter(course=syllabus.course).first()
            if existing:
                existing.content = syllabus.content
                existing.save()
            else:
                syllabus.save()
            return redirect('student_list')
    else:
        form = SyllabusForm()

    return render(request, 'student/add_syllabus.html', {'form': form})


def view_syllabus(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    syllabus = getattr(course, 'syllabus', None)  

    return render(request, 'student/view_syllabus.html', {
        'course': course,
        'syllabus': syllabus
    })