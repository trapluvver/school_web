from django.contrib import admin
from .models import Task, Teacher, Cabinet, Subject, SchoolGroup, Student, Schedule
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.html import format_html
from django.template.response import TemplateResponse

from .views import teacher_report

admin.site.register(Task)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'post', 'lesson', 'category']
    list_filter = ['category', 'post']
    search_fields = ['full_name']
    # filter_horizontal = ['subjects'] # Для выбора предметов

    # Используем кастомный шаблон
    change_list_template = "admin/teachers/teacher_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('teachers-report/', self.teachers_report, name='teachers_report'), # Отчет о преподавательском составе

        ]
        return custom_urls + urls

    def teachers_report(self, request):
        # Получаем всех преподавателей
        teachers = Teacher.objects.all().order_by('full_name')

        # Контекст для шаблона
        context = {
            'teachers': teachers,
            'total_count': teachers.count(),
            'title': 'Отчет о преподавательском составе',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/report_template.html', context)


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ['number', 'teacher']
    list_filter = ['teacher']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'short_name', 'teachers_count']

    def teachers_count(self, obj):
        return obj.teacher_set.count()

    teachers_count.short_description = 'Количество учителей'

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