from django.contrib import admin
from .models import *
from django.urls import path
from django.shortcuts import render
from django import forms


admin.site.register(Task)

class TeacherAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'subjects': forms.SelectMultiple(attrs={'class': 'selector'}),
        }


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'post', 'get_subjects_display', 'category', 'experience']
    list_filter = ['category', 'post', 'subjects']
    search_fields = ['full_name', 'post', 'education']
    filter_horizontal = ['subjects']
    list_per_page = 20

    # Используем кастомный шаблон
    change_list_template = "admin/teachers/teacher_change_list.html"

    # Поля для формы редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'post', 'category', 'experience')
        }),
        ('Образование и предметы', {
            'fields': ('education', 'prof_retrain')
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('teachers-report/', self.teachers_report, name='teachers_report'),
        ]
        return custom_urls + urls

    def teachers_report(self, request):
        # Получаем всех преподавателей с оптимизацией запроса
        teachers = Teacher.objects.all().prefetch_related('subjects').order_by('full_name')

        # Статистика по категориям
        from django.db.models import Count
        categories_stats = Teacher.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')

        # Статистика по должностям
        posts_stats = Teacher.objects.values('post').annotate(
            count=Count('id')
        ).order_by('-count')

        # Контекст для шаблона
        context = {
            'teachers': teachers,
            'total_count': teachers.count(),
            'categories_stats': categories_stats,
            'posts_stats': posts_stats,
            'title': 'Отчет о преподавательском составе',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/report_template.html', context)

    # Дополнительные методы для админки
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('subjects')

        # Добавляем subjects в форму отдельно

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Добавляем поле subjects в нужный fieldset
        fieldsets[1][1]['fields'] = ('education', 'subjects', 'prof_retrain')
        return fieldsets


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

