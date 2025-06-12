from django.db import models

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

class Syllabus(models.Model):
    course = models.OneToOneField(Course,on_delete=models.CASCADE, related_name='syllabus')
    content = models.TextField()

    def __str__(self):
        return f"Syllabus of {self.course.title}"

class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    age = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='members')
    mark = models.IntegerField()
    clubs = models.ManyToManyField(Club, blank=True, related_name='members')
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.student.name}"