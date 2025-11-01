from django.contrib import admin
from .models import Task, Teacher, Cabinet, Subject, SchoolGroup, Student, Schedule


admin.site.register(Task)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'post', 'category', 'lesson']
    search_fields = ['fio']

@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ['number', 'teacher']
    list_filter = ['teacher']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'short_name']

@admin.register(SchoolGroup)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['number', 'teacher', 'cabinet']
    list_filter = ['teacher']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'school_class', 'phone']
    list_filter = ['school_class']
    search_fields = ['full_name']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['subject', 'cabinet', 'school_class']
    list_filter = ['school_class', 'subject']