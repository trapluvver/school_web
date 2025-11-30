from django.contrib import admin
from .models import *
from django.urls import path
from django.shortcuts import render

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'post', 'get_subjects_display', 'category', 'experience']
    list_filter = ['category', 'post', 'subjects']
    search_fields = ['full_name', 'post', 'education']
    filter_horizontal = ['subjects']
    list_per_page = 20

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('teachers-report/', self.teachers_report, name='teachers_report'),
            path('subjects-teachers-report/', self.subjects_teachers_report, name='subjects_teachers_report'),
            # НОВЫЙ ОТЧЕТ
        ]
        return custom_urls + urls

    def subjects_teachers_report(self, request):

        """Отчет по предметам и преподавателям"""
        # Получаем все предметы с преподавателями
        subjects = Subject.objects.all().prefetch_related('teacher_set').order_by('full_name')

        # Статистика
        total_subjects = subjects.count()
        subjects_with_teachers = subjects.filter(teacher__isnull=False).distinct().count()
        subjects_without_teachers = total_subjects - subjects_with_teachers

        # Группируем данные для отчета
        subject_data = []
        for subject in subjects:
            teachers = subject.teacher_set.all()
            subject_data.append({
                'subject': subject,
                'teachers': teachers,
                'teachers_count': teachers.count()
            })

        context = {
            'subject_data': subject_data,
            'total_subjects': total_subjects,
            'subjects_with_teachers': subjects_with_teachers,
            'subjects_without_teachers': subjects_without_teachers,
            'title': 'Отчет по предметам и преподавателям',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/subjects_teachers_report.html', context)

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
    list_display = [
        'day_of_week_display',
        'lesson_display',
        'subject',
        'school_class',
        'cabinet'
    ]
    list_filter = ['day_of_week', 'lesson_number', 'subject', 'school_class']
    search_fields = ['subject__full_name', 'school_class__number']
    list_per_page = 20

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()
    day_of_week_display.short_description = 'День недели'

    def lesson_display(self, obj):
        return obj.get_lesson_number_display()
    lesson_display.short_description = 'Урок'

    # Поля для формы редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('day_of_week', 'lesson_number', 'info')
        }),
        ('Расписание', {
            'fields': ('subject', 'school_class', 'cabinet')
        }),
    )


# Список дополнительных занятий
@admin.register(ExtraActivity)
class ExtraActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'activity_type', 'teacher', 'max_students', 'is_active']
    list_filter = ['activity_type', 'is_active', 'teacher']
    search_fields = ['name', 'description', 'teacher__full_name']
    list_editable = ['is_active']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'activity_type')
        }),
        ('Организация', {
            'fields': ('teacher', 'max_students', 'is_active')
        }),
    )

# Расписание дополнительных занятий
@admin.register(ExtraSchedule)
class ExtraScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'day_of_week_display',
        'lesson_display',
        'activity',
        'teacher',
        'cabinet'
    ]
    list_filter = ['day_of_week', 'lesson_number', 'activity__activity_type']
    search_fields = ['activity__name', 'cabinet__number']

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()

    day_of_week_display.short_description = 'День недели'

    def lesson_display(self, obj):
        return obj.get_lesson_number_display()

    lesson_display.short_description = 'Время'

    def teacher(self, obj):
        return obj.activity.teacher

    teacher.short_description = 'Преподаватель'

    fieldsets = (
        ('Расписание', {
            'fields': ('day_of_week', 'lesson_number', 'cabinet')
        }),
        ('Занятие', {
            'fields': ('activity',)
        }),
    )