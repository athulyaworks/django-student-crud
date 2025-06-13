from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Course, Club, Profile, Syllabus
import datetime
from .forms import SyllabusForm
from django.db.models import Q, Avg, Max, Count, Subquery, OuterRef, Case, When, Value, CharField


# Create your views here.

def student_list(request):
    students = Student.objects.select_related('course', 'profile', 'course__syllabus').prefetch_related('clubs').all()

    filters = Q()

    course_title = request.GET.get('course')
    if course_title:
        filters &= Q(course__title__iexact=course_title)

    if request.GET.get('exclude_failed') == 'true':
        filters &= ~Q(mark__lt=35)

    search = request.GET.get('search')
    if search:
        filters &= Q(name__icontains=search)

    min_mark = request.GET.get('min_mark')
    max_mark = request.GET.get('max_mark')

    try:
        if min_mark:
            filters &= Q(mark__gte=int(min_mark))
        if max_mark:
            filters &= Q(mark__lte=int(max_mark))
    except ValueError:
        pass

    students = students.filter(filters)

    # Annotate pass/fail status
    students = students.annotate(
        status=Case(
            When(mark__gte=35, then=Value('Pass')),
            default=Value('Fail'),
            output_field=CharField()
        )
    )

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

    average_mark = students.aggregate(avg=Avg('mark'))['avg']
    max_mark = students.aggregate(max=Max('mark'))['max']

    students_per_course = Course.objects.annotate(student_count=Count('members'))

    latest_student_subquery = Student.objects.filter(course=OuterRef('pk')).order_by('-id')
    courses_with_latest = Course.objects.annotate(
        latest_student_name=Subquery(latest_student_subquery.values('name')[:1])
    )

    # UNION of courses with 'CS' or 'AI' in title
    cs_courses_qs = Course.objects.filter(title__icontains='Computer Science')
    ai_courses_qs = Course.objects.filter(title__icontains='Artificial Intelligence')
    union_courses = cs_courses_qs.union(ai_courses_qs)


    # INTERSECTION of students with mark>80 AND course title contains 'Data Science'
    high_mark_students = Student.objects.filter(mark__gt=80)
    data_science_students = Student.objects.filter(course__title__icontains='Data Science')
    intersection_students = high_mark_students.intersection(data_science_students)

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
        'empty_qs': empty_qs,
        'average_mark': average_mark,
        'max_mark': max_mark,
        'students_per_course': students_per_course,
        'courses_with_latest': courses_with_latest,
        'union_courses': union_courses,
        'intersection_students': intersection_students,
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

def course_union_view(request):
    cs_courses = Course.objects.filter(title__icontains='Computer Science').values('id', 'title')
    ai_courses = Course.objects.filter(title__icontains='Artificial Intelligence').values('id', 'title')

    union_courses = cs_courses.union(ai_courses).order_by('title')

    return render(request, 'student/courses_union.html', {
        'courses': union_courses,
    })
